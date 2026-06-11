"""
    Streaming 6Dof from QTM
"""

import asyncio
import argparse
import xml.etree.ElementTree as ET

import qtm_rt


def create_body_index(xml_string):
    """ Extract a name to index dictionary from 6dof settings xml """
    xml = ET.fromstring(xml_string)

    body_to_index = {}
    for index, body in enumerate(xml.findall("*/Body/Name")):
        body_to_index[body.text.strip()] = index

    return body_to_index


def body_enabled_count(xml_string):
    xml = ET.fromstring(xml_string)
    return sum(enabled.text == "true" for enabled in xml.findall("*/Body/Enabled"))


async def main(qtm_file):

    # Connect to qtm
    connection = await qtm_rt.connect("127.0.0.1")

    # Connection failed?
    if connection is None:
        print("Failed to connect")
        return

    async with connection:
        # Take control of qtm, context manager will automatically release control after scope end
        async with qtm_rt.TakeControl(connection, "password"):

            realtime = False

            if realtime:
                # Start new realtime
                await connection.new()
            else:
                # Load qtm file
                await connection.load(qtm_file)

                # start rtfromfile
                await connection.start(rtfromfile=True)

        # Get 6dof settings from qtm
        xml_string = await connection.get_parameters(parameters=["6d"])
        body_index = create_body_index(xml_string)

        print(
            "{} of {} 6DoF bodies enabled".format(
                body_enabled_count(xml_string), len(body_index)
            )
        )

        wanted_body = "L-frame"

        def on_packet(packet):
            info, bodies = packet.get_6d()
            print(
                "Framenumber: {} - Body count: {}".format(
                    packet.framenumber, info.body_count
                )
            )

            if wanted_body is not None and wanted_body in body_index:
                # Extract one specific body
                wanted_index = body_index[wanted_body]
                position, rotation = bodies[wanted_index]
                print("{} - Pos: {} - Rot: {}".format(wanted_body, position, rotation))
            else:
                # Print all bodies
                for position, rotation in bodies:
                    print("Pos: {} - Rot: {}".format(position, rotation))

        # Start streaming frames
        await connection.stream_frames(components=["6d"], on_packet=on_packet)

        # Wait asynchronously 5 seconds
        await asyncio.sleep(5)

        # Stop streaming
        await connection.stream_frames_stop()


def parse_args():
    parser = argparse.ArgumentParser(description="Stream 6DoF data from QTM")
    parser.add_argument(
        "--qtm-file",
        type=str,
        required=False,
        default="Demo.qtm",
        help="QTM file to load for rtfromfile playback",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    # Run our asynchronous function until complete
    asyncio.run(main(args.qtm_file))
