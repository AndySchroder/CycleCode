###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


PrintExtra=True



from numpy import linspace,hstack,array

import ParallelCycles					#need to import this way so that can set some variables the module needs
from ParallelCycles import RunParameterSweepPermutations,ParameterSweepAndOptimizeCycleWrapper,WriteAdditionalObjects





####################################################
#set some constant values
####################################################

import helpers
helpers.PrintWarningMessages=False


####################################################
#setup the ranges for the independent variables to be optimized.
####################################################
#initialize the variables to label and store values for each variable to explore
InitialGuessIndependentVariableValues=()
IndependentVariableValueLimits=()
SweptIndependentVariableValues=()
FixedIndependentVariableValues=()
IndependentVariableLabels=()
IndependentVariableMappings=()


###define the parameters to be optimized, fixed, and swept###
#order of parameters doesn't matter within the groups, as long as the Labels and Mappings are grouped with their parameter definitions.
#order of parameter groups does matter

#define the initial guess and range for the independent variables to be optimized
#initial guess is a scalar and the range/limit is a tuple of two scalars, compared to arrays in the brute force design exploration mode

#InitialGuessIndependentVariableValues+=(2.0,)
#IndependentVariableValueLimits+=((1,4),)
#IndependentVariableLabels+=('PreCompressor Pressure Ratio',)
#IndependentVariableMappings+=("CycleInputParameters['PreCompressor']['PressureRatio']",)

#InitialGuessIndependentVariableValues+=(2.0,)
#IndependentVariableValueLimits+=((1.1,4),)
#IndependentVariableLabels+=('Main Compressor Pressure Ratio',)
#IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['PressureRatio']",)

InitialGuessIndependentVariableValues+=(0.5,)
IndependentVariableValueLimits+=((.0010,.991),)			#can't exactly have 0 or 1 because heat exchanger function has a problem if high pressure mass fraction ends up being 0
IndependentVariableLabels+=('Recompression Fraction',)
IndependentVariableMappings+=("CycleInputParameters['RecompressionFraction']",)

InitialGuessIndependentVariableValues+=(0.5,)
IndependentVariableValueLimits+=((.0010,.991),)			#can't exactly have 0 or 1 because heat exchanger function has a problem if high pressure mass fraction ends up being 0
IndependentVariableLabels+=('Low Temperature Recuperator Main Fraction High Pressure Component Mass Fraction',)
IndependentVariableMappings+=("CycleInputParameters['LTRecuperator']['MainFraction']['HighPressure']['ComponentMassFraction']",)

InitialGuessIndependentVariableValues+=(25e6,)
IndependentVariableValueLimits+=((2e6,35e6),)
IndependentVariableLabels+=('Main Compressor Outlet Pressure [Pa]',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['OutletPressure']",)






#define independent variables that are not optimized
#these values are scalars

FixedIndependentVariableValues+=(650.0+273.0,)
IndependentVariableLabels+=('Maximum Temperature [K]',)
IndependentVariableMappings+=("CycleInputParameters['MaximumTemperature']",)

FixedIndependentVariableValues+=(47.0+273.0,)	#for some reason temperatures below 47C aren't working. need to troubleshoot in serial design explorer mode
IndependentVariableLabels+=('Minimum Temperature [K]',)
IndependentVariableMappings+=("CycleInputParameters['StartingProperties']['Temperature']",)

FixedIndependentVariableValues+=(True,)
IndependentVariableLabels+=('ReHeat On',)
IndependentVariableMappings+=("CycleInputParameters['ReHeat']['Active']",)

FixedIndependentVariableValues+=(0.85,)
IndependentVariableLabels+=('Main Compressor Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['IsentropicEfficiency']",)

FixedIndependentVariableValues+=(False,)
IndependentVariableLabels+=('Electrically Powere Main Compressor',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['ElectricallyPowered']",)

FixedIndependentVariableValues+=(0.875,)
IndependentVariableLabels+=('PreCompressor Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['PreCompressor']['IsentropicEfficiency']",)

FixedIndependentVariableValues+=(0.875,)
IndependentVariableLabels+=('ReCompressor Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['ReCompressor']['IsentropicEfficiency']",)

FixedIndependentVariableValues+=(0.93,)
IndependentVariableLabels+=('Power Turbine Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['PowerTurbine']['IsentropicEfficiency']",)

FixedIndependentVariableValues+=(0.89,)
IndependentVariableLabels+=('Main/Re/Pre Compressor Turbine Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['VirtualTurbine']['IsentropicEfficiency']",)

FixedIndependentVariableValues+=(5.0e2,)
IndependentVariableLabels+=('Heat Exchanger Pressure Drop [Pa/K]',)
IndependentVariableMappings+=("CycleInputParameters['DeltaPPerDeltaT']",)

FixedIndependentVariableValues+=(0.0,)
IndependentVariableLabels+=('Heat Exchanger Minimum Temperature Difference [K]',)
IndependentVariableMappings+=("CycleInputParameters['MinimumDeltaT']",)




#define the independent variables that are to be swept
#these are basically a fixed independent variable that are evaluated at many different fixed values.

SweptIndependentVariableValues+=(linspace(1,4,num=20),)
IndependentVariableLabels+=('PreCompressor Pressure Ratio',)
IndependentVariableMappings+=("CycleInputParameters['PreCompressor']['PressureRatio']",)

SweptIndependentVariableValues+=(linspace(1.1,4.1,num=20),)
IndependentVariableLabels+=('Main Compressor Pressure Ratio',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['PressureRatio']",)

####################################################

#assign some values so that when Optimize is run, they can be inherited and used
ParallelCycles.IndependentVariableMappings=IndependentVariableMappings
ParallelCycles.IndependentVariableLabels=IndependentVariableLabels
ParallelCycles.IndependentVariableValueLimits=IndependentVariableValueLimits
ParallelCycles.InitialGuessIndependentVariableValues=InitialGuessIndependentVariableValues
ParallelCycles.FixedIndependentVariableValues=FixedIndependentVariableValues
ParallelCycles.IndependentVariableValues=SweptIndependentVariableValues					#note, IndependentVariableValues is used here to maintain compatibility with the brute force mode, which has everything sent to this variable


#optimize based on initial guesses and fixed values

ParallelCycles.PrintOutputs=False			#think this may have been changed to helpers.PrintWarningMessages, so it is obsolete???
ParallelCycles.NumberOfCPUs=24				#note, setting this to 1 will not use joblib. if raising errors for debugging, seem to need to use 1 because joblib gives weird errors when a permutation has an exception. note error make more sense now that joblib was updated to a new version, but still need to set to serial mode to actually debug them.
ParallelCycles.RunName=helpers.GetCaseName()

#save out a few extra objects needed for post processing
WriteAdditionalObjects(FixedIndependentVariableValues,None,None)

Results=RunParameterSweepPermutations(ParameterSweepAndOptimizeCycleWrapper)



