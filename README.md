# AC/DC Receiver Design Simulation Software

This software models and simulates an AC/DC receiver system, simulating signal processing, power electronics, and system performance metrics. It integrates components for power factor correction, EMI analysis, harmonic distortion, impedance matching, magnetic core behavior, nonlinear devices, SNR, stability, switching devices, THD, thermal modeling, and waveform generation.

_This software is an enhanced version of another similar software I wrote [previously](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software/tree/main) for AC/DC receiver simulation system in C#._

## Core System Simulation
- **Functioning**: Simulates the AC/DC receiver signal path, including AC input, transformer, rectifier, filter, regulator, and modulation (AM, FM, digital, mixed). Generates AC, rectified, and modulated waveforms and updates thermal parameters.
- **Simulation Logic**: Runs a 0.1-second simulation with a 0.1 ms time step (1000 samples). Processes a 60 Hz AC input through transformation, rectification, filtering, regulation, and modulation stages. Updates thermal model based on power dissipation.
- **Algorithms and Calculations**:
  - AC Input: Generates a 120 V RMS, 60 Hz sine wave: V_AC = 120 * sqrt(2) * sin(2 * pi * 60 * t).
  - Transformer: Applies turns ratio (V_transformed = V_AC * turns_ratio) and models leakage inductance as a high-pass filter: V_transformed -= L_coil * dI/dt, with dI/dt approximated numerically.
  - Rectification:
    - Half-wave: Passes positive voltages where diode conducts using Shockley model.
    - Full-wave: Uses absolute input voltage.
    - Bridge: Accounts for two diode drops: V_drop = 2 * V_T * ln(1 + I_D / I_s).
  - Filtering:
    - Capacitive: Solves C * dV_C/dt = (V_rect - V_C) / R_load using Euler integration: V_C(t+dt) = V_C(t) + (I_C * dt) / C.
    - Inductive: Models RL low-pass filter with tau = L / (R_load + R_parasitic): V_out(t) = V_out(t-1) + (dt/tau) * (V_in(t) - V_out(t-1)).
    - Active: Uses first-order low-pass filter with op-amp, tau = 1 / (2 * pi * f_cutoff): V_out(t) = V_out(t-1) + (dt/tau) * opamp_model(V_in, V_out).
  - Regulation:
    - Linear: Clamps output to reference voltage: V_reg = min(V_filtered, V_ref).
    - Switching: Models buck converter with duty cycle D = V_ref / V_filtered, modulated by a square wave at switching frequency.
  - Modulation:
    - AM: V_mod = G * V_carrier * (1 + 0.5 * sin(2 * pi * 100 * t)), where G = 10^(gain/20).
    - FM: V_mod = G * V_regulated * sin(2 * pi * f_c * t + 0.5 * integral(sin(2 * pi * 100 * t))), with integral via cumulative sum.
    - Digital: Generates 500 Hz square wave.
    - Mixed: Combines carrier and digital signals.
  - Thermal Update: Computes power P = V_regulated^2 / R_load, updates temperature: T(t+dt) = T(t) + (dt/tau) * (P * R_th - (T - T_ambient)), and efficiency: eta = 1 - P / P_input.
  - Waveform Analysis:
    - Transient: Computes ripple as V_max - V_min in second half of signal.
    - Steady-state: Calculates average voltage and ripple in second half.
    - Frequency: Uses FFT for THD (sqrt(sum(H_n^2)) / H_1 * 100), fundamental frequency, and phase.
- **Physics Models**:
  - Diode: Shockley model, I_D = I_s * (exp(V_D / V_T) - 1), with exponent clipping.
  - MOSFET: Square-law model for saturation (I_D = 0.5 * k * (V_GS - V_th)^2) and linear regions.
  - Op-amp: Linear model with gain clipping.
  - Thermal: First-order RC model for temperature dynamics.
  - Inductor: Simplified RL circuit for leakage inductance.

## Power Factor Improvement
- **Functioning**: Computes and corrects power factor (PF) by analyzing voltage and current waveforms, supporting active boost or passive PFC.
- **Simulation Logic**: Calculates PF from phase difference and distortion factor. Applies user-selected PFC method, adjusting efficiency.
- **Algorithms and Calculations**:
  - Power Factor: PF = cos(phi) * RMS_fundamental / RMS_total, where phi is phase difference via cross-correlation, and RMS values are from FFT.
  - Active Boost PFC: Assumes PF = 1, reduces efficiency by 2% (eta = 0.98 * eta).
  - Passive PFC: Applies PF = 0.9, reduces efficiency by 1% (eta = 0.99 * eta).
- **Physics Models**: Models PF as displacement and distortion factors, typical in power electronics.

## Electromagnetic Interference (EMI) Analysis
- **Functioning**: Analyzes conducted and radiated EMI, comparing against CISPR 22 Class B limits.
- **Simulation Logic**: Computes EMI spectrum from signal (150 kHz to 1 GHz). Applies EMI filter if enabled, reducing EMI levels.
- **Algorithms and Calculations**:
  - EMI Spectrum: Uses FFT to compute magnitude in dBuV: 20 * log10(V * 10^6).
  - Filter Effect: Reduces EMI by 20 * log10(1 + f / 1e6) dB.
  - Compliance: Compares EMI to CISPR 22 limits (e.g., 66-56 dBuV for 150-500 kHz).
- **Physics Models**: Simplified EMI model based on Fourier transform of switching transients, with filter as a frequency-dependent attenuator.

### Harmonic Distortion Analysis
- **Functioning**: Computes total harmonic distortion plus noise (THD+N) and harmonic spectra (H2-H10), with CSV export.
- **Simulation Logic**: Analyzes modulated signal via FFT for THD+N and harmonic amplitudes. Supports logarithmic scaling.
- **Algorithms and Calculations**:
  - THD+N: sqrt(sum(H_n^2) + noise_power) / H_1 * 100, with H_n from FFT and noise from residuals.
  - Harmonic Amplitudes: H_n = FFT(f_n) / FFT(f_1) * 100 for n = 2 to 10.
  - Spectrum: Computes THD+N across 20 Hz to 20 kHz using band-pass filtering.
- **Physics Models**: Standard harmonic analysis for nonlinear systems, capturing rectifier and switching distortion.

## Impedance Analysis
- **Functioning**: Analyzes impedance matching between source and load, computing reflection coefficient, VSWR, return loss, and Smith chart data.
- **Simulation Logic**: Models source/load impedances with resistive and reactive components. Computes metrics over 10 Hz to 100 MHz.
- **Algorithms and Calculations**:
  - Reflection Coefficient: GAMMA = (Z_L - Z_S*) / (Z_L + Z_S*), where Z_S* is the complex conjugate.
  - VSWR: (1 + |GAMMA|) / (1 - |GAMMA|).
  - Return Loss: -20 * log10(|GAMMA|).
  - Impedance: Z_in = Z_S + j * 2 * pi * f * L, Z_out = Z_L.
- **Physics Models**: RF impedance matching model with complex impedance and transmission line theory.

## Magnetic Core Behavior
- **Functioning**: Simulates magnetic core behavior (H-field, B-field, magnetization, saturation) using a simplified Jiles-Atherton model.
- **Simulation Logic**: Models fields for Ferrite, Iron Powder, or Silicon Steel based on input current and frequency. Tracks hysteresis loop for B-H curve.
- **Algorithms and Calculations**:
  - H-field: H = I * N / l_e, with N = 100, l_e = 0.1 m.
  - Magnetization: M = M_s * tanh((H + alpha * M) / H_c), with material-specific M_s, H_c, alpha.
  - B-field: B = mu_0 * (H + M), where mu_0 = 4 * pi * 10^-7 H/m.
  - Saturation: Clamps B at material limits (e.g., 0.4 T for Ferrite).
- **Physics Models**: Simplified Jiles-Atherton model for magnetic hysteresis and saturation.

## Diode and Transistor Modeling
- **Functioning**: Models nonlinear behavior of diodes and transistors for rectification and switching.
- **Simulation Logic**: Computes diode current from voltage and transistor collector current in active region.
- **Algorithms and Calculations**:
  - Diode: Shockley equation, I_D = 10^-12 * (exp(V_D / 0.025) - 1).
  - Transistor: I_C = 100 * I_B, clipped at V_CE = 0.2 V.
- **Physics Models**: Standard semiconductor models for diodes and BJTs.

## Signal-to-Noise Ratio Analysis
- **Functioning**: Computes overall SNR, noise floor, and SNR spectrum (20 Hz to 20 kHz).
- **Simulation Logic**: Adds Gaussian noise to signal and computes power ratios. Analyzes SNR in frequency bands via FFT.
- **Algorithms and Calculations**:
  - Overall SNR: 10 * log10(P_signal / P_noise), where P_signal = mean(signal^2), P_noise = mean(noise^2).
  - Noise Floor: 10 * log10(P_noise) - 120 dB, relative to 1 V.
  - SNR Spectrum: SNR_f = 10 * log10(P_signal,f / P_noise,f) per frequency band.
- **Physics Models**: Signal processing model with additive white Gaussian noise.

## System Stability Analysis
- **Functioning**: Analyzes stability using Bode, Nyquist, and root locus plots for filter and regulator transfer functions.
- **Simulation Logic**: Constructs transfer functions for capacitive, inductive, or active filters. Updates plots for 1 Hz to 100 kHz.
- **Algorithms and Calculations**:
  - Transfer Functions:
    - Capacitive: H(s) = 1 / (s * R * C + 1).
    - Inductive: H(s) = 1 / (s * L / R + 1).
    - Active: H(s) = A / (s * tau + 1), with regulator gain adjustments.
  - Bode Plot: Computes magnitude (20 * log10|H(jw)|) and phase (angle(H(jw))).
  - Nyquist Plot: Plots real vs. imaginary parts of H(jw), marking -1 point.
  - Root Locus: Plots pole trajectories for gains 0 to 100.
- **Physics Models**: Linear control theory for small-signal dynamics.

## Switching Device Behavior
- **Functioning**: Models transient and steady-state behavior of MOSFET, IGBT, GaN, or SiC devices in a buck converter setup.
- **Simulation Logic**: Simulates gate voltage, drain-source voltage, and power loss over 1 ms. Computes losses, efficiency, and junction temperature.
- **Algorithms and Calculations**:
  - Transients:
    - Gate Voltage: V_g(t) = V_gate * (1 - exp(-t / (R_g * C_g))) during turn-on, V_g(t) = V_gate * exp(-t / (R_g * C_g)) during turn-off.
    - Drain-Source Voltage/Current: Linear ramps during t_on, t_off.
    - Power Loss: P_loss(t) = V_DS(t) * I_DS(t).
  - Metrics:
    - Conduction Loss: P_cond = I_load^2 * R_on * D.
    - Switching Loss: P_sw = 0.5 * V_supply * I_load * (t_on + t_off) * f_sw.
    - Efficiency: eta = P_out / (P_out + P_total) * 100, where P_out = V_supply * I_load * D.
    - Junction Temperature: T_j = T_amb + P_total * R_thJA.
- **Physics Models**: Switching model with RC gate dynamics and linear transients. Steady-state thermal model.

## Total Harmonic Distortion Analysis
- **Functioning**: Computes THD and harmonic amplitudes (H2-H10) for modulated signal, plus THD across 100 Hz to 10 kHz.
- **Simulation Logic**: Uses FFT to extract fundamental and harmonics. Analyzes THD in frequency bands.
- **Algorithms and Calculations**:
  - THD: sqrt(sum(H_n^2)) / H_1 * 100, where H_n = |FFT(f_n)|.
  - Harmonics: H_n = |FFT(n * f_0)| / |FFT(f_0)| * 100.
  - THD vs. Frequency: THD_f = sqrt(sum(H_n,f^2)) / H_1,f * 100 per band.
- **Physics Models**: Fourier-based distortion analysis for nonlinear systems.

## Component Thermal Analysis
- **Functioning**: Simulates thermal behavior of diode, MOSFET, and system, accounting for power dissipation and thermal coupling.
- **Simulation Logic**: Computes power from receiver waveforms. Updates temperatures using RC thermal model over 0.1-second window.
- **Algorithms and Calculations**:
  - Power Dissipation:
    - Diode: P_diode = I_diode * 0.7, where I_diode = V_rectified / 100.
    - MOSFET: P_MOSFET = I_MOSFET^2 * 0.1, where I_MOSFET = |V_modulated| / 50.
  - Temperature Update:
    - Diode: Delta_T_diode = (dt / C_th,diode) * (P_diode * R_th,diode + k * (T_MOSFET - T_diode) - (T_diode - T_amb)).
    - MOSFET: Similar, with C_th,MOSFET, R_th,MOSFET.
    - System: T_system = (T_diode + T_MOSFET) / 2.
  - Thermal Coupling: k = 0.2 for heat transfer between components.
- **Physics Models**: First-order RC thermal model with thermal resistance and capacitance.

## Signal Waveform Generation
- **Functioning**: Generates AC, rectified, and modulated waveforms for analysis.
- **Simulation Logic**: Calls ReceiverModel.generate_waveform for 0.01-second signals. Supports analog, digital, or mixed modes.
- **Algorithms and Calculations**: Relies on ReceiverModel for waveform generation.
- **Physics Models**: Uses ReceiverModel physics for signal generation.

## System Integration and Simulation Loop
- **Functioning**: Integrates all components (ReceiverModel, analyzers) into a cohesive simulation with real-time updates.
- **Simulation Logic**: Runs a 50 ms update loop, generating waveforms and updating analyzers. Supports transient, steady-state, and frequency modes. Injects noise for SNR analysis.
- **Algorithms and Calculations**:
  - Waveform Generation: Uses ReceiverModel for AC, rectified, and modulated signals.
  - Noise Injection: Adds Gaussian noise N(0, sigma) for SNR analysis.
  - Analyzer Updates: Calls HarmonicAnalyzer, PowerFactorCorrection, SNRAnalyzer, THDAnalyzer, EMIAnalyzer, ThermalAnalyzer, and StabilityAnalyzer for respective metrics.
- **Physics Models**: Orchestrates all component physics models for synchronized simulation.

---

| ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(1).png) | ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(2).png) | ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(3).png) | ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(4).png) |
|-------|-------|-------|-------|
| ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(5).png) | ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(6).png) | ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(7).png) | ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(8).png) |
| ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(9).png) | ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(10).png) | ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(11).png) | ![](https://github.com/KMORaza/AC-DC_Receiver_Design_Simulation_Software_2/blob/main/AC-DC%20Reciever%20Design%20Simulation%20Software/screenshots/screenshot%20(12).png) |
