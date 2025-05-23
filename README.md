
### 1. **ReceiverModel.py: Core System Simulation**
   - **Functioning**: Models the AC/DC receiver's signal path, including AC input, transformer, rectifier, filter, regulator, and modulation (AM/FM/digital/mixed). Generates waveforms (AC input, rectified, modulated) and updates thermal parameters.
   - **Simulation Logic**:
     - Simulates a 0.1-second waveform with a time step of 0.1 ms (1000 samples).
     - Generates a 60 Hz AC input voltage, transformed by a turns ratio, and affected by leakage inductance.
     - Processes the signal through rectification, filtering, regulation, and modulation stages.
     - Updates thermal parameters based on power dissipation.
   - **Algorithms and Calculations**:
     - **AC Input**: \( V_{AC} = V_{RMS} \cdot \sqrt{2} \cdot \sin(2\pi \cdot 60 \cdot t) \), where \( V_{RMS} = 120 \, \text{V} \).
     - **Transformer**: Applies turns ratio (\( V_{\text{transformed}} = V_{AC} \cdot \text{turns_ratio} \)) and models leakage inductance as a high-pass filter effect: \( V_{\text{transformed}} -= L_{\text{coil}} \cdot \frac{dI}{dt} \), with \( \frac{dI}{dt} \) approximated via numerical differentiation.
     - **Rectification**:
       - Half-wave: Passes positive voltages where diode conducts (\( I_D = I_s \cdot (\exp(V_D / V_T) - 1) \)).
       - Full-wave: Uses absolute value of input (\( V_{\text{rect}} = |V_{\text{transformed}}| \)).
       - Bridge: Accounts for two diode drops (\( V_D = 2 \cdot V_T \cdot \ln(1 + I_D / I_s) \)).
     - **Filtering**:
       - Capacitive: Solves \( C \frac{dV_C}{dt} = I_C = \frac{V_{\text{rect}} - V_C}{R_{\text{load}}} \), using Euler integration: \( V_C(t+dt) = V_C(t) + \frac{I_C \cdot dt}{C} \).
       - Inductive: Models RL low-pass filter with time constant \( \tau = L / (R_{\text{load}} + R_{\text{parasitic}}) \), using: \( V_{\text{out}}(t) = V_{\text{out}}(t-1) + \frac{dt}{\tau} \cdot (V_{\text{in}}(t) - V_{\text{out}}(t-1)) \).
       - Active: Uses a first-order low-pass filter with op-amp model, \( \tau = 1 / (2\pi \cdot f_{\text{cutoff}}) \), and output: \( V_{\text{out}}(t) = V_{\text{out}}(t-1) + \frac{dt}{\tau} \cdot \text{opamp_model}(V_{\text{in}}, V_{\text{out}}) \).
     - **Regulation**:
       - Linear: Clamps output to reference voltage (\( V_{\text{reg}} = \min(V_{\text{filtered}}, V_{\text{ref}}) \)).
       - Switching: Models a buck converter with duty cycle \( D = V_{\text{ref}} / V_{\text{filtered}} \), modulated by a square wave at switching frequency.
     - **Modulation**:
       - AM: \( V_{\text{mod}} = G \cdot V_{\text{carrier}} \cdot (1 + m \cdot \sin(2\pi \cdot 100 \cdot t)) \), where \( G = 10^{\text{gain}/20} \), \( m = 0.5 \).
       - FM: \( V_{\text{mod}} = G \cdot V_{\text{regulated}} \cdot \sin(2\pi \cdot f_c \cdot t + m \cdot \int \sin(2\pi \cdot 100 \cdot t) \, dt) \), with integral approximated via cumulative sum.
       - Digital: Generates a square wave at 500 Hz.
       - Mixed: Combines carrier and digital signals.
     - **Thermal Update**: Computes power dissipation (\( P = \frac{V_{\text{regulated}}^2}{R_{\text{load}}} \)), updates temperature using: \( T(t+dt) = T(t) + \frac{dt}{\tau} \cdot (P \cdot R_{\text{th}} - (T - T_{\text{ambient}})) \), and calculates efficiency as \( \eta = 1 - P / P_{\text{input}} \).
     - **Waveform Analysis**:
       - Transient: Computes ripple voltage as \( V_{\text{max}} - V_{\text{min}} \) in the second half of the signal.
       - Steady-state: Calculates average voltage and ripple in the second half.
       - Frequency: Performs FFT to compute THD (\( \text{THD} = \sqrt{\sum H_n^2} / H_1 \cdot 100 \)), fundamental frequency, and phase.
   - **Physics Models**:
     - **Diode**: Shockley model, \( I_D = I_s \cdot (\exp(V_D / V_T) - 1) \), with exponent clipping to prevent overflow.
     - **MOSFET**: Square-law model for saturation (\( I_D = 0.5 \cdot k \cdot (V_{GS} - V_{\text{th}})^2 \)) and linear regions.
     - **Op-amp**: Linear model with gain clipping (\( V_{\text{out}} = \text{clip}(A \cdot (V_{\text{in}} - V_{\text{out}})) \)).
     - **Thermal**: First-order RC model for temperature dynamics.
     - **Inductor**: Simplified RL circuit for leakage inductance.

### 2. **PowerFactorCorrection.py: Power Factor Improvement**
   - **Functioning**: Computes and corrects power factor (PF) by analyzing voltage and current waveforms, applying active boost or passive PFC methods.
   - **Simulation Logic**:
     - Calculates PF as the cosine of the phase difference between voltage and current, adjusted by distortion factor.
     - Applies PFC based on user-selected method, adjusting efficiency accordingly.
   - **Algorithms and Calculations**:
     - **Power Factor**: \( \text{PF} = \cos(\phi) \cdot \frac{\text{RMS}_{\text{fundamental}}}{\text{RMS}_{\text{total}}} \), where \( \phi \) is the phase difference computed via cross-correlation, and RMS values are from FFT.
     - **Active Boost PFC**: Assumes ideal correction (\( \text{PF} \approx 1 \)), reduces efficiency by 2% (\( \eta = 0.98 \cdot \eta \)).
     - **Passive PFC**: Applies a correction factor (0.9), reduces efficiency by 1% (\( \eta = 0.99 \cdot \eta \)).
   - **Physics Models**:
     - Models PF as a combination of displacement and distortion factors, typical in power electronics.

### 3. **EMI_Analysis.py: Electromagnetic Interference Analysis**
   - **Functioning**: Analyzes conducted and radiated EMI, comparing against CISPR 22 Class B limits.
   - **Simulation Logic**:
     - Computes EMI spectrum from a signal across 150 kHz to 1 GHz.
     - Applies an EMI filter if enabled, reducing EMI by a frequency-dependent factor.
   - **Algorithms and Calculations**:
     - **EMI Spectrum**: Performs FFT on the input signal, computes magnitude in dBµV (\( 20 \cdot \log_{10}(V \cdot 10^6) \)).
     - **Filter Effect**: Reduces EMI by \( 20 \cdot \log_{10}(1 + f / f_0) \) dB, where \( f_0 = 1 \, \text{MHz} \).
     - **Compliance Check**: Compares EMI levels to CISPR 22 limits (e.g., 66–56 dBµV for 150–500 kHz).
   - **Physics Models**:
     - Simplified EMI model based on Fourier transform of switching transients, with filter modeled as a frequency-dependent attenuator.

### 4. **HarmonicAnalysis.py: Harmonic Distortion Analysis**
   - **Functioning**: Computes total harmonic distortion plus noise (THD+N) and harmonic spectra, with export capability.
   - **Simulation Logic**:
     - Analyzes the modulated signal using FFT to compute THD+N and individual harmonic amplitudes (H2–H10).
     - Supports logarithmic scaling and CSV export of harmonic data.
   - **Algorithms and Calculations**:
     - **THD+N**: \( \text{THD+N} = \sqrt{\sum_{n=2}^{10} H_n^2 + \text{noise_power}} / H_1 \cdot 100 \), where \( H_n \) are harmonic amplitudes from FFT, and noise power is computed from residuals.
     - **Harmonic Amplitudes**: \( H_n = \text{FFT}(f_n) / \text{FFT}(f_1) \cdot 100 \), for harmonics 2 to 10.
     - **Spectrum**: Computes THD+N across 20 Hz to 20 kHz using band-pass filtering.
   - **Physics Models**:
     - Standard harmonic analysis model for nonlinear systems, capturing distortion from rectifier and switching components.

### 5. **ImpedanceMatching.py & ImpedanceAnalyzer.py: Impedance Analysis**
   - **Functioning**: Analyzes impedance matching between source and load, computing reflection coefficient, VSWR, return loss, and Smith chart data.
   - **Simulation Logic**:
     - Models source and load impedances with resistive and reactive components.
     - Computes frequency-dependent metrics over 10 Hz to 100 MHz.
   - **Algorithms and Calculations**:
     - **Reflection Coefficient**: \( \Gamma = (Z_L - Z_S^*) / (Z_L + Z_S^*) \), where \( Z_S^* \) is the complex conjugate of source impedance.
     - **VSWR**: \( \text{VSWR} = (1 + |\Gamma|) / (1 - |\Gamma|) \).
     - **Return Loss**: \( \text{RL} = -20 \cdot \log_{10}(|\Gamma|) \).
     - **Input/Output Impedance**: Computes \( Z_{\text{in}} = Z_S + j \cdot 2\pi f \cdot L \) and \( Z_{\text{out}} = Z_L \).
   - **Physics Models**:
     - Standard RF impedance matching model, incorporating complex impedance and transmission line theory.

### 6. **MagneticCoreModeling.py & MagneticCoreAnalyzer.py: Magnetic Core Behavior**
   - **Functioning**: Simulates magnetic core behavior (H-field, B-field, magnetization, saturation) using a simplified Jiles-Atherton model.
   - **Simulation Logic**:
     - Models magnetic fields for materials (Ferrite, Iron Powder, Silicon Steel) based on input current and frequency.
     - Tracks hysteresis loop data for B-H curve plotting.
   - **Algorithms and Calculations**:
     - **H-field**: \( H = I \cdot N / l_e \), where \( N = 100 \), \( l_e = 0.1 \, \text{m} \).
     - **Magnetization**: \( M = M_s \cdot \tanh((H + \alpha \cdot M) / H_c) \), with material-specific parameters (\( M_s, H_c, \alpha \)).
     - **B-field**: \( B = \mu_0 \cdot (H + M) \), where \( \mu_0 = 4\pi \cdot 10^{-7} \, \text{H/m} \).
     - **Saturation**: Clamps \( B \) at material-specific limits (e.g., 0.4 T for Ferrite).
   - **Physics Models**:
     - Simplified Jiles-Atherton model for magnetic hysteresis, capturing nonlinear magnetization and saturation effects.

### 7. **NonlinearDevices.py: Diode and Transistor Modeling**
   - **Functioning**: Models nonlinear behavior of diodes and transistors for rectification and switching.
   - **Simulation Logic**:
     - Computes current based on voltage for diodes and collector current for transistors in active region.
   - **Algorithms and Calculations**:
     - **Diode**: Shockley equation, \( I_D = I_s \cdot (\exp(V_D / V_T) - 1) \), with \( I_s = 10^{-12} \, \text{A} \), \( V_T = 0.025 \, \text{V} \).
     - **Transistor**: Simplified model, \( I_C = \beta \cdot I_B \), with \( \beta = 100 \), and clipping at \( V_{CE} = 0.2 \, \text{V} \).
   - **Physics Models**:
     - Standard semiconductor models for diodes and BJTs, capturing exponential and linear behavior.

### 8. **SNR_Analysis.py: Signal-to-Noise Ratio Analysis**
   - **Functioning**: Computes overall SNR, noise floor, and SNR spectrum across 20 Hz to 20 kHz.
   - **Simulation Logic**:
     - Adds Gaussian noise to the signal and computes power ratios.
     - Analyzes SNR in frequency bands using FFT.
   - **Algorithms and Calculations**:
     - **Overall SNR**: \( \text{SNR} = 10 \cdot \log_{10}(P_{\text{signal}} / P_{\text{noise}}) \), where \( P_{\text{signal}} = \text{mean}(signal^2) \), \( P_{\text{noise}} = \text{mean}(noise^2) \).
     - **Noise Floor**: \( 10 \cdot \log_{10}(P_{\text{noise}}) - 120 \, \text{dB} \), relative to 1 V.
     - **SNR Spectrum**: Computes \( \text{SNR}_f = 10 \cdot \log_{10}(P_{\text{signal},f} / P_{\text{noise},f}) \) for each frequency band, using FFT magnitudes.
   - **Physics Models**:
     - Standard signal processing model for SNR, assuming additive white Gaussian noise.

### 9. **StabilityAnalysis.py: System Stability Analysis**
   - **Functioning**: Analyzes system stability using Bode, Nyquist, and root locus plots based on filter and regulator transfer functions.
   - **Simulation Logic**:
     - Constructs transfer functions for capacitive, inductive, or active filters, including regulator effects.
     - Updates plots for frequencies from 1 Hz to 100 kHz.
   - **Algorithms and Calculations**:
     - **Transfer Functions**:
       - Capacitive: \( H(s) = 1 / (s \cdot R \cdot C + 1) \).
       - Inductive: \( H(s) = 1 / (s \cdot L / R + 1) \).
       - Active: \( H(s) = A / (s \cdot \tau + 1) \), with regulator gain adjustments.
     - **Bode Plot**: Uses `scipy.signal.bode` to compute magnitude (\( 20 \cdot \log_{10}|H(j\omega)| \)) and phase (\( \angle H(j\omega) \)).
     - **Nyquist Plot**: Computes frequency response (\( H(j\omega) \)) and plots real vs. imaginary parts, marking the -1 point.
     - **Root Locus**: Uses `control.root_locus_map` to plot pole trajectories for gain variations (0 to 100).
   - **Physics Models**:
     - Linear control theory for filter and regulator dynamics, assuming small-signal behavior.

### 10. **SwitchingDeviceModeling.py: Switching Device Behavior**
   - **Functioning**: Models transient and steady-state behavior of switching devices (MOSFET, IGBT, GaN, SiC) in a buck converter-like setup.
   - **Simulation Logic**:
     - Simulates gate voltage, drain-source voltage, and power loss over a 1 ms window.
     - Computes conduction and switching losses, efficiency, and junction temperature.
   - **Algorithms and Calculations**:
     - **Transients**:
       - Gate voltage: \( V_g(t) = V_{\text{gate}} \cdot (1 - \exp(-t / (R_g \cdot C_g))) \) during turn-on, and \( V_g(t) = V_{\text{gate}} \cdot \exp(-t / (R_g \cdot C_g)) \) during turn-off.
       - Drain-source voltage and current: Linear ramps during \( t_{\text{on}} \) and \( t_{\text{off}} \).
       - Power loss: \( P_{\text{loss}}(t) = V_{DS}(t) \cdot I_{DS}(t) \).
     - **Metrics**:
       - Conduction loss: \( P_{\text{cond}} = I_{\text{load}}^2 \cdot R_{\text{on}} \cdot D \).
       - Switching loss: \( P_{\text{sw}} = 0.5 \cdot V_{\text{supply}} \cdot I_{\text{load}} \cdot (t_{\text{on}} + t_{\text{off}}) \cdot f_{\text{sw}} \).
       - Efficiency: \( \eta = P_{\text{out}} / (P_{\text{out}} + P_{\text{total}}) \cdot 100 \), where \( P_{\text{out}} = V_{\text{supply}} \cdot I_{\text{load}} \cdot D \).
       - Junction temperature: \( T_j = T_{\text{amb}} + P_{\text{total}} \cdot R_{\text{thJA}} \).
   - **Physics Models**:
     - Simplified switching model with RC gate dynamics and linear transient approximations.
     - Thermal model based on steady-state power dissipation.

### 11. **THD_Analysis.py: Total Harmonic Distortion Analysis**
   - **Functioning**: Computes THD and individual harmonic amplitudes (H2–H10) for the modulated signal, plus THD across 100 Hz to 10 kHz.
   - **Simulation Logic**:
     - Uses FFT to extract fundamental and harmonic components.
     - Analyzes THD in frequency bands for spectral distortion.
   - **Algorithms and Calculations**:
     - **THD**: \( \text{THD} = \sqrt{\sum_{n=2}^{10} H_n^2} / H_1 \cdot 100 \), where \( H_n = |\text{FFT}(f_n)| \).
     - **Harmonics**: \( H_n = |\text{FFT}(n \cdot f_0)| / |\text{FFT}(f_0)| \cdot 100 \).
     - **THD vs. Frequency**: Computes THD for each band as \( \text{THD}_f = \sqrt{\sum_{n=2}^{10} H_{n,f}^2} / H_{1,f} \cdot 100 \).
   - **Physics Models**:
     - Fourier-based distortion analysis for nonlinear systems.

### 12. **ThermalModeling.py: Component Thermal Analysis**
   - **Functioning**: Simulates thermal behavior of diode, MOSFET, and system, accounting for power dissipation and thermal coupling.
   - **Simulation Logic**:
     - Computes power dissipation from receiver waveforms.
     - Updates temperatures using an RC thermal model, synchronized with the 0.1-second simulation window.
   - **Algorithms and Calculations**:
     - **Power Dissipation**:
       - Diode: \( P_{\text{diode}} = I_{\text{diode}} \cdot V_{\text{drop}} \), where \( I_{\text{diode}} = V_{\text{rectified}} / 100 \), \( V_{\text{drop}} = 0.7 \, \text{V} \).
       - MOSFET: \( P_{\text{MOSFET}} = I_{\text{MOSFET}}^2 \cdot R_{\text{DS(on)}} \), where \( I_{\text{MOSFET}} = |V_{\text{modulated}}| / 50 \), \( R_{\text{DS(on)}} = 0.1 \, \Omega \).
     - **Temperature Update**:
       - Diode: \( \Delta T_{\text{diode}} = \frac{dt}{C_{\text{th,diode}}} \cdot (P_{\text{diode}} \cdot R_{\text{th,diode}} + k \cdot (T_{\text{MOSFET}} - T_{\text{diode}}) - (T_{\text{diode}} - T_{\text{amb}})) \).
       - MOSFET: Similar, with \( C_{\text{th,MOSFET}} \), \( R_{\text{th,MOSFET}} \).
       - System: \( T_{\text{system}} = (T_{\text{diode}} + T_{\text{MOSFET}}) / 2 \).
     - **Thermal Coupling**: \( k = 0.2 \) models heat transfer between components.
   - **Physics Models**:
     - First-order RC thermal model with thermal resistance (\( R_{\text{th}} \)) and capacitance (\( C_{\text{th}} \)).
     - Simplified thermal coupling for component interaction.

### 13. **WaveformDisplay.py: Signal Waveform Generation**
   - **Functioning**: Generates and processes waveforms (AC, rectified, modulated) for analysis.
   - **Simulation Logic**:
     - Calls `ReceiverModel.generate_waveform` to produce signals over a 0.01-second window.
     - Supports analog, digital, or mixed signal modes.
   - **Algorithms and Calculations**:
     - Delegates waveform generation to `ReceiverModel`, ensuring consistency with the main simulation.
   - **Physics Models**:
     - Relies on `ReceiverModel` physics for signal generation.

### 14. **Main.py: System Integration and Simulation Loop**
   - **Functioning**: Integrates all components (ReceiverModel, analyzers) into a cohesive simulation, managing real-time updates and analysis modes.
   - **Simulation Logic**:
     - Runs a 50 ms update loop via QTimer, generating waveforms and updating analyzers.
     - Supports transient, steady-state, and frequency analysis modes.
     - Injects noise for SNR analysis if enabled.
   - **Algorithms and Calculations**:
     - **Waveform Generation**: Calls `ReceiverModel.generate_waveform` for AC, rectified, and modulated signals.
     - **Noise Injection**: Adds Gaussian noise (\( N(0, \sigma) \)) to the modulated signal for SNR analysis.
     - **Analyzer Updates**:
       - HarmonicAnalyzer: Updates THD+N and harmonic spectra.
       - PowerFactorCorrection: Computes and corrects PF.
       - SNRAnalyzer: Computes SNR and noise floor.
       - THDAnalyzer: Computes THD and harmonics.
       - EMIAnalyzer: Analyzes EMI spectrum.
       - ThermalAnalyzer: Updates component temperatures.
       - StabilityAnalyzer: Updates stability plots.
   - **Physics Models**:
     - Orchestrates all physics models from individual components, ensuring synchronized simulation.
