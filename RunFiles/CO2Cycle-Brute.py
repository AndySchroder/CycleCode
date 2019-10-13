###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


from numpy import linspace,hstack
from ParallelCycles import RunPermutations
import ParallelCycles					#need to import this way so that can set some variables the module needs

####################################################
#set some constant values
####################################################

import helpers
helpers.PrintWarningMessages=False


####################################################
#setup the ranges for the independent variables to be optimized.
####################################################
#initialize the variables to label and store values for each variable to explore
IndependentVariableValues=()
IndependentVariableLabels=()
IndependentVariableMappings=()


IndependentVariableValues+=(linspace(1,4,num=4),)
IndependentVariableLabels+=('PreCompressor Pressure Ratio',)
IndependentVariableMappings+=("CycleInputParameters['PreCompressor']['PressureRatio']",)

IndependentVariableValues+=(linspace(1.1,4.1,num=4),)		#have to have the lower value of either the main compressor or precompressor be greater than 1
IndependentVariableLabels+=('Main Compressor Pressure Ratio',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['PressureRatio']",)

IndependentVariableValues+=(linspace(0,.991,num=4),)			#can't exactly have 1 because heat exchanger function has a problem if high pressure mass fraction ends up being 0
IndependentVariableLabels+=('Recompression Fraction',)
IndependentVariableMappings+=("CycleInputParameters['RecompressionFraction']",)

IndependentVariableValues+=(linspace(.0010,.991,num=4),)		#can't exactly have 0 or 1 because heat exchanger function has a problem if high pressure mass fraction ends up being 0
IndependentVariableLabels+=('Low Temperature Recuperator Main Fraction High Pressure Component Mass Fraction',)
IndependentVariableMappings+=("CycleInputParameters['LTRecuperator']['MainFraction']['HighPressure']['ComponentMassFraction']",)

IndependentVariableValues+=(linspace(2e6,35e6,num=4),)
IndependentVariableLabels+=('Main Compressor Outlet Pressure [Pa]',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['OutletPressure']",)

IndependentVariableValues+=(linspace(525,650,num=2)+273.0,)
IndependentVariableLabels+=('Maximum Temperature [K]',)
IndependentVariableMappings+=("CycleInputParameters['MaximumTemperature']",)

IndependentVariableValues+=(linspace(47,60,num=2)+273.0,)	#for some reason temperatures below 47C aren't working. need to run out of optimizer mode in order to figure out where the problem is happening
IndependentVariableLabels+=('Minimum Temperature [K]',)
IndependentVariableMappings+=("CycleInputParameters['StartingProperties']['Temperature']",)

IndependentVariableValues+=(hstack((linspace(.75,.95,num=2),1.0)),)
IndependentVariableLabels+=('Main Compressor Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['IsentropicEfficiency']",)

IndependentVariableValues+=(hstack((linspace(.80,.95,num=2),)),)
IndependentVariableLabels+=('PreCompressor Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['PreCompressor']['IsentropicEfficiency']",)

IndependentVariableValues+=(hstack((linspace(.80,.95,num=2),)),)
IndependentVariableLabels+=('ReCompressor Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['ReCompressor']['IsentropicEfficiency']",)

IndependentVariableValues+=(hstack((linspace(.89,.93,num=2),)),)
IndependentVariableLabels+=('Power Turbine Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['PowerTurbine']['IsentropicEfficiency']",)

IndependentVariableValues+=(hstack((linspace(.84,.89,num=2),)),)
IndependentVariableLabels+=('Main/Re/Pre Compressor Turbine Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['VirtualTurbine']['IsentropicEfficiency']",)

IndependentVariableValues+=(linspace(0.0,5.0e2,num=2),)
IndependentVariableLabels+=('Heat Exchanger Pressure Drop [Pa/K]',)
IndependentVariableMappings+=("CycleInputParameters['DeltaPPerDeltaT']",)

IndependentVariableValues+=(5,)
IndependentVariableLabels+=('Heat Exchanger Minimum Temperature Difference [K]',)
IndependentVariableMappings+=("CycleInputParameters['MinimumDeltaT']",)



####################################################


#run the permutations assigned



#assign some values so that when the RunPermutations is run, they can be inherited and used
ParallelCycles.IndependentVariableMappings=IndependentVariableMappings
ParallelCycles.IndependentVariableValues=IndependentVariableValues
ParallelCycles.IndependentVariableLabels=IndependentVariableLabels

ParallelCycles.PrintOutputs=False
ParallelCycles.NumberOfCPUs=2				#note, setting this to 1 will not use joblib. if raising errors for debugging, seem to need to use 1 because joblib gives weird errors when a permutation has an exception. note error make more sense now that joblib was updated to a new version, but still need to set to serial mode to actually debug them.
ParallelCycles.RunName=helpers.GetCaseName()

Results=RunPermutations()











