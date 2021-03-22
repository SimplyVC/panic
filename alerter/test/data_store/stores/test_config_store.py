import json
import logging
import unittest
from datetime import datetime
from datetime import timedelta
from unittest import mock

import pika
import pika.exceptions
from freezegun import freeze_time
from parameterized import parameterized

from src.data_store.redis import RedisApi
from src.data_store.redis.store_keys import Keys
from src.data_store.stores.config import ConfigStore
from src.message_broker.rabbitmq import RabbitMQApi
from src.utils import env
from src.utils.constants import (CONFIG_EXCHANGE, HEALTH_CHECK_EXCHANGE,
                                 STORE_CONFIGS_QUEUE_NAME,
                                 STORE_CONFIGS_ROUTING_KEY_CHAINS)
from src.utils.exceptions import (PANICException)
from test.utils.utils import (connect_to_rabbit,
                              disconnect_from_rabbit,
                              delete_exchange_if_exists,
                              delete_queue_if_exists)


class TestConfigStore(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_logger = logging.getLogger('Dummy')
        self.dummy_logger.disabled = True
        self.connection_check_time_interval = timedelta(seconds=0)
        self.rabbit_ip = env.RABBIT_IP
        self.rabbitmq = RabbitMQApi(
            self.dummy_logger, self.rabbit_ip,
            connection_check_time_interval=self.connection_check_time_interval)

        self.test_rabbit_manager = RabbitMQApi(
            self.dummy_logger, self.rabbit_ip,
            connection_check_time_interval=self.connection_check_time_interval)

        self.redis_db = env.REDIS_DB
        self.redis_host = env.REDIS_IP
        self.redis_port = env.REDIS_PORT
        self.redis_namespace = env.UNIQUE_ALERTER_IDENTIFIER
        self.redis = RedisApi(self.dummy_logger, self.redis_db,
                              self.redis_host, self.redis_port, '',
                              self.redis_namespace,
                              self.connection_check_time_interval)

        self.mongo_ip = env.DB_IP
        self.mongo_db = env.DB_NAME
        self.mongo_port = env.DB_PORT

        self.test_store_name = 'store name'
        self.test_store = ConfigStore(self.test_store_name,
                                      self.dummy_logger,
                                      self.rabbitmq)

        self.routing_key = 'heartbeat.worker'
        self.test_queue_name = 'test queue'

        connect_to_rabbit(self.rabbitmq)
        self.rabbitmq.exchange_declare(HEALTH_CHECK_EXCHANGE, 'topic', False,
                                       True, False, False)
        self.rabbitmq.exchange_declare(CONFIG_EXCHANGE, 'topic', False,
                                       True, False, False)
        self.rabbitmq.queue_declare(STORE_CONFIGS_QUEUE_NAME, False, True,
                                    False, False)
        self.rabbitmq.queue_bind(STORE_CONFIGS_QUEUE_NAME,
                                 CONFIG_EXCHANGE,
                                 STORE_CONFIGS_ROUTING_KEY_CHAINS)

        connect_to_rabbit(self.test_rabbit_manager)
        self.test_rabbit_manager.queue_declare(self.test_queue_name, False,
                                               True, False, False)
        self.test_rabbit_manager.queue_bind(self.test_queue_name,
                                            HEALTH_CHECK_EXCHANGE,
                                            self.routing_key)

        self.test_parent_id = 'parent_id'
        self.test_config_type = 'config_type'

        self.test_data_str = 'test data'
        self.test_exception = PANICException('test_exception', 1)

        self.last_monitored = datetime(2012, 1, 1).timestamp()

        self.routing_key_1 = 'chains.cosmos.cosmos.nodes_config'
        self.routing_key_2 = 'chains.cosmos.cosmos.alerts_config'
        self.routing_key_3 = 'chains.cosmos.cosmos.repos_config'

        self.routing_key_4 = 'general.repos_config'
        self.routing_key_5 = 'general.alerts_config'
        self.routing_key_6 = 'general.systems_config'

        self.routing_key_7 = 'channels.email_config'
        self.routing_key_8 = 'channels.pagerduty_config'
        self.routing_key_9 = 'channels.opsgenie_config'
        self.routing_key_10 = 'channels.telegram_config'
        self.routing_key_11 = 'channels.twilio_config'

        self.nodes_config_1 = {
            "node_3e0a5189-f474-4120-a0a4-d5ab817c0504": {
                "id": "node_3e0a5189-f474-4120-a0a4-d5ab817c0504",
                "parent_id": "chain_name_7f4bc842-21b1-4bcb-8ab9-d86e08149548",
                "name": "cosmos_sentry_1(46.166.146.165:9100)",
                "monitor_tendermint": "false",
                "monitor_rpc": "false",
                "monitor_prometheus": "false",
                "exporter_url": "http://46.166.146.165:9100/metrics",
                "monitor_system": "true",
                "is_validator": "false",
                "monitor_node": "true",
                "is_archive_node": "true",
                "use_as_data_source": "true"
            },
            "node_f8ebf267-9b53-4aa1-9c45-e84a9cba5fbc": {
                "id": "node_f8ebf267-9b53-4aa1-9c45-e84a9cba5fbc",
                "parent_id": "chain_name_7f4bc842-21b1-4bcb-8ab9-d86e08149548",
                "name": "cosmos_sentry_2(172.16.151.10:9100)",
                "monitor_tendermint": "false",
                "monitor_rpc": "false",
                "monitor_prometheus": "false",
                "exporter_url": "http://172.16.151.10:9100/metrics",
                "monitor_system": "true",
                "is_validator": "false",
                "monitor_node": "true",
                "is_archive_node": "true",
                "use_as_data_source": "true"
            }
        }

        self.repos_config_1 = {
            "repo_4ea76d87-d291-4b68-88af-da2bd1e16e2e": {
                "id": "repo_4ea76d87-d291-4b68-88af-da2bd1e16e2e",
                "parent_id": "chain_name_7f4bc842-21b1-4bcb-8ab9-d86e08149548",
                "repo_name": "tendermint/tendermint/",
                "monitor_repo": "true"
            },
            "repo_83713022-4155-420b-ada1-73a863f58282": {
                "id": "repo_83713022-4155-420b-ada1-73a863f58282",
                "parent_id": "chain_name_7f4bc842-21b1-4bcb-8ab9-d86e08149548",
                "repo_name": "SimplyVC/panic_cosmos/",
                "monitor_repo": "true"
            }
        }

        self.alerts_config_1 = {
            "1": {
                "name": "open_file_descriptors",
                "enabled": "true",
                "parent_id": "GLOBAL",
                "critical_threshold": "95",
                "critical_repeat": "300",
                "critical_enabled": "true",
                "warning_threshold": "85",
                "warning_enabled": "true"
            },
            "2": {
                "name": "system_cpu_usage",
                "enabled": "true",
                "parent_id": "GLOBAL",
                "critical_threshold": "95",
                "critical_repeat": "300",
                "critical_enabled": "true",
                "warning_threshold": "85",
                "warning_enabled": "true"
            },
            "3": {
                "name": "system_storage_usage",
                "enabled": "true",
                "parent_id": "GLOBAL",
                "critical_threshold": "95",
                "critical_repeat": "300",
                "critical_enabled": "true",
                "warning_threshold": "85",
                "warning_enabled": "true"
            },
            "4": {
                "name": "system_ram_usage",
                "enabled": "true",
                "parent_id": "GLOBAL",
                "critical_threshold": "95",
                "critical_repeat": "300",
                "critical_enabled": "true",
                "warning_threshold": "85",
                "warning_enabled": "true"
            },
            "5": {
                "name": "system_is_down",
                "enabled": "true",
                "parent_id": "GLOBAL",
                "critical_threshold": "200",
                "critical_repeat": "300",
                "critical_enabled": "true",
                "warning_threshold": "0",
                "warning_enabled": "true"
            }
        }

        self.systems_config_1 = {
            "system_1d026af1-6cab-403d-8256-c8faa462930a": {
                "id": "system_1d026af1-6cab-403d-8256-c8faa462930a",
                "parent_id": "GLOBAL",
                "name": "matic_full_node_nl(172.26.10.137:9100)",
                "exporter_url": "http://172.26.10.137:9100/metrics",
                "monitor_system": "true"
            },
            "system_a51b3a33-cb3f-4f53-a657-8a5a0efe0822": {
                "id": "system_a51b3a33-cb3f-4f53-a657-8a5a0efe0822",
                "parent_id": "GLOBAL",
                "name": "matic_full_node_mt(172.16.152.137:9100)",
                "exporter_url": "http://172.16.152.137:9100/metrics",
                "monitor_system": "true"
            }
        }

        self.telegram_config_1 = {
            "telegram_8431a28e-a2ce-4e9b-839c-299b62e3d5b9": {
                "id": "telegram_8431a28e-a2ce-4e9b-839c-299b62e3d5b9",
                "channel_name": "telegram_chat_1",
                "bot_token": "1277777773:AAF-78AENtsYXxxdqTL3Ip987N7gmIKJaBE",
                "chat_id": "-759538717",
                "info": "true",
                "warning": "true",
                "critical": "true",
                "error": "true",
                "alerts": "false",
                "commands": "false",
                "parent_ids": "chain_name_7f4bc842-21b1-4bcb-8ab9-d86e08149548,chain_name_94aafe04-8287-463a-8416-0401852b3ca2,GLOBAL",
                "parent_names": "cosmos,kusama,GLOBAL"
            }
        }

        self.twilio_config_1 = {
            "twilio_a7016a6b-9394-4584-abe3-5a5c434b6b7c": {
                "id": "twilio_a7016a6b-9394-4584-abe3-5a5c434b6b7c",
                "channel_name": "twilio_caller_main",
                "account_sid": "ACb77777284e97e49eb2260aada0220e12",
                "auth_token": "d19f777777a0b8e274470d599e5bcc5e8",
                "twilio_phone_no": "+19893077770",
                "twilio_phone_numbers_to_dial_valid": "+35697777380",
                "parent_ids": "chain_name_7f4bc842-21b1-4bcb-8ab9-d86e08149548,chain_name_94aafe04-8287-463a-8416-0401852b3ca2,GLOBAL",
                "parent_names": "cosmos,kusama,GLOBAL"
            }
        }

        self.pagerduty_config_1 = {
            "pagerduty_4092d0ed-ac45-462b-b62a-89cffd4833cc": {
                "id": "pagerduty_4092d0ed-ac45-462b-b62a-89cffd4833cc",
                "channel_name": "pager_duty_1",
                "api_token": "meVp_vyQybcX7dA3o1fS",
                "integration_key": "4a520ce3577777ad89a3518096f3a5189",
                "info": "true",
                "warning": "true",
                "critical": "true",
                "error": "true",
                "parent_ids": "chain_name_7f4bc842-21b1-4bcb-8ab9-d86e08149548,chain_name_94aafe04-8287-463a-8416-0401852b3ca2,GLOBAL",
                "parent_names": "cosmos,kusama,GLOBAL"
            }
        }

        self.opsgenie_config_1 = {
            "opsgenie_9550bee1-5880-41f6-bdcf-a289472d7c35": {
                "id": "opsgenie_9550bee1-5880-41f6-bdcf-a289472d7c35",
                "channel_name": "ops_genie_main",
                "api_token": "77777777-0708-4b7e-a46f-496c85fa0b06",
                "eu": "true",
                "info": "true",
                "warning": "true",
                "critical": "true",
                "error": "true",
                "parent_ids": "chain_name_7f4bc842-21b1-4bcb-8ab9-d86e08149548,chain_name_94aafe04-8287-463a-8416-0401852b3ca2,GLOBAL",
                "parent_names": "cosmos,kusama,GLOBAL"
            }
        }

        self.email_config_1 = {
            "email_01b23d79-10f5-4815-a11f-034f53974b23": {
                "id": "email_01b23d79-10f5-4815-a11f-034f53974b23",
                "channel_name": "main_email_channel",
                "port": "25",
                "smtp": "exchange.olive.com",
                "email_from": "internal-notifications@olive-vc.com.mt",
                "emails_to": "vitaly@olive-vc.com.mt",
                "info": "true",
                "warning": "true",
                "critical": "true",
                "error": "true",
                "parent_ids": "chain_name_7f4bc842-21b1-4bcb-8ab9-d86e08149548,chain_name_94aafe04-8287-463a-8416-0401852b3ca2,GLOBAL",
                "parent_names": "cosmos,kusama,GLOBAL"
            }
        }

        self.config_data_unexpected = {
            "unexpected": {}
        }

    def tearDown(self) -> None:
        connect_to_rabbit(self.rabbitmq)
        delete_queue_if_exists(self.rabbitmq, STORE_CONFIGS_QUEUE_NAME)
        delete_exchange_if_exists(self.rabbitmq, CONFIG_EXCHANGE)
        delete_exchange_if_exists(self.rabbitmq, HEALTH_CHECK_EXCHANGE)
        disconnect_from_rabbit(self.rabbitmq)

        connect_to_rabbit(self.test_rabbit_manager)
        delete_queue_if_exists(self.test_rabbit_manager, self.test_queue_name)
        disconnect_from_rabbit(self.test_rabbit_manager)

        self.redis.delete_all_unsafe()
        self.redis = None
        self.dummy_logger = None
        self.connection_check_time_interval = None
        self.rabbitmq = None
        self.test_rabbit_manager = None

    def test__str__returns_name_correctly(self) -> None:
        self.assertEqual(self.test_store_name, str(self.test_store))

    def test_name_property_returns_name_correctly(self) -> None:
        self.assertEqual(self.test_store_name, self.test_store.name)

    def test_mongo_ip_property_returns_mongo_ip_correctly(self) -> None:
        self.assertEqual(self.mongo_ip, self.test_store.mongo_ip)

    def test_mongo_db_property_returns_mongo_db_correctly(self) -> None:
        self.assertEqual(self.mongo_db, self.test_store.mongo_db)

    def test_mongo_port_property_returns_mongo_port_correctly(self) -> None:
        self.assertEqual(self.mongo_port, self.test_store.mongo_port)

    def test_redis_property_returns_redis_correctly(self) -> None:
        self.assertEqual(type(self.redis), type(self.test_store.redis))

    def test_mongo_property_returns_none_when_mongo_not_init(self) -> None:
        self.assertEqual(None, self.test_store.mongo)

    def test_initialise_rabbitmq_initialises_everything_as_expected(
            self) -> None:
        try:
            # To make sure that the exchanges have not already been declared
            self.rabbitmq.connect()
            self.rabbitmq.exchange_delete(HEALTH_CHECK_EXCHANGE)
            self.rabbitmq.exchange_delete(CONFIG_EXCHANGE)
            self.rabbitmq.disconnect()

            self.test_store._initialise_rabbitmq()

            # Perform checks that the connection has been opened, marked as open
            # and that the delivery confirmation variable is set.
            self.assertTrue(self.test_store.rabbitmq.is_connected)
            self.assertTrue(self.test_store.rabbitmq.connection.is_open)
            self.assertTrue(
                self.test_store.rabbitmq.channel._delivery_confirmation)

            # Check whether the producing exchanges have been created by
            # using passive=True. If this check fails an exception is raised
            # automatically.
            self.test_store.rabbitmq.exchange_declare(
                CONFIG_EXCHANGE, passive=True)
            self.test_store.rabbitmq.exchange_declare(
                HEALTH_CHECK_EXCHANGE, passive=True)

            # Check whether the exchange has been creating by sending messages
            # to it. If this fails an exception is raised, hence the test fails.
            self.test_store.rabbitmq.basic_publish_confirm(
                exchange=HEALTH_CHECK_EXCHANGE, routing_key=self.routing_key,
                body=self.test_data_str, is_body_dict=False,
                properties=pika.BasicProperties(delivery_mode=2),
                mandatory=False)
            # Check whether the exchange has been creating by sending messages
            # to it. If this fails an exception is raised, hence the test fails.
            self.test_store.rabbitmq.basic_publish_confirm(
                exchange=CONFIG_EXCHANGE,
                routing_key=STORE_CONFIGS_ROUTING_KEY_CHAINS,
                body=self.test_data_str, is_body_dict=False,
                properties=pika.BasicProperties(delivery_mode=2),
                mandatory=False)

            # Re-declare queue to get the number of messages
            res = self.test_store.rabbitmq.queue_declare(
                STORE_CONFIGS_QUEUE_NAME, False, True, False, False)

            self.assertEqual(1, res.method.message_count)
        except Exception as e:
            self.fail("Test failed: {}".format(e))

    @mock.patch("src.data_store.stores.store.RedisApi.hset",
                autospec=True)
    def test_process_redis_store_does_nothing_on_error_key(self,
                                                           mock_hset) -> None:
        self.test_store._process_redis_store(self.test_parent_id,
                                             self.config_data_unexpected)
        mock_hset.assert_not_called()

    @parameterized.expand([
        ("self.nodes_config_1", "self.routing_key_1"),
        ("self.alerts_config_1", "self.routing_key_2"),
        ("self.repos_config_1", "self.routing_key_3"),
        ("self.repos_config_1", "self.routing_key_4"),
        ("self.alerts_config_1", "self.routing_key_5"),
        ("self.systems_config_1", "self.routing_key_6"),
        ("self.email_config_1", "self.routing_key_7"),
        ("self.pagerduty_config_1", "self.routing_key_8"),
        ("self.opsgenie_config_1", "self.routing_key_9"),
        ("self.telegram_config_1", "self.routing_key_10"),
        ("self.twilio_config_1", "self.routing_key_11"),
    ])
    @mock.patch("src.data_store.stores.store.RabbitMQApi.basic_ack",
                autospec=True)
    @mock.patch("src.data_store.stores.store.Store._send_heartbeat",
                autospec=True)
    def test_process_data_saves_in_redis(self, mock_config_data,
                                         mock_routing_key, mock_send_hb,
                                         mock_ack) -> None:
        self.rabbitmq.connect()
        mock_ack.return_value = None
        try:
            data = eval(mock_config_data)
            routing_key = eval(mock_routing_key)

            self.test_store._initialise_rabbitmq()

            blocking_channel = self.test_store.rabbitmq.channel
            method_chains = pika.spec.Basic.Deliver(
                routing_key=eval(mock_routing_key))

            properties = pika.spec.BasicProperties()
            self.test_store._process_data(
                blocking_channel,
                method_chains,
                properties,
                json.dumps(data).encode()
            )
            mock_ack.assert_called_once()
            mock_send_hb.assert_called_once()

            self.assertEqual(data, json.loads(
                self.redis.get(Keys.get_config(routing_key)).decode(
                    "utf-8")))

        except Exception as e:
            self.fail("Test failed: {}".format(e))

    @freeze_time("2012-01-01")
    @mock.patch("src.data_store.stores.store.RabbitMQApi.basic_ack",
                autospec=True)
    @mock.patch("src.data_store.stores.config.ConfigStore._process_redis_store",
                autospec=True)
    def test_process_data_sends_heartbeat_correctly(self,
                                                    mock_process_redis_store,
                                                    mock_basic_ack) -> None:

        mock_basic_ack.return_value = None
        try:
            self.test_rabbit_manager.connect()
            self.test_store._initialise_rabbitmq()

            self.test_rabbit_manager.queue_delete(self.test_queue_name)
            res = self.test_rabbit_manager.queue_declare(
                queue=self.test_queue_name, durable=True, exclusive=False,
                auto_delete=False, passive=False
            )
            self.assertEqual(0, res.method.message_count)

            self.test_rabbit_manager.queue_bind(
                queue=self.test_queue_name, exchange=HEALTH_CHECK_EXCHANGE,
                routing_key=self.routing_key)

            blocking_channel = self.test_store.rabbitmq.channel
            method_chains = pika.spec.Basic.Deliver(
                routing_key=self.routing_key_1)

            properties = pika.spec.BasicProperties()
            self.test_store._process_data(
                blocking_channel,
                method_chains,
                properties,
                json.dumps(self.nodes_config_1).encode()
            )

            res = self.test_rabbit_manager.queue_declare(
                queue=self.test_queue_name, durable=True, exclusive=False,
                auto_delete=False, passive=True
            )
            self.assertEqual(1, res.method.message_count)

            heartbeat_test = {
                'component_name': self.test_store_name,
                'is_alive': True,
                'timestamp': datetime(2012, 1, 1).timestamp()
            }

            _, _, body = self.test_rabbit_manager.basic_get(
                self.test_queue_name)
            self.assertEqual(heartbeat_test, json.loads(body))
            mock_process_redis_store.assert_called_once()
        except Exception as e:
            self.fail("Test failed: {}".format(e))

    @mock.patch("src.data_store.stores.store.RabbitMQApi.basic_ack",
                autospec=True)
    def test_process_data_doesnt_send_heartbeat_on_processing_error(
            self, mock_basic_ack) -> None:

        mock_basic_ack.return_value = None
        try:
            self.test_rabbit_manager.connect()
            self.test_store._initialise_rabbitmq()

            self.test_rabbit_manager.queue_delete(self.test_queue_name)
            res = self.test_rabbit_manager.queue_declare(
                queue=self.test_queue_name, durable=True, exclusive=False,
                auto_delete=False, passive=False
            )
            self.assertEqual(0, res.method.message_count)

            self.test_rabbit_manager.queue_bind(
                queue=self.test_queue_name, exchange=HEALTH_CHECK_EXCHANGE,
                routing_key=self.routing_key)

            blocking_channel = self.test_store.rabbitmq.channel
            method_chains = pika.spec.Basic.Deliver(
                routing_key=None)

            properties = pika.spec.BasicProperties()
            self.test_store._process_data(
                blocking_channel,
                method_chains,
                properties,
                json.dumps(self.nodes_config_1).encode()
            )

            res = self.test_rabbit_manager.queue_declare(
                queue=self.test_queue_name, durable=True, exclusive=False,
                auto_delete=False, passive=True
            )
            self.assertEqual(0, res.method.message_count)
        except Exception as e:
            self.fail("Test failed: {}".format(e))

    @parameterized.expand([
        ("self.nodes_config_1", "self.routing_key_1"),
        ("self.alerts_config_1", "self.routing_key_2"),
        ("self.repos_config_1", "self.routing_key_3"),
        ("self.repos_config_1", "self.routing_key_4"),
        ("self.alerts_config_1", "self.routing_key_5"),
        ("self.systems_config_1", "self.routing_key_6"),
        ("self.email_config_1", "self.routing_key_7"),
        ("self.pagerduty_config_1", "self.routing_key_8"),
        ("self.opsgenie_config_1", "self.routing_key_9"),
        ("self.telegram_config_1", "self.routing_key_10"),
        ("self.twilio_config_1", "self.routing_key_11"),
    ])
    @mock.patch("src.data_store.stores.store.RabbitMQApi.basic_ack",
                autospec=True)
    @mock.patch("src.data_store.stores.store.Store._send_heartbeat",
                autospec=True)
    def test_process_data_saves_in_redis_then_removes_it_on_empty_config(
            self, mock_config_data, mock_routing_key, mock_send_hb,
            mock_ack) -> None:

        self.rabbitmq.connect()
        mock_ack.return_value = None
        try:
            data = eval(mock_config_data)
            routing_key = eval(mock_routing_key)

            self.test_store._initialise_rabbitmq()

            blocking_channel = self.test_store.rabbitmq.channel
            method_chains = pika.spec.Basic.Deliver(
                routing_key=routing_key)

            properties = pika.spec.BasicProperties()
            self.test_store._process_data(
                blocking_channel,
                method_chains,
                properties,
                json.dumps(data).encode()
            )
            mock_ack.assert_called_once()
            mock_send_hb.assert_called_once()

            self.assertEqual(data, json.loads(
                self.redis.get(Keys.get_config(routing_key)).decode("utf-8")))

            self.test_store._process_data(
                blocking_channel,
                method_chains,
                properties,
                json.dumps({}).encode()
            )

            self.assertEqual(None,
                             self.redis.get(Keys.get_config(routing_key)))

        except Exception as e:
            self.fail("Test failed: {}".format(e))
