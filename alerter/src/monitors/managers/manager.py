import logging
import os
from typing import Dict

import pika.exceptions

from alerter.src.message_broker.rabbitmq.rabbitmq_api import RabbitMQApi


class MonitorManager:
    def __init__(self, logger: logging.Logger, name: str):
        self._logger = logger
        self._config_process_dict = {}
        self._name = name

        # rabbit_ip = os.environ["RABBIT_IP"]
        self._rabbitmq = RabbitMQApi(logger=self.logger, host='localhost')

    def __str__(self) -> str:
        return self.name

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def rabbitmq(self) -> RabbitMQApi:
        return self._rabbitmq

    @property
    def config_process_dict(self) -> Dict:
        return self._config_process_dict

    @property
    def name(self) -> str:
        return self._name

    def _initialize_rabbitmq(self) -> None:
        pass

    def _listen_for_configs(self) -> None:
        pass

    def _process_configs(
            self, ch, method: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties, body: bytes) -> None:
        pass

    def manage(self) -> None:
        pass
