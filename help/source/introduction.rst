Introduction
************

About
=====

This plug-in is developed by Marco Duiker from `MD-kwadraat <http://www.md-kwadraat.nl/>`_ .

You will find the plugin in the web menu of QGIS. Furthermore you'll find a print icon on a toolbar.

The plug-in provides a simple way to quickly create a pdf from the map as shown in the map pane. The map is not just a screenshot, but a real map with a title, subtitle, scalebar, date, attribution and remarks. 

In this way you get a decent print without the hassle of setting up and using print templates.

As simple things go it is pretty much self-explanatory.

For printing you can choose between A3 and A4 paper sizes and between portrait and landscape paper orientation.


Settings
========

The new settings dialog allows you to:

   - change the date formatting
   - change the font and font size for the texts around the map
   - select an image to use as a logo

If you don't use this settings dialog, QuickPrint will work just as you are used to.


Date formatting
'''''''''''''''

For date formatting you can provide a Python format string, in which the following items will be substituted:

   - ``{day}`` by the number of the day
   - ``{month}`` by the number of the day
   - ``{year}`` by the number of the year


Font and font size
''''''''''''''''''

You can select a font from the font combobox to use for the titles and texts around the map. 

As some fonts tend to work out a little larger or smaller than the default font, you can use the slider to set the font size a little larger or smaller to compensate for this.

Logo
''''

You can put a logo in the top righthand corner of all prints you make, by providing one of the following:

   - A URL to an image file. This URL should start with ``http://`` or ``https://``.
   - A path to a local file on your file system. It's best to use the ``Browse`` button for this.

North Arrow
===========

Some people insist on putting a north pointing arrow on a map, even if the map is oriented to the north. If you want to do so, you can put an image of a north arrow on the page instead of your logo. 

Beware, the north arrow will not rotate if you rotate the map.
