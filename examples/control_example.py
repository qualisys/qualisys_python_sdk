""" Example that takes control of QTM, starts a measurment and stops after 10 seconds and saves the measurement to a file """

import asyncio
import logging


import qtm_rt

LOG = logging.getLogger("example")


async def setup():
    """ Main function that connects to the QTM server, starts a measurement, and saves the data to a file """
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
        # Start the measurement
        await connection.start()
        await connection.await_event(qtm_rt.QRTEvent.EventCaptureStarted, timeout=10)

        # Wait 10 seconds
        await asyncio.sleep(10)

        await connection.stop()
        await connection.await_event(qtm_rt.QRTEvent.EventCaptureStopped, timeout=10)
        await connection.save("Demo.qtm")

        LOG.info("Measurement saved to Demo.qtm")

    connection.disconnect()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
