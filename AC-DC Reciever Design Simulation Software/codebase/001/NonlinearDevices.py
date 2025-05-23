import numpy as np

class Diode:
    def __init__(self, is_=1e-12, n=1.0, vt=0.0259):
        self.is_ = is_  # Saturation current (A)
        self.n = n      # Ideality factor
        self.vt = vt    # Thermal voltage (V)

    def current(self, vd):
        """Calculate diode current given voltage across diode."""
        # Avoid numerical overflow in exponential
        vd = np.clip(vd, -100, 100)
        return self.is_ * (np.exp(vd / (self.n * self.vt)) - 1)

    def voltage_drop(self, current):
        """Calculate voltage drop across diode given current."""
        current = np.clip(current, 1e-15, 1e6)  # Prevent log of zero or negative
        return self.n * self.vt * np.log(current / self.is_ + 1)

class Transistor:
    def __init__(self, beta=100, vbe=0.7, is_=1e-12, vt=0.0259):
        self.beta = beta  # Current gain
        self.vbe = vbe    # Base-emitter voltage
        self.is_ = is_    # Saturation current
        self.vt = vt      # Thermal voltage

    def collector_current(self, vbe, vce):
        """Calculate collector current for NPN transistor in active region."""
        vbe = np.clip(vbe, -100, 100)
        ib = self.is_ * (np.exp(vbe / self.vt) - 1)
        ic = self.beta * ib
        return ic if vce > 0.2 else 0  # Assume saturation if Vce < 0.2V