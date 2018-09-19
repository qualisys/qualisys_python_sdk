""" Example that takes control of QTM, streams data etc """

import asyncio
import logging

import qtm

LOG = logging.getLogger("example")


async def package_receiver(queue):
    """ Asynchronous function that processes queue until None is posted in queue """
    LOG.info("Entering package_receiver")
    while True:
        packet = await queue.get()
        if packet is None:
            break

        LOG.info("Framenumber %s", packet.framenumber)
        header, cameras = packet.get_2d_markers()
        LOG.info("Component info: %s", header)

        for i, camera in enumerate(cameras, 1):
            LOG.info("Camera %d", i)
            for marker in camera:
                LOG.info("\t%s", marker)

    LOG.info("Exiting package_receiver")


async def shutdown(delay, connection, receiver_future, queue):

    # wait desired time before exiting
    await asyncio.sleep(delay)

    # make sure package_receiver task exits
    queue.put_nowait(None)
    await receiver_future

    # tell qtm to stop streaming
    await connection.stream_frames_stop()

    # stop the event loop, thus exiting the run_forever call
    loop.stop()


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

        queue = asyncio.Queue()

        receiver_future = asyncio.ensure_future(package_receiver(queue))

        await connection.stream_frames(components=["2d"], on_packet=queue.put_nowait)

        asyncio.ensure_future(shutdown(30, connection, receiver_future, queue))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(setup())
    loop.run_forever()
