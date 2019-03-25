###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


PrintExtra=False



from numpy import linspace,hstack,array,arange

import ParallelCycles					#need to import this way so that can set some variables the module needs
from ParallelCycles import RunParameterSweepPermutations,ParameterSweepAndOptimizeCombinedCycleWrapper,ReplicateCombinedCycleInputs,WriteAdditionalObjects
from helpers import iarange

from os.path import isfile
import cPickle


####################################################
#set some constant values
####################################################

import helpers
helpers.PrintWarningMessages=PrintExtra			#for some reason have to do it this way because if just import PrintWarningMessages, and then set it, python must think you are overwritting the imported PrintWarningMessages object with a new local one and so the module PrintWarningMessages is not changed.


#initialize the variables to label and store values for each variable to explore

#other values need to be separated from CO2 cycle since the CO2 cycle values are replicated
NonCO2CycleInitialGuessIndependentVariableValues=()
NonCO2CycleIndependentVariableValueLimits=()
NonCO2CycleFixedIndependentVariableValues=[]
NonCO2CycleSweptIndependentVariableValues=[]
NonCO2CycleIndependentVariableLabels=()
NonCO2CycleIndependentVariableMappings=()

#CO2 cycle
InitialGuessIndependentVariableValues=()
IndependentVariableValueLimits=()
CO2CycleFixedIndependentVariableValues=[]			#make a list instead of a tuple in this combined cycle optimization case because some fixed parameters (like maximum temperature) need to be changed.
CO2CycleSweptIndependentVariableValues=[]			#same as above
IndependentVariableLabels=()
IndependentVariableMappings=()

###define the parameters to be optimized, fixed, and swept###
#order of parameters doesn't matter within the groups, as long as the Labels and Mappings are grouped with their parameter definitions.
#order of parameter groups does matter



#####################################################
#define the initial guess and range for the independent variables to be optimized
#initial guess is a scalar and the range/limit is a tuple of two scalars, compared to arrays in the brute force design exploration mode
#####################################################

#set some overall values#

#need to set an upper limit on the number of engines that may be possible with this configuration.
MaxNumberOfEngines=6


#set values for the topping air cycle#

NonCO2CycleInitialGuessIndependentVariableValues+=(35.0,)
NonCO2CycleIndependentVariableValueLimits+=((10.0,45),)
NonCO2CycleIndependentVariableLabels+=('Gas Turbine Pressure Ratio',)
NonCO2CycleIndependentVariableMappings+=("CycleInputParameters['PressureRatio']",)


#CO2 engines#

InitialGuessIndependentVariableValues+=(2.0,)
IndependentVariableValueLimits+=((1,4),)
IndependentVariableLabels+=('PreCompressor Pressure Ratio',)
IndependentVariableMappings+=("CycleInputParameters['PreCompressor']['PressureRatio']",)

InitialGuessIndependentVariableValues+=(2.0,)
IndependentVariableValueLimits+=((1.1,4),)
IndependentVariableLabels+=('Main Compressor Pressure Ratio',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['PressureRatio']",)

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




#####################################################
#define independent variables that are not optimized
#these values are scalars
#####################################################

#set some overall values#

#limit the number of engines to allow in the combined cycle
NonCO2CycleFixedIndependentVariableValues+=(MaxNumberOfEngines,)		#includes the topping cycle
NonCO2CycleIndependentVariableLabels+=('Number of Engines',)
NonCO2CycleIndependentVariableMappings+=('NumberOfEngines',)


#set values for the topping air cycle#

#NonCO2CycleFixedIndependentVariableValues+=[1890.0,]								#used to have max of 1900K, but reduced because refprop had a max of 1993 and want to have 100K buffer on the max temperature so plotting functions don't have cycle points and contour levels all the way to the edge of the range.
#NonCO2CycleIndependentVariableLabels+=('Gas Turbine Rotor Inlet Temperature [K]',)
#NonCO2CycleIndependentVariableMappings+=("CycleInputParameters['MaximumTemperature']",)

NonCO2CycleFixedIndependentVariableValues+=[306.,]								#wanted to have 273+30=303, but that is a little below the critical point so move it up to 33C, since don't know that the code works with liquid vapor mixtures.
NonCO2CycleIndependentVariableLabels+=('Ambient Temperature [K]',)
NonCO2CycleIndependentVariableMappings+=("CycleInputParameters['StartingProperties']['Temperature']",)

NonCO2CycleFixedIndependentVariableValues+=[101*10**3,]
NonCO2CycleIndependentVariableLabels+=('Ambient Pressure [Pa]',)
NonCO2CycleIndependentVariableMappings+=("CycleInputParameters['MainCompressor']['InletPressure']",)


#CO2 engines#

CO2CycleFixedIndependentVariableValues+=[None,]								#must always be None for the combined cycle
IndependentVariableLabels+=('Maximum Temperature [K]',)
IndependentVariableMappings+=("CycleInputParameters['MaximumTemperature']",)

CO2CycleFixedIndependentVariableValues+=[None,]								#must always be None for the combined cycle
IndependentVariableLabels+=('Minimum Temperature [K]',)
IndependentVariableMappings+=("CycleInputParameters['StartingProperties']['Temperature']",)

CO2CycleFixedIndependentVariableValues+=[False,]
IndependentVariableLabels+=('ReHeat On',)
IndependentVariableMappings+=("CycleInputParameters['ReHeat']['Active']",)

CO2CycleFixedIndependentVariableValues+=[0.85,]
IndependentVariableLabels+=('Main Compressor Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['MainCompressor']['IsentropicEfficiency']",)

CO2CycleFixedIndependentVariableValues+=[0.875,]
IndependentVariableLabels+=('PreCompressor Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['PreCompressor']['IsentropicEfficiency']",)

CO2CycleFixedIndependentVariableValues+=[0.875,]
IndependentVariableLabels+=('ReCompressor Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['ReCompressor']['IsentropicEfficiency']",)

CO2CycleFixedIndependentVariableValues+=[0.93,]
IndependentVariableLabels+=('Power Turbine Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['PowerTurbine']['IsentropicEfficiency']",)

CO2CycleFixedIndependentVariableValues+=[0.89,]
IndependentVariableLabels+=('Main/Re/Pre Compressor Turbine Isentropic Efficiency',)
IndependentVariableMappings+=("CycleInputParameters['VirtualTurbine']['IsentropicEfficiency']",)

CO2CycleFixedIndependentVariableValues+=[5.0e2,]
IndependentVariableLabels+=('Heat Exchanger Pressure Drop [Pa/K]',)
IndependentVariableMappings+=("CycleInputParameters['DeltaPPerDeltaT']",)

CO2CycleFixedIndependentVariableValues+=[5,]
IndependentVariableLabels+=('Heat Exchanger Minimum Temperature Difference [K]',)
IndependentVariableMappings+=("CycleInputParameters['MinimumDeltaT']",)




#####################################################
#define the independent variables that are to be swept
#these are basically a fixed independent variable that are evaluated at many different fixed values.
#####################################################

#set some overall values#


#set values for the topping air cycle#

NonCO2CycleSweptIndependentVariableValues+=[linspace(1000+273.0,1890.0,num=20),]								#used to have max of 1900K, but reduced because refprop had a max of 1993 and want to have 100K buffer on the max temperature so plotting functions don't have cycle points and contour levels all the way to the edge of the range.
NonCO2CycleIndependentVariableLabels+=('Gas Turbine Rotor Inlet Temperature [K]',)
NonCO2CycleIndependentVariableMappings+=("CycleInputParameters['MaximumTemperature']",)


#CO2 engines#



#right now meshgrid is not generalized to support 1 dimensional inputs, so just send a fixed parameter in as a swept parameter, as a scalar array
CO2CycleSweptIndependentVariableValues+=(array(0),)
IndependentVariableLabels+=('Dummy Variable',)
IndependentVariableMappings+=("CycleInputParameters['Dummy']",)






#if an initial guess has already been built up, either in a saved file, manually defined, or already in memory in the interpreter from a previous run,
#ignore the values defined above
if isfile('./scratch/OptimizedCombinedCycleResult.p'):
	#load a saved result file
	AllEnginesInitialGuessIndependentVariableValues=cPickle.load(open('./scratch/OptimizedCombinedCycleResult.p', 'rb'))
elif False:
	#manually defined
	AllEnginesInitialGuessIndependentVariableValues=array([  3.50000000e+01,   1.56290810e+00,   3.99999958e+00,  3.45065559e-01,   5.04538832e-01,   1.00000000e+07, 1.25933763e+00,   3.75186129e+00,   3.02641706e-01, 5.03411281e-01,   1.00000000e+07,   1.22956778e+00, 2.25890055e+00,   2.77298954e-01,   5.00737133e-01,         1.00000000e+07,   1.23412373e+00,   1.46798136e+00,         9.90935796e-01,   5.00000000e-01,   1.00000000e+07,         2.00000000e+00,   2.00000000e+00,   5.00000000e-01,         5.00000000e-01,   1.00000000e+07])
elif 'AllEnginesInitialGuessIndependentVariableValues' not in globals():
	#used the values defined above
	#note, only the first engine will use this intial guess if CombinedOptimization is False, but just allowing more initial guess copies to be created for the sake of generality because it won't slow things down much at all to bother caring, and other parts of the code are simpler.
	AllEnginesInitialGuessIndependentVariableValues=ReplicateCombinedCycleInputs(NonCO2CycleInitialGuessIndependentVariableValues,InitialGuessIndependentVariableValues,MaxNumberOfEngines)
else:
	#use whatever is already in memory in the interpreter from a previous run.
	pass

AllEnginesIndependentVariableValueLimits=ReplicateCombinedCycleInputs(NonCO2CycleIndependentVariableValueLimits,IndependentVariableValueLimits,MaxNumberOfEngines)














####################################################

#assign some values so that when Optimize is run, they can be inherited and used
ParallelCycles.AllEnginesInitialGuessIndependentVariableValues=AllEnginesInitialGuessIndependentVariableValues
ParallelCycles.AllEnginesIndependentVariableValueLimits=AllEnginesIndependentVariableValueLimits

#note, this can be a tuple in this case and as below, ReplicateCombinedCycleInputs is done later for this variable in order to reduce unnecessary sweep permutations
ParallelCycles.FixedIndependentVariableValues=(NonCO2CycleFixedIndependentVariableValues,CO2CycleFixedIndependentVariableValues)

#note, IndependentVariableValues is used here to maintain compatibility with the brute force mode, which has everything sent to this variable.
#also note, ReplicateCombinedCycleInputs is done later for this variable in order to reduce unnecessary sweep permutations
ParallelCycles.IndependentVariableValues=NonCO2CycleSweptIndependentVariableValues+CO2CycleSweptIndependentVariableValues

ParallelCycles.IndependentVariableLabels=IndependentVariableLabels
ParallelCycles.NonCO2CycleIndependentVariableLabels=NonCO2CycleIndependentVariableLabels
ParallelCycles.IndependentVariableMappings=IndependentVariableMappings
ParallelCycles.NonCO2CycleIndependentVariableMappings=NonCO2CycleIndependentVariableMappings

ParallelCycles.ValueCount=(MaxNumberOfEngines,len(NonCO2CycleInitialGuessIndependentVariableValues),len(NonCO2CycleFixedIndependentVariableValues), len(NonCO2CycleSweptIndependentVariableValues))



ParallelCycles.PrintOutputs=PrintExtra			#think this may have been changed to helpers.PrintWarningMessages, so it is obsolete???
ParallelCycles.NumberOfCPUs=24				#note, setting this to 1 will not use joblib. if raising errors for debugging, seem to need to use 1 because joblib gives weird errors when a permutation has an exception. note error make more sense now that joblib was updated to a new version, but still need to set to serial mode to actually debug them.
ParallelCycles.RunName=helpers.GetCaseName()



#save out a few extra objects needed for post processing
WriteAdditionalObjects(ParallelCycles.FixedIndependentVariableValues,NonCO2CycleIndependentVariableLabels,ParallelCycles.ValueCount)

#optimize based on initial guesses and fixed values and swept values
Results=RunParameterSweepPermutations(ParameterSweepAndOptimizeCombinedCycleWrapper)







