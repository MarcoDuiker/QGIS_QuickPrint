Updating translation
============


Update the language file with changes in gui and code

	pylupdate5 QuickPrint.pro
	
Add translations by editing `QuickPrint3_nl.ts` (it is an xml file).

Release the translations with:

	lrelease QuickPrint3_nl.ts
	
or something like this (if the wrong lrelease version is selected):

	/usr/lib/x86_64-linux-gnu/qt5/bin/lrelease QuickPrint3_nl.ts