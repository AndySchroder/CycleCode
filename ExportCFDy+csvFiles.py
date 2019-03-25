###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


from subprocess import call
from os import rename

BaseName='StraightEqualHeightChannels'

#turbulent case names and grid levels
Cases=[
	[
		'Re3000T',		#case name
		[0],			#geometry grid levels
		[0],			#property grid levels
		'',			#suffix
	],
	[
		'Re4000T',
		[0],
		[0],
		'',
	],
	[

		'10m-Re3000T',
		[0,1,2],
		[0,1,2],
		'',
	],
	[
		'10m-Re3000T',
		[0],
		[0],
		'_LowPressure',
	],
]

#add some blank lines
print
print

for Case in Cases:
	for GeometryGridLevel in Case[1]:
		for PropertyGridLevel in Case[2]:
			CaseName=BaseName+'-'+Case[0]+'_G'+2*str(GeometryGridLevel)+'R_P'+2*str(PropertyGridLevel)+Case[3]

			#open starccm+ with the current file and run the macro that exports the csv files
			call(['starccm+','-licpath','1999@flex.cd-adapco.com','-power','-podkey','YourPODKeyHERE!','-collab','-batch','ExportCFDyPluscsvFiles.java',CaseName+'.sim'])


			#can't figure out how to get starccm+ to accept a variable on the command line or figure out what it's current simulation name is, so just export data to static filenames and then immediately rename.
			rename('exported_data/y+.csv','exported_data/'+CaseName+'-y+.csv')

			#add a separator
			print
			print
			print '---------------------------------------------'






