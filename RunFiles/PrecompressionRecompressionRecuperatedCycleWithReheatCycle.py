###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


PrintExtra=True

from Cycles import PreCompressionReCompressionCycleWithReheat
from helpers import SmartDictionary,WriteBinaryData,PrintKeysAndValues
import ComponentPreliminaryDesign
import helpers
helpers.PrintWarningMessages=PrintExtra			#for some reason have to do it this way because if just import PrintWarningMessages, and then set it, python must think you are overwritting the imported PrintWarningMessages object with a new local one and so the module PrintWarningMessages is not changed.

#import plotting functions
from Plotters import PlotCycle,PlotHeatExchanger

#set some input values that have been commented out in the main input file.
CycleInputParameters=SmartDictionary()

CycleInputParameters['StartingProperties']['Temperature']=47.0+273.0
CycleInputParameters['MaximumTemperature']=525.0+273.0

CycleInputParameters['MainCompressor']['OutletPressure']=7*10**6#11.0*10**6
CycleInputParameters['MainCompressor']['PressureRatio']=5#1.42304205

#CycleInputParameters['PreCompressor']['PressureRatio']=1.92280632
CycleInputParameters['PreCompressor']['PressureRatio']=1.035
CycleInputParameters['RecompressionFraction']=0.2723962

CycleInputParameters['LTRecuperator']['MainFraction']['HighPressure']['ComponentMassFraction']=.75	#note, this is the mass fraction of the total mass flow through the LTR, and not the fraction of total mass flow. it is later converted to the total mass flow fraction in the InputParameters file. maybe this should be changed?

CycleInputParameters['MainCompressor']['IsentropicEfficiency']=0.85
CycleInputParameters['PreCompressor']['IsentropicEfficiency']=0.875
CycleInputParameters['ReCompressor']['IsentropicEfficiency']=0.875

CycleInputParameters['PowerTurbine']['IsentropicEfficiency']=0.93
CycleInputParameters['VirtualTurbine']['IsentropicEfficiency']=0.89

CycleInputParameters['DeltaPPerDeltaT']=5.0e2
CycleInputParameters['MinimumDeltaT']=5




#choose the input parameters file
execfile('./InputParameters/InputParameters-CO2.py')



#################################################################################################
#run the cycle
#################################################################################################
CycleParameters=PreCompressionReCompressionCycleWithReheat(CycleInputParameters)

#print values
if PrintExtra and CycleParameters['SpecificNetWork']>0:
	
	#compute mass flow rate for the design required power
	CycleParameters['MassFlowRate']=CycleInputParameters['PowerOutput']/CycleParameters['SpecificNetWork']

	#compute static properties and inlet geometry for the compressor and turbine
#	CycleParameters['MainCompressor']['InletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate']*CycleInputParameters['MainCompressor']['MassFraction'],CycleParameters['MainCompressor']['StartingProperties'],CycleInputParameters['MainCompressor']['InletPiping'])
#	CycleParameters['MainCompressor']=ComponentPreliminaryDesign.ComputeCompressorParameters(CycleParameters['MassFlowRate']*CycleInputParameters['MainCompressor']['MassFraction'],CycleParameters['MainCompressor'],CycleInputParameters['MainCompressor'])
#	CycleParameters['MainCompressor']['OutletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate']*CycleInputParameters['MainCompressor']['MassFraction'],CycleParameters['MainCompressor']['CompressedProperties'],CycleInputParameters['MainCompressor']['OutletPiping'])
#see note in the ComputePiping function on what needs to be done to make the above lines work

#	CycleParameters['PreCompressor']['InletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate']*CycleInputParameters['PreCompressor']['MassFraction'],CycleParameters['PreCompressor']['StartingProperties'],CycleInputParameters['PreCompressor']['InletPiping'])
#	CycleParameters['PreCompressor']=ComponentPreliminaryDesign.ComputeCompressorParameters(CycleParameters['MassFlowRate']*CycleInputParameters['PreCompressor']['MassFraction'],CycleParameters['PreCompressor'],CycleInputParameters['PreCompressor'])
#	CycleParameters['PreCompressor']['OutletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate']*CycleInputParameters['PreCompressor']['MassFraction'],CycleParameters['PreCompressor']['CompressedProperties'],CycleInputParameters['PreCompressor']['OutletPiping'])


	CycleParameters['MainCompressorTurbine']['InletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate']*CycleParameters['MainCompressorTurbine']['MassFraction'],CycleParameters['MainCompressorTurbine']['StartingProperties'],CycleInputParameters['MainCompressorTurbine']['InletPiping'])
	CycleParameters['MainCompressorTurbine']['OutletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate']*CycleParameters['MainCompressorTurbine']['MassFraction'],CycleParameters['MainCompressorTurbine']['ExpandedProperties'],CycleInputParameters['MainCompressorTurbine']['OutletPiping'])

	CycleParameters['PreCompressorTurbine']['InletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate']*CycleParameters['PreCompressorTurbine']['MassFraction'],CycleParameters['PreCompressorTurbine']['StartingProperties'],CycleInputParameters['PreCompressorTurbine']['InletPiping'])
	CycleParameters['PreCompressorTurbine']['OutletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate']*CycleParameters['PreCompressorTurbine']['MassFraction'],CycleParameters['PreCompressorTurbine']['ExpandedProperties'],CycleInputParameters['PreCompressorTurbine']['OutletPiping'])

	CycleParameters['PowerTurbine']['InletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate'],CycleParameters['PowerTurbine']['StartingProperties'],CycleInputParameters['PowerTurbine']['InletPiping'])
	CycleParameters['PowerTurbine']['OutletPiping']=ComponentPreliminaryDesign.ComputePiping(CycleParameters['MassFlowRate'],CycleParameters['PowerTurbine']['ExpandedProperties'],CycleInputParameters['PowerTurbine']['OutletPiping'])

	CycleParameters['MainCompressor']=ComponentPreliminaryDesign.ComputeTurbomachineryParameters(CycleParameters['MassFlowRate']*CycleInputParameters['MainCompressor']['MassFraction'],CycleParameters['MainCompressor'],CycleInputParameters['MainCompressor'])
	CycleParameters['PreCompressor']=ComponentPreliminaryDesign.ComputeTurbomachineryParameters(CycleParameters['MassFlowRate']*CycleInputParameters['PreCompressor']['MassFraction'],CycleParameters['PreCompressor'],CycleInputParameters['PreCompressor'])
	CycleParameters['ReCompressor']=ComponentPreliminaryDesign.ComputeTurbomachineryParameters(CycleParameters['MassFlowRate']*CycleInputParameters['ReCompressor']['MassFraction'],CycleParameters['ReCompressor'],CycleInputParameters['ReCompressor'])

	CycleParameters['MainCompressorTurbine']=ComponentPreliminaryDesign.ComputeTurbomachineryParameters(CycleParameters['MassFlowRate']*CycleParameters['MainCompressorTurbine']['MassFraction'],CycleParameters['MainCompressorTurbine'],CycleInputParameters['MainCompressorTurbine'])
	CycleParameters['PreCompressorTurbine']=ComponentPreliminaryDesign.ComputeTurbomachineryParameters(CycleParameters['MassFlowRate']*CycleParameters['PreCompressorTurbine']['MassFraction'],CycleParameters['PreCompressorTurbine'],CycleInputParameters['PreCompressorTurbine'])
	CycleParameters['ReCompressorTurbine']=ComponentPreliminaryDesign.ComputeTurbomachineryParameters(CycleParameters['MassFlowRate']*CycleParameters['ReCompressorTurbine']['MassFraction'],CycleParameters['ReCompressorTurbine'],CycleInputParameters['ReCompressorTurbine'])

	CycleParameters['PowerTurbine']=ComponentPreliminaryDesign.ComputeTurbomachineryParameters(CycleParameters['MassFlowRate'],CycleParameters['PowerTurbine'],CycleInputParameters['PowerTurbine'])

	PrintKeysAndValues("Cycle Input Parameters",CycleInputParameters)
	PrintKeysAndValues("Cycle Outputs",CycleParameters)


print 'Carnot Cycle: '+str(CycleParameters['CycleCarnotEfficiency'])
print 'Real Cycle:   '+str(CycleParameters['CycleRealEfficiency'])




if PrintExtra and CycleParameters['SpecificNetWork']>0:
	WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='SpecificVolume',VerticalAxis='Pressure',ContourLevel='cp',ImageFileType='pdf'),'./scratch/testimage.pdf')



#################################################################################################
#end run the cycle
#################################################################################################

