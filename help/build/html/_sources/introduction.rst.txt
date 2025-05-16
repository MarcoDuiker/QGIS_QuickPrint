Introduction
************

About
=====

This plug-in is developed by Marco Duiker from `MD-kwadraat <http://www.md-kwadraat.nl/>`_ .

You will find the plugin in the web menu of QGIS. Furthermore you'll find a print icon on a toolbar.

The plug-in provides a simple way to quickly create a pdf from the map as shown in the map pane. The map is not just a screenshot, but a real map with a title, subtitle, scalebar, date, attribution, remarks, an optional north arrow and an optional logo.

In this way you get a decent print without the hassle of setting up and using print templates.

As simple things go it is pretty much self-explanatory.

For printing you can choose between A3 and A4 paper sizes and between portrait and landscape paper orientation.

To make things even easier we've added a preview so you see all settings and the exact map coverage before exporting.

Settings
========

The settings dialog allows you to:

   - set the standard for paper sizes
   - change the date formatting
   - change the font and font size for the texts around the map
   - select an image to use as a logo
   - set a default attribution
   - set a default remark

Set the standard for paper sizes
''''''''''''''''''''''''''''''''

The QuickPrint plugin can work with either DIN paper sizes (A3 and A4) or ANSI paper sizes (ANSI-A and ANSI-B).

Choose an option which suites you most.


Date formatting
'''''''''''''''

For date formatting you can provide a Python format string, in which the following items will be substituted:

   - ``{day}`` by the number of the day
   - ``{month}`` by the number of the day
   - ``{year}`` by the number of the year

``{day}-{month}-{year}`` is an example of such a format string. This will print the date as eg. ``22-12-2020``.


Font and font size
''''''''''''''''''

You can select a font from the font selection box to use for the titles and texts around the map.

As some fonts tend to work out a little larger or smaller than the default font, you can use the slider to set the font size a little larger or smaller to compensate for this.

Logo
''''

You can put a logo in the top right hand corner of all prints you make, by providing one of the following:

   - A URL to an image file. This URL should start with ``http://`` or ``https://``.
   - A path to a local file on your file system. It's best to use the ``Browse`` button for this.
   
A checkbox is added to the main dialog to omit the logo temporarily, eg. when creating a map for in a report.

Default attribution
'''''''''''''''''''

When a copyright applies to one or more of the maps in the print, providing attribution is mandatory. Via the settings a default attribution text can be set. This text will be used when starting a QGIS session, and presented in the QuickPrint print window on printing. There you can change the text as it will appear in the print.

During sessions QGIS remembers the last attribution which is used and presents that text in the QuickPrint print window.


Default remark
''''''''''''''

The QuickPrint plugin allows for a remark being printed on the bottom of the page. Via the settings a default remark text can be set. This text will be used when starting a QGIS session, and presented in the QuickPrint print window on printing. There you can change the text as it will appear in the print.

During sessions QGIS remembers the last remark which is used and presents that text in the QuickPrint print window.


North Arrow
===========

Some people insist on putting a north pointing arrow on a map, even if the map is oriented to the north. As this was a much asked for feature we added the possibility to have one. The north arrow will also rotate if you rotate your map.

In the settings you can specify any image to use as a north arrow. If no image is specified in the settings, a default north arrow is used.

Preview
=======

We've added a preview on the main dialog. This preview can be collapsed and also frozen. This is helpful when rendering the preview image takes to much time.
