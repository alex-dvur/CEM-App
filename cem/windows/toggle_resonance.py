# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\windows\toggle_resonance.py
import logging
try:
    from PySide2 import QtWidgets
except ImportError:
    from PySide6 import QtWidgets
import mogui as ui
from cem.style import font_1
from cem.utils.typing import *
logger = logging.getLogger(__name__)

class ToggleResonance(ui.MOGDialog):

    def __init__(self, worker, parent=None):
        super(ToggleResonance, self).__init__("Toggle resonance", parent=parent)
        self.cem_app = parent
        self.worker = worker
        self.setFixedWidth(800)
        self.setFont(font_1)
        vb = QtWidgets.QVBoxLayout(self)
        grid = QtWidgets.QGridLayout()
        vb.addLayout(grid)
        self.on_resonance_frequency_THz = ui.DblSpinner(min=1, max=999, decimals=6, step=0.1, units="THz", default=385)
        self.on_resonance_frequency_THz.setFixedHeight(31)
        grid.addWidget(QtWidgets.QLabel("On resonance frequency:"), 0, 0)
        grid.addWidget(self.on_resonance_frequency_THz, 0, 1)
        self.off_resonance_frequency_THz = ui.DblSpinner(min=2, max=999, decimals=6, step=0.1, units="THz", default=385.1)
        self.off_resonance_frequency_THz.setFixedHeight(31)
        grid.addWidget(QtWidgets.QLabel("Off resonance frequency:"), 1, 0)
        grid.addWidget(self.off_resonance_frequency_THz, 1, 1)
        self.btn_jump_on_resonance = ui.PushButton("Jump on")
        self.btn_jump_on_resonance.setFixedHeight(41)
        self.btn_jump_on_resonance.setStyleSheet("background-color: #00dd00; color: #000000")
        self.btn_jump_on_resonance.setFont(font_1)
        self.btn_jump_on_resonance.pressed.connect(self.jump_on_resonance)
        self.btn_jump_off_resonance = ui.PushButton("Jump off")
        self.btn_jump_off_resonance.setFixedHeight(41)
        self.btn_jump_off_resonance.setStyleSheet("background-color: #ffff00; color: #000000")
        self.btn_jump_off_resonance.setFont(font_1)
        self.btn_jump_off_resonance.pressed.connect(self.jump_off_resonance)
        grid.addWidget(self.btn_jump_on_resonance, 2, 0)
        grid.addWidget(self.btn_jump_off_resonance, 2, 1)
        self.jump_on_current_parameters = QtWidgets.QCheckBox("Use current laser state as on resonance target.")
        self.jump_on_current_parameters.setChecked(False)
        self.jump_on_current_parameters.stateChanged.connect(self.checkBoxState)
        grid.addWidget(self.jump_on_current_parameters, 0, 2)
        self.setFocus()

    def checkBoxState(self):
        if self.jump_on_current_parameters.isChecked():
            self.on_resonance_frequency_THz.setReadOnly(True)
            f = self.worker.get.frequency()
            self.worker.algorithms.previous_on_resonance_frequency = f
            self.on_resonance_frequency_THz.setValue(f)
            self.worker.algorithms.resonance_filter_position = self.worker.get.filter_position()[0]
        else:
            self.on_resonance_frequency_THz.setReadOnly(False)

    @ui.wrap_except
    def jump_on_resonance(self):
        self.worker.queue((self.worker.algorithms.toggle_resonance), on_resonance_frequency_THz=(self.on_resonance_frequency_THz.value()),
          off_resonance_frequency_THz=(self.off_resonance_frequency_THz.value()),
          on_resonance=True,
          debug=(self.cem_app.mog))

    @ui.wrap_except
    def jump_off_resonance(self):
        self.worker.queue((self.worker.algorithms.toggle_resonance), on_resonance_frequency_THz=(self.on_resonance_frequency_THz.value()),
          off_resonance_frequency_THz=(self.off_resonance_frequency_THz.value()),
          on_resonance=False,
          debug=(self.cem_app.mog))

# okay decompiling cem/windows/toggle_resonance.pyc
