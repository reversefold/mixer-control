import logging

import jsonschema
import yaml

from mixer_control import (
    channel as mc_channel,
    target as mc_target,
    sensor as mc_sensor,
)


LOG = logging.getLogger(__name__)


class Config(object):
    def __init__(self, data):
        self.data = data
        self.analog_channels = []
        for chan_conf in self.data["analog_channels"]:
            targets = []
            for target_conf in chan_conf["targets"]:
                targets.append(
                    mc_target.class_map[list(target_conf.keys())[0]](
                        list(target_conf.values())[0]
                    )
                )
            custom_noise_reduction = chan_conf.get("noise_reduction", {})
            weight = custom_noise_reduction.get(
                "weight", self.data["noise_reduction"]["default_weight"]
            )
            epsilon = custom_noise_reduction.get(
                "epsilon", self.data["noise_reduction"]["default_epsilon"]
            )
            sensor = mc_sensor.EMASensor(
                weight,
                epsilon,
            )
            channel = mc_channel.Channel(targets)
            self.analog_channels.append((sensor, channel))

    @classmethod
    def load(cls, filename):
        with open("config.schema.yaml", "r") as f:
            schema = yaml.safe_load(f)

        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except Exception as exc:
            LOG.error("Error validating schema")
            raise

        LOG.debug("Schema valid!")

        with open(filename, "r") as f:
            data = yaml.safe_load(f)

        try:
            jsonschema.validate(data, schema)
        except Exception as exc:
            LOG.error("Error validating config")
            raise

        LOG.debug("Config valid!")

        return cls(data)
