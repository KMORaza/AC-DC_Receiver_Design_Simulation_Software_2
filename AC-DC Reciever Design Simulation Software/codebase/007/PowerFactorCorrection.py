import numpy as np

class PowerFactorCorrection:
    def __init__(self, model):
        self.model = model
        self.pfc_enabled = False
        self.pfc_type = "none"  # Options: "none", "active_boost", "passive"
        self.power_factor = 1.0  # Default PF

    def set_pfc(self, enabled, pfc_type="none"):
        """Enable/disable PFC and set correction type."""
        self.pfc_enabled = enabled
        self.pfc_type = pfc_type.lower() if enabled else "none"

    def compute_power_factor(self, voltage, current):
        """Compute power factor from voltage and current waveforms."""
        if len(voltage) != len(current) or len(voltage) == 0:
            return 1.0
        # Real power (average of instantaneous power)
        real_power = np.mean(voltage * current)
        # RMS voltage and current
        v_rms = np.sqrt(np.mean(voltage ** 2))
        i_rms = np.sqrt(np.mean(current ** 2))
        # Apparent power
        apparent_power = v_rms * i_rms
        # Power factor
        if apparent_power == 0:
            return 1.0
        pf = abs(real_power / apparent_power)
        return min(pf, 1.0)  # Ensure PF <= 1.0

    def apply_pfc(self, t, voltage, current):
        """Apply PFC to the current waveform based on type."""
        if not self.pfc_enabled or self.pfc_type == "none":
            self.power_factor = self.compute_power_factor(voltage, current)
            return current

        if self.pfc_type == "active_boost":
            # Simulate active boost PFC: Align current with voltage, reduce harmonics
            phase_shift = 0.0  # Ideal alignment
            current = np.abs(voltage) * np.sign(voltage) * (np.max(np.abs(current)) / np.max(np.abs(voltage)))
            # Add slight distortion to simulate non-ideal PFC
            distortion = 0.05 * np.random.normal(0, 1, len(t))
            current += distortion * np.std(current)

        elif self.pfc_type == "passive":
            # Simulate passive PFC: Partial phase correction with capacitor/inductor
            phase_shift = -np.pi / 12  # Reduce phase lag by ~15 degrees
            current = np.sin(2 * np.pi * self.model.frequency * t + phase_shift) * np.max(np.abs(current))
            # Add some harmonic content
            current += 0.1 * np.sin(4 * np.pi * self.model.frequency * t) * np.max(np.abs(current))

        self.power_factor = self.compute_power_factor(voltage, current)
        return current

    def get_power_factor(self):
        """Return the computed power factor."""
        return self.power_factor

    def adjust_efficiency(self, base_efficiency):
        """Adjust efficiency based on PFC."""
        if not self.pfc_enabled or self.pfc_type == "none":
            return base_efficiency
        # Active PFC: Slight efficiency penalty due to switching losses
        if self.pfc_type == "active_boost":
            return base_efficiency * 0.98
        # Passive PFC: Minimal efficiency impact
        return base_efficiency * 0.995