#!/usr/bin/env python3
import sys

import serial
import yaml

from mixer_control import sensor as mc_sensor

# import serial.tools.list_ports as port_list

# ports = list(port_list.comports())
# for p in ports:
#     print(p)


## Config
PORT = "COM8"
BAUD = 9600


## Global constants
MINVAL = 0
MAXVAL = 1023


class Config(object):
    def __init__(self, data):
        self.data = data

    @classmethod
    def load(cls, filename):
        with open(filename, "r") as f:
            data = yaml.load(f)
        return cls(data)




class Main(object):
    def main(self):
        config = Config.load("config.yaml")
        print(config.data)
        sensors = []
        for i in range(len(config.data["channels"])):
            if i in config.data.get("noise_reduction", {}).get("channels", {}):
                custom_noise_reduction = config.data["noise_reduction"]["channels"][i]
                sensor = mc_sensor.EMASensor(
                    custom_noise_reduction["weight"], custom_noise_reduction["epsilon"],
                )
            else:
                sensor = mc_sensor.EMASensor(
                    config.data["noise_reduction"]["default_weight"],
                    config.data["noise_reduction"]["default_epsilon"],
                )
            sensors.append(sensor)

        with serial.Serial(config.data["com_port"], config.data["baud_rate"], timeout=1) as ser:
            print(ser.name)

            active_device = pycaw.AudioUtilities.GetSpeakers()
            active_device_interface = active_device.Activate(
                pycaw.IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None
            )
            master_session = comtypes.cast(
                active_device_interface, ctypes.POINTER(pycaw.IAudioEndpointVolume)
            )
            print(master_session)
            print(self._get_session_volume(master_session))
            # import ipdb; ipdb.set_trace()

            while True:
                line = ser.readline().decode("utf8", errors="replace").strip()
                if not line:
                    print(repr(line))
                    continue
                print(line)
                (analog_line, digital_line) = [p.strip() for p in line.split(":")]
                if analog_line:
                    values = [int(s) for s in analog_line.split("|")]
                    for idx, val in enumerate(values):
                        if idx < len(sensors):
                            sensors[idx].nextval(val)
                        else:
                            break
                    print(
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
                            for sensor in sensors
                        )
                    )
                if digital_line:
                    self.digital_values = [i == "1" for i in digital_line.split("|")]
                    # print(self.digital_values)
                    # sessions = AudioUtilities.GetAllSessions()
                    master_session.SetMute(1 if self.digital_values[0] else 0, self._lpcguid)


if __name__ == "__main__":
    Main().main()
