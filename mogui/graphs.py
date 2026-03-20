# uncompyle6 version 3.9.3
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.9.6 (default, Apr 30 2025, 02:07:17) 
# [Clang 17.0.0 (clang-1700.0.13.5)]
# Embedded file name: mogui\graphs.py
"""TODO: Consider to refactor it
"""
import time, numpy as np, pyqtgraph as pg
try:
    from PySide2 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
from pyqtgraph.graphicsItems.LegendItem import ItemSample
from .DateAxisItem import DateAxisItem
from .mogui import msgbox_yesno
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")
pg.setConfigOptions(antialias=True)
DEFAULT_COLS = [
 '#0066ff', '#33cc33', '#ff9933', '#ff0000', '#ff00ff']

def setFiniteData(plt, x, y):
    finite = np.isfinite(y)
    if not np.any(finite):
        plt.setData([], [])
        return
    x = x[finite]
    y = y[finite]
    connect = finite * np.r_[finite[1:], True]
    connect = connect[finite]
    plt.setData(x, y, connect=connect)


def generateTwinX(plt: pg.PlotItem, label=None):
    vb = pg.ViewBox()
    plt.showAxis("right")
    plt.scene().addItem(vb)
    plt.getAxis("right").linkToView(vb)
    vb.setXLink(plt)
    if label is not None:
        plt.getAxis("right").setLabel(label)

    def updateTwinView():
        vb.setGeometry(plt.vb.sceneBoundingRect())
        vb.linkedViewChanged(plt.vb, vb.XAxis)

    plt.vb.sigResized.connect(updateTwinView)
    return vb


pg.GraphicsScene.getContextMenus = lambda self, event: None
pg.PlotItem.getContextMenus = lambda self, event: None
pg.PlotItem.updateButtons = lambda self: self.autoBtn.hide()
originalUpdateState = pg.graphicsItems.ViewBox.ViewBoxMenu.ViewBoxMenu.updateState

def newUpdateState(self):
    state = self.view().getState(copy=False)
    for i in (0, 1):
        tr = state["targetRange"][i]

    for ctrl, val in zip([self.ctrl[i].minText, self.ctrl[i].maxText], tr):
        ctrl.setText = lambda x: None
        if not ctrl.hasFocus():
            QtWidgets.QLineEdit.setText(ctrl, "%0.6g" % val)
    else:
        originalUpdateState(self)


pg.graphicsItems.ViewBox.ViewBoxMenu.ViewBoxMenu.updateState = newUpdateState

class MyAxisItem(pg.AxisItem):

    def __init__(self, orientation, tickSize=None, labelSize=None, dotted=False, *args, **kwargs):
        if "maxTickLength" not in kwargs:
            kwargs["maxTickLength"] = -5
        else:
            (pg.AxisItem.__init__)(self, orientation, *args, **kwargs)
            if tickSize is not None:
                f = QtGui.QFont()
                f.setPointSize(tickSize)
                self.setTickFont(f)
                self.setStyle(tickTextOffset=tickSize)
            else:
                self.tickFont = None
            if labelSize is not None:
                self.labelStyle["font-size"] = "%dpt" % labelSize
            if dotted:
                self.gridPen = pg.mkPen("#000", style=(QtCore.Qt.DotLine))
            else:
                self.gridPen = pg.mkPen(QtGui.QColor.fromRgbF(0.0, 0.0, 0.0, 0.15))
        self.grid = True

    def setTickFont(self, font):
        self.style["tickTextHeight"] = QtGui.QFontMetrics(font).height()
        self.tickFont = font
        pg.AxisItem.setTickFont(self, font)

    def boundingRect(self):
        linkedView = self.linkedView()
        rect = self.mapRectFromParent(self.geometry())
        if linkedView is not None:
            if self.grid:
                rect |= linkedView.mapRectToItem(self, linkedView.boundingRect())
        else:
            tl = self.style["tickLength"]
            h = self.style["tickTextHeight"] // 2 + 15
            if self.orientation == "left":
                rect = rect.adjusted(0, -h, -min(0, tl), h)
            else:
                if self.orientation == "right":
                    rect = rect.adjusted(min(0, tl), -h, 0, h)
                else:
                    if self.orientation == "top":
                        rect = rect.adjusted(-h, 0, h, -min(0, tl))
                    else:
                        if self.orientation == "bottom":
                            rect = rect.adjusted(-h, min(0, tl), h, 0)
        return rect

    def generateDrawSpecs(self, p):
        if self.style["tickFont"] is not None:
            p.setFont(self.style["tickFont"])
        axisSpec, origGrid, textSpec = pg.AxisItem.generateDrawSpecs(self, p)
        tickSpec = []
        gridSpec = []
        tl = self.style["tickLength"]
        for pen, p1, p2 in origGrid:
            delta = QtCore.QPoint(0, -tl) if p1.x() == p2.x() else QtCore.QPoint(tl, 0)
            tickSpec.append((self.pen(), p2, p2 - delta))
            gridSpec.append((self.gridPen, p1, p2))
        else:
            return (
             axisSpec, tickSpec + gridSpec, textSpec)

    def _updateMaxTextSize(self, x):
        pg.AxisItem._updateMaxTextSize(self, x + 10)


def myAxisItems(showValues=False, **kwargs):
    return {k: MyAxisItem(k, showValues=showValues, **kwargs) for k in ('left', 'bottom')}


class MyLabelItem(pg.LabelItem):

    def __init__(self, *args, **kwargs):
        self.padding = (0, 0, 0, 0)
        (pg.LabelItem.__init__)(self, *args, **kwargs)

    def setPadding(self, left=0, top=0, right=0, bottom=0):
        self.padding = (
         -left, -top, right, bottom)

    def itemRect(self):
        return (self.item.mapRectToParent(self.item.boundingRect()).adjusted)(*self.padding)


class LockedViewBox(pg.ViewBox):

    def __init__(self, *args, **kwargs):
        (pg.ViewBox.__init__)(self, *args, **kwargs)


def replacePlotTitle(plot, text=None, *args, **kwargs):
    if text is None:
        text = plot.titleLabel.text
    newtitle = MyLabelItem(*args, **kwargs)
    newtitle.setPadding(top=5, bottom=15)
    plot.layout.removeItem(plot.layout.itemAt(0, 1))
    plot.titleLabel = newtitle
    plot.layout.addItem(newtitle, 0, 1)
    plot.setTitle(None if len(text) == 0 else text)
    return newtitle


class MyLegend(pg.LegendItem):

    def __init__(self, parent, pen=None, brush=None, textColor=None, size=None, spacer=None, **kwargs):
        (pg.LegendItem.__init__)(self, **kwargs)
        self.setParentItem(parent.vb)
        parent.legend = self
        self.pen = pg.mkPen(pen or pg.getConfigOption("foreground"))
        self.brush = pg.mkBrush(brush or pg.getConfigOption("background"))
        self.textColor = pg.mkColor(textColor or pg.getConfigOption("foreground"))
        self.size = size
        if spacer is None:
            spacer = pg.__version__.startswith("0.10")
        self.spacer = spacer

    def paint(self, p, *args):
        p.setPen(self.pen)
        p.setBrush(self.brush)
        p.drawRect(self.boundingRect())

    def addItem(self, item: pg.PlotDataItem, name=None):
        kwargs = {'justify':"left", 
         'color':self.textColor}
        if name is None:
            name = item.name()
        elif self.size is not None:
            kwargs["size"] = self.size
        label = (pg.LabelItem)(name, **kwargs)
        if isinstance(item, ItemSample):
            sample = item
        else:
            sample = ItemSample(item)
        row = self.layout.rowCount()
        self.items.append((sample, label))
        self.layout.setRowAlignment(row, QtCore.Qt.AlignLeft)
        self.layout.addItem(sample, row, 0)
        if self.spacer:
            self.layout.addItem(pg.LabelItem(""), row, 1)
        self.layout.addItem(label, row, 2 if self.spacer else 1)
        self.updateSize()
        return sample


class LoggerPlot(pg.PlotDataItem):

    def __init__(self, parent, count=None, backlog=None, diff=False, **kwargs):
        if "connect" not in kwargs:
            kwargs["connect"] = "finite"
        (super().__init__)(**kwargs)
        if parent is not None:
            parent.addItem(self)
        self.count = count
        self.backlog = backlog
        self.diff = diff
        self.clear()

    def clear(self):
        self.setData(x=None, y=None)
        if self.diff:
            self.y0 = None
        self.update()

    def append(self, val, t=None):
        if val is not None:
            if isinstance(val, str):
                if " " in val:
                    val = val.strip().split(maxsplit=1)[0]
            val = float(val)
            if self.diff:
                if self.y0 is None:
                    self.y0 = val
                val -= self.y0
        elif t is None:
            t = time.time()
        xData, yData = self.getData()
        if xData is None:
            self.setData(x=(np.array([t])), y=(np.array([val])))
        else:
            if self.backlog is not None:
                idx = xData > t - self.backlog
                xData = xData[idx]
                yData = yData[idx]
            if val is not None:
                if self.count is not None:
                    xData = xData[-self.count:]
                    yData = yData[-self.count:]
                yData = np.append(yData, [val])
                xData = np.append(xData, [t])
        self.setData(x=xData, y=yData)
        self.update()

    def update(self):
        self.xDisp = None
        self.yDisp = None
        self.updateItems()
        self.informViewBoundsChanged()
        self.sigPlotChanged.emit(self)


class LoggerGraph(pg.PlotItem):

    def __init__(self, parent=None, ylabel=None, row=None, col=None, legend=None, **kwargs):
        if ylabel is not None:
            if "labels" not in kwargs:
                kwargs["labels"] = {}
            kwargs["labels"]["left"] = ylabel
        (super().__init__)(axisItems={"bottom": (DateAxisItem(orientation="bottom"))}, **kwargs)
        if parent is not None:
            parent.addItem(self, row=row, col=col)
        if legend is not None:
            self.legend = MyLegend(self, offset=legend, spacer=False)
        self.plotitems = []

    def addPlot(self, **kwargs):
        if "pen" not in kwargs:
            if "symbolPen" not in kwargs:
                p = pg.mkPen(DEFAULT_COLS[len(self.plotitems) % len(DEFAULT_COLS)])
                if "symbol" in kwargs:
                    kwargs["symbolPen"] = p
                else:
                    kwargs["pen"] = p
        p = LoggerPlot(self, **kwargs)
        self.plotitems.append(p)
        return p

    def append(self, vals, t=None):
        if isinstance(vals, str):
            vals = vals.split(",")
        if t is None:
            t = time.time()
        for G, y in zip(self.plotitems, vals):
            if y is not None:
                G.append(y, t=t)

    def clear(self):
        for G in self.plotitems:
            G.clear()
        else:
            self.enableAutoRange()

    def autoscale(self, x=True, y=True):
        self.getViewBox().enableAutoRange(x=x, y=y)


def createLoggingPlot(parent, ylabel=None, row=None, col=1, legend=(10, -10), **kwargs):
    import warnings
    warnings.warn("deprecated", DeprecationWarning)
    return LoggerGraph(parent, **kwargs)


class GraphRegion(pg.LinearRegionItem):

    def __init__(self, parent, pen=None, lineMove=True, horizontal=False, **kwargs):
        if horizontal:
            kwargs["orientation"] = pg.LinearRegionItem.Horizontal
        (super().__init__)(**kwargs)
        for l in self.lines:
            if pen is not None:
                l.setPen(pen)
            if not lineMove:
                l.setMovable(False)
        else:
            if parent is not None:
                parent.addItem(self)


class RemovableScatterPlot(pg.ScatterPlotItem):
    pointRemoved = QtCore.Signal(float, float)

    def __init__(self, parent, *args, **kwargs):
        if "symbol" not in kwargs:
            kwargs["symbol"] = "x"
        if "size" not in kwargs:
            kwargs["size"] = 10
        (super().__init__)(*args, **kwargs)
        self.sigClicked.connect(self.queryRemove)
        parent.addItem(self)

    def queryRemove(self, plt, pts):
        if len(pts) == 0:
            return
        changed = False
        for pt in pts:
            x = pt.pos()[0]
            if msgbox_yesno(self.parent(), "Remove datapoint", "Remove value at %s?" % x):
                i = self.data["item"] == pt
                self.data = self.data[~i]
                (self.pointRemoved.emit)(*pt.pos())
                changed = True
        else:
            if changed:
                self.sigPlotChanged.emit(self)

# okay decompiling mogui/graphs.pyc
