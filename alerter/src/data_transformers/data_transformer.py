from abc import ABC, abstractmethod
from typing import Dict
import logging
import os

import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel

from src.data_store.redis.redis_api import RedisApi
from src.message_broker.rabbitmq.rabbitmq_api import RabbitMQApi
from src.moniterables.system import System


class DataTransformer(ABC):
    def __init__(self, transformer_name: str, logger: logging.Logger,
                 redis: RedisApi) -> None:
        self._transformer_name = transformer_name
        self._logger = logger
        self._redis = redis
        self._data_for_saving = {}
        self._data_for_alerting = {}
        self._state = {}

        rabbit_ip = os.environ["RABBIT_IP"]
        self._rabbitmq = RabbitMQApi(logger=self.logger, host=rabbit_ip)

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
    def data_for_saving(self) -> Dict:
        return self._data_for_saving

    @property
    def data_for_alerting(self) -> Dict:
        return self._data_for_alerting

    # TODO: Need to change output type to Dict[str, Union[System, Repo]]
    @property
    def state(self) -> Dict[str, System]:
        return self._state

    @property
    def rabbitmq(self) -> RabbitMQApi:
        return self._rabbitmq

    @abstractmethod
    def _initialize_rabbitmq(self) -> None:
        pass

    @abstractmethod
    def load_transformer_state(self) -> None:
        pass

    @abstractmethod
    def _listen_for_data(self) -> None:
        pass

    @abstractmethod
    def _transform_data_for_storage(self) -> None:
        pass

    @abstractmethod
    def _transform_data_for_alerting(self) -> None:
        pass

    @abstractmethod
    def _send_data_for_saving(self) -> None:
        pass

    @abstractmethod
    def _send_data_for_alerting(self) -> None:
        pass

    @abstractmethod
    def _transform_data(self, ch: BlockingChannel,
                        method: pika.spec.Basic.Deliver,
                        properties: pika.spec.BasicProperties, body: bytes) \
            -> None:
        pass

    def start(self) -> None:
        pass

# TODO: Must handle processing errors (handle as written on design paper)
# TODO: Must handle data received with `error` from monitors (handle as written
#     : on design paper
# TODO: Must check if Redis can be shared across process including it's logger,
#     : otherwise must use a different Redis for each process. i.e. declare
#     : redis here and do not pass it as parameter
# TODO: To store data Vitaly only needs the system_id and parent_id
# TODO: We will use system_id. If the user modifies a part of the
#     : config it means he wants to monitor on the same data
# TODO: In case we decrease per interval, make sure the data is not smaller
#     : but should be this handled in the alerter? It will be handled in the
#     : installer but if this is the case is should be handled in the alerter
# TODO: Must do proper error handling including errors in processing, getting
#     : data etc
