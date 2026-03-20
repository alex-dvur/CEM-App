# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: mogui\DateAxisItem.py
import numpy as np, time
from datetime import datetime
from pyqtgraph.graphicsItems.AxisItem import AxisItem
__all__ = [
 "DateAxisItem", "ZoomLevel"]
MS_SPACING = 0.001
SECOND_SPACING = 1
MINUTE_SPACING = 60
HOUR_SPACING = 3600
DAY_SPACING = 24 * HOUR_SPACING
WEEK_SPACING = 7 * DAY_SPACING
MONTH_SPACING = 30 * DAY_SPACING
YEAR_SPACING = 365 * DAY_SPACING

def makeMSStepper(stepSize):

    def stepper(val, n):
        val *= 1000
        f = stepSize * 1000
        return (val // (n * f) + 1) * (n * f) / 1000.0

    return stepper


def makeSStepper(stepSize):

    def stepper(val, n):
        return (val // (n * stepSize) + 1) * (n * stepSize)

    return stepper


def makeMStepper(stepSize):

    def stepper(val, n):
        d = datetime.utcfromtimestamp(val)
        base0m = d.month + n * stepSize - 1
        d = datetime(d.year + base0m // 12, base0m % 12 + 1, 1)
        return (d - datetime(1970, 1, 1)).total_seconds()

    return stepper


def makeYStepper(stepSize):

    def stepper(val, n):
        d = datetime.utcfromtimestamp(val)
        next_date = datetime((d.year // (n * stepSize) + 1) * (n * stepSize), 1, 1)
        return (next_date - datetime(1970, 1, 1)).total_seconds()

    return stepper


class TickSpec:
    __doc__ = " Specifies the properties for a set of date ticks and computes ticks\n    within a given utc timestamp range "

    def __init__(self, spacing, stepper, format, autoSkip=None):
        """
        ============= ==========================================================
        Arguments
        spacing       approximate (average) tick spacing
        stepper       a stepper function that takes a utc time stamp and a step
                      steps number n to compute the start of the next unit. You
                      can use the make_X_stepper functions to create common
                      steppers.
        format        a strftime compatible format string which will be used to
                      convert tick locations to date/time strings
        autoSkip      list of step size multipliers to be applied when the tick
                      density becomes too high. The tick spec automatically
                      applies additional powers of 10 (10, 100, ...) to the list
                      if necessary. Set to None to switch autoSkip off
        ============= ==========================================================

        """
        self.spacing = spacing
        self.step = stepper
        self.format = format
        self.autoSkip = autoSkip

    def makeTicks(self, minVal, maxVal, minSpc):
        ticks = []
        n = self.skipFactor(minSpc)
        try:
            x = self.step(minVal, n)
            while x <= maxVal:
                ticks.append(x)
                x = self.step(x, n)

        except:
            pass
        else:
            return (
             np.array(ticks), n)

    def skipFactor(self, minSpc):
        if self.autoSkip is None or minSpc < self.spacing:
            return 1
        factors = np.array(self.autoSkip)
        for f in factors:
            spc = self.spacing * f
            if spc > minSpc:
                return f
            factors *= 10


class ZoomLevel:
    __doc__ = " Generates the ticks which appear in a specific zoom level "

    def __init__(self, tickSpecs):
        """
        ============= ==========================================================
        tickSpecs     a list of one or more TickSpec objects with decreasing
                      coarseness
        ============= ==========================================================

        """
        self.tickSpecs = tickSpecs
        self.utcOffset = 0

    def tickValues(self, minVal, maxVal, minSpc):
        allTicks = []
        valueSpecs = []
        utcMin = minVal - self.utcOffset
        utcMax = maxVal - self.utcOffset
        for spec in self.tickSpecs:
            ticks, skipFactor = spec.makeTicks(utcMin, utcMax, minSpc)
            ticks += self.utcOffset
            tick_list = [x for x in ticks.tolist() if x not in allTicks]
            allTicks.extend(tick_list)
            valueSpecs.append((spec.spacing, tick_list))
            if skipFactor > 1:
                break
            return valueSpecs


YEAR_MONTH_ZOOM_LEVEL = ZoomLevel([
 TickSpec(YEAR_SPACING, (makeYStepper(1)), "%Y", autoSkip=[1, 5, 10, 25]),
 TickSpec(MONTH_SPACING, makeMStepper(1), "%b")])
MONTH_DAY_ZOOM_LEVEL = ZoomLevel([
 TickSpec(MONTH_SPACING, makeMStepper(1), "%b"),
 TickSpec(DAY_SPACING, (makeSStepper(DAY_SPACING)), "%d %b", autoSkip=[1, 5])])
DAY_HOUR_ZOOM_LEVEL = ZoomLevel([
 TickSpec(DAY_SPACING, makeSStepper(DAY_SPACING), "%d %b"),
 TickSpec(HOUR_SPACING, (makeSStepper(HOUR_SPACING)), "%H:%M", autoSkip=[1, 6])])
HOUR_MINUTE_ZOOM_LEVEL = ZoomLevel([
 TickSpec(DAY_SPACING, makeSStepper(DAY_SPACING), "%d %b"),
 TickSpec(MINUTE_SPACING, (makeSStepper(MINUTE_SPACING)), "%H:%M", autoSkip=[
  1, 5, 15])])
HMS_ZOOM_LEVEL = ZoomLevel([
 TickSpec(SECOND_SPACING, (makeSStepper(SECOND_SPACING)), "%H:%M:%S", autoSkip=[
  1, 5, 15, 30])])
MS_ZOOM_LEVEL = ZoomLevel([
 TickSpec(MINUTE_SPACING, makeSStepper(MINUTE_SPACING), "%H:%M:%S"),
 TickSpec(MS_SPACING, (makeMSStepper(MS_SPACING)), "%S.%f", autoSkip=[
  1, 5, 10, 25])])

class DateAxisItem(AxisItem):
    __doc__ = " An AxisItem that displays dates from unix timestamps\n\n    The display format is adjusted automatically depending on the current time\n    density (seconds/point) on the axis.\n    You can customize the behaviour by specifying a different set of zoom levels\n    than the default one. The zoomLevels variable is a dictionary with the\n    maximum number of seconds/point which are allowed for each ZoomLevel\n    before the axis switches to the next coarser level.\n\n    "

    def __init__(self, orientation, **kvargs):
        (super(DateAxisItem, self).__init__)(orientation, **kvargs)
        self.utcOffset = time.altzone if time.localtime().tm_isdst > 0 else time.timezone
        self.zoomLevel = YEAR_MONTH_ZOOM_LEVEL
        self.maxTicksPerPt = 0.016666666666666666
        self.zoomLevels = {(self.maxTicksPerPt): MS_ZOOM_LEVEL, 
         (30 * self.maxTicksPerPt): HMS_ZOOM_LEVEL, 
         (900 * self.maxTicksPerPt): HOUR_MINUTE_ZOOM_LEVEL, 
         (21600 * self.maxTicksPerPt): DAY_HOUR_ZOOM_LEVEL, 
         (432000 * self.maxTicksPerPt): MONTH_DAY_ZOOM_LEVEL, 
         (2592000 * self.maxTicksPerPt): YEAR_MONTH_ZOOM_LEVEL}

    def tickStrings(self, values, scale, spacing):
        tickSpecs = self.zoomLevel.tickSpecs
        tickSpec = next((s for s in tickSpecs if s.spacing == spacing), None)
        dates = [datetime.utcfromtimestamp(v - self.utcOffset) for v in values]
        formatStrings = []
        for x in dates:
            try:
                if "%f" in tickSpec.format:
                    formatStrings.append(x.strftime(tickSpec.format)[:-3])
                else:
                    formatStrings.append(x.strftime(tickSpec.format))
            except ValueError:
                formatStrings.append("")

        else:
            return formatStrings

    def tickValues(self, minVal, maxVal, size):
        density = (maxVal - minVal) / size
        self.setZoomLevelForDensity(density)
        minSpacing = density / self.maxTicksPerPt
        values = self.zoomLevel.tickValues(minVal, maxVal, minSpc=minSpacing)
        return values

    def setZoomLevelForDensity(self, density):
        keys = sorted(self.zoomLevels.keys())
        key = next((k for k in keys if density < k), keys[-1])
        self.zoomLevel = self.zoomLevels[key]
        self.zoomLevel.utcOffset = self.utcOffset

# okay decompiling mogui/DateAxisItem.pyc
