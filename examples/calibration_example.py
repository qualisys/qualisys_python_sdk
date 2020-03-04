""" Example that takes control of QTM, connects and starts a calibration. """

import asyncio
import logging
import qtm
from lxml import etree

LOG = logging.getLogger("example")

async def setup():
    """ main function """

    connection = await qtm.connect("127.0.0.1")

    if connection is None:
        return -1

    async with qtm.TakeControl(connection, "password"):

        state = await connection.get_state()
        if state != qtm.QRTEvent.EventConnected:
            await connection.new()
            try:
                await connection.await_event(qtm.QRTEvent.EventConnected, timeout=10)
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
            root = etree.fromstring(cal_response)
            print(etree.tostring(root, pretty_print=True).decode())

    # tell qtm to stop streaming
    await connection.stream_frames_stop()

    # stop the event loop, thus exiting the run_forever call
    loop.stop()    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(setup())
    loop.run_forever()
