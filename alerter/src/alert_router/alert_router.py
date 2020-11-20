import json
import sys
from configparser import ConfigParser, NoOptionError, NoSectionError, \
    ParsingError
from logging import Logger
from threading import RLock
from types import FrameType
from typing import Dict

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from src.abstract.component import Component
from src.message_broker.publisher import QueuingPublisher
from src.message_broker.rabbitmq import RabbitMQApi
from src.utils import env
from src.utils.constants import CONFIG_EXCHANGE, ALERTER_EXCHANGE, \
    CHANNEL_EXCHANGE, STORE_EXCHANGE
from src.utils.exceptions import ConnectionNotInitializedException, \
    MessageWasNotDeliveredException
from src.utils.logging import log_and_print

ALERT_ROUTER_CONFIGS_QUEUE_NAME = "alert_router_configs_queue"
ALERT_ROUTER_INPUT_QUEUE_NAME = "alert_router_input_queue"


class AlertRouter(Component, QueuingPublisher):
    def __init__(self, logger: Logger, rabbit_ip: str):
        self._rabbit = RabbitMQApi(logger.getChild("rabbitmq"), host=rabbit_ip)
        self._enable_console_output = env.ENABLE_CONSOLE_OUTPUT

        # We need to ensure that the config is not read when it is written to.
        # The GIL helps that, but making it explicit is also nice
        self._config_lock = RLock()
        self._config = {}

        self._logger = logger
        super(Component, self).__init__()
        super(QueuingPublisher, self).__init__(
            logger.getChild(QueuingPublisher.__name__), self._rabbit)

    def _initialise_rabbit(self) -> None:
        """
        Initialises the rabbit connection and the exchanges needed
        :return: None
        """
        while True:
            try:
                self._rabbit.connect_till_successful()
                self._logger.info(
                    "Setting delivery confirmation on RabbitMQ channel")
                self._rabbit.confirm_delivery()

                self._declare_exchange_and_bind_queue(
                    ALERT_ROUTER_CONFIGS_QUEUE_NAME, CONFIG_EXCHANGE,
                    "channels.*"
                )
                self._rabbit.basic_consume(
                    queue=ALERT_ROUTER_CONFIGS_QUEUE_NAME,
                    on_message_callback=self._process_configs, auto_ack=False,
                    exclusive=False, consumer_tag=None)

                self._declare_exchange_and_bind_queue(
                    ALERT_ROUTER_INPUT_QUEUE_NAME, ALERTER_EXCHANGE, "#"
                )
                self._rabbit.basic_consume(
                    queue=ALERT_ROUTER_INPUT_QUEUE_NAME,
                    on_message_callback=self._process_alert, auto_ack=False,
                    exclusive=False, consumer_tag=None
                )

                # Declare output exchange
                self._logger.info("Creating %s exchange", CHANNEL_EXCHANGE)
                self._rabbit.exchange_declare(
                    CHANNEL_EXCHANGE, "topic", False, True, False,
                    False
                )

                self._rabbit.confirm_delivery()
                break
            except (ConnectionNotInitializedException,
                    AMQPConnectionError) as connection_error:
                # Should be impossible, but since exchange_declare can throw
                # it we shall ensure to log that the error passed through here
                # too.
                self._logger.error(
                    "Something went wrong that meant a connection was not made")
                self._logger.error(connection_error.message)
                raise connection_error
            except AMQPChannelError:
                # We need to re-initialize the connection
                continue

    def _declare_exchange_and_bind_queue(self, queue_name: str,
                                         exchange_name: str,
                                         routing_key: str) -> None:
        """
        Declare the specified exchange and queue and binds that queue to the
        exchange
        :param queue_name: The queue to declare and bind to the exchange
        :param exchange_name: The exchange to declare and bind the queue to
        :return: None
        """
        self._logger.info("Creating %s exchange", exchange_name)
        self._rabbit.exchange_declare(
            exchange_name, "topic", False, True, False, False
        )
        self._logger.info("Creating and binding queue for %s exchange",
                          exchange_name)
        self._logger.debug("Creating queue %s", queue_name)
        self._rabbit.queue_declare(queue_name, False, True, False, False)
        self._logger.debug("Binding queue %s to %s exchange", queue_name,
                           exchange_name)
        self._rabbit.queue_bind(queue_name, exchange_name, routing_key)

    def _process_configs(self, ch: BlockingChannel,
                         method: pika.spec.Basic.Deliver,
                         properties: pika.spec.BasicProperties,
                         body: bytes) -> None:

        recv_config = ConfigParser()
        recv_config.read_dict(json.loads(body))
        config_filename = method.routing_key

        self._logger.info("Received a new configuration from %s",
                          config_filename)
        self._logger.debug("recv_config = %s", recv_config)

        with self._config_lock:
            self._logger.debug("Got a lock on the config")
            previous_config = self._config.get(config_filename, None)
            self._config[config_filename] = {}

            # Only take from the config if it is not empty
            if recv_config:
                # Taking what we need, and checking types
                try:
                    for key in recv_config.sections():
                        self._config[config_filename][key] = {
                            'id': recv_config.get(key, 'id'),
                            'info': recv_config.getboolean(key, 'info'),
                            'warning': recv_config.getboolean(key, 'warning'),
                            'critical': recv_config.getboolean(key, 'critical'),
                            'error': recv_config.getboolean(key, 'error')
                        }
                except (NoOptionError, NoSectionError) as missing_error:
                    self._logger.error(
                        "The configuration file %s is missing some configs",
                        config_filename)
                    self._logger.error(missing_error.message)
                    self._logger.warning(
                        "The previous configuration will be used instead")
                    self._config[config_filename] = previous_config
                except (ParsingError, ValueError) as parsing_error:
                    self._logger.error(
                        "The configuration file %s has an incorrect entry",
                        config_filename)
                    self._logger.error(parsing_error.message)
                    self._logger.warning(
                        "The previous configuration will be used instead")
                    self._config[config_filename] = previous_config
            self._logger.debug(self._config)
        self._logger.debug("Removed the lock from the config dict")

        self._rabbit.basic_ack(method.delivery_tag, False)

    def _process_alert(self, ch: BlockingChannel,
                       method: pika.spec.Basic.Deliver,
                       properties: pika.spec.BasicProperties,
                       body: bytes) -> None:
        recv_alert: Dict = json.loads(body)
        self._logger.debug("recv_alert = %s", recv_alert)

        # Where to route this alert to
        with self._config_lock:
            self._logger.debug("Got a lock on the config")
            self._logger.debug("Obtaining list of channels to alert")
            self._logger.debug(
                [channel.get('id') for channel_type in self._config.values()
                 for channel in channel_type.values()])
            send_to_ids = [
                channel.get('id') for channel_type in self._config.values()
                for channel in channel_type.values()
                if channel.get(recv_alert.get('severity').lower())
            ]
        self._logger.debug("Removed the lock from the config dict")
        self._logger.debug("send_to_ids = %s", send_to_ids)

        for channel_id in send_to_ids:
            send_alert: Dict = {**recv_alert,
                                'destination_id': channel_id}

            self._logger.debug("Queuing %s to be sent to %s",
                               send_alert, channel_id)

            self._push_to_queue(send_alert, CHANNEL_EXCHANGE,
                                f"channel.{channel_id}")
            self._logger.info("Routed Alert queued")

        # Enqueue once to the console
        if self._enable_console_output:
            self._push_to_queue(
                {**recv_alert, 'destination_id': "console"},
                CHANNEL_EXCHANGE, "channel.console")

        # Enqueue once to the data store
        self._push_to_queue(recv_alert, STORE_EXCHANGE, "alert")

        self._rabbit.basic_ack(method.delivery_tag, False)

        # Send any data waiting in the publisher queue, if any
        try:
            self._send_data()
        except MessageWasNotDeliveredException as e:
            # Log the message and do not raise it as message is residing in the
            # publisher queue.
            self._logger.exception(e)

    def start(self) -> None:
        self._initialise_rabbit()
        while True:
            try:
                # Before listening for new data send the data waiting to be sent
                # in the publishing queue. If the message is not routed, start
                # consuming and perform sending later.
                try:
                    self._send_data()
                except MessageWasNotDeliveredException as e:
                    self._logger.exception(e)

                self._logger.info("Starting the alert router listeners")
                self._rabbit.start_consuming()
            except (pika.exceptions.AMQPConnectionError,
                    pika.exceptions.AMQPChannelError) as e:
                # If we have either a channel error or connection error, the
                # channel is reset, therefore we need to re-initialize the
                # connection or channel settings
                raise e
            except Exception as e:
                self._logger.exception(e)
                raise e

    def on_terminate(self, signum: int, stack: FrameType) -> None:
        log_and_print("{} is terminating. Connections with RabbitMQ will be "
                      "closed, and afterwards the process will exit."
                      .format(self), self._logger)
        self._rabbit.disconnect_till_successful()
        log_and_print("{} terminated.".format(self), self._logger)
        sys.exit()
