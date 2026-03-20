# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\core\parameters.py
"""
Values here should be a starting point and safe for all lasers.

TODO: Note that setting the max currents at 1mA is good for safety, however after changing this in the parameters window the limits of the spin boxes need to be updated.
"""
DELAYS = {
 'loop': 1, 
 'hold_loop': 5, 
 'pre_replicate': 0.1, 
 'post_move_filter': 0.5, 
 'post_move_piezo': 0.5, 
 'post_current_change': 3.0, 
 'post_small_current_change': 0.5, 
 'post_start_piezo_scan': 0.2, 
 'post_fzw_error': 1.0, 
 'post_cem_error': 1.0, 
 'unstable_modes': 2, 
 'post_TEC_turn_on': 10.0}
MODE_DETECTION = {
 'n_derivative': 32, 
 'n_std': 32, 
 'n_join': 1, 
 'max_derivative': 0.3, 
 'max_std': 0.3, 
 'min_mode_width': 0.1, 
 'max_diff_area': 25, 
 'diode_mode_width_GHz': 25}
CALIBRATION = {
 'default_current_mA': 160, 
 'current_step_mA': 5, 
 'n_steps': 3, 
 'encoder_step': 10, 
 'n_replicates': 3, 
 'scan_width': 0.5, 
 'bias_mA': 0.0, 
 'offset': 0.0, 
 'modulation': '"+Ramp"', 
 'min_mode_width': 0.05, 
 'frequency_threshold_GHz': 30, 
 'max_bare_diode_current_mA': 1, 
 'max_laser_current_mA': 1}
LASER_TUNING = {
 'frequency_threshold_MHz': 500, 
 'default_current_mA': 162, 
 'min_current_mA': 124, 
 'max_current_mA': 200, 
 'current_step_mA': 2, 
 'current_step_fine_mA': 0.5, 
 'n_steps': 11, 
 'n_steps_fine': 5, 
 'bias_mA': 70, 
 'slow_bias_mA': 70, 
 'offset': 0.0, 
 'scan_width': 0.3, 
 'slow_scan_width': 0.1, 
 'scan_width_max': 0.5, 
 'tuning_range_ticks': 25, 
 'step_size': 5, 
 'step_size_fine': 1}
SPECTROSCOPY = {
 'direction': '"up"', 
 'scan_frequency_Hz_fast': 1, 
 'scan_frequency_Hz_medium': 0.1, 
 'scan_frequency_Hz_slow': 0.01, 
 'scan_frequency_offset_THz': 0, 
 'n_periods': 1.5, 
 'filter_position_step_size': 3, 
 'min_mode_width': 0.2, 
 'tuning_scan_width': 0.5, 
 'scan_width': 0.5, 
 'offset': 0.0, 
 'filter_position_shift_on_error': 1, 
 'set_frequency_GHz_shift_on_error': 1, 
 'bias_mA': 30}

def initial_parameters():
    return {
     'delays': DELAYS, 
     'mode_detection': MODE_DETECTION, 
     'calibration': CALIBRATION, 
     'laser_tuning': LASER_TUNING, 
     'spectroscopy': SPECTROSCOPY}

# okay decompiling cem/core/parameters.pyc
