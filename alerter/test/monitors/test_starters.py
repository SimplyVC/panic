import logging
import unittest
from datetime import timedelta
from unittest import mock

from src.configs.repo import RepoConfig
from src.configs.system import SystemConfig
from src.message_broker.rabbitmq import RabbitMQApi
from src.monitors.github import GitHubMonitor
from src.monitors.starters import (_initialise_monitor_logger,
                                   _initialise_monitor, start_system_monitor,
                                   start_github_monitor)
from src.monitors.system import SystemMonitor
from src.utils import env
from src.utils.constants import (SYSTEM_MONITOR_NAME_TEMPLATE,
                                 GITHUB_MONITOR_NAME_TEMPLATE)


class TestMonitorStarters(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_logger = logging.getLogger('Dummy')
        self.dummy_logger.disabled = True
        self.monitor_display_name = 'Test Monitor'
        self.monitor_module_name = 'TestMonitor'
        self.connection_check_time_interval = timedelta(seconds=0)
        self.rabbit_ip = env.RABBIT_IP
        self.rabbitmq = RabbitMQApi(
            self.dummy_logger, self.rabbit_ip,
            connection_check_time_interval=self.connection_check_time_interval)
        self.dummy_logger = logging.getLogger('Dummy')
        self.github_monitor_name = 'test_github_monitor'
        self.github_monitoring_period = env.GITHUB_MONITOR_PERIOD_SECONDS
        self.github_repo_id = 'test_repo_id'
        self.github_parent_id = 'test_github_parent_id'
        self.github_repo_name = 'test_repo'
        self.monitor_repo = True
        self.releases_page = 'test_url'
        self.repo_config = RepoConfig(self.github_repo_id,
                                      self.github_parent_id,
                                      self.github_repo_name, self.monitor_repo,
                                      self.releases_page)
        self.test_github_monitor = GitHubMonitor(self.github_monitor_name,
                                                 self.repo_config,
                                                 self.dummy_logger,
                                                 self.github_monitoring_period,
                                                 self.rabbitmq)
        self.system_monitor_name = 'test_system_monitor'
        self.system_monitoring_period = env.SYSTEM_MONITOR_PERIOD_SECONDS
        self.system_id = 'test_system_id'
        self.system_parent_id = 'test_system_parent_id'
        self.system_name = 'test_system'
        self.monitor_system = True
        self.node_exporter_url = 'test_url'
        self.system_config = SystemConfig(self.system_id, self.system_parent_id,
                                          self.system_name, self.monitor_system,
                                          self.node_exporter_url)
        self.test_system_monitor = SystemMonitor(self.system_monitor_name,
                                                 self.system_config,
                                                 self.dummy_logger,
                                                 self.system_monitoring_period,
                                                 self.rabbitmq)

    def tearDown(self) -> None:
        self.dummy_logger = None
        self.repo_config = None
        self.test_github_monitor = None
        self.rabbitmq = None
        self.system_config = None
        self.test_system_monitor = None

    @mock.patch("src.monitors.starters.create_logger")
    def test_initialise_monitor_logger_calls_create_logger_correctly(
            self, mock_create_logger) -> None:
        mock_create_logger.return_value = None

        _initialise_monitor_logger(self.monitor_display_name,
                                   self.monitor_module_name)

        args, _ = mock_create_logger.call_args
        mock_create_logger.assert_called_once_with(
            env.MONITORS_LOG_FILE_TEMPLATE.format(self.monitor_display_name),
            self.monitor_module_name, env.LOGGING_LEVEL, True
        )

    @mock.patch("src.monitors.starters.create_logger")
    def test_initialise_monitor_logger_returns_created_logger_if_init_correct(
            self, mock_create_logger) -> None:
        mock_create_logger.return_value = self.dummy_logger

        actual_output = _initialise_monitor_logger(self.monitor_display_name,
                                                   self.monitor_module_name)

        self.assertEqual(self.dummy_logger, actual_output)

    @mock.patch("src.monitors.starters._initialise_monitor_logger")
    def test_initialise_monitor_github_calls_initialise_logger_correctly(
            self, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger

        _initialise_monitor(GitHubMonitor, self.github_monitor_name,
                            self.github_monitoring_period, self.repo_config)

        mock_init_logger.assert_called_once_with(
            self.github_monitor_name, GitHubMonitor.__name__
        )

    @mock.patch("src.monitors.starters._initialise_monitor_logger")
    def test_initialise_monitor_system_calls_initialise_logger_correctly(
            self, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger

        _initialise_monitor(SystemMonitor, self.system_monitor_name,
                            self.system_monitoring_period, self.system_config)

        mock_init_logger.assert_called_once_with(
            self.system_monitor_name, SystemMonitor.__name__
        )

    @mock.patch("src.monitors.starters._initialise_monitor_logger")
    @mock.patch('src.monitors.starters.RabbitMQApi')
    def test_initialise_monitor_creates_github_monitor_correctly(
            self, mock_rabbit, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_rabbit.return_value = self.rabbitmq
        mock_rabbit.__name__ = RabbitMQApi.__name__

        actual_output = _initialise_monitor(GitHubMonitor,
                                            self.github_monitor_name,
                                            self.github_monitoring_period,
                                            self.repo_config)

        self.assertEqual(self.test_github_monitor.__dict__,
                         actual_output.__dict__)

    @mock.patch("src.monitors.starters._initialise_monitor_logger")
    @mock.patch('src.monitors.starters.RabbitMQApi')
    def test_initialise_monitor_creates_system_monitor_correctly(
            self, mock_rabbit, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_rabbit.return_value = self.rabbitmq
        mock_rabbit.__name__ = RabbitMQApi.__name__

        actual_output = _initialise_monitor(SystemMonitor,
                                            self.system_monitor_name,
                                            self.system_monitoring_period,
                                            self.system_config)

        self.assertEqual(self.test_system_monitor.__dict__,
                         actual_output.__dict__)

    @mock.patch("src.monitors.starters._initialise_monitor")
    @mock.patch('src.monitors.starters.start_monitor')
    def test_start_system_monitor_calls_sub_functions_correctly(
            self, mock_start_monitor, mock_initialise_monitor) -> None:
        mock_start_monitor.return_value = None
        mock_initialise_monitor.return_value = self.test_system_monitor

        start_system_monitor(self.system_config)

        mock_start_monitor.assert_called_once_with(self.test_system_monitor)
        mock_initialise_monitor.assert_called_once_with(
            SystemMonitor,
            SYSTEM_MONITOR_NAME_TEMPLATE.format(self.system_config.system_name),
            env.SYSTEM_MONITOR_PERIOD_SECONDS, self.system_config
        )

    @mock.patch("src.monitors.starters._initialise_monitor")
    @mock.patch('src.monitors.starters.start_monitor')
    def test_start_github_monitor_calls_sub_functions_correctly(
            self, mock_start_monitor, mock_initialise_monitor) -> None:
        mock_start_monitor.return_value = None
        mock_initialise_monitor.return_value = self.test_github_monitor

        start_github_monitor(self.repo_config)

        mock_start_monitor.assert_called_once_with(self.test_github_monitor)
        mock_initialise_monitor.assert_called_once_with(
            GitHubMonitor,
            GITHUB_MONITOR_NAME_TEMPLATE.format(
                self.repo_config.repo_name.replace('/', ' ')[:-1]),
            env.GITHUB_MONITOR_PERIOD_SECONDS, self.repo_config
        )
