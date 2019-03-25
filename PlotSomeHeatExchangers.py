###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


from HeatExchangers import GeneralRealRecuperator
from Plotters import PlotHeatExchanger
from helpers import SmartDictionary,WriteBinaryData,iarange,RoundAndPadToString
from numpy import linspace




BaseOutputFilePath='/tmp/'







Cases=[
	[
		'WildDeltaTSweepAutoRange',
		1.0,				#RecuperatorInputParameters['LowPressure']['MassFraction']
		[0.565],				#RecuperatorInputParameters['HighPressure']['MassFraction']
		200,				#RecuperatorInputParameters['NumberofTemperatures']
		450,				#Recuperator['LowPressure']['StartingProperties']['Temperature']
		5.*10**6,			#Recuperator['LowPressure']['StartingProperties']['Pressure']
		305.0,				#Recuperator['HighPressure']['StartingProperties']['Temperature']
		25.0*10**6,			#Recuperator['HighPressure']['StartingProperties']['Pressure']
		[5],		#RecuperatorInputParameters['MinimumDeltaT']
		0,				#RecuperatorInputParameters['DeltaPPerDeltaT']
		None,		#DeltaTVerticalAxisMax
		None,				#cpRatioAxisMax
	],
	[
		'WildDeltaTSweep',
		1.0,				#RecuperatorInputParameters['LowPressure']['MassFraction']
		[0.565],				#RecuperatorInputParameters['HighPressure']['MassFraction']
		200,				#RecuperatorInputParameters['NumberofTemperatures']
		450,				#Recuperator['LowPressure']['StartingProperties']['Temperature']
		5.*10**6,			#Recuperator['LowPressure']['StartingProperties']['Pressure']
		305.0,				#Recuperator['HighPressure']['StartingProperties']['Temperature']
		25.0*10**6,			#Recuperator['HighPressure']['StartingProperties']['Pressure']
		iarange(0,50,5),		#RecuperatorInputParameters['MinimumDeltaT']
		0,				#RecuperatorInputParameters['DeltaPPerDeltaT']
		'MaxDeltaTCase',		#DeltaTVerticalAxisMax
		None,				#cpRatioAxisMax
	],
	[
		'WildMassFractionSweep',
		1.0,				#RecuperatorInputParameters['LowPressure']['MassFraction']
		linspace(0.1,1,10),		#RecuperatorInputParameters['HighPressure']['MassFraction']
		200,				#RecuperatorInputParameters['NumberofTemperatures']
		450,				#Recuperator['LowPressure']['StartingProperties']['Temperature']
		5.*10**6,			#Recuperator['LowPressure']['StartingProperties']['Pressure']
		305.0,				#Recuperator['HighPressure']['StartingProperties']['Temperature']
		25.0*10**6,			#Recuperator['HighPressure']['StartingProperties']['Pressure']
		[5],				#RecuperatorInputParameters['MinimumDeltaT']
		0,				#RecuperatorInputParameters['DeltaPPerDeltaT']
		120,				#DeltaTVerticalAxisMax
		3,				#cpRatioAxisMax
	],
	[
		'Wild0',
		1.0,				#RecuperatorInputParameters['LowPressure']['MassFraction']
		[0.6],				#RecuperatorInputParameters['HighPressure']['MassFraction']
		200,				#RecuperatorInputParameters['NumberofTemperatures']
		450,				#Recuperator['LowPressure']['StartingProperties']['Temperature']
		8.*10**6,			#Recuperator['LowPressure']['StartingProperties']['Pressure']
		305.0,				#Recuperator['HighPressure']['StartingProperties']['Temperature']
		18.5*10**6,			#Recuperator['HighPressure']['StartingProperties']['Pressure']
		[5],				#RecuperatorInputParameters['MinimumDeltaT']
		0,				#RecuperatorInputParameters['DeltaPPerDeltaT']
		None,				#DeltaTVerticalAxisMax
		None,				#cpRatioAxisMax
	],
	[
		'ConstantAndEqual',
		1.0,				#RecuperatorInputParameters['LowPressure']['MassFraction']
		[1],				#RecuperatorInputParameters['HighPressure']['MassFraction']
		200,				#RecuperatorInputParameters['NumberofTemperatures']
		350,				#Recuperator['LowPressure']['StartingProperties']['Temperature']
		1.*10**6,			#Recuperator['LowPressure']['StartingProperties']['Pressure']
		305.0,				#Recuperator['HighPressure']['StartingProperties']['Temperature']
		1.*10**6,			#Recuperator['HighPressure']['StartingProperties']['Pressure']
		[5],				#RecuperatorInputParameters['MinimumDeltaT']
		0,				#RecuperatorInputParameters['DeltaPPerDeltaT']
		None,				#DeltaTVerticalAxisMax
		2,				#cpRatioAxisMax
	],
	[
		'cpRatioLessThan1',
		1.0,				#RecuperatorInputParameters['LowPressure']['MassFraction']
		[0.6],				#RecuperatorInputParameters['HighPressure']['MassFraction']
		200,				#RecuperatorInputParameters['NumberofTemperatures']
		450.0,				#Recuperator['LowPressure']['StartingProperties']['Temperature']
		1.*10**6,			#Recuperator['LowPressure']['StartingProperties']['Pressure']
		305.0,				#Recuperator['HighPressure']['StartingProperties']['Temperature']
		1.*10**6,			#Recuperator['HighPressure']['StartingProperties']['Pressure']
		[5],				#RecuperatorInputParameters['MinimumDeltaT']
		0,				#RecuperatorInputParameters['DeltaPPerDeltaT']
		None,				#DeltaTVerticalAxisMax
		2,				#cpRatioAxisMax
	],
	[
		'Wild2',
		1.0,				#RecuperatorInputParameters['LowPressure']['MassFraction']
		[0.689],			#RecuperatorInputParameters['HighPressure']['MassFraction']
		200,				#RecuperatorInputParameters['NumberofTemperatures']
		450.0,				#Recuperator['LowPressure']['StartingProperties']['Temperature']
		7.*10**6,			#Recuperator['LowPressure']['StartingProperties']['Pressure']
		400.0,				#Recuperator['HighPressure']['StartingProperties']['Temperature']
		20.*10**6,			#Recuperator['HighPressure']['StartingProperties']['Pressure']
		[5],				#RecuperatorInputParameters['MinimumDeltaT']
		0,				#RecuperatorInputParameters['DeltaPPerDeltaT']
		None,				#DeltaTVerticalAxisMax
		2,				#cpRatioAxisMax
	],
	[
		'Wild22',
		1.0,				#RecuperatorInputParameters['LowPressure']['MassFraction']
		[1.635],				#RecuperatorInputParameters['HighPressure']['MassFraction']
		200,				#RecuperatorInputParameters['NumberofTemperatures']
		350.0,				#Recuperator['LowPressure']['StartingProperties']['Temperature']
		25.*10**6,			#Recuperator['LowPressure']['StartingProperties']['Pressure']
		310.0,				#Recuperator['HighPressure']['StartingProperties']['Temperature']
		5.*10**6,			#Recuperator['HighPressure']['StartingProperties']['Pressure']
		[5],				#RecuperatorInputParameters['MinimumDeltaT']
		0,				#RecuperatorInputParameters['DeltaPPerDeltaT']
		None,				#DeltaTVerticalAxisMax
		2,				#cpRatioAxisMax
	],
]



for Case in Cases:
	for MinimumDeltaT in Case[8]:
		for MassFraction in Case[2]:
			Recuperator=SmartDictionary()
			RecuperatorInputParameters=SmartDictionary()
			RecuperatorInputParameters['LowPressure']['MassFraction']=Case[1]
			RecuperatorInputParameters['HighPressure']['MassFraction']=MassFraction
			RecuperatorInputParameters['NumberofTemperatures']=Case[3]
			Recuperator['LowPressure']['StartingProperties']['Temperature']=Case[4]
			Recuperator['LowPressure']['StartingProperties']['Pressure']=Case[5]
			Recuperator['HighPressure']['StartingProperties']['Temperature']=Case[6]
			Recuperator['HighPressure']['StartingProperties']['Pressure']=Case[7]
			RecuperatorInputParameters['MinimumDeltaT']=MinimumDeltaT
			RecuperatorInputParameters['DeltaPPerDeltaT']=Case[9]

			if Case[10] == 'MaxDeltaTCase':
				DeltaTVerticalAxisMax=max(Case[8]+20)
			else:
				DeltaTVerticalAxisMax=Case[10]

			cpRatioAxisMax=Case[11]

			WriteBinaryData(PlotHeatExchanger(GeneralRealRecuperator(Recuperator,RecuperatorInputParameters),RecuperatorInputParameters,ImageFileType='pdf',DeltaTVerticalAxisMax=DeltaTVerticalAxisMax,cpRatioAxisMax=cpRatioAxisMax),BaseOutputFilePath+'/'+Case[0]+'-'+str(MinimumDeltaT)+'-'+str(MassFraction)+'.pdf')









