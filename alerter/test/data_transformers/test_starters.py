import logging
import unittest
from datetime import timedelta
from queue import Queue
from unittest import mock

from src.data_store.redis import RedisApi
from src.data_transformers.github import GitHubDataTransformer
from src.data_transformers.starters import (_initialise_transformer_logger,
                                            _initialise_transformer_redis,
                                            _initialise_data_transformer,
                                            start_system_data_transformer,
                                            start_github_data_transformer)
from src.data_transformers.system import SystemDataTransformer
from src.message_broker.rabbitmq import RabbitMQApi
from src.utils import env
from src.utils.constants import SYSTEM_DATA_TRANSFORMER_NAME, \
    GITHUB_DATA_TRANSFORMER_NAME


class TestDataTransformersStarters(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_logger = logging.getLogger('Dummy')
        self.dummy_logger.disabled = True
        self.transformer_display_name = 'Test Data Transformer'
        self.transformer_module_name = 'TestDataTransformer'
        self.connection_check_time_interval = timedelta(seconds=0)
        self.rabbit_ip = env.RABBIT_IP
        self.rabbitmq = RabbitMQApi(
            self.dummy_logger, self.rabbit_ip,
            connection_check_time_interval=self.connection_check_time_interval)
        self.redis_db = env.REDIS_DB
        self.redis_host = env.REDIS_IP
        self.redis_host = 'localhost'
        self.redis_port = env.REDIS_PORT
        self.redis_namespace = env.UNIQUE_ALERTER_IDENTIFIER
        self.redis = RedisApi(self.dummy_logger, self.redis_db, self.redis_host,
                              self.redis_port, '', self.redis_namespace,
                              self.connection_check_time_interval)
        self.github_dt_name = 'test_github_data_transformer'
        self.github_dt_publishing_queue_size = 1000
        self.publishing_queue_github_dt = Queue(
            self.github_dt_publishing_queue_size)
        self.test_github_dt = GitHubDataTransformer(
            self.github_dt_name, self.dummy_logger, self.redis, self.rabbitmq,
            self.github_dt_publishing_queue_size)
        self.test_github_dt._publishing_queue = self.publishing_queue_github_dt
        self.system_dt_name = 'test_system_data_transformer'
        self.system_dt_publishing_queue_size = 1001
        self.publishing_queue_system_dt = Queue(
            self.system_dt_publishing_queue_size)
        self.test_system_dt = SystemDataTransformer(
            self.system_dt_name, self.dummy_logger, self.redis, self.rabbitmq,
            self.system_dt_publishing_queue_size
        )
        self.test_system_dt._publishing_queue = self.publishing_queue_system_dt

    def tearDown(self) -> None:
        self.dummy_logger = None
        self.rabbitmq = None
        self.redis = None
        self.test_github_dt = None
        self.test_system_dt = None

    @mock.patch("src.data_transformers.starters.create_logger")
    def test_initialise_transformer_logger_calls_create_logger_correctly(
            self, mock_create_logger) -> None:
        mock_create_logger.return_value = None

        _initialise_transformer_logger(self.transformer_display_name,
                                       self.transformer_module_name)

        mock_create_logger.assert_called_once_with(
            env.TRANSFORMERS_LOG_FILE_TEMPLATE.format(
                self.transformer_display_name), self.transformer_module_name,
            env.LOGGING_LEVEL, True
        )

    @mock.patch("src.data_transformers.starters.create_logger")
    def test_initialise_trans_logger_returns_created_logger_if_init_correct(
            self, mock_create_logger) -> None:
        mock_create_logger.return_value = self.dummy_logger

        actual_output = _initialise_transformer_logger(
            self.transformer_display_name, self.transformer_module_name)

        self.assertEqual(self.dummy_logger, actual_output)

    @mock.patch("src.data_transformers.starters.RedisApi")
    def test_initialise_transformer_redis_initialises_redis_correctly(
            self, mock_init_redis) -> None:
        mock_init_redis.return_value = None
        mock_init_redis.__name__ = RedisApi.__name__

        _initialise_transformer_redis(self.transformer_display_name,
                                      self.dummy_logger)

        mock_init_redis.assert_called_once_with(
            logger=self.dummy_logger.getChild(RedisApi.__name__),
            db=env.REDIS_DB, host=env.REDIS_IP, port=env.REDIS_PORT,
            namespace=env.UNIQUE_ALERTER_IDENTIFIER
        )

    @mock.patch("src.data_transformers.starters.create_logger")
    def test_initialise_transformer_redis_returns_created_redis_if_init_correct(
            self, mock_create_logger) -> None:
        mock_create_logger.return_value = self.dummy_logger

        actual_output = _initialise_transformer_logger(
            self.transformer_display_name, self.transformer_module_name)

        self.assertEqual(self.dummy_logger, actual_output)

    @mock.patch("src.data_transformers.starters._initialise_transformer_logger")
    def test_initialise_data_transformer_github_calls_initialise_logger_correct(
            self, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger

        _initialise_data_transformer(GitHubDataTransformer, self.github_dt_name)

        mock_init_logger.assert_called_once_with(self.github_dt_name,
                                                 GitHubDataTransformer.__name__)

    @mock.patch("src.data_transformers.starters._initialise_transformer_redis")
    @mock.patch("src.data_transformers.starters._initialise_transformer_logger")
    def test_initialise_data_transformer_github_calls_initialise_redis_correct(
            self, mock_init_logger, mock_init_redis) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_init_redis.return_value = self.redis

        _initialise_data_transformer(GitHubDataTransformer, self.github_dt_name)

        mock_init_redis.assert_called_once_with(self.github_dt_name,
                                                self.dummy_logger)

    @mock.patch("src.data_transformers.starters._initialise_transformer_logger")
    @mock.patch("src.data_transformers.starters._initialise_transformer_redis")
    @mock.patch('src.data_transformers.starters.RabbitMQApi')
    @mock.patch('src.abstract.publisher_subscriber.Queue')
    def test_initialise_data_transformer_creates_github_data_trans_correctly(
            self, mock_queue, mock_rabbit, mock_init_redis,
            mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_init_redis.return_value = self.redis
        mock_rabbit.return_value = self.rabbitmq
        mock_rabbit.__name__ = RabbitMQApi.__name__
        mock_queue.return_value = self.publishing_queue_github_dt

        actual_output = _initialise_data_transformer(GitHubDataTransformer,
                                                     self.github_dt_name)

        self.assertEqual(self.test_github_dt.__dict__, actual_output.__dict__)

    @mock.patch("src.data_transformers.starters._initialise_transformer_logger")
    def test_initialise_data_transformer_system_calls_initialise_logger_correct(
            self, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger

        _initialise_data_transformer(SystemDataTransformer, self.system_dt_name)

        mock_init_logger.assert_called_once_with(self.system_dt_name,
                                                 SystemDataTransformer.__name__)

    @mock.patch("src.data_transformers.starters._initialise_transformer_redis")
    @mock.patch("src.data_transformers.starters._initialise_transformer_logger")
    def test_initialise_data_transformer_system_calls_initialise_redis_correct(
            self, mock_init_logger, mock_init_redis) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_init_redis.return_value = self.redis

        _initialise_data_transformer(SystemDataTransformer, self.system_dt_name)

        mock_init_redis.assert_called_once_with(self.system_dt_name,
                                                self.dummy_logger)

    @mock.patch("src.data_transformers.starters._initialise_transformer_logger")
    @mock.patch("src.data_transformers.starters._initialise_transformer_redis")
    @mock.patch('src.data_transformers.starters.RabbitMQApi')
    @mock.patch('src.abstract.publisher_subscriber.Queue')
    def test_initialise_data_transformer_creates_system_data_trans_correctly(
            self, mock_queue, mock_rabbit, mock_init_redis,
            mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_init_redis.return_value = self.redis
        mock_rabbit.return_value = self.rabbitmq
        mock_rabbit.__name__ = RabbitMQApi.__name__
        mock_queue.return_value = self.publishing_queue_system_dt

        actual_output = _initialise_data_transformer(SystemDataTransformer,
                                                     self.system_dt_name)

        self.assertEqual(self.test_system_dt.__dict__, actual_output.__dict__)

    @mock.patch("src.data_transformers.starters._initialise_data_transformer")
    @mock.patch('src.data_transformers.starters.start_transformer')
    def test_start_system_data_transformer_calls_sub_functions_correctly(
            self, mock_start_transformer, mock_initialise_dt) -> None:
        mock_start_transformer.return_value = None
        mock_initialise_dt.return_value = self.test_system_dt

        start_system_data_transformer()

        mock_start_transformer.assert_called_once_with(self.test_system_dt)
        mock_initialise_dt.assert_called_once_with(SystemDataTransformer,
                                                   SYSTEM_DATA_TRANSFORMER_NAME)

    @mock.patch("src.data_transformers.starters._initialise_data_transformer")
    @mock.patch('src.data_transformers.starters.start_transformer')
    def test_start_github_data_transformer_calls_sub_functions_correctly(
            self, mock_start_transformer, mock_initialise_dt) -> None:
        mock_start_transformer.return_value = None
        mock_initialise_dt.return_value = self.test_github_dt

        start_github_data_transformer()

        mock_start_transformer.assert_called_once_with(self.test_github_dt)
        mock_initialise_dt.assert_called_once_with(GitHubDataTransformer,
                                                   GITHUB_DATA_TRANSFORMER_NAME)
