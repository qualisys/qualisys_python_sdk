import asyncio
import struct

import qtm

import logging
logger = logging.getLogger(__name__)


class aenumerate:
    def __init__(self, aiterable, start=0):
        self.aiterable = aiterable
        self.i = start

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self.aiterable.__anext__()
        result = (self.i, item)
        self.i += 1
        return result


async def package_receiver(queue):
    while True:
        packet = await queue.get()
        if packet is None:
            break

        logger.info("Framenumber %s", packet.framenumber)


async def main():

    # await qtm.reboot("192.168.11.2")

    async for _ in qtm.discover("192.168.10.123"):
        pass

    while True:

        connection = await qtm.connect("127.0.0.1", 22223, version='1.18')

        if connection is None:
            return

        await connection.get_state()
        await connection.byte_order()

        async with qtm.take_control(connection, 'password'):

            await connection.load(r'd:\measurements\demo_2018\David ROM 1.qtm')

            await connection.start(rtfromfile=True)

            (await connection.get_current_frame()).get_3d_markers()

            queue = asyncio.Queue()

            asyncio.ensure_future(package_receiver(queue))

            try:
                await connection.stream_frames(
                    components=['incorrect'], on_packet=queue.put_nowait)
            except Exception as e:
                logger.info("exception %s", e)

            await connection.stream_frames(
                components=['3d'], on_packet=queue.put_nowait)

            await asyncio.sleep(0.5)
            await connection.byte_order()
            await asyncio.sleep(0.5)
            await connection.stream_frames_stop()
            queue.put_nowait(None)

            await connection.get_parameters(parameters=['3d'])
            await connection.stop()

            await connection.await_event()

            await connection.new()

            await connection.await_event(qtm.QRTEvent.EventConnected)

            await connection.start()

            await connection.await_event(qtm.QRTEvent.EventWaitingForTrigger)

            await connection.trig()

            await connection.await_event(qtm.QRTEvent.EventCaptureStarted)

            await asyncio.sleep(0.5)

            await connection.set_qtm_event()
            await asyncio.sleep(0.001)
            await connection.set_qtm_event('with_label')

            await asyncio.sleep(0.5)

            await connection.stop()

            await connection.await_event(qtm.QRTEvent.EventCaptureStopped)

            # await connection.save(r'd:\apa.qtm')

            # await asyncio.sleep(3)

            await connection.close()

        connection.disconnect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
