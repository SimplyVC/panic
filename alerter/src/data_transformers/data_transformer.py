import logging
import os
from abc import ABC, abstractmethod
from queue import Queue
from typing import Dict, Union

import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel

from src.data_store.redis.redis_api import RedisApi
from src.message_broker.rabbitmq.rabbitmq_api import RabbitMQApi
from src.monitorables.repo import GitHubRepo
from src.monitorables.system import System
from src.utils.exceptions import MessageWasNotDeliveredException


class DataTransformer(ABC):
    def __init__(self, transformer_name: str, logger: logging.Logger,
                 redis: RedisApi) -> None:
        self._transformer_name = transformer_name
        self._logger = logger
        self._redis = redis
        self._transformed_data = {}
        self._data_for_saving = {}
        self._data_for_alerting = {}
        self._state = {}

        # Set a max queue size so that if the data transformer is not able to
        # send data, old data can be pruned
        max_queue_size = int(os.environ[
                                 "DATA_TRANSFORMER_PUBLISHING_QUEUE_SIZE"])
        self._publishing_queue = Queue(max_queue_size)

        rabbit_ip = os.environ["RABBIT_IP"]
        self._rabbitmq = RabbitMQApi(logger=self.logger, host=rabbit_ip)

    def __str__(self) -> str:
        return self.transformer_name

    @property
    def transformer_name(self) -> str:
        return self._transformer_name

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def redis(self) -> RedisApi:
        return self._redis

    @property
    def transformed_data(self) -> Dict:
        return self._transformed_data

    @property
    def data_for_saving(self) -> Dict:
        return self._data_for_saving

    @property
    def data_for_alerting(self) -> Dict:
        return self._data_for_alerting

    @property
    def state(self) -> Dict[str, Union[System, GitHubRepo]]:
        return self._state

    @property
    def rabbitmq(self) -> RabbitMQApi:
        return self._rabbitmq

    @property
    def publishing_queue(self) -> Queue:
        return self._publishing_queue

    @abstractmethod
    def _initialize_rabbitmq(self) -> None:
        pass

    @abstractmethod
    def load_state(self, monitorable: Union[System, GitHubRepo]) \
            -> Union[System, GitHubRepo]:
        pass

    def _listen_for_data(self) -> None:
        self.rabbitmq.start_consuming()

    @abstractmethod
    def _update_state(self) -> None:
        pass

    @abstractmethod
    def _process_transformed_data_for_saving(self) -> None:
        pass

    @abstractmethod
    def _process_transformed_data_for_alerting(self) -> None:
        pass

    @abstractmethod
    def _transform_data(self, data: Dict) -> None:
        pass

    @abstractmethod
    def _place_latest_data_on_queue(self) -> None:
        pass

    @abstractmethod
    def _send_data(self) -> None:
        pass

    @abstractmethod
    def _process_raw_data(self, ch: BlockingChannel,
                          method: pika.spec.Basic.Deliver,
                          properties: pika.spec.BasicProperties, body: bytes) \
            -> None:
        pass

    def start(self) -> None:
        self._initialize_rabbitmq()
        while True:
            try:
                # Before listening for new data send the data waiting to be sent
                # in the publishing queue. If the message is not routed, start
                # consuming and perform sending later.
                try:
                    self._send_data()
                except MessageWasNotDeliveredException as e:
                    self.logger.exception(e)

                self._listen_for_data()
            except pika.exceptions.AMQPChannelError:
                # Error would have already been logged by RabbitMQ logger. If
                # there is a channel error, the RabbitMQ interface creates a new
                # channel, therefore we can safely continue
                continue
            except pika.exceptions.AMQPConnectionError as e:
                # Error would have already been logged by RabbitMQ logger.
                # Since we have to re-connect just break the loop.
                raise e
            except Exception as e:
                self.logger.exception(e)
                raise e