import numpy as np

class EMIAnalyzer:
    def __init__(self, model):
        self.model = model
        self.emi_level = 0.0

    def compute_emi(self, t, signal):
        """Compute EMI level in dBµV based on regulator type and switching frequency."""
        if self.model.regulator_type != "switching" or not self.model.power_on:
            return 0.0
        # Simulate EMI as high-frequency noise from switching regulator
        emi_freq = self.model.switching_freq  # e.g., 10 kHz
        emi_signal = 0.01 * np.sin(2 * np.pi * emi_freq * t) * np.max(np.abs(signal))
        # Compute EMI level in dBµV (20 * log10(V_rms * 1e6))
        v_rms = np.sqrt(np.mean(emi_signal ** 2))
        if v_rms == 0:
            return 0.0
        emi_dbuv = 20 * np.log10(v_rms * 1e6)
        return max(0.0, min(emi_dbuv, 120.0))  # Clamp to 0–120 dBµV

    def update(self, t, signal):
        """Update EMI level."""
        self.emi_level = self.compute_emi(t, signal)

    def get_emi_level(self):
        """Return the computed EMI level."""
        return self.emi_level