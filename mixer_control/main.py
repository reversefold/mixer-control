#!/usr/bin/env python3
import ctypes
import datetime
import logging
import sys
import time

import comtypes
import pycaw
import serial

from mixer_control import sensor as mc_sensor
from mixer_control import config as mc_config


LOG = logging.getLogger(__name__)


OUTPUT_PERIOD = datetime.timedelta(seconds=10)


# import serial.tools.list_ports as port_list

# ports = list(port_list.comports())
# for p in ports:
#     print(p)


class Main(object):
    def __init__(self):
        self.config = None
        self.analog_channels = None

    def main(self):
        self.config = mc_config.Config.load("config.yaml")
        LOG.debug(self.config.data)
        LOG.debug(self.config.analog_channels)
        self.analog_channels = self.config.analog_channels

        with serial.Serial(
            self.config.data["com_port"], self.config.data["baud_rate"], timeout=1
        ) as ser:
            LOG.info(ser.name)

            active_device = pycaw.AudioUtilities.GetSpeakers()
            active_device_interface = active_device.Activate(
                pycaw.IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None
            )
            master_session = comtypes.cast(
                active_device_interface, ctypes.POINTER(pycaw.IAudioEndpointVolume)
            )
            LOG.debug(master_session)
            # LOG.debug(self._get_session_volume(master_session))

            last_output = datetime.datetime.now() - OUTPUT_PERIOD

            while True:
                line = ser.readline().decode("utf8", errors="replace").strip()
                if "|" not in line:
                    LOG.warning("Unknown line of data from serial interface %r", line)
                    continue
                data = [p.strip() for p in line.split(":")]
                analog_line = data[0]
                digital_line = data[1] if len(data) > 1 else None
                if analog_line:
                    values = [int(s) if s else 0 for s in analog_line.split("|")]
                    for idx, val in enumerate(values):
                        if idx < len(self.analog_channels):
                            (sensor, channel) = self.analog_channels[idx]
                            last = sensor.output
                            sensor.nextval(val)
                            if last != sensor.output:
                                newval = sensor.output / mc_sensor.MAXVAL
                                LOG.info(
                                    f"{channel.targets} {channel.volume:0.4f}/{last / mc_sensor.MAXVAL:0.4f} -> {newval:0.4f}"
                                )
                                channel.volume = newval
                        else:
                            break
                    now = datetime.datetime.now()
                    if now - last_output > OUTPUT_PERIOD:
                        last_output = now
                        LOG.debug(
                            " | ".join(
                                " ".join(
                                    f"{val:7.2f}"
                                    for val in [
                                        sensor.rawval,
                                        sensor.ema,
                                        sensor.delta_ema,
                                        sensor.output,
                                    ]
                                )
                                for sensor, _ in self.analog_channels
                            )
                        )
                if digital_line:
                    self.digital_values = [i == "1" for i in digital_line.split("|")]
                    LOG.debug(self.digital_values)
                    # sessions = AudioUtilities.GetAllSessions()
                    master_session.SetMute(
                        1 if self.digital_values[0] else 0, self._lpcguid
                    )
                # time.sleep(1)


if __name__ == "__main__":
    while True:
        try:
            logging.basicConfig(
                format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
                level=logging.INFO,
            )
            Main().main()
        except Exception:
            LOG.exception("Exception in Main, restarting")
            time.sleep(1)
