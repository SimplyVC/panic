import logging

from opsgenie_sdk import SuccessResponse

from src.alerter.alerts.alert import Alert
from src.channels_manager.apis.opsgenie_api import OpsgenieApi
from src.channels_manager.channels import Channel
from src.utils.data import RequestStatus
from src.utils.types import OpsgenieSeverities


class OpsgenieChannel(Channel):
    def __init__(self, channel_name: str, channel_id: str,
                 logger: logging.Logger, opsgenie_api: OpsgenieApi):
        super().__init__(channel_name, channel_id, logger)
        self._opsgenie_api = opsgenie_api

    def alert(self, alert: Alert) -> RequestStatus:
        severity = {
            "critical": OpsgenieSeverities.CRITICAL,
            "error": OpsgenieSeverities.ERROR,
            "warning": OpsgenieSeverities.WARNING,
            "info": OpsgenieSeverities.INFO,
        }.get(alert.severity.lower(), OpsgenieSeverities.INFO)

        try:
            response = self._opsgenie_api.create_alert(
                "PANIC - {}".format(alert.alert_code.name), alert.message,
                severity, alert.origin_id, alert.timestamp,
                alias=alert.alert_code.value
            )
            self.logger.info(
                "Sent %s to OpsGenie channel %s, received response %s",
                alert.alert_code.name, self.__str__(), response
            )

            if type(response) == SuccessResponse:
                return RequestStatus.SUCCESS
            else:
                return RequestStatus.FAILED
        except Exception as e:
            self.logger.error("Error when sending %s to OpsGenie channel %s",
                              alert.alert_code.name, self.__str__())
            self.logger.exception(e)
            return RequestStatus.FAILED
