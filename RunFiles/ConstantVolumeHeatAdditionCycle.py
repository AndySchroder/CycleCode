###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


PrintExtra=True

from Cycles import ConstantVolumeCycle
from helpers import SmartDictionary,WriteBinaryData,PrintKeysAndValues

import helpers
helpers.PrintWarningMessages=PrintExtra			#for some reason have to do it this way because if just import PrintWarningMessages, and then set it, python must think you are overwritting the imported PrintWarningMessages object with a new local one and so the module PrintWarningMessages is not changed.

#import plotting functions
from Plotters import PlotCycle,PlotHeatExchanger

#set some input values that have been commented out in the main input file.
CycleInputParameters=SmartDictionary()

CycleInputParameters['MinPressure']=7128140.70352		#taken from the parameter sweep


#choose the input parameters file
execfile('./InputParameters/InputParameters-ConstantVolumeCO2.py')



#################################################################################################
#run the cycle
#################################################################################################
CycleParameters=ConstantVolumeCycle(CycleInputParameters)

#print values
if PrintExtra:
	PrintKeysAndValues("Cycle Input Parameters",CycleInputParameters)
	PrintKeysAndValues("Cycle Outputs",CycleParameters)


#print efficiencies
print 'Carnot Cycle: '+str(CycleParameters['CycleCarnotEfficiency'])
print 'Real Cycle:   '+str(CycleParameters['CycleRealEfficiency'])



#create plots
if PrintExtra:

	BaseOutputFilePath='scratch/'

	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='Pressure',ImageFileType='pdf'),BaseOutputFilePath+'/'+'/TemperatureEntropyPressure.pdf')
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='Density',ImageFileType='pdf'),BaseOutputFilePath+'/'+'/TemperatureEntropyDensity.pdf')
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='CompressibilityFactor',ImageFileType='pdf'),BaseOutputFilePath+'/'+'/TemperatureEntropyCompressibilityFactor.pdf')
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='cp',ImageFileType='pdf'),BaseOutputFilePath+'/'+'/TemperatureEntropycp.pdf')
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='gamma',ImageFileType='pdf'),BaseOutputFilePath+'/'+'/TemperatureEntropyGamma.pdf')

	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='Enthalpy',ImageFileType='pdf'),BaseOutputFilePath+'/'+'/TemperatureEntropyEnthalpy.pdf')
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Enthalpy',ContourLevel='Temperature',ImageFileType='pdf'),BaseOutputFilePath+'/'+'/EnthalpyEntropyTemperature.pdf')


	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Pressure',VerticalAxis='Temperature',ContourLevel='Density',ImageFileType='pdf'),BaseOutputFilePath+'/'+'/TemperaturePressureDensity.pdf')
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Pressure',VerticalAxis='Temperature',ContourLevel='cp',ImageFileType='pdf'),BaseOutputFilePath+'/'+'/TemperaturePressurecp.pdf')
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Pressure',VerticalAxis='Temperature',ContourLevel='gamma',ImageFileType='pdf'),BaseOutputFilePath+'/'+'/TemperaturePressureGamma.pdf')


	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='SpecificVolume',VerticalAxis='Pressure',ContourLevel='CompressibilityFactor',ImageFileType='pdf'),BaseOutputFilePath+'/'+'PressureSpecificVolumeCompressibilityFactor.pdf')
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='SpecificVolume',VerticalAxis='Pressure',ContourLevel='gamma',ImageFileType='pdf'),BaseOutputFilePath+'/'+'PressureSpecificVolumeGamma.pdf')
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='SpecificVolume',VerticalAxis='Pressure',ContourLevel='Entropy',ImageFileType='pdf'),BaseOutputFilePath+'/'+'PressureSpecificVolumes.pdf')
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='SpecificVolume',VerticalAxis='Pressure',ContourLevel='Temperature',ImageFileType='pdf'),BaseOutputFilePath+'/'+'PressureSpecificVolumeT.pdf')


#don't plot this since it's not really clear since it shows cp on the high pressure side on the left plot
#	WriteBinaryData(PlotHeatExchanger(CycleParameters['HTRecuperator'],CycleInputParameters['HTRecuperator'],ImageFileType='pdf'),BaseOutputFilePath+'/'+'/HeatExchanger.pdf')


#################################################################################################
#end run the cycle
#################################################################################################

