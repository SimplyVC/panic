import logging
import unittest
from datetime import timedelta

from src.message_broker.rabbitmq import RabbitMQApi
from src.utils import env


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

    def tearDown(self) -> None:
        self.dummy_logger = None
        self.rabbitmq = None
