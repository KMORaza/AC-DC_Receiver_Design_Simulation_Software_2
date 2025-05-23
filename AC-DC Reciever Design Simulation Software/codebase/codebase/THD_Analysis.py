import numpy as np

class THDAnalyzer:
    def __init__(self, model):
        self.model = model
        self.thd = 0.0
        self.harmonics = np.zeros(9)  # H2 to H10
        self.thd_freq = []
        self.freq_bands = np.linspace(100, 10000, 20)  # 100 Hz to 10 kHz

    def compute_thd(self, signal, fs):
        """Compute THD and individual harmonics."""
        if len(signal) == 0:
            self.thd = 0.0
            self.harmonics = np.zeros(9)
            return
        fft = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/fs)
        fft_magnitude = np.abs(fft)[:len(fft)//2]
        freqs = freqs[:len(fft)//2]
        fundamental_idx = np.argmin(np.abs(freqs - self.model.frequency))
        fundamental_power = fft_magnitude[fundamental_idx] ** 2
        harmonic_power = 0
        harmonics = []
        for harmonic in range(2, 11):
            harmonic_freq = self.model.frequency * harmonic
            harmonic_idx = np.argmin(np.abs(freqs - harmonic_freq))
            h_power = fft_magnitude[harmonic_idx] ** 2
            harmonic_power += h_power
            harmonics.append(fft_magnitude[harmonic_idx] / (fft_magnitude[fundamental_idx] + 1e-6) * 100)
        self.harmonics = np.array(harmonics)
        if fundamental_power == 0:
            self.thd = 0.0
        else:
            self.thd = np.sqrt(harmonic_power / fundamental_power) * 100
            self.thd = min(self.thd, 100.0)

    def compute_thd_freq(self, signal, fs):
        """Compute THD across frequency bands."""
        if len(signal) == 0:
            self.thd_freq = np.zeros(len(self.freq_bands))
            return
        fft = np.fft.fft(signal)
        fft_magnitude = np.abs(fft)[:len(fft)//2]
        freqs = np.fft.fftfreq(len(signal), 1/fs)[:len(fft)//2]
        thd_freq = []
        for f in self.freq_bands:
            fundamental_idx = np.argmin(np.abs(freqs - f))
            fundamental_power = fft_magnitude[fundamental_idx] ** 2
            harmonic_power = 0
            for harmonic in range(2, 11):
                harmonic_freq = f * harmonic
                harmonic_idx = np.argmin(np.abs(freqs - harmonic_freq))
                harmonic_power += fft_magnitude[harmonic_idx] ** 2
            thd = 0.0 if fundamental_power == 0 else np.sqrt(harmonic_power / fundamental_power) * 100
            thd_freq.append(min(thd, 100.0))
        self.thd_freq = np.array(thd_freq)

    def update(self, signal, fs):
        """Update THD, harmonics, and THD vs. frequency."""
        self.compute_thd(signal, fs)
        self.compute_thd_freq(signal, fs)

    def get_thd(self):
        """Return overall THD."""
        return self.thd

    def get_harmonics(self):
        """Return individual harmonic amplitudes."""
        return self.harmonics

    def get_thd_freq(self):
        """Return THD vs. frequency data."""
        return self.freq_bands, self.thd_freq