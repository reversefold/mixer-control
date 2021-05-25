from mixer_control import sessions


class Device(object):
    def __init__(self, name):
        self.__name = name
        self.__device = None

    @property
    def device(self):
        if self.__device is None:  # or inactive?
            self.__device = sessions.SessionController.instance().get_device(
                self.__name
            )
        return self.__device

    @property
    def volume(self):
        return self.device.volume.master_scalar

    @volume.setter
    def volume(self, value):
        self.device.volume.master_scalar = value

    @property
    def mute(self):
        return self.device.volume.mute

    @mute.setter
    def mute(self, value):
        self.device.volume.mute = value

    def __repr__(self):
        return f"Device({self.__name}, {self.volume:0.4f})"


class Process(object):
    def __init__(self, name):
        self.__name = name
        self.__process = None

    @property
    def process(self):
        if self.__process is None or self.__process.state != "Active":
            self.__process = sessions.SessionController.instance().get_process(
                self.__name
            )
        return self.__process

    @property
    def volume(self):
        return self.process.volume.master_volume

    @volume.setter
    def volume(self, value):
        self.process.volume.master_volume = value

    @property
    def mute(self):
        return self.process.volume.mute

    @mute.setter
    def mute(self, value):
        self.process.volume.mute = value

    def __repr__(self):
        return f"Process({self.__name}, {self.volume:0.4f})"


class_map = {
    "device": Device,
    "process": Process,
}
