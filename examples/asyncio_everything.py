""" Example that does a bit of everything, error handling, streaming, events etc """

import logging
import asyncio
import argparse
import pkg_resources

import qtm


logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("example")


QTM_FILE = pkg_resources.resource_filename("qtm", "data/Demo.qtm")


class AsyncEnumerate:
    """ Simple async enumeration class """

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


async def packet_receiver(queue):
    """ Asynchronous function that processes queue until None is posted in queue """
    LOG.info("Entering packet_receiver")
    while True:
        packet = await queue.get()
        if packet is None:
            break

        LOG.info("Framenumber %s", packet.framenumber)
    LOG.info("Exiting packet_receiver")


async def choose_qtm_instance(interface):
    """ List running QTM instances, asks for input and return chosen QTM """
    instances = {}
    print("Available QTM instances:")
    async for i, qtm_instance in AsyncEnumerate(qtm.Discover(interface), start=1):
        instances[i] = qtm_instance
        print("{} - {}".format(i, qtm_instance.info))

    try:

        choice = int(input("Connect to: "))

        if choice not in instances:
            raise ValueError

    except ValueError:
        LOG.error("Invalid choice")
        return None

    return instances[choice].host


async def main(interface=None):
    """ Main function """

    qtm_ip = await choose_qtm_instance(interface)
    if qtm_ip is None:
        return

    while True:

        connection = await qtm.connect(qtm_ip, 22223, version="1.18")

        if connection is None:
            return

        await connection.get_state()
        await connection.byte_order()

        async with qtm.TakeControl(connection, "password"):

            result = await connection.close()
            if result == b"Closing connection":
                await connection.await_event(qtm.QRTEvent.EventConnectionClosed)

            await connection.load(QTM_FILE)

            await connection.start(rtfromfile=True)

            (await connection.get_current_frame(components=["3d"])).get_3d_markers()

            queue = asyncio.Queue()

            asyncio.ensure_future(packet_receiver(queue))

            try:
                await connection.stream_frames(
                    components=["incorrect"], on_packet=queue.put_nowait
                )
            except qtm.QRTCommandException as exception:
                LOG.info("exception %s", exception)

            await connection.stream_frames(
                components=["3d"], on_packet=queue.put_nowait
            )

            await asyncio.sleep(0.5)
            await connection.byte_order()
            await asyncio.sleep(0.5)
            await connection.stream_frames_stop()
            queue.put_nowait(None)

            await connection.get_parameters(parameters=["3d"])
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
            await connection.set_qtm_event("with_label")

            await asyncio.sleep(0.5)

            await connection.stop()
            await connection.await_event(qtm.QRTEvent.EventCaptureStopped)

            await connection.save(r"measurement.qtm")

            await asyncio.sleep(3)

            await connection.close()

        connection.disconnect()


def parse_args():
    parser = argparse.ArgumentParser(description="Example to connect to QTM")
    parser.add_argument(
        "--ip",
        type=str,
        required=False,
        default="127.0.0.1",
        help="IP of interface to search for QTM instances",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.get_event_loop().run_until_complete(main(interface=args.ip))
