import numpy as np

class Modulator:

    def __init__(self, signal: np.ndarray, carrier: np.ndarray):
        self.signal = signal
        self.carrier = carrier

    def am_modulate(self)->np.ndarray:
        return self.signal * self.carrier

    def fm_modulate(self)->np.ndarray:
        return np.sin(self.signal + self.carrier)

    def pm_modulate(self)->np.ndarray:
        return np.cos(self.signal + self.carrier)

## Modulator is useless without aasdsadas
# Need to make a major change!
#### minor changes here! Minor fix here and there!