# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: cem\core\single_mode_finder.py
import numpy as np

class _GaussDerivative:
    n = None
    s = None
    y = None

    @staticmethod
    def update(n, s=0.5):
        if _GaussDerivative.n == n:
            if _GaussDerivative.s == s:
                if _GaussDerivative.y:
                    return
        x = np.linspace(-1, 1, 2 * n + 1)
        y = np.exp(-(x * x) / (s * s)) * x
        y /= s * np.sqrt(2 * np.pi) * s * s
        y /= np.sum(np.abs(y))
        _GaussDerivative.y = y


def download_photodiode_scan(dev):
    """
    Download photodiode scan data from B1052-CEM.
    The ADC has 12 bit resolution.

    Keyword arguments:
        dev: Serial device

    return:
        ext_pd (ndarray): External photodiode data
        ext_pd (ndarray): Internal photodiode data
    """
    raw = dev.ask_bin("PD,SCAN,1")
    return np.frombuffer(raw, "<u2").astype(float).reshape((-1, 2)).T


def _smooth_derivative(data_in, n_derivative):
    """
    Performs a combined smoothing and derivative operation through a convolution.
    The start and end of the convolution is filled up with zeros to return an array with the same length as the input.

    Keyword arguments:
        data_in ():
        n_derivative (int): Width of the smoothing

    return:
        ndarray: smoothed derivative with same length as data_in

    """
    data_in[data_in == 0] = 1
    _GaussDerivative.update(n_derivative)
    convolution = np.convolve(data_in, _GaussDerivative.y, "valid")
    convolution /= data_in[(n_derivative - 1)[:-(n_derivative + 1)]]
    original_length = len(data_in)
    convolution_length = len(convolution)
    zeros_start = int(np.floor(0.5 * (original_length - convolution_length)))
    zeros_end = int(original_length - convolution_length - zeros_start)
    return np.r_[(np.zeros(zeros_start), convolution, np.zeros(zeros_end))]


def _normalized_std(data_in, n_std, repeat=False):
    """
    Normalized standard deviation, through std/mean

    Keyword arguments:
        data_in ():
        n_std (int):

    return:
        ndarray: Normalized standard deviation

    """
    n_data = len(data_in)
    if n_data % n_std:
        data_in = data_in[:-(n_data % n_std)]
    data_in = np.reshape(data_in, (-1, n_std))
    data_out = data_in.std(axis=1) / data_in.mean(axis=1)
    if repeat:
        data_out = np.repeat(data_out, n_std)[:n_data]
    return data_out


def _get_bad_region_blocks(bad_data_points, n_join):
    """
    Returns list of tuples with start and end index of bad regions.

    Keyword arguments:
        bad_data_points (list): Data points which got identified as bad (no single mode operation)
        n_join (int): Joining neighbouring blocks

    Returns:
        list: list of tuples with start and end index of bad regions
    """
    if np.all(bad_data_points):
        return [
         (
          0, len(bad_data_points))]
    elif not np.any(bad_data_points):
        return []
        starts = np.nonzero(bad_data_points[1:] * ~bad_data_points[:-1])[0]
        if bad_data_points[0]:
            starts = np.r_[(0, starts)]
        ends = [i + np.argmin(bad_data_points[i + 1:]) for i in starts]
        if bad_data_points[-1]:
            ends[-1] = len(bad_data_points)
        blocks = []
        if n_join > 0:
            starts = list(starts)
            while len(starts):
                i0 = starts.pop(0)
                if len(starts):
                    if starts[0] - ends[0] > n_join:
                        break
                    starts.pop(0)
                    ends.pop(0)
                else:
                    blocks.append((i0, ends.pop(0)))

    else:
        blocks = zip(starts, ends)
    return blocks


def _get_stable_regions(bad_data_points, bad_region_blocks, n_data):
    """
    Convert bad region blocks (defined by start and end) to stable regions (defined by centre and width).
    Return values are normalized.

    Keyword arguments:
        bad_data_points(): Data points which got identified as bad (no single mode operation)
        bad_region_blocks (): List of tuples with start and end index of bad regions
        n_data (int): length of data

    Returns:
        centres: list of floats
        widths: list of floats

    """
    bits = np.asarray(bad_region_blocks).ravel()
    if bad_data_points[0]:
        bits = bits[1:]
    else:
        bits = np.r_[(0, bits)]
    if not bad_data_points[-1]:
        bits = np.r_[(bits, len(bad_data_points))]
    elif len(bits) % 2:
        bits = bits[:-1]
    bits = bits.reshape((-1, 2))
    if len(bad_data_points) > 0:
        widths = bits[:, 1] - bits[:, 0]
        centres = (bits[:, 1] + bits[:, 0]) / 2
    else:
        widths = [
         len(bad_data_points)]
    centres = [
     len(bad_data_points) / 2]
    widths = np.divide(widths, n_data)
    centres = np.divide(centres, n_data)
    return (
     centres, widths)


def stable_regions(ext_pd, int_pd, mode_detection, split_scan=False):
    """
    Returns centres and widths of stable regions.

    Keyword arguments:
        ext_pd (list): Raw data from external photodiode
        int_pd (list): Raw data from internal photodiode
        mode_detection (dict): Parameter set for mode detection algorithm
        return_raw_data (bool): Return mode_finder_raw_data along with centres, widths
        split_scan (bool): Split scan in half, needed when using a periodic piezo scan with ramp up and down

    Returns:
        centres (list): list of floats
        widths (list): list of floats

    """
    n_data = len(ext_pd)
    derivative_ext_pd = _smooth_derivative(data_in=ext_pd, n_derivative=(mode_detection["n_derivative"]))
    normalized_std_ext_pd = _normalized_std(data_in=ext_pd, n_std=(mode_detection["n_std"]), repeat=True)
    derivative_int_pd = _smooth_derivative(data_in=int_pd, n_derivative=(mode_detection["n_derivative"]))
    normalized_std_int_pd = _normalized_std(data_in=int_pd, n_std=(mode_detection["n_std"]), repeat=True)
    bad_data_points = np.abs(derivative_ext_pd) > mode_detection["max_derivative"] / 100
    bad_data_points += normalized_std_ext_pd[:len(derivative_ext_pd)] > mode_detection["max_std"] / 100
    bad_data_points += np.abs(derivative_int_pd) > mode_detection["max_derivative"] / 100
    bad_data_points += normalized_std_int_pd[:len(derivative_int_pd)] > mode_detection["max_std"] / 100
    if split_scan:
        bad_data_points[len(bad_data_points) // 2] = True
    else:
        bad_region_blocks = _get_bad_region_blocks(bad_data_points=bad_data_points, n_join=(mode_detection["n_join"] * mode_detection["n_derivative"]))
        if len(bad_region_blocks) > 0:
            centres, widths = _get_stable_regions(bad_data_points=bad_data_points, bad_region_blocks=bad_region_blocks,
              n_data=n_data)
        else:
            centres, widths = [
             len(ext_pd) / 2], [len(ext_pd)]
    mode_finder_raw_data = {'ext_pd': ext_pd, 'int_pd': int_pd, 
     'bad_region_blocks': bad_region_blocks, 
     'derivative_ext_pd': derivative_ext_pd, 
     'normalized_std_ext_pd': normalized_std_ext_pd, 
     'derivative_int_pd': derivative_int_pd, 
     'normalized_std_int_pd': normalized_std_int_pd}
    return (
     centres, widths, mode_finder_raw_data)

# okay decompiling cem/core/single_mode_finder.pyc
