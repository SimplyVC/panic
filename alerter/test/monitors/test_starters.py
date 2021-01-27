import logging
import unittest
from datetime import timedelta
from unittest import mock

from src.configs.repo import RepoConfig
from src.configs.system import SystemConfig
from src.message_broker.rabbitmq import RabbitMQApi
from src.monitors.github import GitHubMonitor
from src.monitors.starters import _initialize_monitor_logger, \
    _initialize_monitor, start_system_monitor, start_github_monitor
from src.monitors.system import SystemMonitor
from src.utils.constants import SYSTEM_MONITOR_NAME_TEMPLATE, \
    GITHUB_MONITOR_NAME_TEMPLATE


class TestMonitorStarters(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_logger = logging.getLogger('Dummy')
        self.monitor_display_name = 'Test Monitor'
        self.monitor_module_name = 'TestMonitor'
        self.connection_check_time_interval = timedelta(seconds=0)
        self.rabbit_ip = 'localhost'
        # self.rabbit_ip = env.RABBIT_IP
        self.rabbitmq = RabbitMQApi(
            self.dummy_logger, self.rabbit_ip,
            connection_check_time_interval=self.connection_check_time_interval)
        self.dummy_logger = logging.getLogger('Dummy')
        self.github_monitor_name = 'test_github_monitor'
        self.github_monitoring_period = 10
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
        self.system_monitoring_period = 10
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
    def test_initialize_monitor_logger_calls_create_logger_correctly(
            self, mock_create_logger) -> None:
        mock_create_logger.return_value = None

        _initialize_monitor_logger(self.monitor_display_name,
                                   self.monitor_module_name)

        args, _ = mock_create_logger.call_args
        self.assertEqual('logs/monitors/{}.log'.format(
            self.monitor_display_name), args[0])
        self.assertEqual(self.monitor_module_name, args[1])
        self.assertEqual('INFO', args[2])
        self.assertEqual(True, args[3])

    @mock.patch("src.monitors.starters.create_logger")
    def test_initialize_monitor_logger_returns_created_logger_if_init_correct(
            self, mock_create_logger) -> None:
        mock_create_logger.return_value = self.dummy_logger

        actual_output = _initialize_monitor_logger(self.monitor_display_name,
                                                   self.monitor_module_name)

        self.assertEqual(self.dummy_logger, actual_output)

    @mock.patch("src.monitors.starters._initialize_monitor_logger")
    def test_initialize_monitor_github_calls_initialize_logger_correctly(
            self, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger

        _initialize_monitor(GitHubMonitor, self.github_monitor_name,
                            self.github_monitoring_period, self.repo_config)

        args, _ = mock_init_logger.call_args
        self.assertEqual(self.github_monitor_name, args[0])
        self.assertEqual(GitHubMonitor.__name__, args[1])

    @mock.patch("src.monitors.starters._initialize_monitor_logger")
    def test_initialize_monitor_system_calls_initialize_logger_correctly(
            self, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger

        _initialize_monitor(SystemMonitor, self.system_monitor_name,
                            self.system_monitoring_period, self.system_config)

        args, _ = mock_init_logger.call_args
        self.assertEqual(self.system_monitor_name, args[0])
        self.assertEqual(SystemMonitor.__name__, args[1])

    @mock.patch("src.monitors.starters._initialize_monitor_logger")
    @mock.patch('src.monitors.starters.RabbitMQApi')
    def test_initialize_monitor_creates_github_monitor_correctly(
            self, mock_rabbit, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_rabbit.return_value = self.rabbitmq
        mock_rabbit.__name__ = RabbitMQApi.__name__

        actual_output = _initialize_monitor(GitHubMonitor,
                                            self.github_monitor_name,
                                            self.github_monitoring_period,
                                            self.repo_config)

        self.assertEqual(self.test_github_monitor.__dict__,
                         actual_output.__dict__)

    @mock.patch("src.monitors.starters._initialize_monitor_logger")
    @mock.patch('src.monitors.starters.RabbitMQApi')
    def test_initialize_monitor_creates_system_monitor_correctly(
            self, mock_rabbit, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_rabbit.return_value = self.rabbitmq
        mock_rabbit.__name__ = RabbitMQApi.__name__

        actual_output = _initialize_monitor(SystemMonitor,
                                            self.system_monitor_name,
                                            self.system_monitoring_period,
                                            self.system_config)

        self.assertEqual(self.test_system_monitor.__dict__,
                         actual_output.__dict__)

    @mock.patch("src.monitors.starters._initialize_monitor")
    @mock.patch('src.monitors.starters.start_monitor')
    def test_start_system_monitor_calls_sub_functions_correctly(
            self, mock_start_monitor, mock_initialize_monitor) -> None:
        mock_start_monitor.return_value = None
        mock_initialize_monitor.return_value = self.test_system_monitor

        start_system_monitor(self.system_config)

        args, _ = mock_start_monitor.call_args
        self.assertEqual(self.test_system_monitor, args[0])

        args, _ = mock_initialize_monitor.call_args
        self.assertEqual(SystemMonitor, args[0])
        self.assertEqual(SYSTEM_MONITOR_NAME_TEMPLATE.format(
            self.system_config.system_name), args[1])
        self.assertEqual(60, args[2])
        self.assertEqual(self.system_config, args[3])

    @mock.patch("src.monitors.starters._initialize_monitor")
    @mock.patch('src.monitors.starters.start_monitor')
    def test_start_github_monitor_calls_sub_functions_correctly(
            self, mock_start_monitor, mock_initialize_monitor) -> None:
        mock_start_monitor.return_value = None
        mock_initialize_monitor.return_value = self.test_github_monitor

        start_github_monitor(self.repo_config)

        args, _ = mock_start_monitor.call_args
        self.assertEqual(self.test_github_monitor, args[0])

        args, _ = mock_initialize_monitor.call_args
        self.assertEqual(GitHubMonitor, args[0])
        self.assertEqual(GITHUB_MONITOR_NAME_TEMPLATE.format(
            self.repo_config.repo_name.replace('/', ' ')[:-1]), args[1])
        self.assertEqual(3600, args[2])
        self.assertEqual(self.repo_config, args[3])

# TODO: Remove tearDown() commented code
# TODO: Remove SIGHUP comment
# TODO: Fix rabbit host
# TODO: Remove env commented code in system manager, github manager, monitor
#     : starters, compare with develop to see what changed
# TODO: Now since tests finished we need to run in docker environment.
#     : Do not forget to do the three TODOs above before.
# TODO: Use env in path format
