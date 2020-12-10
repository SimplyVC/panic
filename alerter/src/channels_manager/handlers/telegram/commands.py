import json
import logging
import signal
import sys
from datetime import datetime
from types import FrameType
from typing import Dict

import pika
import pika.exceptions
from pika.adapters.blocking_connection import BlockingChannel
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

from src.channels_manager.apis.telegram_bot_api import TelegramBotApi
from src.channels_manager.channels.telegram import TelegramChannel
from src.channels_manager.commands.handlers.telegram_cmd_handlers import \
    TelegramCommandHandlers
from src.channels_manager.handlers.handler import ChannelHandler
from src.data_store.redis import Keys
from src.message_broker.rabbitmq import RabbitMQApi
# from src.utils import env
from src.utils.constants import HEALTH_CHECK_EXCHANGE
from src.utils.exceptions import MessageWasNotDeliveredException
from src.utils.logging import log_and_print, create_logger


class TelegramCommandsHandler(ChannelHandler):
    def __init__(self, logger: logging.Logger, handler_name: str,
                 associated_chains: Dict, telegram_channel: TelegramChannel) \
            -> None:
        super().__init__(handler_name, logger)

        self._telegram_channel = telegram_channel
        self._cmd_handlers = TelegramCommandHandlers(
            'Telegram Command Handlers', logger, associated_chains,
            telegram_channel)

        command_specific_handlers = [
            CommandHandler('start', self.cmd_handlers.start_callback),
            CommandHandler('mute', self.cmd_handlers.mute_callback),
            CommandHandler('unmute', self.cmd_handlers.unmute_callback),
            CommandHandler('mute_all', self.cmd_handlers.mute_all_callback),
            CommandHandler('unmute_all', self.cmd_handlers.unmute_all_callback),
            CommandHandler('status', self.cmd_handlers.status_callback),
            CommandHandler('ping', self.cmd_handlers.ping_callback),
            CommandHandler('help', self.cmd_handlers.help_callback),
            MessageHandler(Filters.command, self.cmd_handlers.unknown_callback)
        ]

        # Set up updater
        self._updater = Updater(token=telegram_channel.telegram_bot.bot_token,
                                use_context=True)

        for handler in command_specific_handlers:
            self._updater.dispatcher.add_handler(handler)

        # rabbit_ip = env.RABBIT_IP
        rabbit_ip = 'localhost'
        self._rabbitmq = RabbitMQApi(logger=self.logger.getChild('rabbitmq'),
                                     host=rabbit_ip)

        # Handle termination signals by stopping the handler gracefully
        signal.signal(signal.SIGTERM, self.on_terminate)
        signal.signal(signal.SIGINT, self.on_terminate)
        # signal.signal(signal.SIGHUP, self.on_terminate)

    @property
    def cmd_handlers(self) -> TelegramCommandHandlers:
        return self._cmd_handlers

    @property
    def rabbitmq(self) -> RabbitMQApi:
        return self._rabbitmq

    @property
    def telegram_channel(self) -> TelegramChannel:
        return self._telegram_channel

    def _initialize_rabbitmq(self) -> None:
        self.rabbitmq.connect_till_successful()

        # Declare consuming intentions
        self.logger.info("Creating '{}' exchange".format(HEALTH_CHECK_EXCHANGE))
        self.rabbitmq.exchange_declare(HEALTH_CHECK_EXCHANGE, 'topic', False,
                                       True, False, False)
        self.logger.info(
            "Creating queue 'telegram_{}_commands_handler_queue'".format(
                self.telegram_channel.channel_id))
        self.rabbitmq.queue_declare('telegram_{}_commands_handler_queue'.format(
            self.telegram_channel.channel_id), False, True, False, False)
        self.logger.info("Binding queue 'telegram_{}_commands_handler_queue' "
                         "to exchange '{}' with routing key "
                         "'ping'".format(self.telegram_channel.channel_id,
                                         HEALTH_CHECK_EXCHANGE))
        self.rabbitmq.queue_bind('telegram_{}_commands_handler_queue'.format(
            self.telegram_channel.channel_id), HEALTH_CHECK_EXCHANGE, 'ping')
        self.logger.info("Declaring consuming intentions on "
                         "'telegram_{}_commands_handler_queue'"
                         .format(self.telegram_channel.channel_id))
        self.rabbitmq.basic_consume('telegram_{}_commands_handler_queue'.format(
            self.telegram_channel.channel_id), self._process_ping, True, False,
            None)

        # Declare publishing intentions
        self.logger.info("Setting delivery confirmation on RabbitMQ channel")
        self.rabbitmq.confirm_delivery()

    def _send_heartbeat(self, data_to_send: Dict) -> None:
        self.rabbitmq.basic_publish_confirm(
            exchange=HEALTH_CHECK_EXCHANGE, routing_key='heartbeat.worker',
            body=data_to_send, is_body_dict=True,
            properties=pika.BasicProperties(delivery_mode=2), mandatory=True)
        self.logger.info("Sent heartbeat to '{}' exchange".format(
            HEALTH_CHECK_EXCHANGE))

    def _listen_for_data(self) -> None:
        self.rabbitmq.start_consuming()

    def _start_handling(self, run_in_background: bool = False) -> None:
        # Start polling
        self._updater.start_polling(clean=True)

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        if not run_in_background:
            self._updater.idle(stop_signals=[])

    def _stop_handling(self) -> None:
        # This is useful only when the Updater is set to run in background
        self._updater.stop()
        self.logger.info("Stopped handling commands.")

    def _process_ping(
            self, ch: BlockingChannel, method: pika.spec.Basic.Deliver,
            properties: pika.spec.BasicProperties, body: bytes) -> None:
        data = body
        self.logger.info("Received {}".format(data))

        heartbeat = {}
        try:
            heartbeat['component_name'] = self.handler_name
            heartbeat['running_processes'] = self._updater.running
            heartbeat['timestamp'] = datetime.now().timestamp()

            # If updater is not running, try to restart it.
            if not self._updater.running:
                self._start_handling(run_in_background=True)
        except Exception as e:
            # If we encounter an error during processing log the error and
            # return so that no heartbeat is sent
            self.logger.error("Error when processing {}".format(data))
            self.logger.exception(e)
            return

        # Send heartbeat if processing was successful
        try:
            self._send_heartbeat(heartbeat)
        except MessageWasNotDeliveredException as e:
            # Log the message and do not raise it as there is no use in
            # re-trying to send a heartbeat
            self.logger.exception(e)
        except Exception as e:
            # For any other exception raise it.
            raise e

    def start(self) -> None:
        self._initialize_rabbitmq()
        while True:
            try:
                self._start_handling(run_in_background=True)
                self._listen_for_data()
            except (pika.exceptions.AMQPConnectionError,
                    pika.exceptions.AMQPChannelError) as e:
                # If we have either a channel error or connection error, the
                # channel is reset, therefore we need to re-initialize the
                # connection or channel settings. Also, stop the updater thread.
                self._stop_handling()
                raise e
            except Exception as e:
                self.logger.exception(e)
                self._stop_handling()
                raise e

    def on_terminate(self, signum: int, stack: FrameType) -> None:
        pass
        log_and_print("{} is terminating. Connections with RabbitMQ will be "
                      "closed, and afterwards the process will "
                      "exit.".format(self), self.logger)
        self.rabbitmq.disconnect_till_successful()
        self.cmd_handlers.rabbitmq.disconnect_till_successful()
        self._stop_handling()
        log_and_print("{} terminated.".format(self), self.logger)
        sys.exit()


test_logger = create_logger('test.log', 'test', 'DEBUG', rotating=True)
bot_token = '1214185733:AAF-78AENtsYXxxdqTL3Ip987N7gmIKJaBE'
chat_id = '933795729'
associated_chains = {'kusama_12345': 'Kusama_ah', 'polkadot_12345': 'Polkadot',
                     'akala_12345': 'Akala'}
telegram_bot = TelegramBotApi(bot_token, chat_id)
telegram_channel = TelegramChannel('test_channel', 'channel12345', test_logger,
                                   telegram_bot)
tch = TelegramCommandsHandler(test_logger, 'Telegram Commands Handler',
                              associated_chains, telegram_channel)

# key_heartbeat = Keys.get_component_heartbeat('Heartbeat Handler')
# handler_heartbeat = {'component_name': 'Heartbeat Handler',
#                      'timestamp': datetime.now().timestamp()}
# transformed_handler_heartbeat = json.dumps(handler_heartbeat)
# tch.cmd_handlers.redis.set(key_heartbeat, transformed_handler_heartbeat)
#
# key_heartbeat = Keys.get_component_heartbeat('Ping Publisher')
# ping_pub_heartbeat = {'component_name': 'Ping Publisher',
#                       'timestamp': datetime.now().timestamp()}
# transformed_ping_pub_heartbeat = json.dumps(ping_pub_heartbeat)
# tch.cmd_handlers.redis.set(key_heartbeat, transformed_ping_pub_heartbeat)

while True:
    try:
        tch.start()
    except Exception as e:
        pass


# TODO: Need to clean up commented code and test code