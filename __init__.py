# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickPrint3
                                 A QGIS plugin
 The QuickPrint Plugin for QGIS3
                             -------------------
        begin                : 2018-01-15
        copyright            : (C) 2018 by Marco Duiker MD-kwadraat
        email                : info@md-kwadraat.nl
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QuickPrint3 class from file QuickPrint3.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .quick_print3 import QuickPrint3
    return QuickPrint3(iface)
