def name():
    return "AniMove for SEXTANTE"
def description():
    return "MCP and Kernel functions for UD"
def version():
    return "Version 1.2.6"
def icon():
    return "icons/animalmove.png"
def qgisMinimumVersion():
    return "1.0"
def author():
    return "Francesco Boccacci"
def email():
    return "francescoboccacci@libero.it"
def repository():
    return "https://github.com/volterra79/sextante_animove"
def classFactory(iface):
    from animoveProviderPlugin import animoveProviderPlugin
    return animoveProviderPlugin()


