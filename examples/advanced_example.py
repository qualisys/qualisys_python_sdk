import asyncio
import logging

import qtm

logger = logging.getLogger(__name__)


async def package_receiver(queue):
    logger.info('Entering package_receiver')
    while True:
        packet = await queue.get()
        if packet is None:
            break

        logger.info("Framenumber %s", packet.framenumber)
        header, cameras = packet.get_2d_markers()
        logger.info("Component info: %s", header)

        for i, camera in enumerate(cameras, 1):
            logger.info('Camera %d', i)
            for marker in camera:
                logger.info("\t%s", marker)

    logger.info('Exiting package_receiver')


async def main():
    connection = await qtm.connect("127.0.0.1")

    if connection is None:
        return -1

    async with qtm.take_control(connection, 'password'):

        state = await connection.get_state()
        if state != qtm.QRTEvent.EventConnected:
            await connection.new()
            try:
                await connection.await_event(
                    qtm.QRTEvent.EventConnected, timeout=10)
            except asyncio.TimeoutError:
                logger.error('Failed to start new measurement')
                return -1

        queue = asyncio.Queue()
        asyncio.ensure_future(package_receiver(queue))

        await connection.stream_frames(
            components=['2d'], on_packet=queue.put_nowait)
        await asyncio.sleep(60)
        await connection.stream_frames_stop()
        queue.put_nowait(None)

        await connection.close()


if __name__ == '__main__':
    exit(asyncio.get_event_loop().run_until_complete(main()))
