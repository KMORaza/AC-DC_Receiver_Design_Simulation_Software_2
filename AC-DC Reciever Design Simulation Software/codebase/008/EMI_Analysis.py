import numpy as np

class EMIAnalyzer:
    def __init__(self, model):
        self.model = model
        self.conducted_emi = 0.0
        self.radiated_emi = 0.0
        self.emi_spectrum = []
        self.freq_bands = np.logspace(np.log10(150e3), np.log10(1e9), 50)  # 150 kHz to 1 GHz
        self.emi_filter_enabled = False
        self.cispr_limits = self.generate_cispr_limits()

    def generate_cispr_limits(self):
        """Generate CISPR 22 Class B limits (dBµV)."""
        limits = np.zeros_like(self.freq_bands)
        for i, f in enumerate(self.freq_bands):
            if f <= 30e6:  # Conducted (150 kHz–30 MHz)
                limits[i] = 60 if f < 5e6 else 56
            else:  # Radiated (30 MHz–1 GHz)
                limits[i] = 40 if f < 230e6 else 47
        return limits

    def compute_emi(self, t, signal):
        """Compute conducted and radiated EMI levels."""
        if self.model.regulator_type != "switching" or not self.model.power_on:
            self.conducted_emi = self.radiated_emi = 0.0
            return
        emi_freq = self.model.switching_freq
        # Conducted EMI (150 kHz–30 MHz)
        conducted_signal = 0.01 * np.sin(2 * np.pi * emi_freq * t) * np.max(np.abs(signal))
        v_rms_conducted = np.sqrt(np.mean(conducted_signal ** 2))
        conducted_dbuv = 20 * np.log10(v_rms_conducted * 1e6) if v_rms_conducted > 0 else 0.0
        # Radiated EMI (30 MHz–1 GHz, scaled down)
        radiated_signal = 0.005 * np.sin(2 * np.pi * emi_freq * 10 * t) * np.max(np.abs(signal))
        v_rms_radiated = np.sqrt(np.mean(radiated_signal ** 2))
        radiated_dbuv = 20 * np.log10(v_rms_radiated * 1e6) if v_rms_radiated > 0 else 0.0
        # Apply EMI filter
        filter_attenuation = 20 if self.emi_filter_enabled else 0
        self.conducted_emi = max(0.0, min(conducted_dbuv - filter_attenuation, 120.0))
        self.radiated_emi = max(0.0, min(radiated_dbuv - filter_attenuation, 120.0))

    def compute_emi_spectrum(self, t, signal):
        """Compute EMI spectrum."""
        if self.model.regulator_type != "switching" or not self.model.power_on:
            self.emi_spectrum = np.zeros(len(self.freq_bands))
            return
        emi_spectrum = []
        for f in self.freq_bands:
            emi_signal = 0.01 * np.sin(2 * np.pi * f * t) * np.max(np.abs(signal))
            v_rms = np.sqrt(np.mean(emi_signal ** 2))
            emi_dbuv = 20 * np.log10(v_rms * 1e6) if v_rms > 0 else 0.0
            filter_attenuation = 20 if self.emi_filter_enabled else 0
            emi_spectrum.append(max(0.0, min(emi_dbuv - filter_attenuation, 120.0)))
        self.emi_spectrum = np.array(emi_spectrum)

    def toggle_emi_filter(self, enabled):
        """Toggle EMI filter."""
        self.emi_filter_enabled = enabled

    def update(self, t, signal):
        """Update EMI levels and spectrum."""
        self.compute_emi(t, signal)
        self.compute_emi_spectrum(t, signal)

    def get_conducted_emi(self):
        """Return conducted EMI level."""
        return self.conducted_emi

    def get_radiated_emi(self):
        """Return radiated EMI level."""
        return self.radiated_emi

    def get_emi_spectrum(self):
        """Return EMI spectrum and CISPR limits."""
        return self.freq_bands, self.emi_spectrum, self.cispr_limits