from typing import Dict, List

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, \
    CallbackContext

from src.utils.alert import Severity


class TelegramCommandsHandler:
    def __init__(self, associated_chains: Dict) -> None:
        self._associated_chains = associated_chains

    @property
    def associated_chains(self) -> Dict:
        return self._associated_chains

    def authorise(self, update: Update, context: CallbackContext) -> bool:
        return True
