###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


#################################################################################################
#Input parameters
#################################################################################################

###########################
#cycle input parameters
###########################

CycleInputParameters['MaximumTemperature']=650.0+273.0
CycleInputParameters['StartingProperties']['Temperature']=273.0+47

CycleInputParameters['FluidType']='Carbon Dioxide'

CycleInputParameters['PowerOutput']=1.0*10**6	#1MW


###########################
#common recuperator parameters
DeltaPPerDeltaT=0




###########################
#piston related design assumptions and required pressure ratio
###########################
CycleInputParameters['Piston']['MassFraction']=1.0

CycleInputParameters['Piston']['IsentropicEfficiency']=1.0



###########################
#heater related design assumptions
###########################
CycleInputParameters['SecondPlusThirdHeating']['MaximumTemperature']=CycleInputParameters['MaximumTemperature']
CycleInputParameters['SecondPlusThirdHeating']['MassFraction']=1
CycleInputParameters['SecondPlusThirdHeating']['DeltaPPerDeltaT']=DeltaPPerDeltaT

###########################
#cooler related design assumptions
###########################

CycleInputParameters['TotalFractionCooler']['MinimumTemperature']=CycleInputParameters['StartingProperties']['Temperature']
CycleInputParameters['TotalFractionCooler']['MassFraction']=1
CycleInputParameters['TotalFractionCooler']['DeltaPPerDeltaT']=DeltaPPerDeltaT



###########################
#recuperator related design assumptions
###########################
CycleInputParameters['HTRecuperator']['NumberofTemperatures']=200					#keep in mind that the resolution of the data being interpolated is the real upper limit on the usefulness of this value
CycleInputParameters['HTRecuperator']['LowPressure']['MassFraction']=1
CycleInputParameters['HTRecuperator']['HighPressure']['MassFraction']=1
CycleInputParameters['HTRecuperator']['HighPressure']['ConstantVolume']=True
CycleInputParameters['HTRecuperator']['DeltaPPerDeltaT']=DeltaPPerDeltaT				#maybe this should be different for high and low pressure sides?
CycleInputParameters['HTRecuperator']['MinimumDeltaT']=0

#################################################################################################
#end Input parameters
#################################################################################################
