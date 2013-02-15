import os

from PyQt4 import QtGui

from sextante.core.AlgorithmProvider import AlgorithmProvider

from mcp import mcp
from href import href


class animoveAlgorithmProvider(AlgorithmProvider):

    def __init__(self):
        AlgorithmProvider.__init__(self)
        self.alglist = [mcp(),href()]

    def getDescription(self):
        return "AniMove (MCP and Kernel analysis UD)"

    def getName(self):
        return "AniMove"

    def getIcon(self):
        return  QtGui.QIcon(os.path.dirname(__file__) + "/icons/animalmove.png")

    def _loadAlgorithms(self):
        self.algs = self.alglist

    def getSupportedOutputTableExtensions(self):
        return ["csv"]

    def supportsNonFileBasedOutput(self):
        return True
