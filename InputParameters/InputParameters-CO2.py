###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


#################################################################################################
#Input parameters
#################################################################################################
#this file is executed rather than imported, so it is also not a function. doing it this way
#because may want to change some of these things and it is easier to reference as a string
#if importing and it doesn't totally make sense to have configuration variables in a module

#many things in here could be defined as inputs, but they aren't for now because not really
#exploring everything, so this can sort of be looked at as a default values file
#however, may want to quickly change something, just be swapping out the default
#values file, rather than make everything that runs also have that value no longer revert
#to the default, so keeping it this way.
#################################################################################################





#################################################################################################
#values that are not defined by this input file and must be defined first by whatever executes this file
#################################################################################################

#CycleInputParameters['PreCompressor']['PressureRatio']
#CycleInputParameters['MainCompressor']['PressureRatio']
#CycleInputParameters['RecompressionFraction']
#CycleInputParameters['LTRecuperator']['MainFraction']['HighPressure']['ComponentMassFraction']
#CycleInputParameters['MainCompressor']['OutletPressure']
#CycleInputParameters['MaximumTemperature']
#CycleInputParameters['StartingProperties']['Temperature']
#CycleInputParameters['MainCompressor']['IsentropicEfficiency']
#CycleInputParameters['PreCompressor']['IsentropicEfficiency']
#CycleInputParameters['ReCompressor']['IsentropicEfficiency']
#CycleInputParameters['PowerTurbine']['IsentropicEfficiency']
#CycleInputParameters['VirtualTurbine']['IsentropicEfficiency']
#CycleInputParameters['DeltaPPerDeltaT']
#CycleInputParameters['MinimumDeltaT']





#################################################################################################
#cycle input parameters
#################################################################################################


###########################
#common recuperator parameters
###########################
NumberofTemperatures=200					#keep in mind that the resolution of the data being interpolated is the real upper limit on the usefulness of this value


###########################
#Common compressor parameters
CompressorInletPipingVelocity=15.0				#m/s
CompressorHubToTipRatio=.7					#assumes axial design only and constant radius?
CompressorRotorTipMetalVelocity=300.				#m/s
IGVVelocity=15.0						#m/s		#150.0 was giving problems so just changed to 15.0 to make things run since not even looking at what this does right now anyway.






#################################################################################################
#values used by ComponentPreliminaryDesign, which don't effect the efficiency or layout of the engine
#################################################################################################

CycleInputParameters['PowerOutput']=1.0*10**6	#1MW

CycleInputParameters['PreCompressor']['Ns']=1.5
CycleInputParameters['PreCompressor']['StageCount']=2

CycleInputParameters['MainCompressor']['Ns']=1.0
CycleInputParameters['MainCompressor']['StageCount']=1

CycleInputParameters['ReCompressor']['Ns']=.75
CycleInputParameters['ReCompressor']['StageCount']=1

CycleInputParameters['MainCompressorTurbine']['Ns']=1.5
CycleInputParameters['MainCompressorTurbine']['StageCount']=1

CycleInputParameters['PreCompressorTurbine']['Ns']=1.5
CycleInputParameters['PreCompressorTurbine']['StageCount']=1

CycleInputParameters['ReCompressorTurbine']['Ns']=.75
CycleInputParameters['ReCompressorTurbine']['StageCount']=1

CycleInputParameters['PowerTurbine']['Ns']=1.5
CycleInputParameters['PowerTurbine']['StageCount']=3








#################################################################################################
#dependent values (currently) or fixed values by design or based on a common value
#some are used by the cycle and some are used by ComponentPreliminaryDesign
#################################################################################################

CycleInputParameters['MainFraction']=1.0-CycleInputParameters['RecompressionFraction']

CompressorOutletPipingVelocity=CompressorInletPipingVelocity

###########################
#Common turbine parameters
###########################
TurbineInletPipingVelocity=CompressorInletPipingVelocity
TurbineOutletPipingVelocity=CompressorOutletPipingVelocity

###########################
#pre compressor related design assumptions and required pressure ratio
###########################
CycleInputParameters['PreCompressor']['MassFraction']=1

CycleInputParameters['PreCompressor']['InletPiping']['Velocity']=CompressorInletPipingVelocity
CycleInputParameters['PreCompressor']['OutletPiping']['Velocity']=CompressorOutletPipingVelocity

CycleInputParameters['PreCompressor']['HubToTipRatio']=CompressorHubToTipRatio
CycleInputParameters['PreCompressor']['RotorTipMetalVelocity']=CompressorRotorTipMetalVelocity
CycleInputParameters['PreCompressor']['IGVVelocity']=IGVVelocity

###########################
#main compressor related design assumptions and required pressure ratio
###########################
CycleInputParameters['MainCompressor']['MassFraction']=CycleInputParameters['MainFraction']

CycleInputParameters['MainCompressor']['InletPiping']['Velocity']=CompressorInletPipingVelocity
CycleInputParameters['MainCompressor']['OutletPiping']['Velocity']=CompressorOutletPipingVelocity

CycleInputParameters['MainCompressor']['HubToTipRatio']=CompressorHubToTipRatio
CycleInputParameters['MainCompressor']['RotorTipMetalVelocity']=CompressorRotorTipMetalVelocity
CycleInputParameters['MainCompressor']['IGVVelocity']=IGVVelocity

###########################
#Re compressor related design assumptions and required pressure ratio
###########################
CycleInputParameters['ReCompressor']['MassFraction']=CycleInputParameters['RecompressionFraction']

CycleInputParameters['ReCompressor']['InletPiping']['Velocity']=CompressorInletPipingVelocity
CycleInputParameters['ReCompressor']['OutletPiping']['Velocity']=CompressorOutletPipingVelocity

CycleInputParameters['ReCompressor']['HubToTipRatio']=CompressorHubToTipRatio
CycleInputParameters['ReCompressor']['RotorTipMetalVelocity']=CompressorRotorTipMetalVelocity
CycleInputParameters['ReCompressor']['IGVVelocity']=IGVVelocity

###########################
#virtual turbine that represents three compressors' turbines in parallel. assumes all three turbines have the same efficiency
###########################
CycleInputParameters['VirtualTurbine']['MassFraction']=1

CycleInputParameters['VirtualTurbine']['MaximumTemperature']=CycleInputParameters['MaximumTemperature']

###########################
#main compressor turbine related design assumptions and required pressure ratio
###########################
CycleInputParameters['MainCompressorTurbine']['InletPiping']['Velocity']=TurbineInletPipingVelocity
CycleInputParameters['MainCompressorTurbine']['OutletPiping']['Velocity']=TurbineOutletPipingVelocity

###########################
#PreCompressor turbine related design assumptions and required pressure ratio
###########################
CycleInputParameters['PreCompressorTurbine']['InletPiping']['Velocity']=TurbineInletPipingVelocity
CycleInputParameters['PreCompressorTurbine']['OutletPiping']['Velocity']=TurbineOutletPipingVelocity

###########################
#ReCompressor turbine related design assumptions and required pressure ratio
###########################
CycleInputParameters['ReCompressorTurbine']['InletPiping']['Velocity']=TurbineInletPipingVelocity
CycleInputParameters['ReCompressorTurbine']['OutletPiping']['Velocity']=TurbineOutletPipingVelocity

###########################
#power turbine related design assumptions and required pressure ratio
###########################
CycleInputParameters['PowerTurbine']['MassFraction']=1

CycleInputParameters['PowerTurbine']['MaximumTemperature']=CycleInputParameters['MaximumTemperature']

CycleInputParameters['PowerTurbine']['InletPiping']['Velocity']=TurbineInletPipingVelocity
CycleInputParameters['PowerTurbine']['OutletPiping']['Velocity']=TurbineOutletPipingVelocity

###########################
#heater related design assumptions
###########################
CycleInputParameters['FirstHPHeating']['MaximumTemperature']=CycleInputParameters['MaximumTemperature']
CycleInputParameters['FirstHPHeating']['MassFraction']=CycleInputParameters['MainFraction']
CycleInputParameters['FirstHPHeating']['DeltaPPerDeltaT']=CycleInputParameters['DeltaPPerDeltaT']

CycleInputParameters['SecondPlusThirdHeating']['MaximumTemperature']=CycleInputParameters['MaximumTemperature']
CycleInputParameters['SecondPlusThirdHeating']['MassFraction']=1
CycleInputParameters['SecondPlusThirdHeating']['DeltaPPerDeltaT']=CycleInputParameters['DeltaPPerDeltaT']

CycleInputParameters['ReHeat']['MaximumTemperature']=CycleInputParameters['MaximumTemperature']
CycleInputParameters['ReHeat']['MassFraction']=1
CycleInputParameters['ReHeat']['DeltaPPerDeltaT']=CycleInputParameters['DeltaPPerDeltaT']

###########################
#cooler related design assumptions
###########################
CycleInputParameters['MainFractionCooler']['MinimumTemperature']=CycleInputParameters['StartingProperties']['Temperature']
CycleInputParameters['MainFractionCooler']['MassFraction']=CycleInputParameters['MainFraction']
CycleInputParameters['MainFractionCooler']['DeltaPPerDeltaT']=CycleInputParameters['DeltaPPerDeltaT']

CycleInputParameters['TotalFractionCooler']['MinimumTemperature']=CycleInputParameters['StartingProperties']['Temperature']
CycleInputParameters['TotalFractionCooler']['MassFraction']=1
CycleInputParameters['TotalFractionCooler']['DeltaPPerDeltaT']=CycleInputParameters['DeltaPPerDeltaT']



###########################
#recuperator related design assumptions
#note, there is an additional flow split on the high pressure side of the "main fraction" because of the two recuperators.
###########################
CycleInputParameters['HTRecuperator']['NumberofTemperatures']=NumberofTemperatures
CycleInputParameters['HTRecuperator']['LowPressure']['MassFraction']=1
CycleInputParameters['HTRecuperator']['HighPressure']['MassFraction']=1
CycleInputParameters['HTRecuperator']['DeltaPPerDeltaT']=CycleInputParameters['DeltaPPerDeltaT']						#maybe this should be different for high and low pressure sides?
CycleInputParameters['HTRecuperator']['MinimumDeltaT']=CycleInputParameters['MinimumDeltaT']

CycleInputParameters['MTRecuperator']['NumberofTemperatures']=NumberofTemperatures
CycleInputParameters['MTRecuperator']['LowPressure']['MassFraction']=1
CycleInputParameters['MTRecuperator']['HighPressure']['MassFraction']=CycleInputParameters['MainFraction']
CycleInputParameters['MTRecuperator']['DeltaPPerDeltaT']=CycleInputParameters['DeltaPPerDeltaT']						#maybe this should be different for high and low pressure sides?
CycleInputParameters['MTRecuperator']['MinimumDeltaT']=CycleInputParameters['MinimumDeltaT']

#LTR after the precompressor
CycleInputParameters['LTRecuperator']['MainFraction']['NumberofTemperatures']=NumberofTemperatures
CycleInputParameters['LTRecuperator']['MainFraction']['LowPressure']['MassFraction']=CycleInputParameters['MainFraction']
CycleInputParameters['LTRecuperator']['MainFraction']['HighPressure']['MassFraction']=CycleInputParameters['LTRecuperator']['MainFraction']['HighPressure']['ComponentMassFraction']*CycleInputParameters['MainFraction']	#mass fraction based on the total mass fraction
CycleInputParameters['LTRecuperator']['MainFraction']['DeltaPPerDeltaT']=CycleInputParameters['DeltaPPerDeltaT']				#maybe this should be different for high and low pressure sides?
CycleInputParameters['LTRecuperator']['MainFraction']['MinimumDeltaT']=CycleInputParameters['MinimumDeltaT']

#LTR before the precompressor and precooler
CycleInputParameters['LTRecuperator']['TotalFraction']['NumberofTemperatures']=NumberofTemperatures
CycleInputParameters['LTRecuperator']['TotalFraction']['LowPressure']['MassFraction']=1
CycleInputParameters['LTRecuperator']['TotalFraction']['HighPressure']['MassFraction']=(1-CycleInputParameters['LTRecuperator']['MainFraction']['HighPressure']['ComponentMassFraction'])*CycleInputParameters['MainFraction']	#mass fraction based on the total mass fraction
CycleInputParameters['LTRecuperator']['TotalFraction']['DeltaPPerDeltaT']=CycleInputParameters['DeltaPPerDeltaT']				#maybe this should be different for high and low pressure sides?
CycleInputParameters['LTRecuperator']['TotalFraction']['MinimumDeltaT']=CycleInputParameters['MinimumDeltaT']












#################################################################################################
#end Input parameters
#################################################################################################
