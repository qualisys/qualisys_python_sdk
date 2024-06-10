""" Example that takes control of QTM, connects and starts a calibration. """

import asyncio
import logging
import qtm_rt
import xml.etree.ElementTree as ET

LOG = logging.getLogger("example")

async def setup():
    """ main function """

    connection = await qtm_rt.connect("127.0.0.1")

    if connection is None:
        return -1

    async with qtm_rt.TakeControl(connection, "password"):

        state = await connection.get_state()
        if state != qtm_rt.QRTEvent.EventConnected:
            await connection.new()
            try:
                await connection.await_event(qtm_rt.QRTEvent.EventConnected, timeout=10)
            except asyncio.TimeoutError:
                LOG.error("Failed to start new measurement")
                return -1

        try:
            cal_response = await connection.calibrate()
        except asyncio.TimeoutError:
            LOG.error("Timeout waiting for calibration result.")
        except Exception as e:
            LOG.error(e)
        else:
            root = ET.fromstring(cal_response)
            print(ET.tostring(root, pretty_print=True).decode())

    # tell qtm to stop streaming
    await connection.stream_frames_stop()

if __name__ == "__main__":
    asyncio.run(setup())
