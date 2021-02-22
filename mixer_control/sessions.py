import ctypes
import datetime
import gc
import itertools
import math
import typing

import comtypes
from pyWinCoreAudio import device as wca_device, session as wca_session


# class AudioSession(object):
#     def __init__(self, session, lpcguid):
#         self._session = session
#         self._lpcguid = lpcguid

#     def _get_volume(self):
#         if hasattr(self._session, "SimpleAudioVolume"):
#             return self._clean_session_volume(
#                 self._session.SimpleAudioVolume.GetMasterVolume()
#             )

#         return self._clean_session_volume(self._session.GetMasterVolumeLevelScalar())

#     def _set_volume(self, value):
#         if hasattr(self._session, "SimpleAudioVolume"):
#             self._session.SimpleAudioVolume.SetMasterVolume(value, self._lpcguid)
#         else:
#             self._session.SetMasterVolumeLevelScalar(value, self._lpcguid)

#     volume = property(_get_volume, _set_volume)

#     # Clamp to 1.2 digits
#     def _clean_session_volume(self, value):
#         return math.floor(value * 100) / 100.0

#     def _get_mute(self):
#         return self._session.GetMute(self._lpcguid) == 1

#     def _set_mute(self, value):
#         self._session.SetMute(1 if value else 0, self._lpcguid)

#     mute = property(_get_mute, _set_mute)


class SessionController(object):
    def __init__(self):
        self.__device_enumerator = wca_device.AudioDeviceEnumerator()

        # self._lpcguid = ctypes.pointer(comtypes.GUID.create_new())
        self.active_render_endpoint = None
        self.sessions = None
        self.devices = None
        self._last_session_refresh: datetime.datetime = None
        self.refresh()

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


endpoint.volume.master_scalar = 1
endpoint.volume.mute = False

        # active_device = pycaw.AudioUtilities.GetSpeakers()
        # active_device_interface = active_device.Activate(
        #     pycaw.IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None
        # )
        # self.master_session = AudioSession(
        #     comtypes.cast(
        #         active_device_interface, ctypes.POINTER(pycaw.IAudioEndpointVolume)
        #     )
        # )

        # self._sessions = [
        #     AudioSession(s) for s in pycaw.AudioUtilities.GetAllSessions()
        # ]

        # self._devices = [
        #     d for d in pycaw.AudioUtilities.GetAllDevices()
        # ]
