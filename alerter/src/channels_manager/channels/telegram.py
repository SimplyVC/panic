import logging

from src.alerter.alerts.alert import Alert
from src.channels_manager.apis.telegram_bot_api import TelegramBotApi
from src.channels_manager.channels.channel import Channel, RequestStatus


class TelegramChannel(Channel):

    def __init__(self, channel_name: str, logger: logging.Logger,
                 telegram_bot: TelegramBotApi) -> None:
        super().__init__(channel_name, logger)

        self._telegram_bot = telegram_bot

    def alert(self, alert: Alert) -> RequestStatus:
        subject = 'PANIC {}'.format(alert.severity.upper())
        try:
            ret = self._telegram_bot.send_message('*{}*: `{}`'.format(
                subject, alert.message))
            self.logger.debug("alert: telegram_ret: %s", ret)
            if ret['ok']:
                self.logger.info("Sent {} to Telegram channel {}.".format(
                    alert.alert_code.name, self))
                return RequestStatus.SUCCESS
            else:
                self.logger.error(
                    "Error when sending {} to Telegram channel {}: {}.".format(
                        alert.alert_code.name, self, ret['description']))
                return RequestStatus.FAILED
        except Exception as e:
            self.logger.error(
                "Error when sending {} to Telegram channel {}.".format(
                    alert.alert_code.name, self))
            self.logger.exception(e)
            return RequestStatus.FAILED
