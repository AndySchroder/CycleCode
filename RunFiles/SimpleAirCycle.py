###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


PrintExtra=True

from FluidProperties.REFPROP import SetupFluid
SetupFluid('air')

from Cycles import SimpleCycle
from helpers import SmartDictionary,WriteBinaryData,PrintKeysAndValues
import ComponentPreliminaryDesign
import helpers
helpers.PrintWarningMessages=PrintExtra			#for some reason have to do it this way because if just import PrintWarningMessages, and then set it, python must think you are overwritting the imported PrintWarningMessages object with a new local one and so the module PrintWarningMessages is not changed.

#import plotting functions
from Plotters import PlotCycle,PlotHeatExchanger

#set some input values that have been commented out in the main input file.
CycleInputParameters=SmartDictionary()

CycleInputParameters['MainCompressor']['InletPressure']=0.101*10**6

CycleInputParameters['PressureRatio']=37.15

#CycleInputParameters['PressureRatio']=31.25
#CycleInputParameters['PressureRatio']=25.0
#CycleInputParameters['PressureRatio']=6.52

CycleInputParameters['MaximumTemperature']=1890.
#CycleInputParameters['MaximumTemperature']=1452.
CycleInputParameters['StartingProperties']['Temperature']=273.0+33

#choose the input parameters file
execfile('./InputParameters/InputParameters-SimpleAirCycle.py')



#################################################################################################
#run the cycle
#################################################################################################
CycleParameters=SimpleCycle(CycleInputParameters)

#print values
if PrintExtra and (CycleParameters['CycleRealEfficiency']>0.0):			#don't do if a bad cycle, because some functions are probably going to error out.

	#compute mass flow rate for the design required power
	CycleParameters['MassFlowRate']=CycleInputParameters['PowerOutput']/CycleParameters['SpecificNetWork']

	#compute static properties and inlet geometry for the compressor and turbine
#	CycleParameters['MainCompressor']['InletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate']*CycleInputParameters['MainCompressor']['MassFraction'],CycleParameters['MainCompressor']['StartingProperties'],CycleInputParameters['MainCompressor']['InletPiping'])
#	CycleParameters['MainCompressor']=ComponentPreliminaryDesign.ComputeCompressorParameters(CycleParameters['MassFlowRate']*CycleInputParameters['MainCompressor']['MassFraction'],CycleParameters['MainCompressor'],CycleInputParameters['MainCompressor'])
#	CycleParameters['MainCompressor']['OutletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate']*CycleInputParameters['MainCompressor']['MassFraction'],CycleParameters['MainCompressor']['CompressedProperties'],CycleInputParameters['MainCompressor']['OutletPiping'])


#	CycleParameters['PowerTurbine']['InletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate'],CycleParameters['PowerTurbine']['StartingProperties'],CycleInputParameters['PowerTurbine']['InletPiping'])
#	CycleParameters['PowerTurbine']['OutletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate'],CycleParameters['PowerTurbine']['ExpandedProperties'],CycleInputParameters['PowerTurbine']['OutletPiping'])

#	CycleParameters['PowerTurbine']=ComponentPreliminaryDesign.ComputeTurbomachineryParameters(CycleParameters['MassFlowRate'],CycleParameters['PowerTurbine'],CycleInputParameters['PowerTurbine'])

if PrintExtra:									#still plot the values if a bad cycle so can review if troubleshooting
	PrintKeysAndValues("Cycle Input Parameters",CycleInputParameters)
	PrintKeysAndValues("Cycle Outputs",CycleParameters)


print 'Carnot Cycle: '+str(CycleParameters['CycleCarnotEfficiency'])
print 'Real Cycle:   '+str(CycleParameters['CycleRealEfficiency'])




#if PrintExtra and (CycleParameters['CycleRealEfficiency']>0.0):			#don't do if a bad cycle, because some functions are probably going to error out.
#	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='gamma'),'./scratch/testimage.png')
#need to fix this to work with AIR


#################################################################################################
#end run the cycle
#################################################################################################

