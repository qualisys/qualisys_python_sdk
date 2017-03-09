from collections import namedtuple
from functools import wraps
import struct

from enum import Enum

RTDataQRTPacket = struct.Struct("<qII")
RTComponentData = struct.Struct("<II")


# 2D
RT2DComponent = namedtuple('RT2DComponent', 'camera_count drop_rate out_of_sync_rate')
RT2DComponent.format = struct.Struct("<Ihh")

RT2DCamera = namedtuple('RT2DCamera', 'marker_count status_flag')
RT2DCamera.format = struct.Struct("<ic")

RT2DMarker = namedtuple('RT2DMarker', 'x y d_x d_y')
RT2DMarker.format = struct.Struct("<iihh")


# 3D
RT3DComponent = namedtuple('RT3DComponent', 'marker_count drop_rate out_of_sync_rate')
RT3DComponent.format = struct.Struct("<Ihh")

RT3DMarkerPosition = namedtuple('RT3DMarkerPosition', 'x y z')
RT3DMarkerPosition.format = struct.Struct("<3f")

RT3DMarkerPositionResidual = namedtuple('RT3DMarkerPositionResidual', 'x y z residual')
RT3DMarkerPositionResidual.format = struct.Struct("<4f")

RT3DMarkerPositionNoLabel = namedtuple('RT3DMarkerPositionNoLabel', 'x y z id')
RT3DMarkerPositionNoLabel.format = struct.Struct("<3fi")

RT3DMarkerPositionNoLabelResidual = namedtuple('RT3DMarkerPositionNoLabelResidual', 'x y z id residual')
RT3DMarkerPositionNoLabelResidual.format = struct.Struct("<3fif")


# 6D
RT6DComponent = namedtuple('RT6DComponent', 'body_count drop_rate out_of_sync_rate')
RT6DComponent.format = struct.Struct("<ihh")

RT6DBodyPosition = namedtuple('RT6DBodyPosition', 'x y z')
RT6DBodyPosition.format = struct.Struct("<3f")

RT6DBodyRotation = namedtuple('RT6DBodyRotation', 'matrix')
RT6DBodyRotation.format = struct.Struct("<9f")

RT6DBodyResidual = namedtuple('RT6DBodyResidual', 'residual')
RT6DBodyResidual.format = struct.Struct("<f")

RT6DBodyEuler = namedtuple('RT6DBodyEuler', 'a1 a2 a3')
RT6DBodyEuler.format = struct.Struct("<3f")


# Analog
RTAnalogComponent = namedtuple('RTAnalogComponent', 'device_count')
RTAnalogComponent.format = struct.Struct("<i")

RTAnalogDevice = namedtuple('RTAnalogDevice', 'id channel_count sample_count')
RTAnalogDevice.format = struct.Struct("<iii")

RTSampleNumber = namedtuple('RTSampleNumber', 'sample_number')
RTSampleNumber.format = struct.Struct("<i")

RTAnalogChannel = namedtuple('RTAnalogChannel', 'samples')
RTAnalogChannel.format_str = '<%df'

RTAnalogDeviceSingle = namedtuple('RTAnalogDeviceSingle', 'id channel_count')
RTAnalogDeviceSingle.format = struct.Struct("<ii")

RTAnalogDeviceSamples = namedtuple('RTAnalogDeviceSamples', 'samples')
RTAnalogDeviceSamples.format_str = "<%df"


# Force
RTForceComponent = namedtuple('RTForceComponent', 'plate_count')
RTForceComponent.format = struct.Struct("<i")

RTForcePlate = namedtuple('RTForcePlate', 'id force_count force_number')
RTForcePlate.format = struct.Struct("<iii")

RTForcePlateSingle = namedtuple('RTForcePlateSingle', 'id')
RTForcePlateSingle.format = struct.Struct("<i")

RTForce = namedtuple('RTForce', 'x y z x_m y_m z_m x_a y_a z_a')
RTForce.format = struct.Struct("<9f")

# GazeVector
RTGazeVectorComponent = namedtuple('RTGazeVectorComponent', 'vector_count')
RTGazeVectorComponent.format = struct.Struct("<i")

RTGazeVector = namedtuple('RTGazeVector', 'sample_count')
RTGazeVector.format = struct.Struct("<i")

# Image
RTImageComponent = namedtuple('RTImageComponent', 'image_count')
RTImageComponent.format = struct.Struct("<i")

RTImage = namedtuple('RTImage', 'id format width height left_crop top_crop right_crop bottom_crop image_size')
RTImage.format = struct.Struct("<iiiiffffi")


class QRTPacketType(Enum):
    PacketError = 0
    PacketCommand = 1
    PacketXML = 2
    PacketData = 3
    PacketNoMoreData = 4
    PacketC3DFile = 5
    PacketEvent = 6
    PacketDiscover = 7
    PacketQTMFile = 8
    PacketNone = 9


class QRTComponentType(Enum):
    Component3d = 1
    Component3dNoLabels = 2
    ComponentAnalog = 3
    ComponentForce = 4
    Component6d = 5
    Component6dEuler = 6
    Component2d = 7
    Component2dLin = 8
    Component3dRes = 9
    Component3dNoLabelsRes = 10
    Component6dRes = 11
    Component6dEulerRes = 12
    ComponentAnalogSingle = 13
    ComponentImage = 14
    ComponentForceSingle = 15
    ComponentGazeVector = 16
    ComponentNone = 17


class QRTImageFormat(Enum):
    FormatRawGrayscale = 0
    FormatRawBGR = 1
    FormatJPG = 2
    FormatPNG = 3


class QRTEvent(Enum):
    EventConnected = 1
    EventConnectionClosed = 2
    EventCaptureStarted = 3
    EventCaptureStopped = 4
    EventCaptureFetchingFinished = 5  # Not used in version 1.10 and later
    EventCalibrationStarted = 6
    EventCalibrationStopped = 7
    EventRTfromFileStarted = 8
    EventRTfromFileStopped = 9
    EventWaitingForTrigger = 10
    EventCameraSettingsChanged = 11
    EventQTMShuttingDown = 12
    EventCaptureSaved = 13
    EventReprocessingStarted = 14
    EventReprocessingStopped = 15
    EventTrigger = 16
    EventNone = 17  # Must be the last. Not actually an event. Just used to cont number of events.


class component_getter(object):
    def __init__(self, component_enum, base_component):
        self.component_enum = component_enum
        self.base_component = base_component

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            calling_object = args[0]
            component_position = calling_object.components.get(self.component_enum, None)
            if component_position is None:
                return None

            component_position, component_info = QRTPacket._get_exact(self.base_component,
                                                                      calling_object.data, component_position)

            return (component_info, f(*args, component_info=component_info,
                                      data=calling_object.data, component_position=component_position, **kwargs))
        return wrapper


# noinspection PyTypeChecker
class QRTPacket(object):
    """Packet containing data measured with QTM.

    Too check for existence of a specific component in a packet:

    ::

        from qtm.packet import QRTComponentType
        if QRTComponentType.Component3d in packet.components:
            header, markers = packet.get_3d_markers()

    Component retriever functions will return None if a component is not in the packet.

    """

    def __init__(self, data):
        self.data = data

        self.timestamp, self.framenumber, component_count = RTDataQRTPacket.unpack_from(data, 0)

        self.components = {}
        position = RTDataQRTPacket.size
        for i in range(component_count):
            c_size, c_type = RTComponentData.unpack_from(data, position)
            self.components[QRTComponentType(c_type)] = position + RTComponentData.size
            position += c_size

    @staticmethod
    def _get_exact(component_type, data, position):
        value = component_type._make(component_type.format.unpack_from(data, position))
        position += component_type.format.size
        return position, value

    @staticmethod
    def _get_tuple(component_type, data, position):
        value = component_type._make([component_type.format.unpack_from(data, position)])
        position += component_type.format.size
        return position, value

    @staticmethod
    def _get_2d_markers(data, component_info, component_position, index=None):
        components = []
        append_components = components.append
        for camera in range(component_info.camera_count):
            component_position, camera_info = QRTPacket._get_exact(RT2DCamera, data, component_position)

            if index is None or index == camera:
                marker_list = []
                append_marker = marker_list.append
                append_components(marker_list)

                for markers in range(camera_info.marker_count):
                    component_position, marker = QRTPacket._get_exact(RT2DMarker, data, component_position)
                    append_marker(marker)
            else:
                component_position += RT2DMarker.format.size * camera_info.marker_count

        return components

    @staticmethod
    def _get_3d_markers(type_, component_info, data, component_position):
        components = []
        append_components = components.append
        for j in range(component_info.marker_count):
            component_position, position = QRTPacket._get_exact(type_, data, component_position)
            append_components(position)

        return components

    @component_getter(QRTComponentType.ComponentAnalog, RTAnalogComponent)
    def get_analog(self, component_info=None, data=None, component_position=None):
        """Get analog data."""
        components = []
        append_components = components.append
        for j in range(component_info.device_count):
            component_position, device = QRTPacket._get_exact(RTAnalogDevice, data, component_position)
            if device.sample_count > 0:
                component_position, sample_number = QRTPacket._get_exact(RTSampleNumber, data, component_position)

                RTAnalogChannel.format = struct.Struct(RTAnalogChannel.format_str % device.sample_count)
                for i in range(device.channel_count):
                    component_position, channel = QRTPacket._get_tuple(RTAnalogChannel, data, component_position)
                    append_components((device, sample_number, channel))

        return components

    @component_getter(QRTComponentType.ComponentAnalogSingle, RTAnalogComponent)
    def get_analog_single(self, component_info=None, data=None, component_position=None):
        """Get a single analog data channel."""
        components = []
        append_components = components.append
        for j in range(component_info.device_count):
            component_position, device = QRTPacket._get_exact(RTAnalogDeviceSingle, data, component_position)

            RTAnalogDeviceSamples.format = struct.Struct(RTAnalogDeviceSamples.format_str % device.channel_count)
            component_position, sample = QRTPacket._get_tuple(RTAnalogDeviceSamples, data, component_position)
            append_components((device, sample))
        return components

    @component_getter(QRTComponentType.ComponentForce, RTForceComponent)
    def get_force(self, component_info=None, data=None, component_position=None):
        """Get force data."""
        components = []
        append_components = components.append
        for j in range(component_info.plate_count):
            component_position, plate = QRTPacket._get_exact(RTForcePlate, data, component_position)
            force_list = []
            for i in range(plate.force_count):
                component_position, force = QRTPacket._get_exact(RTForce, data, component_position)
                force_list.append(force)
            append_components((plate, force_list))
        return components

    @component_getter(QRTComponentType.ComponentForceSingle, RTForceComponent)
    def get_force_single(self, component_info=None, data=None, component_position=None):
        """Get a single force data channel."""
        components = []
        append_components = components.append
        for j in range(component_info.plate_count):
            component_position, plate = QRTPacket._get_exact(RTForcePlateSingle, data, component_position)
            component_position, force = QRTPacket._get_exact(RTForce, data, component_position)
            append_components((plate, force))
        return components

    @component_getter(QRTComponentType.Component6d, RT6DComponent)
    def get_6d(self, component_info=None, data=None, component_position=None):
        """Get 6D data."""
        components = []
        append_components = components.append
        for j in range(component_info.body_count):
            component_position, position = QRTPacket._get_exact(RT6DBodyPosition, data, component_position)
            component_position, matrix = QRTPacket._get_tuple(RT6DBodyRotation, data, component_position)
            append_components((position, matrix))
        return components

    @component_getter(QRTComponentType.Component6dRes, RT6DComponent)
    def get_6d_residual(self, component_info=None, data=None, component_position=None):
        """Get 6D data with residual."""
        components = []
        append_components = components.append
        for j in range(component_info.body_count):
            component_position, position = QRTPacket._get_exact(RT6DBodyPosition, data, component_position)
            component_position, matrix = QRTPacket._get_tuple(RT6DBodyRotation, data, component_position)
            component_position, residual = QRTPacket._get_exact(RT6DBodyResidual, data, component_position)
            append_components((position, matrix, residual))
        return components

    @component_getter(QRTComponentType.Component6dEuler, RT6DComponent)
    def get_6d_euler(self, component_info=None, data=None, component_position=None):
        """Get 6D data with euler rotations."""
        components = []
        append_components = components.append
        for j in range(component_info.body_count):
            component_position, position = QRTPacket._get_exact(RT6DBodyPosition, data, component_position)
            component_position, euler = QRTPacket._get_exact(RT6DBodyEuler, data, component_position)
            append_components((position, euler))
        return components

    @component_getter(QRTComponentType.Component6dEulerRes, RT6DComponent)
    def get_6d_euler_residual(self, component_info=None, data=None, component_position=None):
        """Get 6D data with residuals and euler rotations."""
        components = []
        append_components = components.append
        for j in range(component_info.body_count):
            component_position, position = QRTPacket._get_exact(RT6DBodyPosition, data, component_position)
            component_position, euler = QRTPacket._get_exact(RT6DBodyEuler, data, component_position)
            component_position, residual = QRTPacket._get_exact(RT6DBodyResidual, data, component_position)
            append_components((position, euler, residual))
        return components

    @component_getter(QRTComponentType.ComponentImage, RTImageComponent)
    def get_image(self, component_info=None, data=None, component_position=None):
        """Get image."""
        components = []
        append_components = components.append
        for j in range(component_info.image_count):
            component_position, image_info = QRTPacket._get_exact(RTImage, data, component_position)
            append_components((image_info, data[component_position:-1]))
        return components

    @component_getter(QRTComponentType.Component3d, RT3DComponent)
    def get_3d_markers(self, component_info=None, data=None, component_position=None):
        """Get 3D markers."""
        return self._get_3d_markers(RT3DMarkerPosition, component_info, data, component_position)

    @component_getter(QRTComponentType.Component3dRes, RT3DComponent)
    def get_3d_markers_residual(self, component_info=None, data=None, component_position=None):
        """Get 3D markers with residual."""
        return self._get_3d_markers(RT3DMarkerPositionResidual, component_info, data, component_position)

    @component_getter(QRTComponentType.Component3dNoLabels, RT3DComponent)
    def get_3d_markers_no_label(self, component_info=None, data=None, component_position=None):
        """Get 3D markers without label."""
        return self._get_3d_markers(RT3DMarkerPositionNoLabel, component_info, data, component_position)

    @component_getter(QRTComponentType.Component3dNoLabelsRes, RT3DComponent)
    def get_3d_markers_no_label_residual(self, component_info=None, data=None, component_position=None):
        """Get 3D markers without label with residual."""
        return self._get_3d_markers(RT3DMarkerPositionNoLabelResidual, component_info, data, component_position)

    @component_getter(QRTComponentType.Component2d, RT2DComponent)
    def get_2d_markers(self, component_info=None, data=None, component_position=None, index=None):
        """Get 2D markers.

        :param index: Specify which camera to get 2D from, will be returned as first entry in the returned array.
        """
        return self._get_2d_markers(data, component_info, component_position, index=index)

    @component_getter(QRTComponentType.Component2dLin, RT2DComponent)
    def get_2d_markers_linearized(self, component_info=None, data=None, component_position=None, index=None):
        """Get 2D linearized markers.

        :param index: Specify which camera to get 2D from, will be returned as first entry in the returned array.
        """

        return self._get_2d_markers(data, component_info, component_position, index=index)
