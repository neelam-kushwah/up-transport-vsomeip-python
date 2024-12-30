"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import asyncio
import logging
import time
from typing import List

from uprotocol.communication.upayload import UPayload
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.v1.uattributes_pb2 import UPayloadFormat
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus

from uprotocol_vsomeip.vsomeip_utransport import VsomeipHelper, VsomeipTransport

logger = logging.getLogger()
LOG_FORMAT = "%(asctime)s [%(levelname)s] @ %(filename)s.%(module)s.%(funcName)s:%(lineno)d \n %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.getLevelName("DEBUG"))


class Helper(VsomeipHelper):
    """
    Helper class to provide list of services to be offered
    """

    def services_info(self) -> List[VsomeipHelper.UEntityInfo]:
        return [
            VsomeipHelper.UEntityInfo(
                service_id=1,
                events=[0x8000],
                port=30509,
                major_version=1,
            )
        ]


someip = VsomeipTransport(helper=Helper(), source=UUri(ue_id=1, ue_version_major=1, resource_id=0))
uuri = UUri(ue_id=1, ue_version_major=1, resource_id=0x8000)


async def publish():
    """
    Publish data to a topic
    """
    data = "Hello World!"
    payload = UPayload.pack_from_data_and_format(data.encode("utf-8"), UPayloadFormat.UPAYLOAD_FORMAT_TEXT)
    message = UMessageBuilder.publish(uuri).build_from_upayload(payload)
    logger.debug("Sending %s to %s...", data, uuri)
    await someip.send(message)


class MyListener(UListener):
    """
    Listener class to define callback
    """

    async def on_receive(self, message: UMessage) -> UStatus:
        """
        on_receive call back method
        :param message:
        :return: UStatus
        """
        logger.debug(
            "listener -> id: %s, data: %s",
            message.attributes.source.resource_id,
            message.payload,
        )
        return UStatus(message="Received event")


listener = MyListener()


async def subscribe():
    """
    Subscribe to a topic
    """
    await someip.register_listener(source_filter=uuri, listener=listener)


async def unsubscribe():
    """
    Unsubscribe to a topic
    """
    await someip.unregister_listener(source_filter=uuri, listener=listener)


async def main() -> None:
    """
    Main function to demonstrate publish and subscribe
    """
    await subscribe()
    time.sleep(1)
    await publish()
    time.sleep(5)
    # await unsubscribe()
    time.sleep(1)
    await publish()
    time.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
