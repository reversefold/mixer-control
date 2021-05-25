class Channel(object):
    def __init__(self, targets):
        self.targets = targets
        self.__volume = sum(t.volume for t in targets) / len(targets)
        self.__muted = False

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, value):
        self.__volume = value
        for target in self.targets:
            target.volume = self.__volume

    @property
    def mute(self):
        return self.__muted

    @mute.setter
    def mute(self, value):
        self.__muted = value
        for target in self.targets:
            target.mute = self.__value
