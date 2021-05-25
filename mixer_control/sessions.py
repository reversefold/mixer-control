import ctypes
import datetime
import gc
import itertools
import math
import typing

import comtypes
from pyWinCoreAudio import (
    device as wca_device,
    session as wca_session,
)


class SessionController(object):
    __instance = None

    def __init__(self):
        if self.__class__.__instance is not None:
            raise Exception("This is a singleton class, use instance()")

        self.__device_enumerator = wca_device.AudioDeviceEnumerator()

        # self._lpcguid = ctypes.pointer(comtypes.GUID.create_new())
        self.active_render_endpoint = None
        self.sessions = None
        self.devices = None
        self._last_session_refresh: datetime.datetime = None

    def refresh(self):
        self._last_session_refresh = datetime.datetime.now()

        self.devices = [
            wca_device.AudioDevice(dev.GetId(), self.__device_enumerator)
            for dev in self.__device_enumerator.endpoints
        ]
        self.device_endpoints = list(
            itertools.chain.from_iterable(
                ((device, endpoint) for endpoint in device.render_endpoints)
                for device in self.devices
            )
        )

        self.active_render_endpoint = self.__device_enumerator.default_endpoint(
            wca_device.EDataFlow.eRender
        )

        audio_session_manager = wca_session.AudioSessionManager(
            self.active_render_endpoint
        )
        audio_session_manager.update_sessions()
        self.sessions = list(audio_session_manager)
        gc.collect()

    def maybe_refresh(self):
        if self._last_session_refresh is None or datetime.datetime.now() - self._last_session_refresh > datetime.timedelta(minutes=5):
            self.refresh()

    def get_process(self, name):
        self.maybe_refresh()
        for process in self.sessions:
            if process.id == name:
                return process
            if not name.endswith(".exe") and f"\\{name}.exe%b" in process.id:
                return process
            if f"\\{name}%b" in process.id:
                return process
        raise Exception(f"No process named {name} found")

    def get_device(self, name):
        self.maybe_refresh()
        for device, endpoint in self.device_endpoints:
            if endpoint.name == name:
                return endpoint
        raise Exception(f"No device named {name} found")

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = SessionController()
        return cls.__instance
