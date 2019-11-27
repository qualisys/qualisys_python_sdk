from .util import rest_endpoint

class QRest(object):
    """QRest

        :param host: Address of the computer running QTM.
        :param port: QTM REST port(always 7979).
        :param verbose: Set to True to print REST commands to stdout.

    """

    def __init__(self, host, port=7979, verbose=False):
        self.host = host
        self.port = port
        self.url = 'http://{host}:{port}'.format(host=host, port=port)
        self.verbose = verbose
    
    @rest_endpoint('GET', '/api/experimental/settings')
    def get_settings(self):
        """Get QTM Settings as json.
            This method returns all settings for QTM. You can use the specialized settings methods
            to only get the settings you require.*
        """
        pass

    @rest_endpoint('POST', '/api/experimental/settings')
    def set_settings(self, data=None):
        """Set QTM Settings.
            This method sets all settings for QTM. You can use the specialized settings methods
            to only set the settings you require.*
        """
        pass

    @rest_endpoint('GET', '/api/experimental/settings', filter='ExportC3d')
    def get_export_c3d(self):
        """Get QTM C3D export Settings as json.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/settings', filter='ExportC3d')
    def set_export_c3d(self, data=None):
        """Set QTM C3D export Settings.*"""
        pass

    @rest_endpoint('GET', '/api/experimental/settings', filter='ExportMat')
    def get_export_mat(self):
        """Get QTM matlab export Settings as json.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/settings', filter='ExportMat')
    def set_export_mat(self, data=None):
        """Set QTM matlab export Settings.*"""
        pass

    @rest_endpoint('GET', '/api/experimental/settings', filter='ExportTsv')
    def get_export_tsv(self):
        """Get QTM tsv export Settings as json.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/settings', filter='ExportTsv')
    def set_export_tsv(self, data=None):
        """Set QTM tsv export Settings.*"""
        pass

    @rest_endpoint('GET', '/api/experimental/settings', filter='Reprocess')
    def get_reprocess(self):
        """Get QTM reprocess Settings as json.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/settings', filter='Reprocess')
    def set_reprocess(self, data=None):
        """Set QTM reprocess Settings.*"""
        pass

    @rest_endpoint('GET', '/api/experimental/settings', filter='Timing')
    def get_timing(self):
        """Get QTM timing Settings as json.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/settings', filter='Timing')
    def set_timing(self, data=None):
        """Set QTM timing Settings.*"""
        pass

    @rest_endpoint('GET', '/api/experimental/settings', filter='Cameras')
    def get_cameras(self):
        """Get QTM cameras Settings as json.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/settings', filter='Cameras')
    def set_cameras(self, data=None):
        """Set QTM cameras Settings.*"""
        pass

    @rest_endpoint('GET', '/api/experimental/settings', filter='AllCameras')
    def get_all_cameras(self):
        """Get QTM all cameras Settings as json.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/settings', filter='AllCameras')
    def set_all_cameras(self, data=None):
        """Set QTM all cameras Settings.*"""
        pass

    @rest_endpoint('GET')
    def get_root(self):
        """Get root."""
        pass

    @rest_endpoint('GET', '/api/')
    def get_api(self):
        """Get api."""
        pass

    @rest_endpoint('GET', '/api/v1/')
    def get_v1(self):
        """Get v1."""
        pass

    @rest_endpoint('GET', '/api/v1/version')
    def get_version(self):
        """Get QTM and PAF versions."""
        pass

    @rest_endpoint('GET', '/api/v1/project')
    def get_project(self):
        """Get info about the currently open project."""
        pass

    @rest_endpoint('GET', '/api/experimental')
    def get_experimental(self):
        pass

    @rest_endpoint('GET', '/api/experimental/workerstate')
    def get_workerstate(self):
        pass

    @rest_endpoint('POST', '/api/experimental/command/load_file')
    def load_file(self, filename):
        """Load a measurement or project.*"""
        return {'FileName': filename}

    @rest_endpoint('POST', '/api/experimental/command/save_file')
    def save_file(self, filename):
        """Save a measurement.*"""
        return {'FileName': filename}

    @rest_endpoint('POST', '/api/experimental/command/close')
    def close(self, force=False):
        """Close a measurement.*"""
        return {'Force': force}

    @rest_endpoint('POST', '/api/experimental/command/start_preview')
    def start_preview(self):
        """Start Preview in QTM.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/command/start_capture')
    def start_capture(self, frequency=None, capture_time=None):
        """Start a capture in QTM.*

        :param frequency: Desired frequency.
        :param capture_time: Length of capture in seconds.

        """
        d = {}
        if frequency is not None:
            d['Frequency'] = frequency
        if capture_time is not None:
            d['CaptureTime'] = capture_time
        return d

    @rest_endpoint('POST', '/api/experimental/command/stop_capture')
    def stop_capture(self):
        """Stop capture.*"""
        pass

    # TODO: Add parameters to functions below
    @rest_endpoint('POST', '/api/experimental/command/reprocess')
    def reprocess(self, data=None):
        """Reprocess a measurement.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/command/export_c3d')
    def export_c3d(self, data=None):
        """Export to C3D.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/command/export_mat')
    def export_mat(self, data=None):
        """Export to matlab.*"""
        pass

    @rest_endpoint('POST', '/api/experimental/command/export_tsv')
    def export_tsv(self, data=None):
        """Export to tsv.*"""
        pass
