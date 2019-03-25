###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


#import packages needed by functions defined in this file
from helpers import SmartDictionary,PrintWarning
from FluidProperties.REFPROP import *


#heat exchanger functions are in a separate file because they are so in depth
from HeatExchangers import GeneralRealRecuperator










#calculate the properties after a temperature drop with a pressure loss
def Cooler(StartingProperties,CoolerInputParameters,MinTemperature=0):
	Cooler=SmartDictionary()
	Cooler['MassFraction']=CoolerInputParameters['MassFraction']		#copy mass fraction so it is available later all in the same dictionary
	Cooler['StartingProperties']=StartingProperties

	if MinTemperature==0:
		Cooler['CooledProperties']['Temperature']=CoolerInputParameters['MinimumTemperature']
	else:
		Cooler['CooledProperties']['Temperature']=MinTemperature

	#calculate pressure drop
	DeltaT=Cooler['StartingProperties']['Temperature']-Cooler['CooledProperties']['Temperature']
	DeltaP=DeltaT*CoolerInputParameters['DeltaPPerDeltaT']
	PressureRatio=1-DeltaP/Cooler['StartingProperties']['Pressure']			#don't realy need to do this step, but doing so so it is available, if want to know pressure ratio
	if PressureRatio<0:
		#if pressure drop is so high that the pressure drop goes negative, make it slightly positive and the very low pressure ratio should cause the cycle to have a 0 efficiency condition
		PressureRatio=1e-6
	Cooler['PressureRatio']=PressureRatio
	Cooler['CooledProperties']['Pressure']=Cooler['StartingProperties']['Pressure']*PressureRatio

	#get the rest of the values
	Cooler['CooledProperties']=GetFluidProperties(Cooler['CooledProperties']['Pressure'],Temperature=Cooler['CooledProperties']['Temperature'])
	#calculate how much heat was cooled
	Cooler['SpecificHeatCooled_TotalMassFlow']=(Cooler['StartingProperties']['Enthalpy']-Cooler['CooledProperties']['Enthalpy'])*Cooler['MassFraction']
	#calculate how much work was done while cooling
	Cooler['SpecificWorkCooling_TotalMassFlow']=((Cooler['StartingProperties']['Enthalpy']-Cooler['StartingProperties']['InternalEnergy'])-(Cooler['CooledProperties']['Enthalpy']-Cooler['CooledProperties']['InternalEnergy']))*Cooler['MassFraction']

	return Cooler



def ConstantVolumeHeater(StartingProperties,HeaterInputParameters,MaxTemperature=0,MaxPressure=35.*10.**6.):
	Heater=SmartDictionary()
	Heater['MassFraction']=HeaterInputParameters['MassFraction']		#copy mass fraction so it is available later all in the same dictionary

	#refetch properties, making sure to get extended properties since the calling StartingProperties most likely doesn't have that populated. not sure if temperature and pressure
	#are the most accurate or fastest option to use though, compared to another parameter combination.
	Heater['StartingProperties']=GetFluidProperties(Temperature=StartingProperties['Temperature'],Pressure=StartingProperties['Pressure'],ExtendedProperties=True)

	if MaxTemperature==0:
		Heater['HeatedProperties']['Temperature']=HeaterInputParameters['MaximumTemperature']
	else:
		Heater['HeatedProperties']['Temperature']=MaxTemperature

#any pressure drop (loss) during the inflow phase??????????

	#heat at constant volume, limited to maximum temperature or pressure
	try:
		Heater['HeatedProperties']=GetFluidProperties(Density=Heater['StartingProperties']['Density'],Temperature=Heater['HeatedProperties']['Temperature'])
		if Heater['HeatedProperties']['Pressure']>MaxPressure:
			Heater['HeatedProperties']=GetFluidProperties(Density=Heater['StartingProperties']['Density'],Pressure=MaxPressure)
			print "pressure limited, temperature="+str(Heater['HeatedProperties']['Temperature'])
	except:		#probably errored out because was out of range, so limit to the max pressure.
		Heater['HeatedProperties']=GetFluidProperties(Density=Heater['StartingProperties']['Density'],Pressure=MaxPressure)
		print "pressure limited, temperature="+str(Heater['HeatedProperties']['Temperature'])


	#add a pressure drop (loss)during the outflow phase

	#calculate pressure drop

	DeltaT=Heater['HeatedProperties']['Temperature']-Heater['StartingProperties']['Temperature']
	if DeltaT<0.0:
		#if the heated temperature is less than the unheated temperature, then the heater isn't actually able to do anything, so don't let it act like a cooler instead.
		PrintWarning("Warning: Heater inlet temperature is already above the maximum temperature, no heating done.")
		DeltaT=0.0

#	DeltaP=DeltaT*HeaterInputParameters['DeltaPPerDeltaT']
#don't think the above line is really right way to do it, so DeltaP is set to 0 for now
#also need to have checks like in other heater and the cooler for negative pressure ratio
	DeltaP=0

	#calculate new properties after outflow pressure loss
	Heater['HeatedProperties']['Pressure']=Heater['HeatedProperties']['Pressure']-DeltaP
	Heater['HeatedProperties']=GetFluidProperties(Heater['HeatedProperties']['Pressure'],Temperature=(Heater['StartingProperties']['Temperature']+DeltaT))

	#calculate the pressure ratio
	Heater['PressureRatio']=Heater['HeatedProperties']['Pressure']/Heater['StartingProperties']['Pressure']

	#calculate how much heat was added
	Heater['SpecificHeatAdded_TotalMassFlow']=(Heater['HeatedProperties']['InternalEnergy']-Heater['StartingProperties']['InternalEnergy'])*Heater['MassFraction']

	return Heater


def Heater(StartingProperties,HeaterInputParameters,MaxTemperature=0):
	Heater=SmartDictionary()
	Heater['MassFraction']=HeaterInputParameters['MassFraction']		#copy mass fraction so it is available later all in the same dictionary
	Heater['StartingProperties']=StartingProperties

	if MaxTemperature==0:
		Heater['HeatedProperties']['Temperature']=HeaterInputParameters['MaximumTemperature']
	else:
		if MaxTemperature>HeaterInputParameters['MaximumTemperature']:
			raise Exception("defined heater outlet temperature is above the maximum heat source temperature. this error may be occurring because the recompressor pressure ratio is too high. probably need to reduce the pre-compressor pressure ratio so that the re-compressor outlet temperature is closer to the main compressor outlet temperature. handling this scenario properly is not yet implemented")
		else:
			Heater['HeatedProperties']['Temperature']=MaxTemperature

	#calculate pressure drop
	DeltaT=Heater['HeatedProperties']['Temperature']-Heater['StartingProperties']['Temperature']
	if DeltaT<0.0:
		#if the heated temperature is less than the unheated temperature, then the heater isn't actually able to do anything, so don't let it act like a cooler instead.
		PrintWarning("Warning: Heater inlet temperature is already above the maximum temperature, no heating done.")
		DeltaT=0.0

	DeltaP=DeltaT*HeaterInputParameters['DeltaPPerDeltaT']
	PressureRatio=1-DeltaP/Heater['StartingProperties']['Pressure']			#don't realy need to do this step, but doing so so it is available, if want to know pressure ratio
	if PressureRatio<0:
		#if pressure drop is so high that the pressure drop goes negative, make it slightly positive and the very low pressure ratio should cause the cycle to have a 0 efficiency condition
		PressureRatio=1e-6
	Heater['PressureRatio']=PressureRatio
	Heater['HeatedProperties']['Pressure']=Heater['StartingProperties']['Pressure']*PressureRatio

	#get the rest of the values
	Heater['HeatedProperties']=GetFluidProperties(Heater['HeatedProperties']['Pressure'],Temperature=(Heater['StartingProperties']['Temperature']+DeltaT))
	#calculate how much heat was added
	Heater['SpecificHeatAdded_TotalMassFlow']=(Heater['HeatedProperties']['Enthalpy']-Heater['StartingProperties']['Enthalpy'])*Heater['MassFraction']

	return Heater



#setup component functions
def RealCompressor(StartingProperties,CompressorInputParameters,PressureRatio=0):
	Compressor=SmartDictionary()
	Compressor['MassFraction']=CompressorInputParameters['MassFraction']		#copy mass fraction so it is available later all in the same dictionary
	Compressor['StartingProperties']=StartingProperties

	#figure out where to get the pressure ratio from
	if (PressureRatio==0) and ('PressureRatio' in CompressorInputParameters):
		Compressor['PressureRatio']=CompressorInputParameters['PressureRatio']
	elif (PressureRatio!=0) and ('PressureRatio' not in CompressorInputParameters):
		Compressor['PressureRatio']=PressureRatio
	else:
		raise Exception("no compressor pressure ratio defined or compressor pressure ratio doubly defined")

	CompressedPressure=Compressor['StartingProperties']['Pressure']*Compressor['PressureRatio']

	try:
		IdealCompressedProperties=GetFluidProperties(CompressedPressure,Entropy=Compressor['StartingProperties']['Entropy'])
		Extrapolate=False
	except:
		if FluidProperties.REFPROP.FluidName == 'methane':
			PrintWarning('fluid is methane and temperature is probably too high, so trying to get a lower pressure ratio first and then extrapolate using ideal gas and constant specific heats from near the limits of methane property data')
			Extrapolate=True
			IdealCompressedProperties=SmartDictionary()
			IdealCompressedProperties['Pressure']=CompressedPressure
			IdealCompressedProperties['Entropy']=Compressor['StartingProperties']['Entropy']

			#assume ideal gas and constant specific heats and then just take 90% of that pressure ratio to be conservative not too close to the peak temperature available in REFPROP
			IntermediateCompressedPressure=0.90*((625./Compressor['StartingProperties']['Temperature'])**((Compressor['StartingProperties']['gamma'])/(Compressor['StartingProperties']['gamma']-1)))*Compressor['StartingProperties']['Pressure']
			IntermediateIdealCompressedProperties=GetFluidProperties(IntermediateCompressedPressure,Entropy=Compressor['StartingProperties']['Entropy'],ExtendedProperties=True)			#temperature will be less than 625K because of only taking 90% of the pressure ratio
			SecondaryPressureRatio=CompressedPressure/IntermediateCompressedPressure
			IdealCompressedProperties['Temperature']=IntermediateIdealCompressedProperties['Temperature']*(SecondaryPressureRatio)**((IntermediateIdealCompressedProperties['gamma']-1)/(IntermediateIdealCompressedProperties['gamma']))
			IdealCompressedProperties['Enthalpy']=(IdealCompressedProperties['Temperature']-IntermediateIdealCompressedProperties['Temperature'])*IntermediateIdealCompressedProperties['cp']+IntermediateIdealCompressedProperties['Enthalpy']

		else:
			raise

	CompressedEnthalpy=(IdealCompressedProperties['Enthalpy'] - Compressor['StartingProperties']['Enthalpy'])/(CompressorInputParameters['IsentropicEfficiency'])+Compressor['StartingProperties']['Enthalpy']

	#first assign the known values as a fallback if the rest of the property data can't be obtained
	Compressor['CompressedProperties']['Enthalpy']=CompressedEnthalpy
	Compressor['CompressedProperties']['Pressure']=CompressedPressure
	#if the fallback is used, skipping plotting of the state point and don't know that temperature and entropy are really needed otherwise, so don't bother calculating them.

	#try to populate all of the property data
	if not Extrapolate:
		try:
			Compressor['CompressedProperties']=GetFluidProperties(CompressedPressure,Enthalpy=CompressedEnthalpy)
		except:
			if FluidProperties.REFPROP.FluidName == 'methane':
				#isentropic compression is not out of range, but actual compression is
				#use just the limited known, exact values already defined above for methane
				pass
			else:
				raise

	else:
		#Extrapolation was used
		#use just the limited known, extrapolated values already defined above for methane
		pass

	Compressor['CompressedProperties']['Enthalpy_TotalMassFlow']=Compressor['MassFraction']*Compressor['CompressedProperties']['Enthalpy']			#used by air cycle because needed to do combustion chemistry
	
	#if the pressure ratio is really low and the interpolation is not accurate enough, temperature may actually drop. if so, fix this from giving erros and slightly messing up the answer
	if Compressor['CompressedProperties']['Temperature']<Compressor['StartingProperties']['Temperature']:
		Compressor['CompressedProperties']=Compressor['StartingProperties']
		Compressor['SpecificWorkInput_TotalMassFlow']=0
		PrintWarning("Warning: Compressor pressure ratio too low to be accurate")
	else:
		Compressor['SpecificWorkInput_TotalMassFlow']=(Compressor['CompressedProperties']['Enthalpy']-Compressor['StartingProperties']['Enthalpy'])*Compressor['MassFraction']
	
	return Compressor





def RealTurbine(StartingProperties,TurbineInputParameters,WorkToMatch=0,PressureRatio=0):
	Turbine=SmartDictionary()
	Turbine['MassFraction']=TurbineInputParameters['MassFraction']		#copy mass fraction so it is available later all in the same dictionary
	Turbine['StartingProperties']=StartingProperties

	if ('PressureRatio' not in TurbineInputParameters) and (WorkToMatch!=0) and (PressureRatio==0):
		ExpandedEnthalpy=Turbine['StartingProperties']['Enthalpy']-WorkToMatch
		IdealExpandedEnthalpy=Turbine['StartingProperties']['Enthalpy']-WorkToMatch/TurbineInputParameters['IsentropicEfficiency']
		IdealExpandedProperties=GetFluidProperties(Enthalpy=IdealExpandedEnthalpy, Entropy=Turbine['StartingProperties']['Entropy'])
		Turbine['ExpandedProperties']=GetFluidProperties(IdealExpandedProperties['Pressure'],Enthalpy=ExpandedEnthalpy)
		Turbine['PressureRatio']=Turbine['StartingProperties']['Pressure']/Turbine['ExpandedProperties']['Pressure']
	elif ('PressureRatio' not in TurbineInputParameters) and (PressureRatio!=0) and (WorkToMatch==0):
		Turbine['PressureRatio']=PressureRatio
		ExpandedPressure=Turbine['StartingProperties']['Pressure']/Turbine['PressureRatio']
		IdealExpandedProperties=GetFluidProperties(ExpandedPressure,Entropy=Turbine['StartingProperties']['Entropy'])
		ExpandedEnthalpy=Turbine['StartingProperties']['Enthalpy'] - (Turbine['StartingProperties']['Enthalpy'] - IdealExpandedProperties['Enthalpy'])*TurbineInputParameters['IsentropicEfficiency']
		Turbine['ExpandedProperties']=GetFluidProperties(ExpandedPressure,Enthalpy=ExpandedEnthalpy)
	#so 'PressureRatio' in TurbineInputParameters never implemented?



	#if the pressure ratio is really low and the interpolation is not accurate enough, temperature may actually rise. if so, fix this from giving errors and slightly messing up the answer
	if Turbine['ExpandedProperties']['Temperature']>Turbine['StartingProperties']['Temperature']:
		Turbine['ExpandedProperties']=Turbine['StartingProperties']
		Turbine['SpecificWorkOutput_TotalMassFlow']=0
		PrintWarning("Warning: Turbine pressure ratio too low to be accurate")
	else:
		Turbine['SpecificWorkOutput_TotalMassFlow']=(Turbine['StartingProperties']['Enthalpy']-Turbine['ExpandedProperties']['Enthalpy'])*Turbine['MassFraction']
	
	return Turbine



def RealPiston(StartingProperties,InputParameters,PressureRatio):			#different from RealTurbine because it uses internal energy and doesn't have a fixed work to match implemented
	Piston=SmartDictionary()
	Piston['MassFraction']=InputParameters['MassFraction']		#copy mass fraction so it is available later all in the same dictionary
	Piston['StartingProperties']=StartingProperties

	Piston['PressureRatio']=PressureRatio
	ExpandedPressure=Piston['StartingProperties']['Pressure']/Piston['PressureRatio']
	IdealExpandedProperties=GetFluidProperties(ExpandedPressure,Entropy=Piston['StartingProperties']['Entropy'])
#need to make sure this formula is correct for internal energy and a piston... think it is.
	ExpandedInternalEnergy=Piston['StartingProperties']['InternalEnergy'] - (Piston['StartingProperties']['InternalEnergy'] - IdealExpandedProperties['InternalEnergy'])*InputParameters['IsentropicEfficiency']
	Piston['ExpandedProperties']=GetFluidProperties(ExpandedPressure,InternalEnergy=ExpandedInternalEnergy)
	#if the pressure ratio is really low and the interpolation is not accurate enough, temperature may actually rise. if so, fix this from giving errors and slightly messing up the answer
	if Piston['ExpandedProperties']['Temperature']>Piston['StartingProperties']['Temperature']:
		Piston['ExpandedProperties']=Piston['StartingProperties']
		Piston['SpecificWorkOutput_TotalMassFlow']=0
		PrintWarning("Warning: piston pressure ratio too low to be accurate")
	else:
		Piston['SpecificWorkOutput_TotalMassFlow']=(Piston['StartingProperties']['InternalEnergy']-Piston['ExpandedProperties']['InternalEnergy'])*Piston['MassFraction']

	return Piston




















def CombinedFuelCellAndCombustor(AirStartingProperties,FuelStartingProperties,InputParameters):				#for methane, CH4
	CombinedFuelCellAndCombustor=SmartDictionary()
	CombinedFuelCellAndCombustor['StartingProperties']['Air']=AirStartingProperties
	CombinedFuelCellAndCombustor['StartingProperties']['Fuel']=FuelStartingProperties
	CombinedFuelCellAndCombustor['MassFraction']=InputParameters['MassFraction']

	FuelHHV=MethaneHHV*ComputeMassOfFuelToTotalMassRatio(PercentExcessOxygen=InputParameters['PercentExcessOxygen'])		#J/kg, TotalMassFlow, assumes combustion at FluidProperties.REFPROP.ReferenceTemperature1 and FluidProperties.REFPROP.ReferencePressure

	ElectricalWorkOutput=FuelHHV*InputParameters['FuelCellFuelUtilization']*InputParameters['ElectroChemicalEfficiency']		#don't know that this is actually correct to use MethaneHHV, but it's probably pretty close.



#old way, using air only and no combustion products or fuel
#	CombinedFuelCellAndCombustor['HeatedProperties']=GetFluidProperties(CombinedFuelCellAndCombustor['HeatedProperties']['Pressure'],Temperature=(CombinedFuelCellAndCombustor['StartingProperties']['Temperature']+TemperatureRise))
#	CombinedFuelCellAndCombustor['SpecificHeatRejected_TotalMassFlow']=(CombinedFuelCellAndCombustor['HeatedProperties']['Enthalpy']-CombinedFuelCellAndCombustor['StartingProperties']['Enthalpy'])*CombinedFuelCellAndCombustor['MassFraction']
#	CombinedFuelCellAndCombustor['SpecificEnergyAdded_TotalMassFlow']=CombinedFuelCellAndCombustor['SpecificHeatRejected_TotalMassFlow']/(1.-Efficiency)
#	CombinedFuelCellAndCombustor['SpecificWorkOutput_TotalMassFlow']=CombinedFuelCellAndCombustor['SpecificEnergyAdded_TotalMassFlow']*Efficiency



	SetupFluid('CombustionProducts',PercentExcessOxygen=InputParameters['PercentExcessOxygen'])

#no pressure drop yet!!!
	CombinedFuelCellAndCombustor['HeatedProperties']['Pressure']=CombinedFuelCellAndCombustor['StartingProperties']['Air']['Pressure']		#pressure of air and fuel is the same, so just use one of them

	EnthalpyOfProducts=((CombinedFuelCellAndCombustor['StartingProperties']['Air']['Enthalpy_TotalMassFlow']+CombinedFuelCellAndCombustor['StartingProperties']['Fuel']['Enthalpy_TotalMassFlow'])-ElectricalWorkOutput)
	CombinedFuelCellAndCombustor['HeatedProperties']=GetFluidProperties(CombinedFuelCellAndCombustor['HeatedProperties']['Pressure'],Enthalpy=EnthalpyOfProducts)

	CombinedFuelCellAndCombustor['SpecificEnergyAdded_TotalMassFlow']=FuelHHV
	CombinedFuelCellAndCombustor['SpecificWorkOutput_TotalMassFlow']=ElectricalWorkOutput

	if CombinedFuelCellAndCombustor['HeatedProperties']['Temperature']>InputParameters['CombustorMaximumTemperature']:
		raise Exception('maximum temperature too high, percent excess air probably too low for the current fuel cell efficiency')

	return CombinedFuelCellAndCombustor








