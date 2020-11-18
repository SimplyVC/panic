import logging
from typing import Optional, Dict, List

from src.alerters.reactive.node import Node
from src.store.mongo.mongo_api import MongoApi
from src.store.redis.redis_api import RedisApi
from src.utils.config_parsers.internal import InternalConfig
from src.utils.config_parsers.internal_parsed import InternalConf
from src.utils.config_parsers.user import UserConfig
from src.utils.config_parsers.user_parsed import UserConf

# TODO: Commands responses do not need to be re-queued as the data must be
#     : in real time. Therefore log the error only


class Commands:

    def __init__(self, logger: logging.Logger, redis: Optional[RedisApi],
                 mongo: Optional[MongoApi],
                 node_monitor_nodes_by_chain: Dict[str, List[Node]],
                 archive_alerts_disabled_by_chain: Dict[str, bool],
                 internal_conf: InternalConfig = InternalConf,
                 user_conf: UserConfig = UserConf) -> None:
        self._logger = logger

        self._redis = redis
        self._mongo = mongo

        self._redis_enabled = redis is not None

        # Whether archive alerts disabled for the chain that a node is running
        self._archive_alerts_disabled_for_chain_by_node = {}
        for c, ns in node_monitor_nodes_by_chain.items():
            for n in ns:
                self._archive_alerts_disabled_for_chain_by_node[n.name] = \
                    archive_alerts_disabled_by_chain[c]

        self._internal_conf = internal_conf
        self._user_conf = user_conf

    def snooze(self) -> None:
        pass

    def unsnooze(self) -> None:
        pass

    def mute(self) -> None:
        pass

    def unmute(self) -> None:
        pass

    def add_node(self) -> None:
        pass

    def remove_node(self) -> None:
        pass

    def current_nodes(self) -> None:
        pass
