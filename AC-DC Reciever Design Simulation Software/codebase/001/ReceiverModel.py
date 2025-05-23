import numpy as np
from scipy import signal
import control

class ReceiverModel:
    def __init__(self):
        self.frequency = 1000
        self.gain = 0
        self.signal_mode = "analog"
        self.modulation = None
        self.analysis_mode = "transient"
        self.rectifier_type = "half_wave"
        self.filter_type = "capacitive"
        self.filter_capacitance = 100e-6
        self.filter_inductance = 10e-3
        self.active_filter_cutoff = 100
        self.regulator_type = "none"
        self.linear_vref = 5.0
        self.switching_freq = 10000
        self.turns_ratio = 1.0
        self.coil_inductance = 1e-3
        self.diode_is = 1e-12
        self.mosfet_vth = 2.0
        self.power_on = False
        self.temperature = 25.0
        self.efficiency = 1.0

    def set_frequency(self, freq):
        self.frequency = freq

    def set_gain(self, gain):
        self.gain = gain

    def set_signal_mode(self, mode):
        self.signal_mode = mode

    def set_modulation(self, mod_type):
        self.modulation = mod_type

    def set_analysis_mode(self, mode):
        self.analysis_mode = mode

    def set_filter_type(self, filter_type):
        self.filter_type = filter_type

    def set_filter_inductance(self, inductance):
        self.filter_inductance = inductance

    def set_active_filter_cutoff(self, cutoff):
        self.active_filter_cutoff = cutoff

    def set_regulator_type(self, reg_type):
        self.regulator_type = reg_type

    def set_linear_vref(self, vref):
        self.linear_vref = vref

    def set_switching_freq(self, freq):
        self.switching_freq = freq

    def set_coil_inductance(self, inductance):
        self.coil_inductance = inductance

    def set_power(self, state):
        self.power_on = state

    def get_transfer_function(self):
        if self.filter_type == "capacitive":
            R = 100
            C = self.filter_capacitance
            num = [1]
            den = [R*C, 1]
        elif self.filter_type == "inductive":
            R = 100
            L = self.filter_inductance
            num = [R]
            den = [L, R]
        else:
            omega = 2 * np.pi * self.active_filter_cutoff
            Q = 0.707
            num = [omega**2]
            den = [1, omega/Q, omega**2]

        if self.regulator_type == "linear":
            num = [self.linear_vref * n for n in num]
        elif self.regulator_type == "switching":
            num = [self.switching_freq * n for n in num]

        return control.TransferFunction(num, den)

    def get_bode_data(self):
        sys = self.get_transfer_function()
        w = np.logspace(0, 5, 1000)
        mag, phase, omega = control.bode(sys, w, dB=True, Hz=True, plot=False)
        return omega, mag, phase

    def get_nyquist_data(self):
        sys = self.get_transfer_function()
        w = np.logspace(0, 5, 1000)
        re, im, freq = control.nyquist_response(sys, w, plot=False)
        return re, im, freq

    def get_root_locus_data(self):
        sys = self.get_transfer_function()
        gains = np.logspace(-2, 2, 100)
        poles = []
        for k in gains:
            cl_sys = control.feedback(sys * k)
            p = control.pole(cl_sys)
            poles.append(p)
        return gains, poles

    def get_stability_metrics(self):
        sys = self.get_transfer_function()
        gm, pm, _, _ = control.margin(sys)
        return {
            "gain_margin": gm if gm is not None else float('inf'),
            "phase_margin": pm if pm is not None else 0.0
        }

    def generate_waveform(self, t):
        if not self.power_on:
            return np.zeros_like(t), np.zeros_like(t), np.zeros_like(t)

        amplitude = 10 * (10 ** (self.gain / 20))
        ac_signal = amplitude * np.sin(2 * np.pi * self.frequency * t)

        if self.rectifier_type == "half_wave":
            rectified_signal = np.maximum(ac_signal, 0)
        elif self.rectifier_type == "full_wave":
            rectified_signal = np.abs(ac_signal)
        else:
            rectified_signal = np.abs(ac_signal)

        if self.filter_type == "capacitive":
            system = signal.TransferFunction([1], [self.filter_capacitance * 100, 1])
            t_out, filtered_signal, x_out = signal.lsim(system, rectified_signal, t)
        elif self.filter_type == "inductive":
            system = signal.TransferFunction([100], [self.filter_inductance, 100])
            t_out, filtered_signal, x_out = signal.lsim(system, rectified_signal, t)
        else:
            system = signal.TransferFunction([self.active_filter_cutoff**2], [1, self.active_filter_cutoff/0.707, self.active_filter_cutoff**2])
            t_out, filtered_signal, x_out = signal.lsim(system, rectified_signal, t)

        if self.regulator_type == "linear":
            filtered_signal = np.clip(filtered_signal, 0, self.linear_vref)
        elif self.regulator_type == "switching":
            filtered_signal = filtered_signal * np.sin(2 * np.pi * self.switching_freq * t)

        if self.modulation == "AM":
            modulated_signal = filtered_signal * (1 + 0.5 * np.sin(2 * np.pi * 100 * t))
        elif self.modulation == "FM":
            modulated_signal = filtered_signal * np.sin(2 * np.pi * (self.frequency + 100 * np.sin(2 * np.pi * 10 * t)) * t)
        else:
            modulated_signal = filtered_signal

        modulated_signal *= self.turns_ratio
        if self.coil_inductance > 0:
            system = signal.TransferFunction([1], [self.coil_inductance, 0])
            t_out, modulated_signal, x_out = signal.lsim(system, modulated_signal, t)

        if self.signal_mode in ["digital", "mixed"]:
            modulated_signal = np.where(modulated_signal > self.mosfet_vth, self.linear_vref, 0)

        return ac_signal, rectified_signal, modulated_signal

    def analyze_waveform(self, signal, t):
        if not self.power_on:
            return {
                "ripple_voltage": 0.0,
                "avg_voltage": 0.0,
                "thd": 0.0,
                "phase": 0.0,
                "power": 0.0,
                "gain_margin": 0.0,
                "phase_margin": 0.0
            }

        ripple_voltage = np.max(signal) - np.min(signal)
        avg_voltage = np.mean(signal)
        fft = np.fft.fft(signal)
        fundamental = np.abs(fft[1])
        harmonics = np.sum(np.abs(fft[2:10]))
        thd = (harmonics / fundamental) * 100 if fundamental > 0 else 0
        phase = np.angle(fft[1]) * 180 / np.pi
        power = np.mean(signal**2 / 100)
        stability = self.get_stability_metrics()

        return {
            "ripple_voltage": ripple_voltage,
            "avg_voltage": avg_voltage,
            "thd": thd,
            "phase": phase,
            "power": power,
            "gain_margin": stability["gain_margin"],
            "phase_margin": stability["phase_margin"]
        }