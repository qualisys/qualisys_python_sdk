# -*- coding: utf-8 -*-

"""Example script for a behavioral experiment.

Displays full-screen images randomly drawn from a specified folder,
and syncs with QTM to insert events into QTM timeline as images are shown.

A new (blank) measurement must be open in QTM before the script is run!

The script connects to QTM in the beginning and starts capture with the first
key press. With each subsequent key press, the script displays a new image and
creates a QTM event labeled with the name of the image file.

Requires pyglet (pypi.python.org/pypi/pyglet) to display full-screen images and
pigtwist (github.com/padraigkitterick/pigtwist) for pyglet-twisted
interoperability.
"""

import os
from datetime import datetime
import random

import pyglet

from pigtwist import pygletreactor
reactor = pygletreactor.install()

from twisted.internet import defer

import qtm
from qtm.packet import QRTEvent
from qtm.protocol import QRTCommandException


class Globals():
    """Global variables to keep track of experiment flow, image files, etc.

    The following are options, to be edited to suit:
        FULLSCREEN (bool): Toggles fullscreen or windowed mode for pyglet.
        IMAGES_DIR (str): Path to folder with images. Include trailing slash!
        IMAGES_SCALE (float): Scaling factor to resize images.
        LEGAL_FILE_EXTENSIONS (list of str): Types of image files to read from
            the directory. Case sensitive! Include leading dot!
        LOG_FILE (str): Path to a text file where the log will be written.
            Include extension!
        QTM_PROJECT_DATA_DIR (str): Path to the Data directory in the QTM
            project. Include trailing slash!
        QTM_RT_PASSWORD (str): Password for QTM real-time client control.
            Default is blank ("").
        QTM_RT_PORT (int): Port number (little endian) for QTM real-time
            connection. Default is 22223.
        SCREEN_IDX (int): Index of screen to create pyglet window on. See
            pyglet documentation for more info.


    STATUS_* variables can be changed or added (along with new directories for
    images) to modify experiment flow; this is only a rudimentary example.
    """

    FULLSCREEN = False
    IMAGES_DIR = "PATH_TO_IMAGES_DIR/"
    IMAGES_SCALE = 0.65
    LEGAL_FILE_EXTENSIONS = ('.JPG', '.jpg')
    LOG_FILE = "log.txt"
    QTM_PROJECT_DATA_DIR = "PATH_TO_DATA_DIR/"
    QTM_RT_PASSWORD = ""
    QTM_RT_PORT = 22223
    SCREEN_IDX = 0

    STATUS_BEGIN = 0
    STATUS_EXPERIMENT = 1
    STATUS_DONE = 2

    img_files = []
    for f in os.listdir(IMAGES_DIR):
        if f.endswith(LEGAL_FILE_EXTENSIONS):
            img_files.append(os.path.join(IMAGES_DIR, f))
    print(img_files)
    random.shuffle(img_files)
    print(img_files)


    status = None
    sprite = None
    connection = None
    event_queue = defer.DeferredQueue()

    startTime = datetime.now().strftime('%m%d%H%M')


# Init globals
g = Globals()
g.status = g.STATUS_BEGIN

# Create pyglet window
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screens = display.get_screens()
window = pyglet.window.Window(
        fullscreen=g.FULLSCREEN,
        screen=screens[g.SCREEN_IDX])


class QScript():

    def __init__(self):
        global g

        print("Connecting to QTM...")
        self.qrt = qtm.QRT("127.0.0.1", g.QTM_RT_PORT)
        self.qrt.connect(
                on_connect=self.on_connect,
                on_disconnect=self.on_disconnect,
                on_event=self.on_event)

    def on_connect(self, connection, version):
        global g

        print("Connected to QTM", format(version))

        self.connection = connection
        g.connection = connection

        print("Taking control of QTM...")
        self.connection.take_control(
                password=g.QTM_RT_PASSWORD,
                on_ok=self.on_ok,
                on_error=self.on_error)

    def on_disconnect(self, reason):
        print("QTM RT Disconnect:", reason)
        qtm.stop()
        reactor.stop()

    def on_ok(self, event):
        print("QTM RT OK:", event)

    def on_event(self, event):
        print("QTM RT Event:", event)
        g.event_queue.put(event)

    def on_error(self, error):
        error_message = error.getErrorMessage()
        print("QTM RT Error:", error)
        print("QTM RT Error Message:", error_message)
        self.connection.disconnect()


@defer.inlineCallbacks
def appendToRecords(s):
    global g

    t = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')

    with open(LOG_FILE, 'a') as logFile:
        logFile.write(t + '\t' + s + "\n")

    yield g.connection.set_qtm_event(
            s,
            on_ok=lambda p: print("Event set:", s),
            on_error=lambda p: print("Event set failed."))


def showImage(imgFile):
    global g

    print("Displaying:", imgFile)

    img = pyglet.image.load(imgFile)

    # Center image on screen
    img.anchor_x = int(img.width / 2)
    img.anchor_y = int(img.height / 2)

    g.sprite = pyglet.sprite.Sprite(img, x=window.width/2, y=window.height/2)
    g.sprite.scale = g.IMAGES_SCALE


@window.event
def on_draw():
    window.clear()
    if g.sprite:
        g.sprite.draw()


def advance():
    global g

    # If there are still images left to show, show one.
    if g.img_files:
        img = g.img_files.pop()
        showImage(img)
        appendToRecords(img)
    # If there are no images left to show, advance experiment flow.
    else:
        g.status += 1


@defer.inlineCallbacks
def await_event(event_type):
    global g

    while True:
        event = yield g.event_queue.get()
        if event == event_type:
            break

@defer.inlineCallbacks
def start_measurement():
    yield g.connection.start()
    yield await_event(QRTEvent.EventCaptureStarted)

    appendToRecords("NEW")


@defer.inlineCallbacks
def stop_measurement():
    yield g.connection.stop()
    yield await_event(QRTEvent.EventCaptureStopped)

    try:
        yield g.connection.save(
                g.QTM_PROJECT_DATA_DIR + g.startTime + '.qtm',
                overwrite=False)
        yield await_event(QRTEvent.EventCaptureSaved)
    except QRTCommandException as e:
        print('Save - ', e)

    yield g.connection.disconnect()
    yield await_event(QRTEvent.EventConnectionClosed)


@window.event
def on_key_press(symbol, modifiers):
    global g

    if g.STATUS = g.STATUS_DONE + 1:
        reactor.stop()

    if g.status == g.STATUS_DONE:
        sprite = None
        stop_measurement()

    if g.status == g.STATUS_BEGIN:
        sprite = None
        start_measurement()
        g.status += 1

    elif g.status == g.STATUS_EXPERIMENT:
        advance()


print("Experiment started.")
QScript()
reactor.run()
