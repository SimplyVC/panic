import logging
from typing import Dict

from src.channels_manager.channels.telegram import TelegramChannel
from src.channels_manager.commands.handlers.telegram_cmd_handlers import \
    TelegramCommandHandlers
from src.channels_manager.handlers.handler import ChannelHandler
from src.data_store.mongo import MongoApi
from src.data_store.redis import RedisApi
from telegram.ext import CommandHandler, MessageHandler, Filters


class TelegramCommandsHandler(ChannelHandler):
    def __init__(self, logger: logging.Logger, handler_name: str,
                 associated_chains: Dict, telegram_channel: TelegramChannel,
                 redis: RedisApi, mongo: MongoApi) -> None:
        super().__init__(handler_name, logger)

        self._cmd_handlers = TelegramCommandHandlers(
            'Telegram Command Handlers', logger, redis, mongo,
            associated_chains, telegram_channel)

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

        # TODO: Todo continue from TleemgraCommandHandler (from beginning) in
        #     : panic_polakdot class.

        # TODO: Must have it's own rabbit connection as this is in a separate
        #     : thread and may block. This must also check that the updater
        #     : thread is running and it must respond to heartbeats (similar to
        #     : configs manager. If we do not manager to do this, block till we
        #     : get an exit signal.

        # TODO: Must also have graceful termination.

    @property
    def cmd_handlers(self) -> TelegramCommandHandlers:
        return self._cmd_handlers
