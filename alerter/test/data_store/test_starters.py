import logging
import unittest
from datetime import timedelta
from unittest import mock
import copy

from src.message_broker.rabbitmq import RabbitMQApi

from src.data_store.stores.alert import AlertStore
from src.data_store.stores.github import GithubStore
from src.data_store.stores.system import SystemStore
from src.data_store.stores.store import Store

from src.data_store.starters import (
    _initialise_store_logger, _initialise_store, start_system_store,
    start_github_store, start_alert_store)

from src.utils.constants import (SYSTEM_STORE_NAME, GITHUB_STORE_NAME,
                                 ALERT_STORE_NAME)

from src.utils import env


class TestAlertersStarters(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_logger = logging.getLogger('Dummy')
        self.dummy_logger.disabled = True

        self.store_name = 'test_store'
        self.github_store_name = 'test_github_store'
        self.system_store_name = 'test_github_store'
        self.alerter_store_name = 'test_github_store'
        self.connection_check_time_interval = timedelta(seconds=0)
        self.rabbit_ip = env.RABBIT_IP
        self.rabbitmq = RabbitMQApi(
            self.dummy_logger, self.rabbit_ip,
            connection_check_time_interval=self.connection_check_time_interval)
        self.test_github_store = GithubStore(GITHUB_STORE_NAME,
                                             self.dummy_logger,
                                             self.rabbitmq)
        self.test_system_store = SystemStore(SYSTEM_STORE_NAME,
                                             self.dummy_logger,
                                             self.rabbitmq)
        self.test_alert_store = AlertStore(ALERT_STORE_NAME,
                                           self.dummy_logger,
                                           self.rabbitmq)

    def tearDown(self) -> None:
        self.rabbitmq = None
        self.dummy_logger = None
        self.store_name = ''

    @mock.patch("src.data_store.starters.create_logger")
    def test_initialise_store_logger_calls_create_logger_correctly(
            self, mock_create_logger) -> None:
        mock_create_logger.return_value = None

        _initialise_store_logger(GITHUB_STORE_NAME, self.store_name)

        mock_create_logger.assert_called_once_with(
            env.DATA_STORE_LOG_FILE_TEMPLATE.format(GITHUB_STORE_NAME),
            self.store_name, env.LOGGING_LEVEL, rotating=True)

    @mock.patch("src.data_store.starters.create_logger")
    def test_initialise_store_logger_returns_created_logger_if_init_correct(
            self, mock_create_logger) -> None:
        mock_create_logger.return_value = self.dummy_logger

        actual_output = _initialise_store_logger(
            GITHUB_STORE_NAME, self.store_name)

        self.assertEqual(self.dummy_logger, actual_output)

    @mock.patch("src.data_store.starters._initialise_store_logger")
    def test_initialise_store_github_calls_initialise_logger_correctly(
            self, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger

        _initialise_store(GithubStore, GITHUB_STORE_NAME)

        args, _ = mock_init_logger.call_args
        mock_init_logger.assert_called_once_with(
            GITHUB_STORE_NAME,
            GithubStore.__name__
        )

    @mock.patch("src.data_store.starters._initialise_store_logger")
    def test_initialise_store_system_calls_initialise_logger_correctly(
            self, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger

        _initialise_store(SystemStore, SYSTEM_STORE_NAME)

        args, _ = mock_init_logger.call_args
        mock_init_logger.assert_called_once_with(
            SYSTEM_STORE_NAME,
            SystemStore.__name__
        )

    @mock.patch("src.data_store.starters._initialise_store_logger")
    def test_initialise_store_alerter_calls_initialise_logger_correctly(
            self, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger

        _initialise_store(AlertStore, ALERT_STORE_NAME)

        args, _ = mock_init_logger.call_args
        mock_init_logger.assert_called_once_with(
            ALERT_STORE_NAME,
            AlertStore.__name__
        )

    @mock.patch("src.data_store.starters.RabbitMQApi")
    @mock.patch("src.data_store.starters._initialise_store_logger")
    @mock.patch("src.data_store.starters.GithubStore")
    def test_initialise_store_creates_github_store_correctly(
            self, mock_github_store, mock_init_logger, mock_rabbit) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_github_store.__name__ = 'GithubStore'
        mock_rabbit.__name__ = 'RabbitMQApi'
        mock_rabbit.return_value = self.rabbitmq
        _initialise_store(mock_github_store, GITHUB_STORE_NAME)

        mock_init_logger.assert_called_once()
        mock_github_store.assert_called_once_with(
            GITHUB_STORE_NAME,
            self.dummy_logger,
            self.rabbitmq
        )

    @mock.patch("src.data_store.starters.RabbitMQApi")
    @mock.patch("src.data_store.starters._initialise_store_logger")
    @mock.patch("src.data_store.starters.SystemStore")
    def test_initialise_store_creates_system_store_correctly(
            self, mock_system_store, mock_init_logger, mock_rabbit) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_system_store.__name__ = 'SystemStore'
        mock_rabbit.__name__ = 'RabbitMQApi'
        mock_rabbit.return_value = self.rabbitmq

        _initialise_store(mock_system_store, SYSTEM_STORE_NAME)

        mock_init_logger.assert_called_once()
        mock_system_store.assert_called_once_with(
            SYSTEM_STORE_NAME,
            self.dummy_logger,
            self.rabbitmq
        )

    @mock.patch("src.data_store.starters.RabbitMQApi")
    @mock.patch("src.data_store.starters._initialise_store_logger")
    @mock.patch("src.data_store.starters.AlertStore")
    def test_initialise_store_creates_alert_store_correctly(
            self, mock_alert_store, mock_init_logger, mock_rabbit) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_alert_store.__name__ = 'AlertStore'
        mock_rabbit.__name__ = 'RabbitMQApi'
        mock_rabbit.return_value = self.rabbitmq

        _initialise_store(mock_alert_store, ALERT_STORE_NAME)

        mock_init_logger.assert_called_once()
        mock_alert_store.assert_called_once_with(
            ALERT_STORE_NAME,
            self.dummy_logger,
            self.rabbitmq
        )

    @mock.patch("src.data_store.starters.SystemStore")
    @mock.patch("src.data_store.starters._initialise_store_logger")
    @mock.patch("src.data_store.starters.start_store")
    def test_start_system_store_calls_sub_functions_correctly(
            self, mock_start_store, mock_init_logger,
            mock_system_store) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_system_store.__name__ = 'SystemStore'
        mock_system_store.return_value = self.test_system_store

        start_system_store()

        mock_init_logger.assert_called_once()
        mock_start_store.assert_called_once_with(self.test_system_store)

    @mock.patch("src.data_store.starters.GithubStore")
    @mock.patch("src.data_store.starters._initialise_store_logger")
    @mock.patch("src.data_store.starters.start_store")
    def test_start_github_store_calls_sub_functions_correctly(
            self, mock_start_store, mock_init_logger,
            mock_github_store) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_github_store.__name__ = 'GithubStore'
        mock_github_store.return_value = self.test_github_store

        start_github_store()

        mock_init_logger.assert_called_once()
        mock_start_store.assert_called_once_with(self.test_github_store)

    @mock.patch("src.data_store.starters.AlertStore")
    @mock.patch("src.data_store.starters._initialise_store_logger")
    @mock.patch("src.data_store.starters.start_store")
    def test_start_alert_store_calls_sub_functions_correctly(
            self, mock_start_store, mock_init_logger,
            mock_alert_store) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_alert_store.__name__ = 'AlertStore'
        mock_alert_store.return_value = self.test_alert_store

        start_alert_store()

        mock_init_logger.assert_called_once()
        mock_start_store.assert_called_once_with(self.test_alert_store)
