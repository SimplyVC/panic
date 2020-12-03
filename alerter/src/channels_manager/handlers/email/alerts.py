import json
import logging
from enum import Enum
from queue import Queue
from types import FrameType

import pika
from pika.adapters.blocking_connection import BlockingChannel

from src.alerter.alert_code import AlertCode
from src.alerter.alerts.alert import Alert
from src.channels_manager.handlers import ChannelHandler
from src.configs.email_channel import EmailChannelConfig
from src.message_broker.rabbitmq import RabbitMQApi
from src.utils.constants import ALERT_EXCHANGE


class EmailAlertsHandler(ChannelHandler):
    def __init__(self, handler_name: str, logger: logging.Logger,
                 rabbit_ip: str, queue_size: int, config: EmailChannelConfig):
        super().__init__(handler_name, logger)
        self._config = config
        self._alerts_queue = Queue(queue_size)

        self._rabbit = RabbitMQApi(logger=logger.getChild(RabbitMQApi.__name__),
                                   host=rabbit_ip)

    def _process_alert(self, ch: BlockingChannel,
                       method: pika.spec.Basic.Deliver,
                       properties: pika.spec.BasicProperties,
                       body: bytes) -> None:
        alert_json = json.loads(body)
        self.logger.info("Received and processing alert: %s", alert_json)
        processing_error = False
        try:
            # We check that everything is in the alert dict
            alert_code = alert_json['alert_code']
            alert_code_enum = AlertCode.get_enum_by_value(alert_code['code'])
            alert = Alert(alert_code_enum, alert_json['message'],
                          alert_json['severity'], alert_json['timestamp'],
                          alert_json['parent_id'], alert_json['origin_id'])
            self.logger.info("Successfully processed {}".format(alert_json))
        except Exception as e:
            self.logger.error("Error when processing {}".format(alert_json))
            self.logger.exception(e)
            processing_error = True



    def _initialise_rabbitmq(self) -> None:
        email_channel_queue_name = "email_{}_alerts_handler_queue".format(
            self._config.id_)
        email_channel_routing_key = "channel.{}".format(self._config.id_)

        self._rabbit.connect_till_successful()

        # Set consuming configuration
        self.logger.info("Creating %s exchange", ALERT_EXCHANGE)
        self._rabbit.exchange_declare(ALERT_EXCHANGE, 'topic', False, True,
                                      False, False)
        self.logger.info(
            "Creating queue 'email_%s_alerts_handler_queue'", self._config.id_)
        self._rabbit.queue_declare(email_channel_queue_name, False, True, False,
                                   False)

        self.logger.info(
            "Binding queue '%s' to exchange '%s' with routing key 'channel.%s'",
            email_channel_queue_name, ALERT_EXCHANGE, email_channel_routing_key
        )
        self._rabbit.queue_bind(email_channel_queue_name, ALERT_EXCHANGE,
                                email_channel_routing_key)

        # Pre-fetch count is 5 times less the maximum queue size
        prefetch_count = round(self._alerts_queue.maxsize / 5)
        self._rabbit.basic_qos(prefetch_count=prefetch_count)
        self.logger.info("Declaring consuming intentions")
        self._rabbit.basic_consume(email_channel_queue_name,
                                   self._process_alert, False,
                                   False, None)

    def disconnect(self):
        self._rabbit.disconnect_till_successful()

    def start(self) -> None:
        pass

    def on_terminate(self, signum: int, stack: FrameType) -> None:
        pass
