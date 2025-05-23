from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class ControlPanel(QWidget):
    parameters_changed = pyqtSignal()
    
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #C0C0C0;
                border: 3px outset #A0A0A0;
                padding: 15px;
            }
            QSlider {
                border: 3px inset #A0A0A0;
                background-color: #D0D0D0;
                height: 30px;
            }
            QPushButton {
                border: 3px outset #A0A0A0;
                background-color: #D0D0D0;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 14pt;
                min-width: 100px;
                min-height: 40px;
            }
            QPushButton:pressed {
                border: 3px inset #A0A0A0;
                background-color: #B0B0B0;
            }
            QComboBox {
                border: 3px inset #A0A0A0;
                background-color: #D0D0D0;
                font-family: 'Courier New';
                font-size: 14pt;
                padding: 5px;
            }
            QLabel {
                font-family: 'Courier New';
                font-size: 14pt;
                color: #000000;
                min-width: 150px;
            }
        """)
        
        # Frequency control
        freq_layout = QHBoxLayout()
        freq_layout.setSpacing(15)
        freq_label = QLabel("Frequency (Hz):")
        self.freq_value = QLabel("1000")
        self.freq_slider = QSlider(Qt.Horizontal)
        self.freq_slider.setRange(100, 10000)
        self.freq_slider.setValue(1000)
        self.freq_slider.setMinimumWidth(300)
        self.freq_slider.valueChanged.connect(self.update_frequency)
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_slider)
        freq_layout.addWidget(self.freq_value)
        layout.addLayout(freq_layout)
        
        # Gain control
        gain_layout = QHBoxLayout()
        gain_layout.setSpacing(15)
        gain_label = QLabel("Gain (dB):")
        self.gain_value = QLabel("0")
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(-20, 20)
        self.gain_slider.setValue(0)
        self.gain_slider.setMinimumWidth(300)
        self.gain_slider.valueChanged.connect(self.update_gain)
        gain_layout.addWidget(gain_label)
        gain_layout.addWidget(self.gain_slider)
        gain_layout.addWidget(self.gain_value)
        layout.addLayout(gain_layout)
        
        # Modulation control
        mod_layout = QHBoxLayout()
        mod_layout.setSpacing(15)
        mod_label = QLabel("Modulation:")
        self.mod_button_am = QPushButton("AM")
        self.mod_button_fm = QPushButton("FM")
        self.mod_button_am.setCheckable(True)
        self.mod_button_fm.setCheckable(True)
        self.mod_button_am.clicked.connect(lambda: self.update_modulation("AM"))
        self.mod_button_fm.clicked.connect(lambda: self.update_modulation("FM"))
        mod_layout.addWidget(mod_label)
        mod_layout.addWidget(self.mod_button_am)
        mod_layout.addWidget(self.mod_button_fm)
        mod_layout.addStretch()
        layout.addLayout(mod_layout)
        
        # ADC Resolution control
        adc_layout = QHBoxLayout()
        adc_layout.setSpacing(15)
        adc_label = QLabel("ADC Resolution (bits):")
        self.adc_value = QLabel("8")
        self.adc_slider = QSlider(Qt.Horizontal)
        self.adc_slider.setRange(4, 16)
        self.adc_slider.setValue(8)
        self.adc_slider.setMinimumWidth(300)
        self.adc_slider.valueChanged.connect(self.update_adc_resolution)
        adc_layout.addWidget(adc_label)
        adc_layout.addWidget(self.adc_slider)
        adc_layout.addWidget(self.adc_value)
        layout.addLayout(adc_layout)
        
        # Analysis mode control
        analysis_layout = QHBoxLayout()
        analysis_layout.setSpacing(15)
        analysis_label = QLabel("Analysis Mode:")
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems(["Transient", "Steady-State", "Frequency"])
        self.analysis_combo.currentTextChanged.connect(self.update_analysis_mode)
        analysis_layout.addWidget(analysis_label)
        analysis_layout.addWidget(self.analysis_combo)
        analysis_layout.addStretch()
        layout.addLayout(analysis_layout)
        
        # Power button
        self.power_button = QPushButton("Power")
        self.power_button.setCheckable(True)
        self.power_button.clicked.connect(self.toggle_power)
        layout.addWidget(self.power_button)
        
        layout.addStretch()
    
    def update_frequency(self, value):
        self.model.set_frequency(value)
        self.freq_value.setText(str(value))
        self.parameters_changed.emit()
    
    def update_gain(self, value):
        self.model.set_gain(value)
        self.gain_value.setText(str(value))
        self.parameters_changed.emit()
    
    def update_modulation(self, mod_type):
        self.model.set_modulation(mod_type)
        self.mod_button_am.setChecked(mod_type == "AM")
        self.mod_button_fm.setChecked(mod_type == "FM")
        self.parameters_changed.emit()
    
    def update_adc_resolution(self, value):
        self.model.adc_resolution = value
        self.adc_value.setText(str(value))
        self.parameters_changed.emit()
    
    def update_analysis_mode(self, mode):
        mode_map = {"Transient": "transient", "Steady-State": "steady_state", "Frequency": "frequency"}
        self.model.set_analysis_mode(mode_map[mode])
        self.parameters_changed.emit()
    
    def toggle_power(self):
        self.model.set_power(self.power_button.isChecked())
        self.parameters_changed.emit()