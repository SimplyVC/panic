import logging
from abc import ABC

from src.abstract.publisher_subscriber import PublisherSubscriberComponent
from src.message_broker.rabbitmq import RabbitMQApi


class ChannelHandler(PublisherSubscriberComponent, ABC):
    def __init__(self, handler_name: str, logger: logging.Logger,
                 rabbitmq: RabbitMQApi) -> None:
        super().__init__(logger, rabbitmq)

        self._handler_name = handler_name

    def __str__(self) -> str:
        return self.handler_name

    @property
    def handler_name(self) -> str:
        return self._handler_name

    def _listen_for_data(self) -> None:
        self.rabbitmq.start_consuming()
