## constants
MINVAL = 0
MAXVAL = 1023


class EMASensor(object):
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
