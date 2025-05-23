import numpy as np

class SNRAnalyzer:
    def __init__(self, model):
        self.model = model
        self.snr = 0.0
        self.noise_floor = 0.0
        self.snr_spectrum = []
        self.freq_bands = np.logspace(np.log10(20), np.log10(20000), 50)  # 20 Hz to 20 kHz

    def compute_snr(self, signal, noise_level, fs):
        """Compute overall SNR and noise floor."""
        if len(signal) == 0 or noise_level <= 0:
            self.snr = 0.0
            self.noise_floor = 0.0
            return
        signal_power = np.mean(signal ** 2)
        noise = np.random.normal(0, noise_level * np.std(signal), len(signal))
        noise_power = np.mean(noise ** 2)
        if noise_power == 0:
            self.snr = 100.0
            self.noise_floor = -100.0
        else:
            self.snr = 10 * np.log10(signal_power / noise_power)
            self.noise_floor = 10 * np.log10(noise_power) - 120  # Relative to 1 V
        self.snr = max(0.0, min(self.snr, 100.0))
        self.noise_floor = max(-120.0, min(self.noise_floor, 0.0))

    def compute_snr_spectrum(self, signal, noise_level, fs):
        """Compute SNR across frequency bands."""
        if len(signal) == 0 or noise_level <= 0:
            self.snr_spectrum = np.zeros(len(self.freq_bands))
            return
        fft_signal = np.abs(np.fft.fft(signal))[:len(signal)//2]
        fft_noise = np.abs(np.fft.fft(np.random.normal(0, noise_level * np.std(signal), len(signal))))[:len(signal)//2]
        freqs = np.fft.fftfreq(len(signal), 1/fs)[:len(signal)//2]
        snr_spectrum = []
        for f in self.freq_bands:
            idx = np.where((freqs >= f * 0.9) & (freqs <= f * 1.1))[0]
            if len(idx) > 0:
                signal_power = np.mean(fft_signal[idx] ** 2)
                noise_power = np.mean(fft_noise[idx] ** 2)
                snr_db = 100.0 if noise_power == 0 else 10 * np.log10(signal_power / noise_power)
                snr_spectrum.append(max(0.0, min(snr_db, 100.0)))
            else:
                snr_spectrum.append(0.0)
        self.snr_spectrum = np.array(snr_spectrum)

    def update(self, signal, noise_level, fs):
        """Update SNR, noise floor, and spectrum."""
        self.compute_snr(signal, noise_level, fs)
        self.compute_snr_spectrum(signal, noise_level, fs)

    def get_snr(self):
        """Return overall SNR."""
        return self.snr

    def get_noise_floor(self):
        """Return noise floor."""
        return self.noise_floor

    def get_snr_spectrum(self):
        """Return SNR spectrum and frequency bands."""
        return self.freq_bands, self.snr_spectrum