import numpy as np

class SNRAnalyzer:
    def __init__(self, model):
        self.model = model
        self.snr = 0.0

    def compute_snr(self, signal, noise_level):
        """Compute SNR in dB based on signal and noise level."""
        if len(signal) == 0 or noise_level <= 0:
            return 0.0
        signal_power = np.mean(signal ** 2)
        noise = np.random.normal(0, noise_level * np.std(signal), len(signal))
        noise_power = np.mean(noise ** 2)
        if noise_power == 0:
            return 100.0  # Arbitrary high SNR if no noise
        snr_db = 10 * np.log10(signal_power / noise_power)
        return max(0.0, min(snr_db, 100.0))  # Clamp to 0–100 dB

    def update(self, signal, noise_level):
        """Update SNR value."""
        self.snr = self.compute_snr(signal, noise_level)

    def get_snr(self):
        """Return the computed SNR."""
        return self.snr