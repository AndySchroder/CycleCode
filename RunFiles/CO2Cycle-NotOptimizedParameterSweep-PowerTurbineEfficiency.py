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



from helpers import irange

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

#actually not doing optimization here but still doing a parameter sweep.
#not using the old brute force parameter sweep mode because don't think the post processor is up to date
#and this is currently the quickest thing to do to get a parameter sweep of power turbine efficiency without changing the other parameters that are normally optimized
IndependentVariableValueLimits+=((0,1),)
IndependentVariableLabels+=('Dummy Variable',)
IndependentVariableMappings+=("CycleInputParameters['Dummy']",)





#since just optimizing a dummy variable, try to make the optimizer run as little as possible

FixedIndependentVariableValues+=(10,)
IndependentVariableLabels+=('Optimizer Polish Tolerance',)
IndependentVariableMappings+=("polishtol",)

FixedIndependentVariableValues+=(1,)
IndependentVariableLabels+=('Optimizer Polish Max Iterations',)
IndependentVariableMappings+=("polishmaxiter",)


FixedIndependentVariableValues+=(3,)
IndependentVariableLabels+=('Optimizer Population Size',)
IndependentVariableMappings+=("popsize",)

FixedIndependentVariableValues+=(10,)
IndependentVariableLabels+=('Optimizer Tolerance',)
IndependentVariableMappings+=("tol",)





#define independent variables that are not optimized
#these values are scalars


#get the optimized values from a previous run

from helpers import SmartDictionary,RoundAndPadToString
import cPickle
BaseInputFilePath='outputs/'
CaseName='CO2Cycle-Optimized'
CycleParametersOptimized=cPickle.load(open(BaseInputFilePath+'/'+CaseName+'/Results.p', 'rb'))[0]

FixedIndependentVariableValues+=(CycleParametersOptimized['PreCompressor']['PressureRatio'],)
IndependentVariableLabels+=('PreCompressor Pressure Ratio',)
IndependentVariableMappings+=("CycleInputParameters['PreCompressor']['PressureRatio']",)

FixedIndependentVariableValues+=(CycleParametersOptimized['MainCompressor']['PressureRatio'],)
IndependentVariableLabels+=('Main Compressor Pressure Ratio',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['PressureRatio']",)

FixedIndependentVariableValues+=(CycleParametersOptimized['ReCompressor']['MassFraction'],)
IndependentVariableLabels+=('Recompression Fraction',)
IndependentVariableMappings+=("CycleInputParameters['RecompressionFraction']",)

FixedIndependentVariableValues+=(0,)
IndependentVariableLabels+=('Low Temperature Recuperator Main Fraction High Pressure Component Mass Fraction',)
IndependentVariableMappings+=("CycleInputParameters['LTRecuperator']['MainFraction']['HighPressure']['ComponentMassFraction']",)

FixedIndependentVariableValues+=(CycleParametersOptimized['MainCompressor']['CompressedProperties']['Pressure'],)
IndependentVariableLabels+=('Main Compressor Outlet Pressure [Pa]',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['OutletPressure']",)





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

#FixedIndependentVariableValues+=(0.93,)
#IndependentVariableLabels+=('Power Turbine Isentropic Efficiency',)
#IndependentVariableMappings+=("CycleInputParameters['PowerTurbine']['IsentropicEfficiency']",)

FixedIndependentVariableValues+=(0.89,)
IndependentVariableLabels+=('Main/Re/Pre Compressor Turbine Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['VirtualTurbine']['IsentropicEfficiency']",)

FixedIndependentVariableValues+=(5.0e2,)
IndependentVariableLabels+=('Heat Exchanger Pressure Drop [Pa/K]',)
IndependentVariableMappings+=("CycleInputParameters['DeltaPPerDeltaT']",)

FixedIndependentVariableValues+=(5,)
IndependentVariableLabels+=('Heat Exchanger Minimum Temperature Difference [K]',)
IndependentVariableMappings+=("CycleInputParameters['MinimumDeltaT']",)




#define the independent variables that are to be swept
#these are basically a fixed independent variable that are evaluated at many different fixed values.


SweptIndependentVariableValues+=(linspace(-1,1,51)*.03+0.93,)
IndependentVariableLabels+=('Power Turbine Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['PowerTurbine']['IsentropicEfficiency']",)

#right now meshgrid is not generalized to support 1 dimensional inputs, so just send a fixed parameter in as a swept parameter, as a scalar array
SweptIndependentVariableValues+=(array(0),)
IndependentVariableLabels+=('Dummy Variable',)
IndependentVariableMappings+=("CycleInputParameters['Dummy']",)


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



