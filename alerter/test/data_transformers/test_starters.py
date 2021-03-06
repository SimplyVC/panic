import logging
import unittest
from datetime import timedelta
from queue import Queue
from unittest import mock

from parameterized import parameterized

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
from src.utils.constants import (SYSTEM_DATA_TRANSFORMER_NAME,
                                 GITHUB_DATA_TRANSFORMER_NAME)


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
    def test_initialise_transformer_logger_creates_and_returns_logger_correctly(
            self, mock_create_logger) -> None:
        # In this test we will check that _create_logger was called correctly,
        # and that the created logger is returned. The actual logic of logger
        # creation should be tested when testing _create_logger
        mock_create_logger.return_value = self.dummy_logger

        returned_logger = _initialise_transformer_logger(
            self.transformer_display_name, self.transformer_module_name)

        mock_create_logger.assert_called_once_with(
            env.TRANSFORMERS_LOG_FILE_TEMPLATE.format(
                self.transformer_display_name), self.transformer_module_name,
            env.LOGGING_LEVEL, True
        )

        self.assertEqual(self.dummy_logger, returned_logger)

    @mock.patch("src.data_transformers.starters.RedisApi")
    def test_initialise_transformer_redis_creates_and_returns_redis_correctly(
            self, mock_init_redis) -> None:
        # In this test we will check that redis initialisation was done
        # correctly, and that the created redis instance is returned. The actual
        # logic of redis creation should be tested when testing the redis API
        mock_init_redis.return_value = self.redis
        mock_init_redis.__name__ = RedisApi.__name__

        returned_redis = _initialise_transformer_redis(
            self.transformer_display_name, self.dummy_logger)

        mock_init_redis.assert_called_once_with(
            logger=self.dummy_logger.getChild(RedisApi.__name__),
            db=env.REDIS_DB, host=env.REDIS_IP, port=env.REDIS_PORT,
            namespace=env.UNIQUE_ALERTER_IDENTIFIER
        )

        self.assertEqual(self.redis, returned_redis)

    @parameterized.expand([
        (GitHubDataTransformer, GITHUB_DATA_TRANSFORMER_NAME,
         GitHubDataTransformer.__name__),
        (SystemDataTransformer, SYSTEM_DATA_TRANSFORMER_NAME,
         SystemDataTransformer.__name__),
    ])
    @mock.patch("src.data_transformers.starters._initialise_transformer_logger")
    def test_initialise_data_transformer_calls_initialise_logger_correct(
            self, transformer_class, transformer_display_name,
            transformer_module_name, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger

        _initialise_data_transformer(transformer_class,
                                     transformer_display_name)

        mock_init_logger.assert_called_once_with(transformer_display_name,
                                                 transformer_module_name)

    @parameterized.expand([
        (GitHubDataTransformer, GITHUB_DATA_TRANSFORMER_NAME,),
        (SystemDataTransformer, SYSTEM_DATA_TRANSFORMER_NAME,),
    ])
    @mock.patch("src.data_transformers.starters._initialise_transformer_redis")
    @mock.patch("src.data_transformers.starters._initialise_transformer_logger")
    def test_initialise_data_transformer_calls_initialise_redis_correct(
            self, transformer_class, transformer_display_name, mock_init_logger,
            mock_init_redis) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_init_redis.return_value = self.redis

        _initialise_data_transformer(transformer_class,
                                     transformer_display_name)

        mock_init_redis.assert_called_once_with(transformer_display_name,
                                                self.dummy_logger)

    @parameterized.expand([
        (GitHubDataTransformer, 'self.github_dt_name',
         'self.publishing_queue_github_dt', 'self.test_github_dt'),
        (SystemDataTransformer, 'self.system_dt_name',
         'self.publishing_queue_system_dt', 'self.test_system_dt'),
    ])
    @mock.patch("src.data_transformers.starters._initialise_transformer_logger")
    @mock.patch("src.data_transformers.starters._initialise_transformer_redis")
    @mock.patch('src.data_transformers.starters.RabbitMQApi')
    @mock.patch('src.abstract.publisher_subscriber.Queue')
    def test_initialise_data_transformer_creates_data_transformer_correctly(
            self, transformer_class, transformer_display_name, publishing_queue,
            expected_data_transformer, mock_queue, mock_rabbit, mock_init_redis,
            mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_init_redis.return_value = self.redis
        mock_rabbit.return_value = self.rabbitmq
        mock_rabbit.__name__ = RabbitMQApi.__name__
        mock_queue.return_value = eval(publishing_queue)

        actual_output = _initialise_data_transformer(
            transformer_class, eval(transformer_display_name))

        self.assertEqual(eval(expected_data_transformer).__dict__,
                         actual_output.__dict__)

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
