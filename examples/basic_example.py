"""
    Minimal usage example
    Connects to QTM and streams 3D data forever
    (start QTM first, load file, Play->Play with Real-Time output)
"""

import asyncio
import qtm


def on_packet(packet):
    """ Callback function that is called everytime a data packet arrives from QTM """
    print("Framenumber: {}".format(packet.framenumber))
    header, markers = packet.get_3d_markers()
    print("Component info: {}".format(header))
    for marker in markers:
        print("\t", marker)


async def setup():
    """ Main function """
    connection = await qtm.connect("127.0.0.1")
    if connection is None:
        return

    await connection.stream_frames(components=["3d"], on_packet=on_packet)


if __name__ == "__main__":
    asyncio.ensure_future(setup())
    asyncio.get_event_loop().run_forever()
