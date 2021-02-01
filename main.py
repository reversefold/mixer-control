#!/usr/bin/env python3
import sys
from typing import List, Tuple

import serial
import yaml


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


class Sensor(object):
    def __init__(self, weight, epsilon):
        self.weight: float = weight
        self.inverse_weight = 1.0 - weight
        self.epsilon: int = epsilon

        self._initialized = False
        self.rawval: int = -1
        self.ema: float = -1
        self.output: int = -1
        self.delta_ema: float = 0

    def nextval(self, rawval):
        self.rawval = rawval
        if not self._initialized:
            self.ema = rawval
            self.output = rawval
            self._initialized = True
        else:
            # EMA of the signal to reduce noise
            self.ema = self.inverse_weight * self.ema + self.weight * rawval
            # EMA of the distance between the output value and the raw value to decide if we're getting noise or a real change
            self.delta_ema = self.inverse_weight * self.delta_ema + self.weight * (
                rawval - self.output
            )
            if MAXVAL - self.ema < self.epsilon:
                self.output = MAXVAL
                self.delta_ema = 0
            elif self.ema - MINVAL < self.epsilon:
                self.output = MINVAL
                self.delta_ema = 0
            elif abs(self.delta_ema) > self.epsilon:
                self.output = self.ema
                self.delta_ema = 0
        return self.output


def main():
    config = Config.load("config.yaml")
    print(config.data)
    sensors = []
    for i in range(len(config.data["channels"])):
        if i in config.data.get("noise_reduction", {}).get("channels", {}):
            custom_noise_reduction = config.data["noise_reduction"]["channels"][i]
            sensor = Sensor(
                custom_noise_reduction["weight"], custom_noise_reduction["epsilon"],
            )
        else:
            sensor = Sensor(
                config.data["noise_reduction"]["default_weight"],
                config.data["noise_reduction"]["default_epsilon"],
            )
        sensors.append(sensor)

    with serial.Serial(config.data["com_port"], config.data["baud_rate"], timeout=1) as ser:
        print(ser.name)

        while True:
            line = ser.readline().decode("utf8", errors="replace").strip()
            values = [int(s) for s in line.split("|")]
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


if __name__ == "__main__":
    main()
