from qgis.core import *
import os, sys
import inspect
from sextante.core.Sextante import Sextante
from sextante_animove.animoveAlgorithmProvider import animoveAlgorithmProvider


cmd_folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

class animoveProviderPlugin:

    def __init__(self):
        self.provider = animoveAlgorithmProvider()
    def initGui(self):
        Sextante.addProvider(self.provider)

    def unload(self):
        Sextante.removeProvider(self.provider)

