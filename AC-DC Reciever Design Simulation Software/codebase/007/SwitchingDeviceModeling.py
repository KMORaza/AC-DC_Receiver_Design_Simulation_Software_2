import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QComboBox, QGridLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QDoubleValidator

class SwitchingDeviceModel:
    def __init__(self):
        self.device_type = "MOSFET"
        self.params = {
            "MOSFET": {"V_th": 2.0, "R_on": 0.1, "C_g": 1000e-12, "t_on": 50e-9, "t_off": 50e-9, "V_br": 600, "R_thJA": 50},
            "IGBT": {"V_th": 4.0, "R_on": 0.2, "C_g": 2000e-12, "t_on": 100e-9, "t_off": 100e-9, "V_br": 1200, "R_thJA": 40},
            "GaN": {"V_th": 1.5, "R_on": 0.05, "C_g": 500e-12, "t_on": 20e-9, "t_off": 20e-9, "V_br": 650, "R_thJA": 30},
            "SiC": {"V_th": 2.5, "R_on": 0.08, "C_g": 800e-12, "t_on": 30e-9, "t_off": 30e-9, "V_br": 1200, "R_thJA": 35}
        }
        self.f_sw = 10000  # Hz
        self.I_load = 1.0  # A
        self.V_supply = 100.0  # V
        self.duty_cycle = 0.5
        self.T_amb = 25.0  # °C

    def set_device_type(self, device_type):
        self.device_type = device_type

    def set_parameters(self, V_th=None, R_on=None, C_g=None, t_on=None, t_off=None, V_br=None):
        if V_th is not None:
            self.params[self.device_type]["V_th"] = V_th
        if R_on is not None:
            self.params[self.device_type]["R_on"] = R_on
        if C_g is not None:
            self.params[self.device_type]["C_g"] = C_g
        if t_on is not None:
            self.params[self.device_type]["t_on"] = t_on
        if t_off is not None:
            self.params[self.device_type]["t_off"] = t_off
        if V_br is not None:
            self.params[self.device_type]["V_br"] = V_br

    def set_operating_conditions(self, f_sw=None, I_load=None, V_supply=None):
        if f_sw is not None:
            self.f_sw = f_sw
        if I_load is not None:
            self.I_load = I_load
        if V_supply is not None:
            self.V_supply = V_supply

    def compute_transients(self):
        t = np.linspace(0, 1e-3, 1000)  # 1 ms window
        T = 1 / self.f_sw
        V_g = np.zeros_like(t)
        V_ds = np.zeros_like(t)
        I_ds = np.zeros_like(t)
        P_loss = np.zeros_like(t)

        params = self.params[self.device_type]
        V_th = params["V_th"]
        R_on = params["R_on"]
        C_g = params["C_g"]
        t_on = params["t_on"]
        t_off = params["t_off"]
        R_g = 10.0  # Gate resistance (Ω)
        V_gate = 10.0  # Gate drive voltage

        for i, ti in enumerate(t):
            t_cycle = ti % T
            if t_cycle < self.duty_cycle * T:
                # On-state
                if t_cycle < t_on:
                    # Turn-on transient
                    tau = R_g * C_g
                    V_g[i] = V_gate * (1 - np.exp(-t_cycle / tau))
                    V_ds[i] = self.V_supply * (1 - t_cycle / t_on)
                    I_ds[i] = self.I_load * (t_cycle / t_on)
                else:
                    # Fully on
                    V_g[i] = V_gate
                    V_ds[i] = self.I_load * R_on
                    I_ds[i] = self.I_load
            else:
                # Off-state
                if t_cycle < (self.duty_cycle * T + t_off):
                    # Turn-off transient
                    t_off_phase = t_cycle - self.duty_cycle * T
                    tau = R_g * C_g
                    V_g[i] = V_gate * np.exp(-t_off_phase / tau)
                    V_ds[i] = self.V_supply * (t_off_phase / t_off)
                    I_ds[i] = self.I_load * (1 - t_off_phase / t_off)
                else:
                    # Fully off
                    V_g[i] = 0
                    V_ds[i] = self.V_supply
                    I_ds[i] = 0
            P_loss[i] = V_ds[i] * I_ds[i]  # Instantaneous power loss

        return t, V_g, V_ds, P_loss

    def compute_metrics(self):
        params = self.params[self.device_type]
        R_on = params["R_on"]
        t_on = params["t_on"]
        t_off = params["t_off"]
        R_thJA = params["R_thJA"]

        P_cond = self.I_load**2 * R_on * self.duty_cycle
        P_sw = 0.5 * self.V_supply * self.I_load * (t_on + t_off) * self.f_sw
        P_total = P_cond + P_sw
        P_out = self.V_supply * self.I_load * self.duty_cycle
        efficiency = P_out / (P_out + P_total) * 100 if P_out + P_total > 0 else 100
        T_j = self.T_amb + P_total * R_thJA

        return {
            "P_cond": P_cond,
            "P_sw": P_sw,
            "P_total": P_total,
            "efficiency": efficiency,
            "T_j": T_j
        }

class SwitchingDeviceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model = SwitchingDeviceModel()
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(50)

    def init_ui(self):
        self.setWindowTitle("Switching Device Modeling")
        self.setGeometry(200, 200, 800, 600)

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Control Panel
        control_widget = QWidget()
        control_layout = QVBoxLayout()

        # Device Selection
        device_group = QGroupBox("DEVICE SELECTION")
        device_group.setObjectName("panel")
        device_layout = QHBoxLayout()
        self.device_combo = QComboBox()
        self.device_combo.addItems(["MOSFET", "IGBT", "GaN", "SiC"])
        self.device_combo.currentTextChanged.connect(self.update_device_type)
        device_layout.addWidget(self.device_combo)
        device_group.setLayout(device_layout)
        control_layout.addWidget(device_group)

        # Device Parameters
        params_group = QGroupBox("DEVICE PARAMETERS")
        params_group.setObjectName("panel")
        params_layout = QGridLayout()
        self.v_th_input = QLineEdit("2.0")
        self.v_th_input.setValidator(QDoubleValidator(0.0, 5.0, 2))
        self.v_th_input.textChanged.connect(self.update_parameters)
        self.r_on_input = QLineEdit("0.1")
        self.r_on_input.setValidator(QDoubleValidator(0.01, 1.0, 3))
        self.r_on_input.textChanged.connect(self.update_parameters)
        self.c_g_input = QLineEdit("1000")
        self.c_g_input.setValidator(QDoubleValidator(100, 5000, 0))
        self.c_g_input.textChanged.connect(self.update_parameters)
        self.t_on_input = QLineEdit("50")
        self.t_on_input.setValidator(QDoubleValidator(10, 500, 0))
        self.t_on_input.textChanged.connect(self.update_parameters)
        self.t_off_input = QLineEdit("50")
        self.t_off_input.setValidator(QDoubleValidator(10, 500, 0))
        self.t_off_input.textChanged.connect(self.update_parameters)
        self.v_br_input = QLineEdit("600")
        self.v_br_input.setValidator(QDoubleValidator(100, 2000, 0))
        self.v_br_input.textChanged.connect(self.update_parameters)

        params_layout.addWidget(QLabel("V_th (V):").setObjectName("led-label"), 0, 0)
        params_layout.addWidget(self.v_th_input, 0, 1)
        params_layout.addWidget(QLabel("R_on (Ω):").setObjectName("led-label"), 1, 0)
        params_layout.addWidget(self.r_on_input, 1, 1)
        params_layout.addWidget(QLabel("C_g (pF):").setObjectName("led-label"), 2, 0)
        params_layout.addWidget(self.c_g_input, 2, 1)
        params_layout.addWidget(QLabel("t_on (ns):").setObjectName("led-label"), 3, 0)
        params_layout.addWidget(self.t_on_input, 3, 1)
        params_layout.addWidget(QLabel("t_off (ns):").setObjectName("led-label"), 4, 0)
        params_layout.addWidget(self.t_off_input, 4, 1)
        params_layout.addWidget(QLabel("V_br (V):").setObjectName("led-label"), 5, 0)
        params_layout.addWidget(self.v_br_input, 5, 1)
        params_group.setLayout(params_layout)
        control_layout.addWidget(params_group)

        # Operating Conditions
        cond_group = QGroupBox("OPERATING CONDITIONS")
        cond_group.setObjectName("panel")
        cond_layout = QGridLayout()
        self.f_sw_input = QLineEdit("10000")
        self.f_sw_input.setValidator(QDoubleValidator(1000, 100000, 0))
        self.f_sw_input.textChanged.connect(self.update_conditions)
        self.i_load_input = QLineEdit("1.0")
        self.i_load_input.setValidator(QDoubleValidator(0.0, 10.0, 2))
        self.i_load_input.textChanged.connect(self.update_conditions)
        self.v_supply_input = QLineEdit("100.0")
        self.v_supply_input.setValidator(QDoubleValidator(0.0, 600.0, 1))
        self.v_supply_input.textChanged.connect(self.update_conditions)

        cond_layout.addWidget(QLabel("f_sw (Hz):").setObjectName("led-label"), 0, 0)
        cond_layout.addWidget(self.f_sw_input, 0, 1)
        cond_layout.addWidget(QLabel("I_load (A):").setObjectName("led-label"), 1, 0)
        cond_layout.addWidget(self.i_load_input, 1, 1)
        cond_layout.addWidget(QLabel("V_supply (V):").setObjectName("led-label"), 2, 0)
        cond_layout.addWidget(self.v_supply_input, 2, 1)
        cond_group.setLayout(cond_layout)
        control_layout.addWidget(cond_group)

        # Metrics Display
        metrics_group = QGroupBox("METRICS")
        metrics_group.setObjectName("panel")
        metrics_layout = QGridLayout()
        self.p_cond_label = QLabel("P_COND: 0.00 W")
        self.p_cond_label.setObjectName("led-display")
        self.p_sw_label = QLabel("P_SW: 0.00 W")
        self.p_sw_label.setObjectName("led-display")
        self.p_total_label = QLabel("P_TOTAL: 0.00 W")
        self.p_total_label.setObjectName("led-display")
        self.eff_label = QLabel("EFF: 100.00 %")
        self.eff_label.setObjectName("led-display")
        self.t_j_label = QLabel("T_J: 25.00 °C")
        self.t_j_label.setObjectName("led-display")

        metrics_layout.addWidget(QLabel("P_COND:").setObjectName("led-label"), 0, 0)
        metrics_layout.addWidget(self.p_cond_label, 0, 1)
        metrics_layout.addWidget(QLabel("P_SW:").setObjectName("led-label"), 1, 0)
        metrics_layout.addWidget(self.p_sw_label, 1, 1)
        metrics_layout.addWidget(QLabel("P_TOTAL:").setObjectName("led-label"), 2, 0)
        metrics_layout.addWidget(self.p_total_label, 2, 1)
        metrics_layout.addWidget(QLabel("EFF:").setObjectName("led-label"), 3, 0)
        metrics_layout.addWidget(self.eff_label, 3, 1)
        metrics_layout.addWidget(QLabel("T_J:").setObjectName("led-label"), 4, 0)
        metrics_layout.addWidget(self.t_j_label, 4, 1)
        metrics_group.setLayout(metrics_layout)
        control_layout.addWidget(metrics_group)

        control_layout.addStretch()
        control_widget.setLayout(control_layout)
        main_layout.addWidget(control_widget)

        # Plot Panel
        plot_widget = QWidget()
        plot_layout = QVBoxLayout()

        self.v_g_plot = pg.PlotWidget()
        self.v_g_plot.setBackground("#0A0A0A")
        self.v_g_plot.setTitle("Gate Voltage", color="#FFFF99", size="12pt")
        self.v_g_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.v_g_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.v_g_plot.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.v_g_plot)

        self.v_ds_plot = pg.PlotWidget()
        self.v_ds_plot.setBackground("#0A0A0A")
        self.v_ds_plot.setTitle("Drain-Source Voltage", color="#FFFF99", size="12pt")
        self.v_ds_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.v_ds_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.v_ds_plot.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.v_ds_plot)

        self.p_loss_plot = pg.PlotWidget()
        self.p_loss_plot.setBackground("#0A0A0A")
        self.p_loss_plot.setTitle("Power Loss", color="#FFFF99", size="12pt")
        self.p_loss_plot.getAxis("left").setPen({"color": "#FFFF99", "width": 2})
        self.p_loss_plot.getAxis("bottom").setPen({"color": "#FFFF99", "width": 2})
        self.p_loss_plot.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.p_loss_plot)

        plot_widget.setLayout(plot_layout)
        main_layout.addWidget(plot_widget)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        main_widget.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: 'Courier New';
            }
            QGroupBox#panel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4A4A4A, stop:1 #2E2E2E);
                border: 3px outset #5C5C5C;
                border-radius: 5px;
                margin-top: 15px;
                padding: 10px;
                font: bold 12pt 'Courier New';
                color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #5C5C5C, stop:1 #3A3A3A);
                border: 2px outset #5C5C5C;
                border-radius: 3px;
                color: #FFFFFF;
                font: bold 12pt 'Courier New';
            }
            QLineEdit, QComboBox {
                background: #1A1A1A;
                border: 2px inset #5C5C5C;
                border-radius: 3px;
                padding: 4px;
                color: #FFFF99;
                font: 12pt 'Courier New';
            }
            QComboBox::drop-down {
                border: 2px outset #5C5C5C;
                background: #3A3A3A;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
            }
            QLabel#led-label {
                background: transparent;
                color: #FFFFFF;
                font: bold 12pt 'Courier New';
            }
            QLabel#led-display {
                background: #1A1A1A;
                border: 2px inset #5C5C5C;
                border-radius: 3px;
                padding: 4px;
                color: #FFFF99;
                font: 12pt 'Courier New';
            }
        """)

    def update_device_type(self, device_type):
        self.model.set_device_type(device_type)
        params = self.model.params[device_type]
        self.v_th_input.setText(f"{params['V_th']:.2f}")
        self.r_on_input.setText(f"{params['R_on']:.3f}")
        self.c_g_input.setText(f"{params['C_g']*1e12:.0f}")
        self.t_on_input.setText(f"{params['t_on']*1e9:.0f}")
        self.t_off_input.setText(f"{params['t_off']*1e9:.0f}")
        self.v_br_input.setText(f"{params['V_br']:.0f}")
        self.update_plots()

    def update_parameters(self):
        try:
            V_th = float(self.v_th_input.text())
            R_on = float(self.r_on_input.text())
            C_g = float(self.c_g_input.text()) * 1e-12
            t_on = float(self.t_on_input.text()) * 1e-9
            t_off = float(self.t_off_input.text()) * 1e-9
            V_br = float(self.v_br_input.text())
            self.model.set_parameters(V_th, R_on, C_g, t_on, t_off, V_br)
            self.update_plots()
        except ValueError:
            pass

    def update_conditions(self):
        try:
            f_sw = float(self.f_sw_input.text())
            I_load = float(self.i_load_input.text())
            V_supply = float(self.v_supply_input.text())
            self.model.set_operating_conditions(f_sw, I_load, V_supply)
            self.update_plots()
        except ValueError:
            pass

    def update_plots(self):
        t, V_g, V_ds, P_loss = self.model.compute_transients()
        metrics = self.model.compute_metrics()

        self.v_g_plot.clear()
        self.v_g_plot.plot(t*1e3, V_g, pen=pg.mkPen(color="#FFFF99", width=2))
        self.v_g_plot.setLabel("left", "V_g (V)")
        self.v_g_plot.setLabel("bottom", "Time (ms)")

        self.v_ds_plot.clear()
        self.v_ds_plot.plot(t*1e3, V_ds, pen=pg.mkPen(color="#FFFF99", width=2))
        self.v_ds_plot.setLabel("left", "V_ds (V)")
        self.v_ds_plot.setLabel("bottom", "Time (ms)")

        self.p_loss_plot.clear()
        self.p_loss_plot.plot(t*1e3, P_loss, pen=pg.mkPen(color="#FFFF99", width=2))
        self.p_loss_plot.setLabel("left", "Power Loss (W)")
        self.p_loss_plot.setLabel("bottom", "Time (ms)")

        self.p_cond_label.setText(f"P_COND: {metrics['P_cond']:.2f} W")
        self.p_sw_label.setText(f"P_SW: {metrics['P_sw']:.2f} W")
        self.p_total_label.setText(f"P_TOTAL: {metrics['P_total']:.2f} W")
        self.eff_label.setText(f"EFF: {metrics['efficiency']:.2f} %")
        self.t_j_label.setText(f"T_J: {metrics['T_j']:.2f} °C")