# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickPrint
                                 A QGIS plugin
 Create a quick print with a minimum of fuzz
                             -------------------
        begin                : 2014-05-28
        copyright            : (C) 2017 by Marco Duiker (MD-kwadraat)
        email                : info@md-kwadraat.nl
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

def classFactory(iface):
    # load QuickPrint class from file QuickPrint
    from quickprint import QuickPrint
    return QuickPrint(iface)
