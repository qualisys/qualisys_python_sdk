"""
Example that enables images from a camera and writes a single frame to a file.
"""

import argparse
import asyncio
import logging
import os
import qtm_rt
import xml.etree.ElementTree as ET


def output_format(output_path):
    extension = os.path.splitext(output_path)[1].lower()
    if extension == ".jpg":
        return "jpg"
    if extension == ".png":
        return "png"

    raise RuntimeError("Unsupported output format {extension}")


def enable_disable_cameras(output_path, target_camera_id, xml_str):
    format = output_format(output_path)
    xml = ET.fromstring(xml_str)
    for camera in xml.findall("./Image/Camera"):
        camera_id = camera.find("ID").text
        is_target_camera = camera_id == target_camera_id
        logging.info("Setting Enabled for Camera %s to %s", camera_id, is_target_camera)
        camera.find("Enabled").text = str(is_target_camera)

        if is_target_camera:
            camera.find("Format").text = format

    xml.tag = "QTM_Settings"
    return ET.tostring(xml).decode("utf-8")


async def main(password, target_camera_id, output_path):
    connection = await qtm_rt.connect("127.0.0.1")

    if connection is None:
        raise RuntimeError("Failed to connect")

    settings = await connection.get_parameters(parameters=["image"])
    updated_settings = enable_disable_cameras(output_path, target_camera_id, settings)

    async with qtm_rt.TakeControl(connection, password):
        logging.debug("%s", await connection.send_xml(updated_settings))

        frame = await connection.get_current_frame(components=["image"])
        info, images = frame.get_image()
        logging.info("%s", info)
        logging.info("%s", images[0][0])
        with open(output_path, "wb") as f:
            logging.info("Writing %s", output_path)
            f.write(images[0][1])

    connection.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get single camera image from QTM over RT protocol."
    )
    parser.add_argument("-o", "--output", required=True, help="Output file path.")
    parser.add_argument("-c", "--camera", required=True, help="Camera ID.")
    parser.add_argument("-p", "--password", default="", help="RT server password.")
    args = parser.parse_args()

    asyncio.run(main(args.password, args.camera, args.output))
