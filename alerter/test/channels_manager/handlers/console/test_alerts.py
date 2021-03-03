import logging
import unittest
from datetime import timedelta
from unittest import mock

import pika

from src.channels_manager.channels.console import ConsoleChannel
from src.channels_manager.handlers.console.alerts import ConsoleAlertsHandler, \
    CONSOLE_HANDLER_INPUT_ROUTING_KEY
from src.message_broker.rabbitmq import RabbitMQApi
from src.utils import env
from src.utils.constants import ALERT_EXCHANGE, HEALTH_CHECK_EXCHANGE


class TestConsoleAlertsHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.test_handler_name = 'test_console_alerts_handler'
        self.dummy_logger = logging.getLogger('Dummy')
        self.dummy_logger.disabled = True
        self.connection_check_time_interval = timedelta(seconds=0)
        self.rabbit_ip = env.RABBIT_IP
        self.rabbitmq = RabbitMQApi(
            self.dummy_logger, self.rabbit_ip,
            connection_check_time_interval=self.connection_check_time_interval)
        self.test_channel_name = 'test_console_channel'
        self.test_channel_id = 'test_console1234'
        self.test_channel_logger = self.dummy_logger.getChild('dummy_channel')
        self.test_channel = ConsoleChannel(self.test_channel_name,
                                           self.test_channel_id,
                                           self.test_channel_logger)
        self.test_console_alerts_handler = ConsoleAlertsHandler(
            self.test_handler_name, self.dummy_logger, self.rabbitmq,
            self.test_channel)
        self.test_data_str = "this is a test string"
        self.test_rabbit_queue_name = 'Test Queue'

    def tearDown(self) -> None:
        # Delete any queues and exchanges which are common across many tests
        try:
            self.test_console_alerts_handler.rabbitmq.connect()

            # Declare them before just in case there are tests which do not
            # use these queues and exchanges
            self.test_console_alerts_handler.rabbitmq.queue_declare(
                queue=self.test_rabbit_queue_name, durable=True,
                exclusive=False, auto_delete=False, passive=False
            )
            self.test_console_alerts_handler.rabbitmq.queue_declare(
                self.test_console_alerts_handler._console_alerts_handler_queue,
                False, True, False, False)
            self.test_console_alerts_handler.rabbitmq.exchange_declare(
                ALERT_EXCHANGE, 'topic', False, True, False, False)
            self.test_console_alerts_handler.rabbitmq.exchange_declare(
                HEALTH_CHECK_EXCHANGE, 'topic', False, True, False, False)

            self.test_console_alerts_handler.rabbitmq.queue_purge(
                self.test_rabbit_queue_name)
            self.test_console_alerts_handler.rabbitmq.queue_purge(
                self.test_console_alerts_handler._console_alerts_handler_queue)
            self.test_console_alerts_handler.rabbitmq.queue_delete(
                self.test_rabbit_queue_name)
            self.test_console_alerts_handler.rabbitmq.queue_delete(
                self.test_console_alerts_handler._console_alerts_handler_queue)
            self.test_console_alerts_handler.rabbitmq.exchange_delete(
                HEALTH_CHECK_EXCHANGE)
            self.test_console_alerts_handler.rabbitmq.exchange_delete(
                ALERT_EXCHANGE)
            self.test_console_alerts_handler.rabbitmq.disconnect()
        except Exception as e:
            print("Deletion of queues and exchanges failed: {}".format(e))

        self.dummy_logger = None
        self.test_channel_logger = None
        self.rabbitmq = None
        self.test_channel = None
        self.test_console_alerts_handler = None

    def test__str__returns_handler_name(self) -> None:
        self.assertEqual(self.test_handler_name,
                         str(self.test_console_alerts_handler))

    def test_handler_name_returns_handler_name(self) -> None:
        self.assertEqual(self.test_handler_name,
                         self.test_console_alerts_handler.handler_name)

    def test_console_channel_returns_associated_console_channel(self) -> None:
        self.assertEqual(self.test_channel,
                         self.test_console_alerts_handler.console_channel)

    def test_init_initialises_handler_correctly(self) -> None:
        # In this test we will check that all fields that do not have a getter
        # were initialised correctly, as the previous tests test the getters.
        self.assertEqual('console_{}_alerts_handler_queue'.format(
            self.test_channel_id),
            self.test_console_alerts_handler._console_alerts_handler_queue)

    @mock.patch.object(RabbitMQApi, "basic_qos")
    def test_initialise_rabbitmq_initialises_rabbit_correctly(
            self, mock_basic_qos) -> None:
        try:
            # To make sure that there is no connection/channel already
            # established
            self.assertIsNone(self.rabbitmq.connection)
            self.assertIsNone(self.rabbitmq.channel)

            # To make sure that the exchanges and queues have not already been
            # declared
            self.rabbitmq.connect()
            self.test_console_alerts_handler.rabbitmq.queue_delete(
                self.test_console_alerts_handler._console_alerts_handler_queue)
            self.test_console_alerts_handler.rabbitmq.exchange_delete(
                HEALTH_CHECK_EXCHANGE)
            self.test_console_alerts_handler.rabbitmq.exchange_delete(
                ALERT_EXCHANGE)
            self.rabbitmq.disconnect()

            self.test_console_alerts_handler._initialise_rabbitmq()

            # Perform checks that the connection has been opened and marked as
            # open, that the delivery confirmation variable is set and basic_qos
            # called successfully.
            self.assertTrue(
                self.test_console_alerts_handler.rabbitmq.is_connected)
            self.assertTrue(
                self.test_console_alerts_handler.rabbitmq.connection.is_open)
            self.assertTrue(
                self.test_console_alerts_handler.rabbitmq.channel
                    ._delivery_confirmation)
            mock_basic_qos.assert_called_once_with(prefetch_count=200)

            # Check whether the producing exchanges have been created by
            # using passive=True. If this check fails an exception is raised
            # automatically.
            self.test_console_alerts_handler.rabbitmq.exchange_declare(
                HEALTH_CHECK_EXCHANGE, passive=True)

            # Check whether the consuming exchanges and queues have been
            # creating by sending messages with the same routing keys as for the
            # bindings. We will also check if the size of the queues is 0 to
            # confirm that basic_consume was called (it will store the msg in
            # the component memory immediately). If one of the exchanges or
            # queues is not created or basic_consume is not called, then either
            # an exception will be thrown or the queue size would be 1
            # respectively. Note when deleting the exchanges in the beginning we
            # also released every binding, hence there are no other queue binded
            # with the same routing key to any exchange at this point.
            self.test_console_alerts_handler.rabbitmq.basic_publish_confirm(
                exchange=ALERT_EXCHANGE,
                routing_key=CONSOLE_HANDLER_INPUT_ROUTING_KEY,
                body=self.test_data_str, is_body_dict=False,
                properties=pika.BasicProperties(delivery_mode=2),
                mandatory=True)

            # Re-declare queue to get the number of messages
            res = self.test_console_alerts_handler.rabbitmq.queue_declare(
                self.test_console_alerts_handler._console_alerts_handler_queue,
                False, True, False, False)
            self.assertEqual(0, res.method.message_count)
        except Exception as e:
            self.fail("Test failed: {}".format(e))
