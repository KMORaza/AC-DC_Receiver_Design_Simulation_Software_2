import numpy as np

class THDAnalyzer:
    def __init__(self, model):
        self.model = model
        self.thd = 0.0

    def compute_thd(self, signal, fs):
        """Compute pure THD as a percentage, excluding noise."""
        if len(signal) == 0:
            return 0.0
        # FFT to get frequency components
        fft = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/fs)
        fft_magnitude = np.abs(fft)[:len(fft)//2]
        freqs = freqs[:len(fft)//2]
        # Find fundamental frequency (closest to model frequency)
        fundamental_idx = np.argmin(np.abs(freqs - self.model.frequency))
        fundamental_power = fft_magnitude[fundamental_idx] ** 2
        # Sum power of harmonics (2nd to 10th, excluding fundamental)
        harmonic_power = 0
        for harmonic in range(2, 11):
            harmonic_freq = self.model.frequency * harmonic
            harmonic_idx = np.argmin(np.abs(freqs - harmonic_freq))
            harmonic_power += fft_magnitude[harmonic_idx] ** 2
        if fundamental_power == 0:
            return 0.0
        thd = np.sqrt(harmonic_power / fundamental_power) * 100
        return min(thd, 100.0)  # Clamp to 0–100%

    def update(self, signal, fs):
        """Update THD value."""
        self.thd = self.compute_thd(signal, fs)

    def get_thd(self):
        """Return the computed THD."""
        return self.thd