import numpy as np
from PyQt5.QtWidgets import QWidget
import pyqtgraph as pg

class WaveformDisplay(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.init_ui()
    
    def init_ui(self):
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#C0C0C0')
        self.plot_widget.setTitle("Signal Waveform", color='#000000', size='16pt')
        self.plot_widget.setLabel('left', 'Amplitude', units='V', color='#000000', size='14pt')
        self.plot_widget.setLabel('bottom', 'Time', units='s', color='#000000', size='14pt')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setMinimumSize(600, 500)  # Larger plot area
        
        # 90s-style stylesheet
        self.setStyleSheet("""
            QWidget {
                border: 3px outset #A0A0A0;
                background-color: #C0C0C0;
                padding: 15px;
            }
        """)
        
        # Create layout
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Larger margins
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)
        
        # Initial plot
        self.update_plot()
    
    def update_plot(self):
        if not self.model.power:
            self.plot_widget.clear()
            return
        
        t = np.linspace(0, 0.01, 1000)
        signal = self.model.generate_signal(t)
        self.plot_widget.clear()
        self.plot_widget.plot(t, signal, pen=pg.mkPen(color='#000000', width=3))