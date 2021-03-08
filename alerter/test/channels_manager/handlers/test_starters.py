import logging
import unittest
from datetime import timedelta
from unittest import mock
from unittest.mock import call

from src.channels_manager.apis.telegram_bot_api import TelegramBotApi
from src.channels_manager.apis.twilio_api import TwilioApi
from src.channels_manager.channels import TelegramChannel
from src.channels_manager.channels.twilio import TwilioChannel
from src.channels_manager.commands.handlers.telegram_cmd_handlers import \
    TelegramCommandHandlers
from src.channels_manager.handlers import TelegramAlertsHandler
from src.channels_manager.handlers.starters import (
    _initialise_channel_handler_logger, _initialise_alerts_logger,
    _initialise_telegram_alerts_handler, start_telegram_alerts_handler,
    _initialise_telegram_commands_handler, start_telegram_commands_handler,
    _initialise_twilio_alerts_handler, start_twilio_alerts_handler)
from src.channels_manager.handlers.telegram.commands import \
    TelegramCommandsHandler
from src.channels_manager.handlers.twilio.alerts import TwilioAlertsHandler
from src.data_store.mongo import MongoApi
from src.data_store.redis import RedisApi
from src.message_broker.rabbitmq import RabbitMQApi
from src.utils import env
from src.utils.constants import (TELEGRAM_ALERTS_HANDLER_NAME_TEMPLATE,
                                 TELEGRAM_COMMANDS_HANDLER_NAME_TEMPLATE,
                                 TELEGRAM_COMMAND_HANDLERS_NAME,
                                 TWILIO_ALERTS_HANDLER_NAME_TEMPLATE)


class TestHandlerStarters(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_logger = logging.getLogger('Dummy')
        self.dummy_logger.disabled = True
        self.handler_display_name = 'Test Channel Handler'
        self.handler_module_name = 'TestChannelHandler'
        self.connection_check_time_interval = timedelta(seconds=0)
        self.rabbit_ip = env.RABBIT_IP
        self.rabbitmq = RabbitMQApi(
            self.dummy_logger, self.rabbit_ip,
            connection_check_time_interval=self.connection_check_time_interval)
        self.telegram_channel_name = 'test_telegram_channel'
        self.telegram_channel_id = 'test_telegram_id12345'
        self.telegram_channel_logger = self.dummy_logger.getChild(
            'telegram_channel_logger')
        self.bot_token = '1234567891:ABC-67ABCrfZFdddqRT5Gh837T2rtUFHgTY'
        self.bot_chat_id = 'test_bot_chat_id'
        self.telegram_base_url = "https://api.telegram.org/bot" + self.bot_token
        self.telegram_bot_api = TelegramBotApi(self.bot_token, self.bot_chat_id)
        self.telegram_channel = TelegramChannel(
            self.telegram_channel_name, self.telegram_channel_id,
            self.telegram_channel_logger, self.telegram_bot_api)
        self.test_queue_size = 1000
        self.test_max_attempts = 5
        self.test_alert_validity_threshold = 300
        self.telegram_alerts_handler = TelegramAlertsHandler(
            self.handler_display_name, self.dummy_logger, self.rabbitmq,
            self.telegram_channel, self.test_queue_size, self.test_max_attempts,
            self.test_alert_validity_threshold)
        self.cmd_handlers_rabbit = RabbitMQApi(
            logger=self.dummy_logger.getChild(RabbitMQApi.__name__),
            host=self.rabbit_ip,
            connection_check_time_interval=self.connection_check_time_interval)
        self.redis = RedisApi(
            logger=self.dummy_logger.getChild(RedisApi.__name__),
            host=env.REDIS_IP, db=env.REDIS_DB, port=env.REDIS_PORT,
            namespace=env.UNIQUE_ALERTER_IDENTIFIER)
        self.mongo = MongoApi(
            logger=self.dummy_logger.getChild(MongoApi.__name__),
            host=env.DB_IP, db_name=env.DB_NAME, port=env.DB_PORT)
        self.command_handlers_logger = self.dummy_logger.getChild(
            TelegramCommandHandlers.__name__)
        self.test_chain_1 = 'Kusama'
        self.test_chain_2 = 'Cosmos'
        self.test_chain_3 = 'Test_Chain'
        self.test_chain1_id = 'kusama1234'
        self.test_chain2_id = 'cosmos1234'
        self.test_chain3_id = 'test_chain11123'
        self.test_associated_chains = {
            self.test_chain1_id: self.test_chain_1,
            self.test_chain2_id: self.test_chain_2,
            self.test_chain3_id: self.test_chain_3
        }
        self.telegram_command_handlers = TelegramCommandHandlers(
            self.handler_display_name, self.command_handlers_logger,
            self.test_associated_chains, self.telegram_channel,
            self.cmd_handlers_rabbit, self.redis, self.mongo)
        self.telegram_commands_handler = TelegramCommandsHandler(
            self.handler_display_name, self.dummy_logger, self.rabbitmq,
            self.telegram_channel, self.telegram_command_handlers)
        self.twilio_channel_name = 'test_twilio_channel'
        self.twilio_channel_id = 'test_twilio_id12345'
        self.twilio_channel_logger = self.dummy_logger.getChild(
            'twilio_channel')
        self.account_sid = 'test_account_sid'
        self.auth_token = 'test_auth_token'
        self.call_from = '+35699999999'
        self.call_to = ['+35611111111', '+35644545454', '+35634343434']
        self.twiml = '<Response><Reject/></Response>'
        self.twiml_is_url = False
        self.twilio_api = TwilioApi(self.account_sid, self.auth_token)
        self.twilio_channel = TwilioChannel(
            self.twilio_channel_name, self.twilio_channel_id,
            self.twilio_channel_logger, self.twilio_api)
        self.twilio_alerts_handler = TwilioAlertsHandler(
            self.handler_display_name, self.dummy_logger, self.rabbitmq,
            self.twilio_channel, self.call_from, self.call_to, self.twiml,
            self.twiml_is_url, self.test_max_attempts,
            self.test_alert_validity_threshold)

    def tearDown(self) -> None:
        self.dummy_logger = None
        self.rabbitmq = None
        self.telegram_channel_logger = None
        self.telegram_bot_api = None
        self.telegram_channel = None
        self.telegram_alerts_handler = None
        self.cmd_handlers_rabbit = None
        self.redis = None
        self.mongo = None
        self.command_handlers_logger = None
        self.telegram_command_handlers = None
        self.telegram_commands_handler = None
        self.twilio_api = None
        self.twilio_channel = None
        self.twilio_alerts_handler = None

    @mock.patch("src.channels_manager.handlers.starters.create_logger")
    def test_initialise_channel_handler_logger_creates_and_returns_logger(
            self, mock_create_logger) -> None:
        # In this test we will check that _create_logger was called correctly,
        # and that the created logger is returned. The actual logic of logger
        # creation should be tested when testing _create_logger
        mock_create_logger.return_value = self.dummy_logger

        returned_logger = _initialise_channel_handler_logger(
            self.handler_display_name, self.handler_module_name)

        mock_create_logger.assert_called_once_with(
            env.CHANNEL_HANDLERS_LOG_FILE_TEMPLATE.format(
                self.handler_display_name), self.handler_module_name,
            env.LOGGING_LEVEL, True
        )

        self.assertEqual(self.dummy_logger, returned_logger)

    @mock.patch("src.channels_manager.handlers.starters.create_logger")
    def test_initialise_alerts_logger_creates_and_returns_logger(
            self, mock_create_logger) -> None:
        # In this test we will check that _create_logger was called correctly,
        # and that the created logger is returned. The actual logic of logger
        # creation should be tested when testing _create_logger
        mock_create_logger.return_value = self.dummy_logger

        returned_logger = _initialise_alerts_logger()

        mock_create_logger.assert_called_once_with(
            env.ALERTS_LOG_FILE, 'Alerts', env.LOGGING_LEVEL, True
        )

        self.assertEqual(self.dummy_logger, returned_logger)

    @mock.patch("src.channels_manager.handlers.starters."
                "_initialise_channel_handler_logger")
    @mock.patch("src.channels_manager.handlers.starters.TelegramBotApi")
    @mock.patch("src.channels_manager.handlers.starters.TelegramChannel")
    @mock.patch("src.channels_manager.handlers.starters.RabbitMQApi")
    @mock.patch("src.channels_manager.handlers.starters.TelegramAlertsHandler")
    def test_initialise_telegram_alerts_handler_creates_TAH_correctly(
            self, mock_alerts_handler, mock_rabbit, mock_telegram_channel,
            mock_bot_api, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_bot_api.return_value = self.telegram_bot_api
        mock_telegram_channel.return_value = self.telegram_channel
        mock_rabbit.return_value = self.rabbitmq
        mock_alerts_handler.return_value = self.telegram_alerts_handler
        mock_alerts_handler.__name__ = TelegramAlertsHandler.__name__
        mock_rabbit.__name__ = RabbitMQApi.__name__
        mock_telegram_channel.__name__ = TelegramChannel.__name__

        _initialise_telegram_alerts_handler(
            self.bot_token, self.bot_chat_id, self.telegram_channel_id,
            self.telegram_channel_name)

        handler_display_name = TELEGRAM_ALERTS_HANDLER_NAME_TEMPLATE.format(
            self.telegram_channel_name)
        mock_init_logger.assert_called_once_with(handler_display_name,
                                                 TelegramAlertsHandler.__name__)
        mock_bot_api.assert_called_once_with(self.bot_token, self.bot_chat_id)
        mock_telegram_channel.assert_called_once_with(
            self.telegram_channel_name, self.telegram_channel_id,
            self.dummy_logger.getChild(TelegramChannel.__name__),
            self.telegram_bot_api)
        mock_rabbit.assert_called_once_with(
            logger=self.dummy_logger.getChild(RabbitMQApi.__name__),
            host=env.RABBIT_IP)
        mock_alerts_handler.assert_called_once_with(
            handler_display_name, self.dummy_logger, self.rabbitmq,
            self.telegram_channel, env.CHANNELS_MANAGER_PUBLISHING_QUEUE_SIZE)

    @mock.patch("src.channels_manager.handlers.starters."
                "_initialise_telegram_alerts_handler")
    @mock.patch("src.channels_manager.handlers.starters.start_handler")
    def test_start_telegram_alerts_handler_starts_handler_correctly(
            self, mock_start_handler, mock_init_tah) -> None:
        mock_init_tah.return_value = self.telegram_alerts_handler
        mock_start_handler.return_value = None

        start_telegram_alerts_handler(self.bot_token, self.bot_chat_id,
                                      self.telegram_channel_id,
                                      self.telegram_channel_name)

        mock_init_tah.assert_called_once_with(self.bot_token, self.bot_chat_id,
                                              self.telegram_channel_id,
                                              self.telegram_channel_name)
        mock_start_handler.assert_called_once_with(self.telegram_alerts_handler)

    @mock.patch("src.channels_manager.handlers.starters.MongoApi")
    @mock.patch("src.channels_manager.handlers.starters.RedisApi")
    @mock.patch("src.channels_manager.handlers.starters."
                "_initialise_channel_handler_logger")
    @mock.patch("src.channels_manager.handlers.starters.TelegramBotApi")
    @mock.patch("src.channels_manager.handlers.starters.TelegramChannel")
    @mock.patch("src.channels_manager.handlers.starters.RabbitMQApi")
    @mock.patch("src.channels_manager.handlers.starters."
                "TelegramCommandsHandler")
    @mock.patch("src.channels_manager.handlers.starters."
                "TelegramCommandHandlers")
    def test_initialise_telegram_commands_handler_creates_TCH_correctly(
            self, mock_command_handlers, mock_commands_handler, mock_rabbit,
            mock_telegram_channel, mock_bot_api, mock_init_logger, mock_redis,
            mock_mongo) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_bot_api.return_value = self.telegram_bot_api
        mock_telegram_channel.return_value = self.telegram_channel
        mock_rabbit.side_effect = [self.cmd_handlers_rabbit, self.rabbitmq]
        mock_commands_handler.return_value = self.telegram_commands_handler
        mock_commands_handler.__name__ = TelegramCommandsHandler.__name__
        mock_rabbit.__name__ = RabbitMQApi.__name__
        mock_telegram_channel.__name__ = TelegramChannel.__name__
        mock_redis.return_value = self.redis
        mock_redis.__name__ = RedisApi.__name__
        mock_mongo.return_value = self.mongo
        mock_mongo.__name__ = MongoApi.__name__
        mock_command_handlers.return_value = self.telegram_command_handlers
        mock_command_handlers.__name__ = TelegramCommandHandlers.__name__

        _initialise_telegram_commands_handler(
            self.bot_token, self.bot_chat_id, self.telegram_channel_id,
            self.telegram_channel_name, self.test_associated_chains)

        handler_display_name = TELEGRAM_COMMANDS_HANDLER_NAME_TEMPLATE.format(
            self.telegram_channel_name)
        mock_init_logger.assert_called_once_with(
            handler_display_name, TelegramCommandsHandler.__name__)
        mock_bot_api.assert_called_once_with(self.bot_token, self.bot_chat_id)
        mock_telegram_channel.assert_called_once_with(
            self.telegram_channel_name, self.telegram_channel_id,
            self.dummy_logger.getChild(TelegramChannel.__name__),
            self.telegram_bot_api)
        actual_rabbit_calls = mock_rabbit.call_args_list
        expected_rabbit_calls = [
            call(logger=self.command_handlers_logger.getChild(
                RabbitMQApi.__name__), host=env.RABBIT_IP),
            call(logger=self.dummy_logger.getChild(RabbitMQApi.__name__),
                 host=env.RABBIT_IP),
        ]
        self.assertEqual(expected_rabbit_calls, actual_rabbit_calls)
        mock_redis.assert_called_once_with(
            logger=self.command_handlers_logger.getChild(RedisApi.__name__),
            host=env.REDIS_IP, db=env.REDIS_DB, port=env.REDIS_PORT,
            namespace=env.UNIQUE_ALERTER_IDENTIFIER)
        mock_mongo.assert_called_once_with(
            logger=self.command_handlers_logger.getChild(MongoApi.__name__),
            host=env.DB_IP, db_name=env.DB_NAME, port=env.DB_PORT)
        mock_command_handlers.assert_called_once_with(
            TELEGRAM_COMMAND_HANDLERS_NAME, self.command_handlers_logger,
            self.test_associated_chains, self.telegram_channel,
            self.cmd_handlers_rabbit, self.redis, self.mongo)
        mock_commands_handler.assert_called_once_with(
            handler_display_name, self.dummy_logger, self.rabbitmq,
            self.telegram_channel, self.telegram_command_handlers)

    @mock.patch("src.channels_manager.handlers.starters."
                "_initialise_telegram_commands_handler")
    @mock.patch("src.channels_manager.handlers.starters.start_handler")
    def test_start_telegram_commands_handler_starts_handler_correctly(
            self, mock_start_handler, mock_init_tch) -> None:
        mock_init_tch.return_value = self.telegram_commands_handler
        mock_start_handler.return_value = None

        start_telegram_commands_handler(self.bot_token, self.bot_chat_id,
                                        self.telegram_channel_id,
                                        self.telegram_channel_name,
                                        self.test_associated_chains)

        mock_init_tch.assert_called_once_with(self.bot_token, self.bot_chat_id,
                                              self.telegram_channel_id,
                                              self.telegram_channel_name,
                                              self.test_associated_chains)
        mock_start_handler.assert_called_once_with(
            self.telegram_commands_handler)

    @mock.patch("src.channels_manager.handlers.starters."
                "_initialise_channel_handler_logger")
    @mock.patch("src.channels_manager.handlers.starters.TwilioApi")
    @mock.patch("src.channels_manager.handlers.starters.TwilioChannel")
    @mock.patch("src.channels_manager.handlers.starters.RabbitMQApi")
    @mock.patch("src.channels_manager.handlers.starters.TwilioAlertsHandler")
    def test_initialise_twilio_alerts_handler_creates_TAH_correctly(
            self, mock_alerts_handler, mock_rabbit, mock_twilio_channel,
            mock_twilio_api, mock_init_logger) -> None:
        mock_init_logger.return_value = self.dummy_logger
        mock_twilio_api.return_value = self.twilio_api
        mock_twilio_channel.return_value = self.twilio_channel
        mock_rabbit.return_value = self.rabbitmq
        mock_alerts_handler.return_value = self.twilio_alerts_handler
        mock_alerts_handler.__name__ = TwilioAlertsHandler.__name__
        mock_rabbit.__name__ = RabbitMQApi.__name__
        mock_twilio_channel.__name__ = TwilioChannel.__name__

        _initialise_twilio_alerts_handler(
            self.account_sid, self.auth_token, self.twilio_channel_id,
            self.twilio_channel_name, self.call_from, self.call_to, self.twiml,
            self.twiml_is_url)

        handler_display_name = TWILIO_ALERTS_HANDLER_NAME_TEMPLATE.format(
            self.twilio_channel_name)
        mock_init_logger.assert_called_once_with(handler_display_name,
                                                 TwilioAlertsHandler.__name__)
        mock_twilio_api.assert_called_once_with(self.account_sid,
                                                self.auth_token)
        mock_twilio_channel.assert_called_once_with(
            self.twilio_channel_name, self.twilio_channel_id,
            self.dummy_logger.getChild(TwilioChannel.__name__), self.twilio_api)
        mock_rabbit.assert_called_once_with(
            logger=self.dummy_logger.getChild(RabbitMQApi.__name__),
            host=env.RABBIT_IP)
        mock_alerts_handler.assert_called_once_with(
            handler_display_name, self.dummy_logger, self.rabbitmq,
            self.twilio_channel, self.call_from, self.call_to, self.twiml,
            self.twiml_is_url)

    @mock.patch("src.channels_manager.handlers.starters."
                "_initialise_twilio_alerts_handler")
    @mock.patch("src.channels_manager.handlers.starters.start_handler")
    def test_start_twilio_alerts_handler_starts_handler_correctly(
            self, mock_start_handler, mock_init_tah) -> None:
        mock_init_tah.return_value = self.twilio_alerts_handler
        mock_start_handler.return_value = None

        start_twilio_alerts_handler(self.account_sid, self.auth_token,
                                    self.twilio_channel_id,
                                    self.twilio_channel_name, self.call_from,
                                    self.call_to, self.twiml, self.twiml_is_url)

        mock_init_tah.assert_called_once_with(self.account_sid, self.auth_token,
                                              self.twilio_channel_id,
                                              self.twilio_channel_name,
                                              self.call_from, self.call_to,
                                              self.twiml, self.twiml_is_url)
        mock_start_handler.assert_called_once_with(self.twilio_alerts_handler)
