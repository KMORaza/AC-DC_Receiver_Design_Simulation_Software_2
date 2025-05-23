import numpy as np
from scipy import signal

class ReceiverModel:
    def __init__(self):
        # Signal parameters
        self.frequency = 1000  # Hz
        self.gain = 0  # dB
        self.modulation = "am"  # "am", "fm", "digital", "mixed"
        self.power_on = False
        self.signal_mode = "analog"  # "analog", "digital", "mixed"

        # Circuit parameters
        self.rectifier_type = "bridge"  # "half_wave", "full_wave", "bridge"
        self.filter_type = "capacitive"  # "capacitive", "inductive", "active"
        self.filter_capacitance = 100e-6  # Farads (100 µF)
        self.filter_inductance = 10e-3  # Henries (10 mH)
        self.active_filter_cutoff = 100  # Hz for active filter
        self.regulator_type = "none"  # "none", "linear", "switching"
        self.linear_vref = 5.0  # Reference voltage for linear regulator (V)
        self.switching_freq = 10000  # Switching regulator frequency (Hz)
        self.turns_ratio = 1.0  # Transformer turns ratio
        self.coil_inductance = 1e-3  # Transformer leakage inductance (1 mH)
        self.load_resistance = 100  # Ohms
        self.dc_voltage = 0  # Initial DC voltage across capacitor
        self.input_voltage = 120  # RMS input voltage (60 Hz)

        # Nonlinear device parameters
        self.diode_is = 1e-12  # Diode saturation current (A)
        self.diode_vt = 0.025  # Thermal voltage (V) at 25°C
        self.mosfet_vth = 2.0  # MOSFET threshold voltage (V)
        self.mosfet_k = 0.1  # MOSFET gain factor (A/V^2)
        self.opamp_gain = 1000  # Op-amp open-loop gain for active filter/regulator

        # Passive component parameters
        self.parasitic_resistance = 0.1  # Series resistance for inductors (Ohms)

        # Thermal parameters
        self.temperature = 25  # °C
        self.thermal_resistance = 10  # °C/W
        self.efficiency = 1.0

        # Simulation parameters
        self.dt = 0.1 / 1000  # Time step (0.1 s / 1000 samples)
        self.modulation_index = 0.5  # AM/FM modulation index
        self.digital_freq = 500  # Hz for digital signal

        # Analysis mode
        self.analysis_mode = "transient"  # "transient", "steady_state", "frequency"

    def set_frequency(self, value):
        self.frequency = value

    def set_gain(self, value):
        self.gain = value

    def set_modulation(self, mod_type):
        self.modulation = mod_type.lower()

    def set_power(self, state):
        self.power_on = state

    def set_signal_mode(self, mode):
        self.signal_mode = mode.lower()

    def set_analysis_mode(self, mode):
        self.analysis_mode = mode.lower()

    def set_filter_type(self, f_type):
        self.filter_type = f_type.lower()

    def set_regulator_type(self, r_type):
        self.regulator_type = r_type.lower()

    def set_filter_inductance(self, value):
        self.filter_inductance = value

    def set_active_filter_cutoff(self, value):
        self.active_filter_cutoff = value

    def set_linear_vref(self, value):
        self.linear_vref = value

    def set_switching_freq(self, value):
        self.switching_freq = value

    def set_coil_inductance(self, value):
        self.coil_inductance = value

    def diode_model(self, v):
        """Nonlinear diode model with exponent clipping to prevent overflow."""
        max_exp = 700  # Maximum exponent to prevent overflow in np.exp
        v_scaled = np.clip(v / self.diode_vt, -max_exp, max_exp)
        return self.diode_is * (np.exp(v_scaled) - 1)

    def mosfet_model(self, vgs, vds):
        """Simple MOSFET model (square-law for saturation region)."""
        if vgs < self.mosfet_vth:
            return 0  # Cutoff
        if vds < (vgs - self.mosfet_vth):
            return self.mosfet_k * (vgs - self.mosfet_vth) * vds  # Linear region
        return 0.5 * self.mosfet_k * (vgs - self.mosfet_vth)**2  # Saturation region

    def opamp_model(self, v_in, v_out):
        """Simple op-amp model for active filter/regulator with clipping."""
        max_output = 1000  # Maximum output voltage to prevent overflow
        output = self.opamp_gain * (v_in - v_out)
        return np.clip(output, -max_output, max_output)

    def generate_waveform(self, t):
        if not self.power_on:
            self.dc_voltage = 0
            self.temperature = 25
            self.efficiency = 1.0
            return np.zeros_like(t), np.zeros_like(t), np.zeros_like(t)

        # AC input (60 Hz)
        ac_voltage = self.input_voltage * np.sqrt(2) * np.sin(2 * np.pi * 60 * t)

        # Transformer with leakage inductance
        max_voltage = 1000
        transformed_voltage = ac_voltage * self.turns_ratio
        if self.coil_inductance > 0:
            # Model leakage inductance as a high-pass filter effect
            di_dt = np.diff(ac_voltage) / self.dt
            di_dt = np.append(di_dt, di_dt[-1])  # Pad last value
            transformed_voltage -= self.coil_inductance * di_dt
        transformed_voltage = np.clip(transformed_voltage, -max_voltage, max_voltage)

        # Rectifier with nonlinear diode model
        rectified = np.zeros_like(transformed_voltage)
        if self.rectifier_type == "half_wave":
            rectified = np.where(self.diode_model(transformed_voltage) > 0, transformed_voltage, 0)
        elif self.rectifier_type == "full_wave":
            rectified = np.where(self.diode_model(np.abs(transformed_voltage)) > 0, np.abs(transformed_voltage), 0)
        else:  # bridge
            v = np.abs(transformed_voltage)
            diode_drop = 2 * self.diode_vt * np.log1p(self.diode_model(v) / self.diode_is + 1)
            rectified = np.maximum(v - diode_drop, 0)

        # Filter
        filtered = np.zeros_like(rectified)
        if self.filter_type == "capacitive":
            for i in range(len(t)):
                if self.filter_capacitance > 0:
                    current = (rectified[i] - self.dc_voltage) / self.load_resistance
                    self.dc_voltage += current * self.dt / self.filter_capacitance
                    self.dc_voltage = max(self.dc_voltage, 0)
                    filtered[i] = self.dc_voltage
                else:
                    filtered[i] = rectified[i]
        elif self.filter_type == "inductive":
            # Simple RL low-pass filter
            tau = self.filter_inductance / (self.load_resistance + self.parasitic_resistance)
            for i in range(1, len(t)):
                filtered[i] = filtered[i-1] + self.dt / tau * (rectified[i] - filtered[i-1])
            filtered[0] = rectified[0]
        else:  # active
            # First-order low-pass active filter using op-amp
            tau = 1 / (2 * np.pi * self.active_filter_cutoff)
            for i in range(1, len(t)):
                v_in = rectified[i]
                v_out = filtered[i-1]
                filtered[i] = v_out + self.dt / tau * self.opamp_model(v_in, v_out)
            filtered[0] = rectified[0]

        # Regulator
        regulated = filtered.copy()
        if self.regulator_type == "linear":
            # Simple linear regulator: clamp to reference voltage
            regulated = np.clip(filtered, 0, self.linear_vref)
        elif self.regulator_type == "switching":
            # Basic buck converter model
            duty_cycle = np.clip(self.linear_vref / (np.mean(filtered) + 1e-9), 0, 1)
            switching_signal = np.sign(np.sin(2 * np.pi * self.switching_freq * t))
            regulated = filtered * duty_cycle * (switching_signal > 0)

        # Digital signal (square wave for mixed-signal or digital mode)
        digital_signal = np.zeros_like(t)
        if self.signal_mode in ["digital", "mixed"]:
            digital_signal = np.sign(np.sin(2 * np.pi * self.digital_freq * t))

        # Apply AM/FM modulation or digital/mixed signal
        carrier = regulated * np.sin(2 * np.pi * self.frequency * t)
        gain_linear = 10 ** (self.gain / 20)
        if self.signal_mode == "digital":
            modulated = gain_linear * digital_signal
        elif self.signal_mode == "mixed":
            modulated = gain_linear * (carrier + digital_signal)
        elif self.modulation == "am":
            modulating = self.modulation_index * np.sin(2 * np.pi * 100 * t)
            modulated = gain_linear * carrier * (1 + modulating)
        else:  # fm
            modulating = self.modulation_index * np.sin(2 * np.pi * 100 * t)
            phase = 2 * np.pi * self.frequency * t + self.modulation_index * np.cumsum(modulating) * self.dt
            modulated = gain_linear * regulated * np.sin(phase)

        # Update thermal model
        max_amplitude = 1000  # Clip signal to prevent overflow in power calculation
        regulated = np.clip(regulated, -max_amplitude, max_amplitude)
        power = np.mean(regulated**2 / self.load_resistance)
        self.update_thermal(power)

        return ac_voltage, rectified, modulated

    def update_thermal(self, power):
        ambient_temp = 25
        time_constant = 1.0  # seconds
        self.temperature += (power * self.thermal_resistance - (self.temperature - ambient_temp)) * self.dt / time_constant
        self.temperature = max(self.temperature, ambient_temp)
        input_power = self.dc_voltage**2 / self.load_resistance + 1e-9
        self.efficiency = 1 - (power / input_power) if input_power > 0 else 1.0
        self.efficiency = min(max(self.efficiency, 0), 1)

    def analyze_waveform(self, signal, t):
        max_amplitude = 1000  # Clip signal to prevent overflow
        signal = np.clip(signal, -max_amplitude, max_amplitude)
        if self.analysis_mode == "transient":
            steady_state = signal[len(signal)//2:]
            ripple_voltage = np.max(steady_state) - np.min(steady_state) if len(steady_state) > 0 else 0
            return {
                "ripple_voltage": ripple_voltage,
                "thd": 0,
                "power": np.mean(signal**2 / self.load_resistance) if len(signal) > 0 else 0,
                "transient_time": len(t) * self.dt / 2
            }
        elif self.analysis_mode == "steady_state":
            steady_state = signal[len(signal)//2:]
            avg_voltage = np.mean(steady_state) if len(steady_state) > 0 else 0
            ripple_voltage = np.max(steady_state) - np.min(steady_state) if len(steady_state) > 0 else 0
            return {
                "ripple_voltage": ripple_voltage,
                "avg_voltage": avg_voltage,
                "power": np.mean(steady_state**2 / self.load_resistance) if len(steady_state) > 0 else 0
            }
        else:  # frequency
            fft = np.fft.fft(signal)
            freqs = np.fft.fftfreq(len(signal), self.dt)[:len(signal)//2]
            fft = fft[:len(signal)//2]
            fundamental_idx = np.argmin(np.abs(freqs - 60))
            fundamental = np.abs(fft[fundamental_idx]) / len(signal) if len(signal) > 0 else 1e-9
            harmonics = sum(np.abs(fft[2*fundamental_idx:11*fundamental_idx])**2) / len(signal) if len(signal) > 0 else 0
            thd = np.sqrt(harmonics) / fundamental * 100 if fundamental > 0 else 0
            phase = np.angle(fft[fundamental_idx], deg=True) if len(signal) > 0 else 0
            return {
                "thd": thd,
                "fundamental_freq": freqs[fundamental_idx] if len(signal) > 0 else 0,
                "phase": phase,
                "power": np.mean(signal**2 / self.load_resistance) if len(signal) > 0 else 0
            }