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



CycleInputParameters['PowerOutput']=1.0*10**6	#1MW



###########################
#common recuperator parameters
DeltaPPerDeltaT=0.5e2



###########################
#Common compressor parameters
CompressorInletPipingVelocity=15.0			#m/s
CompressorOutletPipingVelocity=CompressorInletPipingVelocity
CompressorHubToTipRatio=.7				#assumes axial design only and constant radius?
CompressorRotorTipMetalVelocity=300.			#m/s
IGVVelocity=150.0					#m/s

###########################
#Common turbine parameters
TurbineInletPipingVelocity=CompressorInletPipingVelocity
TurbineOutletPipingVelocity=CompressorOutletPipingVelocity


###########################
#main compressor related design assumptions and required pressure ratio
###########################

CycleInputParameters['MainCompressor']['PressureRatio']=CycleInputParameters['PressureRatio']
if 'IsentropicEfficiency' not in CycleInputParameters['MainCompressor']:
	CycleInputParameters['MainCompressor']['IsentropicEfficiency']=.84	#if changing this, need to update the pressure ratio for the fuel cell cycle to match a 650C compressor outlet

CycleInputParameters['MainCompressor']['InletPiping']['Velocity']=CompressorInletPipingVelocity
CycleInputParameters['MainCompressor']['OutletPiping']['Velocity']=CompressorOutletPipingVelocity

CycleInputParameters['MainCompressor']['HubToTipRatio']=CompressorHubToTipRatio
CycleInputParameters['MainCompressor']['RotorTipMetalVelocity']=CompressorRotorTipMetalVelocity
CycleInputParameters['MainCompressor']['IGVVelocity']=IGVVelocity

CycleInputParameters['MainCompressor']['Ns']=1.0
CycleInputParameters['MainCompressor']['StageCount']=1

###########################
#main compressor related design assumptions and required pressure ratio
###########################

CycleInputParameters['FuelCompressor']['PressureRatio']=CycleInputParameters['PressureRatio']
CycleInputParameters['FuelCompressor']['IsentropicEfficiency']=.84

CycleInputParameters['FuelCompressor']['InletPiping']['Velocity']=CompressorInletPipingVelocity
CycleInputParameters['FuelCompressor']['OutletPiping']['Velocity']=CompressorOutletPipingVelocity

CycleInputParameters['FuelCompressor']['HubToTipRatio']=CompressorHubToTipRatio
CycleInputParameters['FuelCompressor']['RotorTipMetalVelocity']=CompressorRotorTipMetalVelocity
CycleInputParameters['FuelCompressor']['IGVVelocity']=IGVVelocity

CycleInputParameters['FuelCompressor']['Ns']=1.0
CycleInputParameters['FuelCompressor']['StageCount']=1


###########################
#power turbine related design assumptions and required pressure ratio
###########################
CycleInputParameters['PowerTurbine']['MassFraction']=1

CycleInputParameters['PowerTurbine']['IsentropicEfficiency']=.90
CycleInputParameters['PowerTurbine']['MaximumTemperature']=CycleInputParameters['MaximumTemperature']

CycleInputParameters['PowerTurbine']['InletPiping']['Velocity']=TurbineInletPipingVelocity
CycleInputParameters['PowerTurbine']['OutletPiping']['Velocity']=TurbineOutletPipingVelocity

CycleInputParameters['PowerTurbine']['Ns']=1.5
CycleInputParameters['PowerTurbine']['StageCount']=3

###########################
#heater related design assumptions
###########################

CycleInputParameters['CombinedFuelCellAndCombustor']['CombustorMaximumTemperature']=CycleInputParameters['MaximumTemperature']
CycleInputParameters['CombinedFuelCellAndCombustor']['FuelCellMaximumTemperature']=1000.+273.		#don't know that this is actually used for anything right now, but could be used to automatically set the percent excess air based on fuel cell getting too hot???
CycleInputParameters['CombinedFuelCellAndCombustor']['MassFraction']=1
CycleInputParameters['CombinedFuelCellAndCombustor']['DeltaPPerDeltaT']=0				#not yet implimented!!!!!!!!!!!!!!!!!

CycleInputParameters['CombinedFuelCellAndCombustor']['ElectroChemicalEfficiency']=0.65*(50.016e6)/(55.528e6)
CycleInputParameters['CombinedFuelCellAndCombustor']['PercentExcessOxygen']=26.3


CycleInputParameters['SecondPlusThirdHeating']['MaximumTemperature']=CycleInputParameters['MaximumTemperature']
CycleInputParameters['SecondPlusThirdHeating']['MassFraction']=1
CycleInputParameters['SecondPlusThirdHeating']['DeltaPPerDeltaT']=DeltaPPerDeltaT



###########################
#cooler related design assumptions
###########################

CycleInputParameters['TotalFractionCooler']['MinimumTemperature']=CycleInputParameters['StartingProperties']['Temperature']
CycleInputParameters['TotalFractionCooler']['MassFraction']=1
CycleInputParameters['TotalFractionCooler']['DeltaPPerDeltaT']=0					#not yet implimented!!!!!!!!!!!!!!!!!




#################################################################################################
#end Input parameters
#################################################################################################
