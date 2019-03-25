###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


#fix the path because sometimes can't find custom packages when importing
import os,sys
sys.path.append(os.getcwd())	#for some reason this is needed if not running interactively


#import packages needed by functions defined in this file
from numpy import *
from FluidProperties.REFPROP import *			#import this way because used so many times don't want to have to keep retyping FluidProperties. in front of everything.
import FluidProperties.REFPROP				#also import this way so can get changes to FluidProperties.REFPROP.FluidName
from helpers import *
from Components import *
from copy import deepcopy

if False:		#set to true to raise warnings as an exception so can debug and figure out where they are. don't leave turned on though because causes problems if a module raises a warning and is able to catches it itself.
	#raise a warning as an exception so it can be located
	import warnings
	warnings.filterwarnings('error')



def AddState(States,StateProperties,StateNumber,ArrowAngle,ArrowAngleTP=None):
	if ArrowAngleTP is None:
		ArrowAngleTP=ArrowAngle

	if States==SmartDictionary():
		States['Enthalpy']=[StateProperties['Enthalpy']]
		States['Entropy']=[StateProperties['Entropy']]
		States['Density']=[StateProperties['Density']]
		States['SpecificVolume']=[1/StateProperties['Density']]
		States['Temperature']=[StateProperties['Temperature']]
		States['Pressure']=[StateProperties['Pressure']]
		States['StateNumber']=[StateNumber]
		States['ArrowAngle']=[ArrowAngle]
		States['ArrowAngleTP']=[ArrowAngleTP]
#		States['EnthalpyEntropyLabels']=text(StateNumber,(StateProperties['Entropy']-30,StateProperties['Enthalpy']))
#		States['TemperatureEntropyLabels']=text(StateNumber,(StateProperties['Entropy']-30,StateProperties['Temperature']))
	else:
		States['Enthalpy']=hstack((States['Enthalpy'],StateProperties['Enthalpy']))
		States['Entropy']=hstack((States['Entropy'],StateProperties['Entropy']))
		States['Density']=hstack((States['Density'],StateProperties['Density']))
		States['SpecificVolume']=hstack((States['SpecificVolume'],1/StateProperties['Density']))
		States['Temperature']=hstack((States['Temperature'],StateProperties['Temperature']))
		States['Pressure']=hstack((States['Pressure'],StateProperties['Pressure']))
		States['StateNumber']=hstack((States['StateNumber'],StateNumber))
		States['ArrowAngle']=hstack((States['ArrowAngle'],ArrowAngle))
		States['ArrowAngleTP']=hstack((States['ArrowAngleTP'],ArrowAngleTP))
#		States['EnthalpyEntropyLabels']=States['EnthalpyEntropyLabels']+text(StateNumber,(StateProperties['Entropy']-30,StateProperties['Enthalpy']))
#		States['TemperatureEntropyLabels']=States['TemperatureEntropyLabels']+text(StateNumber,(StateProperties['Entropy']-30,StateProperties['Temperature']))

	return States






















def PreCompressionReCompressionCycleWithReheat(CycleInputParameters):
	CycleParameters=SmartDictionary()

	CycleParameters['Fluid']=FluidProperties.REFPROP.FluidName

	#compute the carnot cycle efficiency for reference, now rather than later in case the cycle can't run because of too high heat exchanger pressure drops
	CycleParameters['CycleCarnotEfficiency']=1-(CycleInputParameters['StartingProperties']['Temperature'])/(CycleInputParameters['MaximumTemperature'])

	CycleParameters['TotalSpecificWorkInput_TotalMassFlow']=0
	CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']=0
	CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']=0


	#starting the cycle at the point of lowest pressure and temperature (the precompressor inlet). this is more convenient and clear from a cycle standpoint what is going on
	#because don't have to keep jumping in and out of sequence (as the code used to be written). but, it is more convenient from a design exploration standpoint (at least right now)
	#to control the point of lowest entropy and temperature. so, when this is defined, an iterative process needs to be followed to determine the actual starting pressure of the cycle.
	#this is because solving the cycle backwards is not possible (i think).
	#overall, the cycle iterates for the precompressor inlet pressure, recompressor pressure ratio, and the power turbine pressure ratio. if the power turbine outlet pressure were
	#defined, then only the recompressor pressure ratio would have to be iterated for, but again, that is also an inconvenient way to control the cycle design exploration.



	#need to iteratively solve for the PreCompressorInletPressure
	#define the convergence parameters
	ConvergenceCriteria=1.0e-6
	SecondaryConvergenceCriteria=3.0e-3
	MaxIterations=20

	#first guess is that the MainFractionCooler has no pressure drop
	PreCompressorInletPressureOld=CycleInputParameters['MainCompressor']['OutletPressure']/CycleInputParameters['MainCompressor']['PressureRatio']/CycleInputParameters['PreCompressor']['PressureRatio']
	#preallocate all so they are defined, so they can all be deleted without having to check for existence
	PreCompressorInletPressureOldOld=PreCompressorInletPressureOldOldOld=0

	for count in arange(0,MaxIterations):
		#pre compressor
		CurrentProperties=GetFluidProperties(PreCompressorInletPressureOld,Temperature=CycleInputParameters['StartingProperties']['Temperature'])
		CycleParameters['PreCompressor']=RealCompressor(CurrentProperties,CycleInputParameters['PreCompressor'])

		#main fraction cooler (lumping of recuperators and heat rejection, mainly just here to figure out the pressure drop and get all the properties)
		CycleParameters['MainFractionCooler']=Cooler(CycleParameters['PreCompressor']['CompressedProperties'],CycleInputParameters['MainFractionCooler'])

		#calculate the pre compressor inlet pressure based on the pressure drop in the main fraction cooler
		PreCompressorInletPressure=CycleInputParameters['MainCompressor']['OutletPressure']/(CycleParameters['MainFractionCooler']['PressureRatio']*CycleInputParameters['MainCompressor']['PressureRatio']*CycleInputParameters['PreCompressor']['PressureRatio'])
		PrintWarning("PreCompressorInletPressure: "+str(PreCompressorInletPressure))

		#check for convergence
		#first see if the residual is really low
		#note, in this search (the main fraction cooler), the first guess may be right, whereas, in the heat exchangers, the first guess was never right because the temperature AND pressure were unknown
		PreCompressorInletPressureResidual=abs(1-PreCompressorInletPressure/PreCompressorInletPressureOld)
		PrintWarning("PreCompressorInletPressure Residual: "+str(PreCompressorInletPressureResidual))
		if PreCompressorInletPressureResidual<ConvergenceCriteria:
			break
		#next, see if even if the residual is not low, is it oscillating around a fixed value?
		if count>0:
			if CheckPercentage(PreCompressorInletPressure,PreCompressorInletPressureOldOld,1.0e-13) or (count>1 and CheckPercentage(PreCompressorInletPressure,PreCompressorInletPressureOldOldOld,1.0e-13)):
				if PreCompressorInletPressureResidual<SecondaryConvergenceCriteria:
					PrintWarning("PreCompressorInletPressure residuals stopped changing but primary convergence criteria not yet met. secondary convergence criteria met.")
					break
				elif count==(MaxIterations-1):
					print("PreCompressorInletPressure did not converge in "+str(MaxIterations)+" iterations. residuals stopped changing but primary and secondary convergence criteria not met.")
					break
		#did not converge
		if count==(MaxIterations-1):
			raise Exception("PreCompressorInletPressure did not converge in "+str(MaxIterations)+" iterations. residuals did not stop changing")

		#save values for the next iteration to test convergence
		if count>0:
			PreCompressorInletPressureOldOldOld=PreCompressorInletPressureOldOld
		PreCompressorInletPressureOldOld=PreCompressorInletPressureOld
		PreCompressorInletPressureOld=PreCompressorInletPressure

	#get rid of some variables since this same code is used for the power turbine pressure ratio, and it isn't placed in a function
	del(count,PreCompressorInletPressureResidual,PreCompressorInletPressure,PreCompressorInletPressureOld,PreCompressorInletPressureOldOld,PreCompressorInletPressureOldOldOld)

	#now that the correct precompressor inlet pressure has been found, assign some values
	#precompressor
	CurrentProperties=CycleParameters['PreCompressor']['CompressedProperties']
	CycleParameters['TotalSpecificWorkInput_TotalMassFlow']+=CycleParameters['PreCompressor']['SpecificWorkInput_TotalMassFlow']
	CycleParameters['PreCompressor']['StartingProperties']['StateNumber']=13
	CycleParameters['States']=AddState(SmartDictionary(),CycleParameters['PreCompressor']['StartingProperties'],CycleParameters['PreCompressor']['StartingProperties']['StateNumber'],5.25*math.pi/4,ArrowAngleTP=5*math.pi/4)

	#main fraction cooler (current properties are the main compressor inlet pressure)
	CurrentProperties=CycleParameters['MainFractionCooler']['CooledProperties']




	#main compressor
	CycleParameters['MainCompressor']=RealCompressor(CurrentProperties,CycleInputParameters['MainCompressor'])
	CycleParameters['TotalSpecificWorkInput_TotalMassFlow']+=CycleParameters['MainCompressor']['SpecificWorkInput_TotalMassFlow']
	CycleParameters['MainCompressor']['StartingProperties']['StateNumber']=1
	CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['MainCompressor']['StartingProperties']['StateNumber'],5*math.pi/4,ArrowAngleTP=-math.pi/6)
	CurrentProperties=CycleParameters['MainCompressor']['CompressedProperties']




	#need to iteratively solve for the recompressor pressure ratio
	#define the convergence parameters
	ConvergenceCriteria=1.0e-6
	SecondaryConvergenceCriteria=3.0e-3
	MaxIterations=20

	#first guess is that main compressor and precompressor pressure ratios are equal		#is this supposed to say recompressor????
	PressureRatioOld=CycleInputParameters['MainCompressor']['PressureRatio']
	#preallocate all so they are defined, so they can all be deleted without having to check for existence
	PressureRatioOldOld=PressureRatioOldOldOld=0

	for count in arange(0,MaxIterations):
		#run the recompressor with the guessed pressure ratio
		CycleParameters['ReCompressor']=RealCompressor(CycleParameters['PreCompressor']['CompressedProperties'],CycleInputParameters['ReCompressor'],PressureRatioOld)

		#heat input to the high pressure side (lumping of recuperators and heat addition, mainly just here to figure out the pressure drop and get all the properties)
		CycleParameters['FirstHPHeating']=Heater(CurrentProperties,CycleInputParameters['FirstHPHeating'],CycleParameters['ReCompressor']['CompressedProperties']['Temperature'])	#temperature of the first heater is limited to the recompressor inlet
		PressureRatio=CycleParameters['MainFractionCooler']['PressureRatio']*CycleParameters['MainCompressor']['PressureRatio']*CycleParameters['FirstHPHeating']['PressureRatio']

		PrintWarning("recompressor Pressure Ratio: "+str(PressureRatio))

		#check for convergence
		#first see if the residual is really low
		#note, in this search (the recompressor), the first guess may be right, whereas, in the heat exchangers, the first guess was never right because the temperature AND pressure were unknown
		PressureRatioResidual=abs(1-PressureRatio/PressureRatioOld)
		PrintWarning("Recompressor PressureRatioResidual: "+str(PressureRatioResidual))
		if PressureRatioResidual<ConvergenceCriteria:
			break
		#next, see if even if the residual is not low, is it oscillating around a fixed value?
		if count>0:
			if CheckPercentage(PressureRatio,PressureRatioOldOld,1.0e-13) or (count>1 and CheckPercentage(PressureRatio,PressureRatioOldOldOld,1.0e-13)):
				if PressureRatioResidual<SecondaryConvergenceCriteria:
					PrintWarning("Recompressor Presure ratio residuals stopped changing but primary convergence criteria not yet met. secondary convergence criteria met.")
					break
				elif count==(MaxIterations-1):
					print("Recompressor pressure did not converge in "+str(MaxIterations)+" iterations. residuals stopped changing but primary and secondary convergence criteria not met.")
					break
		#did not converge
		if count==(MaxIterations-1):
			raise Exception("pressure did not converge in "+str(MaxIterations)+" iterations. residuals did not stop changing")

		#save values for the next iteration to test convergence
		if count>0:
			PressureRatioOldOldOld=PressureRatioOldOld
		PressureRatioOldOld=PressureRatioOld
		PressureRatioOld=PressureRatio

	#get rid of some variables since this same code is used for the power turbine pressure ratio, and it isn't placed in a function
	del(count,PressureRatioResidual,PressureRatio,PressureRatioOld,PressureRatioOldOld,PressureRatioOldOldOld)


	if CycleParameters['ReCompressor']['CompressedProperties']['Temperature']<CycleParameters['MainCompressor']['CompressedProperties']['Temperature']:
		raise Exception("main compressor outlet temperature is higher than the recompressor outlet temperature, most likely because main compressor efficiency is too low and/or precompressor pressure ratio is too low. handling this scenario properly is not yet implemented")

#need to check and see if the main compressor outlet temperature is below certain temperatures (maximum temperature, anything else??)
#any other similiar scenarios that need to be caught other places????????




	#now that the correct recompressor pressure ratio has been found, assign some values
	#recompressor
	CycleParameters['TotalSpecificWorkInput_TotalMassFlow']+=CycleParameters['ReCompressor']['SpecificWorkInput_TotalMassFlow']
	CycleParameters['ReCompressor']['StartingProperties']['StateNumber']=14
	#FirstHPHeating
	CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']+=CycleParameters['FirstHPHeating']['SpecificHeatAdded_TotalMassFlow']
	CycleParameters['FirstHPHeating']['StartingProperties']['StateNumber']=2
	CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['FirstHPHeating']['StartingProperties']['StateNumber'],3*math.pi/4,ArrowAngleTP=math.pi/4)
	CurrentProperties=CycleParameters['FirstHPHeating']['HeatedProperties']




	#second and third heat input on the high pressure side includes both recuporator and heat input
	CycleParameters['SecondPlusThirdHeating']=Heater(CurrentProperties,CycleInputParameters['SecondPlusThirdHeating'])
	CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']+=CycleParameters['SecondPlusThirdHeating']['SpecificHeatAdded_TotalMassFlow']
	CycleParameters['SecondPlusThirdHeating']['StartingProperties']['StateNumber']=CycleParameters['ReCompressor']['CompressedProperties']['StateNumber']=4
	CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['SecondPlusThirdHeating']['StartingProperties']['StateNumber'],3*math.pi/4,ArrowAngleTP=math.pi/4)
	CurrentProperties=CycleParameters['SecondPlusThirdHeating']['HeatedProperties']

	#virtual turbine that combines three parallel turbines since they are supposed to have the same pressure ratio and the flow splits at the inlets and recombines at the outlets

	#check to see how the main compressor should be powered
	if CycleInputParameters['MainCompressor']['ElectricallyPowered'] == True:		#if this field is not set, then it defaults to a dedicated turbine for the main compressor.
		#a dedicated turbine for the main compressor does not exist, so don't require the "VirtualTurbine" to include work to power it. instead, the work will come from the rest of the output power, which is in the power turbine.
		WorkToMatch=CycleParameters['TotalSpecificWorkInput_TotalMassFlow']-CycleParameters['MainCompressor']['SpecificWorkInput_TotalMassFlow']
	else:
		#a dedicated turbine for the main compressor does exist.
		WorkToMatch=CycleParameters['TotalSpecificWorkInput_TotalMassFlow']

	#now that WorkToMatch has been defined, process the VirtualTurbine
	CycleParameters['VirtualTurbine']=RealTurbine(CurrentProperties,CycleInputParameters['VirtualTurbine'],WorkToMatch=WorkToMatch)

	CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']+=CycleParameters['VirtualTurbine']['SpecificWorkOutput_TotalMassFlow']
	CycleParameters['VirtualTurbine']['StartingProperties']['StateNumber']=6
	CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['VirtualTurbine']['StartingProperties']['StateNumber'],3*math.pi/4,ArrowAngleTP=math.pi/4)
	CurrentProperties=CycleParameters['VirtualTurbine']['ExpandedProperties']

	#calculate the mass fraction through each of the turbines
	CycleParameters['MainCompressorTurbine']=CycleParameters['VirtualTurbine'].copy()
	CycleParameters['MainCompressorTurbine']['MassFraction']=CycleParameters['MainCompressor']['SpecificWorkInput_TotalMassFlow']/CycleParameters['VirtualTurbine']['SpecificWorkOutput_TotalMassFlow']
	CycleParameters['MainCompressorTurbine']['SpecificWorkOutput_TotalMassFlow']=CycleParameters['VirtualTurbine']['SpecificWorkOutput_TotalMassFlow']*CycleParameters['MainCompressorTurbine']['MassFraction']

	CycleParameters['PreCompressorTurbine']=CycleParameters['VirtualTurbine'].copy()
	CycleParameters['PreCompressorTurbine']['MassFraction']=CycleParameters['PreCompressor']['SpecificWorkInput_TotalMassFlow']/CycleParameters['VirtualTurbine']['SpecificWorkOutput_TotalMassFlow']
	CycleParameters['PreCompressorTurbine']['SpecificWorkOutput_TotalMassFlow']=CycleParameters['VirtualTurbine']['SpecificWorkOutput_TotalMassFlow']*CycleParameters['PreCompressorTurbine']['MassFraction']

	CycleParameters['ReCompressorTurbine']=CycleParameters['VirtualTurbine'].copy()
	CycleParameters['ReCompressorTurbine']['MassFraction']=CycleParameters['ReCompressor']['SpecificWorkInput_TotalMassFlow']/CycleParameters['VirtualTurbine']['SpecificWorkOutput_TotalMassFlow']
	CycleParameters['ReCompressorTurbine']['SpecificWorkOutput_TotalMassFlow']=CycleParameters['VirtualTurbine']['SpecificWorkOutput_TotalMassFlow']*CycleParameters['ReCompressorTurbine']['MassFraction']


	#reheat
	if CycleInputParameters['ReHeat']['Active'] != False:		#assume reheat should be turned on unless explicitly set to false or 0 or 0.0
		CycleParameters['ReHeat']['Stages']=[Heater(CurrentProperties,CycleInputParameters['ReHeat'])]			#note, this is a list with one element in it that is a dictionary. more dictionaries will be added to the list below if there is interstage reheat.
		CycleParameters['ReHeat']['Stages'][0]['StartingProperties']['StateNumber']=7
		CurrentProperties=CycleParameters['ReHeat']['Stages'][0]['HeatedProperties']

		#figure out how many stages there are with interstage reheat
		if (CycleInputParameters['ReHeat']['Active']=={}) or (CycleInputParameters['ReHeat']['Active']==True):			#no value defaults to a single inter turbine reheat.
			#there is not interstage reheat, so just set the number of stages to 1 because the code below will just treat a single stage with interstage reheat as a regular turbine
			Stages=1
		else:
			Stages=CycleInputParameters['ReHeat']['Active']

			#if there is interstage reheat, modify the turbines isentropic efficiency so that it is actually per stage isentropic efficiency.
			#currently, just setting it to the the same as an entire regular turbine. this isn't correct, but have no idea what the real thing would be without actually doing a preliminary design
			#of a turbine with interstage reheat. so, don't want to make up a number right now here since it will be a lot of work will be required to rationalize anything and it will probably have low accruacy anyway.
			#also, need to derive a formula for a per stage efficiency based on total turbine efficiency and per stage pressure ratio as well as the pressure drop in the heat exchanger, and variable fluid properties
			#(formula found in text book was for no interstage reheat (obviously) and constant fluid properties).
			CycleInputParameters['PowerTurbine']=CycleInputParameters['PowerTurbine']

	else:
		#there is no reheat, so just set the number of stages to 1 because the code below will just treat a single stage with no reheat as a regular turbine
		Stages=1


	#power turbine
	#need to iteratively solve for the power turbine pressure ratio
	#define the convergence parameters
	ConvergenceCriteria=1.0e-6
	SecondaryConvergenceCriteria=3.0e-3
	MaxIterations=20

	#first guess is based on no pressure drop in the heat exchangers
	PressureRatioOld=CurrentProperties['Pressure']/(CycleParameters['PreCompressor']['StartingProperties']['Pressure'])	#warning, this is starting/final, instead of final/starting like the rest of the code
	#preallocate all so they are defined, so they can all be deleted without having to check for existence
	PressureRatioOldOld=PressureRatioOldOldOld=0

	if PressureRatioOld<1.0:
		PrintWarning('pressure drop during heating too high and turbine inlet pressure is below the minimum cycle pressure, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	for count in arange(0,MaxIterations):

		CurrentPropertiesTrial=CurrentProperties

		#intialize the interstage reheat pressure loss
		InterstageReHeatPressureRatio=1.0

		if Stages>0:
			StagePressureRatio=(PressureRatioOld)**(1/float(Stages))

		#pre-allocate the lists

		if CycleInputParameters['ReHeat']['Active'] != False:				#even though this variable will never be used if there is no reheat, SmartDictionary will great an empty dictionary for CycleParameters['ReHeat']['Stages'], just by trying to access it.
			ReHeatStages=deepcopy(CycleParameters['ReHeat']['Stages'])		#first stage of reheat is not interstage, but determined above.
		else:
			ReHeatStages=None							#set this so some things below are simpler


		CycleParameters.pop('PowerTurbine',None)					#clear out PowerTurbine, just to avoid potential bugs from not being found
		CycleParameters['PowerTurbine']['SpecificWorkOutput_TotalMassFlow']=0		#initialize to 0
		CycleParameters['PowerTurbine']['Stages']=[]

		for Stage in range(Stages):
			#process half of a stage (the rotor) and then half of the next stage (the nozzle)
			#first half of first stage is a regular nozzle and has no reheat because that was already done in a regular heat exchanger.

			#run the turbine with the guessed pressure ratio
			CycleParameters['PowerTurbine']['Stages']+=[RealTurbine(CurrentPropertiesTrial,CycleInputParameters['PowerTurbine'],PressureRatio=StagePressureRatio)]		#add another element to the list

			CycleParameters['PowerTurbine']['SpecificWorkOutput_TotalMassFlow']+=CycleParameters['PowerTurbine']['Stages'][Stage]['SpecificWorkOutput_TotalMassFlow']

			#remember the state. note these are a new nomenclature, ie. 7, 72, 73, etc..
			if Stage==0:
				CycleParameters['PowerTurbine']['Stages'][Stage]['StartingProperties']['StateNumber']=8
			else:
				CycleParameters['PowerTurbine']['Stages'][Stage]['StartingProperties']['StateNumber']=CycleParameters['PowerTurbine']['Stages'][0]['StartingProperties']['StateNumber']*10+Stage+1

			#do reheat for the next stage.
			#assumes there is a pressure loss that is the same relationship as the other heaters.
			if Stage!=(Stages-1):		#don't do reheat after the last stage.
				ReHeatStages+=[Heater(CycleParameters['PowerTurbine']['Stages'][Stage]['ExpandedProperties'],CycleInputParameters['ReHeat'])]		#add another element to the list

				#need to use CurrentPropertiesTrial above in RealTurbine because don't know if there is regular (not interstage) reheat or not for the beginning of the turbine
				CurrentPropertiesTrial=ReHeatStages[Stage+1]['HeatedProperties']

				#figure out the pressure drop due to each of the interstage reheats
				InterstageReHeatPressureRatio*=ReHeatStages[Stage+1]['PressureRatio']

				#remember the state. note these are a new nomenclature, ie. 7, 72, 73, etc..
				ReHeatStages[Stage+1]['StartingProperties']['StateNumber']=CycleParameters['ReHeat']['Stages'][0]['StartingProperties']['StateNumber']*10+Stage+1+1




		#create a combined CycleParameters['PowerTurbine']
		CycleParameters['PowerTurbine']['StartingProperties']=CycleParameters['PowerTurbine']['Stages'][0]['StartingProperties']
		CycleParameters['PowerTurbine']['ExpandedProperties']=CycleParameters['PowerTurbine']['Stages'][-1]['ExpandedProperties']
		CycleParameters['PowerTurbine']['PressureRatio']=CycleParameters['PowerTurbine']['StartingProperties']['Pressure']/CycleParameters['PowerTurbine']['ExpandedProperties']['Pressure']



		#once a temperature is calculated for the power turbine exit, calculate the pressure drop accross the heat exchangers
		CycleParameters['TotalFractionCooler']=Cooler(CycleParameters['PowerTurbine']['ExpandedProperties'],CycleInputParameters['TotalFractionCooler'])

		#then calculate a new power turbine pressure ratio for the next iteration
		PressureRatio=(CycleParameters['PowerTurbine']['StartingProperties']['Pressure']/CycleParameters['PreCompressor']['StartingProperties']['Pressure'])*CycleParameters['TotalFractionCooler']['PressureRatio']*InterstageReHeatPressureRatio		#warning, this is starting/final, instead of final/starting like the rest of the code


		#!!!!!!!!!!!!!!!note, if there is interstage reheat, this is really the per stage pressure ratio times the number of stages!!!!!!!!!!!!!!!!!!!!!!!!!!
		PrintWarning("power turbine Pressure Ratio: "+str(PressureRatio))

		if PressureRatio<0.25:
			#if pressure ratio is far less than 1, don't even try any more because it is probably not a running engine and other functions may error out because fluid properties are out of range
			break

		#check for convergence (minimize the residual) --- may want to change this section of code (above and below) to use a root finding function instead....
		#first see if the residual is really low
		#note, in this search (the turbine), the first guess may be right, whereas, in the heat exchangers, the first guess was never right because the temperature AND pressure were unknown
		PressureRatioResidual=abs(1-PressureRatio/PressureRatioOld)
		PrintWarning("power turbine PressureRatioResidual: "+str(PressureRatioResidual))
		if PressureRatioResidual<ConvergenceCriteria:
			break
		#next, see if even if the residual is not low, is it oscillating around a fixed value?
		if count>0:
			if CheckPercentage(PressureRatio,PressureRatioOldOld,1.0e-13) or (count>1 and CheckPercentage(PressureRatio,PressureRatioOldOldOld,1.0e-13)):
				if PressureRatioResidual<SecondaryConvergenceCriteria:
					PrintWarning("power turbine Presure ratio residuals stopped changing but primary convergence criteria not yet met. secondary convergence criteria met.")
					break
				elif count==(MaxIterations-1):
					print("power turbine pressure did not converge in "+str(MaxIterations)+" iterations. residuals stopped changing but primary and secondary convergence criteria not met.")
					break
		#did not converge
		if count==(MaxIterations-1):
			raise Exception("pressure did not converge in "+str(MaxIterations)+" iterations. residuals did not stop changing")

		#save values for the next iteration to test convergence
		if count>0:
			PressureRatioOldOldOld=PressureRatioOldOld
		PressureRatioOldOld=PressureRatioOld
		PressureRatioOld=PressureRatio

	if PressureRatio<1.00000001:					#require it to be slightly over 1 because if roundoff error allows it to be greater than one it will allow for a non-running engine.
		PrintWarning('pressure drops in heat exchangers too high, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	#now that the pressure ratio has converged, save the reheats (if there is any reheat)
	if ReHeatStages is not None:
		CycleParameters['ReHeat']['Stages']=ReHeatStages

	#add up all the heat added by the reheats and also add the state points
	CycleParameters['ReHeat']['SpecificHeatAdded_TotalMassFlow']=0			#initialize to 0
	for StageDictionary in CycleParameters['ReHeat']['Stages']:
		CycleParameters['ReHeat']['SpecificHeatAdded_TotalMassFlow']+=StageDictionary['SpecificHeatAdded_TotalMassFlow']
		CycleParameters['States']=AddState(CycleParameters['States'],StageDictionary['StartingProperties'],StageDictionary['StartingProperties']['StateNumber'],5.25*math.pi/4)

	if CycleInputParameters['ReHeat']['Active'] != False:
		#now add the total heat added by the reheats to the heat added in the cycle
		CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']+=CycleParameters['ReHeat']['SpecificHeatAdded_TotalMassFlow']


	#get rid of some variables since this same code is used for the power turbine pressure ratio, and it isn't placed in a function
	del(count,PressureRatioResidual,PressureRatio,PressureRatioOld,PressureRatioOldOld,PressureRatioOldOldOld,ReHeatStages)



	#add the state points for the turbine stages
	for StageDictionary in CycleParameters['PowerTurbine']['Stages']:
		CycleParameters['States']=AddState(CycleParameters['States'],StageDictionary['StartingProperties'],StageDictionary['StartingProperties']['StateNumber'],2*math.pi/4)

	#now that the correct power turbine pressure ratio has been found, assign some values
	CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']+=CycleParameters['PowerTurbine']['SpecificWorkOutput_TotalMassFlow']


	CurrentProperties=CycleParameters['PowerTurbine']['ExpandedProperties']

	#############################################################################################################################################
	#recuperators
	#############################################################################################################################################
	#high temperature recuperator
	if CycleParameters['PowerTurbine']['ExpandedProperties']['Temperature']-CycleInputParameters['HTRecuperator']['MinimumDeltaT']>CycleParameters['ReCompressor']['CompressedProperties']['Temperature']:	#high temperature recuperator exists
		PrintWarning('==high temperature recuperator==')
		CycleParameters['HTRecuperator']['LowPressure']['StartingProperties']=CycleParameters['PowerTurbine']['ExpandedProperties']
		CycleParameters['HTRecuperator']['HighPressure']['StartingProperties']=CycleParameters['ReCompressor']['CompressedProperties']
		CycleParameters['HTRecuperator']=GeneralRealRecuperator(CycleParameters['HTRecuperator'],CycleInputParameters['HTRecuperator'])
		CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']-=CycleParameters['HTRecuperator']['SpecificHeatRecuperated_TotalMassFlow']
		CycleParameters['HTRecuperator']['LowPressure']['StartingProperties']['StateNumber']=9
		CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['HTRecuperator']['LowPressure']['StartingProperties'],CycleParameters['HTRecuperator']['LowPressure']['StartingProperties']['StateNumber'],-2*math.pi/4,ArrowAngleTP=math.pi)
		CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties']['StateNumber']=5
		CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties'],CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties']['StateNumber'],3*math.pi/4,ArrowAngleTP=math.pi/4)
		CurrentProperties=CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties']
		HTRecuperator=True
	else:
		HTRecuperator=False


	#medium temperature recuperator
	if HTRecuperator and (CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties']['Temperature']-CycleInputParameters['MTRecuperator']['MinimumDeltaT']>CycleParameters['MainCompressor']['CompressedProperties']['Temperature']):	#medium temperature recuperator exists
		PrintWarning('==medium temperature recuperator==')







#need to allow for medium and/or(?) low temperature recuperators with no high temperature recuperator

#note, if there are no recuperators, having recompression makes no sense and the optimizer SHOULD drive the
#precompressor to 1 and the recompression fraction to anything (because main compressor and recompressor will have the same pressure ratio and oulet (they are really the same thing)) and the main compressor (and recompressor) away from 1
#OR the main compressor (and recompressor) to 1 and the recompression fraction to 1 and the precompressor away from 1
#OR the recompression fraction to 0 and the main and precompressor pressure ratios to anything (and they can each be different)
#some of the above statements assume that the main compressor and precompressor are configured to always have the same inlet temperature (which the cycle currently enforces)
#see also the combined cycle treatment that depends on this common main and precompressor inlet temperature




		#note:seems to be a little bit of error stack up that can make
		#	CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties']['Temperature']<CycleParameters['MainCompressor']['CompressedProperties']['Temperature']
		#instead of just being equal, when precompressor pressure ratio is 1 and the medium temperature recuperator does not exist
		#although, the medium temperature recuperator can exist if the precompressor inlet temperature is greater than the main compressor inlet temperature (which is not yet implemented)

		CycleParameters['MTRecuperator']['LowPressure']['StartingProperties']=CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties']

		#check to see if there is a low temperature recuperator or not
		#there is a separate low temperature recuperator if the precompressor outlet temperature is greater than
		#the main compressor outlet temperature. actually, didn't necessarily really need to make a seperate low temperature recuperator
		#for the main fraction, before precompression (points 11-12), but originally did that because both low temperature recuperators were
		#lumped together. now they have actually been separated, but think it is still useful to keep medium temperature recuperator (points 10-11) and low
		#temperature recuperator (points 11-12) separated because both low temperature recuperators are operating in parallel, so they have
		#to be dealt with together in order to evaluate pinching on the high pressure side. when there is no low temperature recuperator on the
		#precompressed fluid, this combined pinching effect isn't an issue, so medium temperature recuperator and low temperature recuperator
		#on the low pressure side can be lumped together and both low temperature recuperators can be skipped alltogether.

		if CycleParameters['PreCompressor']['CompressedProperties']['Temperature']-CycleInputParameters['LTRecuperator']['MainFraction']['MinimumDeltaT']>CycleParameters['MainCompressor']['CompressedProperties']['Temperature']:
			#precompressor is used to do more recuperation
			#low temperature recuperators still exist
			#medium temperature recuperator lower temperature is equal to the pre compressor outlet temperature
			CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']['Temperature']=CycleParameters['PreCompressor']['CompressedProperties']['Temperature']
			LTRecuperators=True
		else:
			#precompressor is just used for intercooling effects (or not at all if PR=1)
			#both low temperature recuperators don't exist and the efforts of the main low temperature recuperator (points 11-12) is lumped in with the medium temperature recuperator
			#medium temperature recuperator lower temperature is equal to the main compressor outlet temperature
			CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']['Temperature']=CycleParameters['MainCompressor']['CompressedProperties']['Temperature']
			LTRecuperators=False
		#note, didn't have to do an extra check for the High Temperature Recuperator high pressure inlet temperature (depending on if medium temperature recuperator existed)
		#because the high temperature recuperator high pressure inlet temperature will always be the recompressor outlet, which is always greater than or equal to the main compressor outlet

		CycleParameters['MTRecuperator']['HighPressure']['RecuperatedProperties']=CycleParameters['ReCompressor']['CompressedProperties']

		#since the MTRecuperator starting and recuperated properties have been defined, calculate the pressure drop before running the recuperator function (which calculates how much the recuperator is actually a heater and cooler, and the other unknown boundary)
		CycleParameters['MTRecuperator']['HighPressure']['DeltaT']=CycleParameters['MTRecuperator']['HighPressure']['RecuperatedProperties']['Temperature']-CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']['Temperature']
		CycleParameters['MTRecuperator']['HighPressure']['DeltaP']=CycleParameters['MTRecuperator']['HighPressure']['DeltaT']*CycleInputParameters['MTRecuperator']['DeltaPPerDeltaT']
		CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']['Pressure']=CycleParameters['MTRecuperator']['HighPressure']['RecuperatedProperties']['Pressure']+CycleParameters['MTRecuperator']['HighPressure']['DeltaP']

		#now that the entire starting properties has been defined, populate the rest of the values
		CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']=GetFluidProperties(CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']['Pressure'],Temperature=CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']['Temperature'])

		#run the recuperator
		CycleParameters['MTRecuperator']=GeneralRealRecuperator(CycleParameters['MTRecuperator'],CycleInputParameters['MTRecuperator'])

	#need to check heater and coolers add up to how the same values are calculated in this part of the code

		CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']-=CycleParameters['MTRecuperator']['SpecificHeatRecuperated_TotalMassFlow']
		CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']['StateNumber']=3
		CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['MTRecuperator']['HighPressure']['StartingProperties'],CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']['StateNumber'],3*math.pi/4,ArrowAngleTP=math.pi/4)
		CycleParameters['MTRecuperator']['LowPressure']['StartingProperties']['StateNumber']=10
		CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['MTRecuperator']['LowPressure']['StartingProperties'],CycleParameters['MTRecuperator']['LowPressure']['StartingProperties']['StateNumber'],-1*math.pi/4,ArrowAngleTP=3*math.pi/4)
		CurrentProperties=CycleParameters['MTRecuperator']['LowPressure']['RecuperatedProperties']


		if LTRecuperators:
			#low temperature recuperator
			#define common inputs on the high pressure side
			CycleParameters['LTRecuperator']['HighPressure']['StartingProperties']=CycleParameters['MainCompressor']['CompressedProperties']
			CycleParameters['LTRecuperator']['HighPressure']['RecuperatedProperties']=CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']

			#low temperature recuperator, main fraction
			PrintWarning('==low temperature recuperator, main fraction==')
			CycleParameters['LTRecuperator']['MainFraction']['HighPressure']=CycleParameters['LTRecuperator']['HighPressure']	#make a copy so the inputs to the recouporator function will be common
			CycleParameters['LTRecuperator']['MainFraction']['LowPressure']['StartingProperties']=CycleParameters['PreCompressor']['CompressedProperties']
			CycleParameters['LTRecuperator']['MainFraction']=GeneralRealRecuperator(CycleParameters['LTRecuperator']['MainFraction'],CycleInputParameters['LTRecuperator']['MainFraction'])
			CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']-=CycleParameters['LTRecuperator']['MainFraction']['SpecificHeatRecuperated_TotalMassFlow']
			CycleParameters['LTRecuperator']['MainFraction']['LowPressure']['StartingProperties']['StateNumber']=14
			CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['LTRecuperator']['MainFraction']['LowPressure']['StartingProperties'],CycleParameters['LTRecuperator']['MainFraction']['LowPressure']['StartingProperties']['StateNumber'],5.25*math.pi/4)
			CycleParameters['LTRecuperator']['MainFraction']['LowPressure']['RecuperatedProperties']['StateNumber']=15
			CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['LTRecuperator']['MainFraction']['LowPressure']['RecuperatedProperties'],CycleParameters['LTRecuperator']['MainFraction']['LowPressure']['RecuperatedProperties']['StateNumber'],5.25*math.pi/4)

			#low temperature recuperator, total fraction
			PrintWarning('==low temperature recuperator, total fraction==')
			CycleParameters['LTRecuperator']['TotalFraction']['HighPressure']=CycleParameters['LTRecuperator']['HighPressure']	#make a copy so the inputs to the recouporator function will be common
			CycleParameters['LTRecuperator']['TotalFraction']['LowPressure']['StartingProperties']=CycleParameters['MTRecuperator']['LowPressure']['RecuperatedProperties']
			CycleParameters['LTRecuperator']['TotalFraction']=GeneralRealRecuperator(CycleParameters['LTRecuperator']['TotalFraction'],CycleInputParameters['LTRecuperator']['TotalFraction'])
			CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']-=CycleParameters['LTRecuperator']['TotalFraction']['SpecificHeatRecuperated_TotalMassFlow']
			CycleParameters['LTRecuperator']['TotalFraction']['LowPressure']['StartingProperties']['StateNumber']=11
			CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['LTRecuperator']['TotalFraction']['LowPressure']['StartingProperties'],CycleParameters['LTRecuperator']['TotalFraction']['LowPressure']['StartingProperties']['StateNumber'],-1*math.pi/4,ArrowAngleTP=3*math.pi/4)
			CycleParameters['LTRecuperator']['TotalFraction']['LowPressure']['RecuperatedProperties']['StateNumber']=12
			CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['LTRecuperator']['TotalFraction']['LowPressure']['RecuperatedProperties'],CycleParameters['LTRecuperator']['TotalFraction']['LowPressure']['RecuperatedProperties']['StateNumber'],6*math.pi/4,ArrowAngleTP=math.pi)

#			raise Exception('break')


		else:
			#make the low pressure outlet of the medium temperature recuperator and precompressor outlet show up on the cycle plot
			CycleParameters['MTRecuperator']['LowPressure']['RecuperatedProperties']['StateNumber']=11
			CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['MTRecuperator']['LowPressure']['RecuperatedProperties'],CycleParameters['MTRecuperator']['LowPressure']['RecuperatedProperties']['StateNumber'],-1*math.pi/4,ArrowAngleTP=3*math.pi/4)
			CycleParameters['PreCompressor']['CompressedProperties']['StateNumber']=14
			CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['PreCompressor']['CompressedProperties'],CycleParameters['PreCompressor']['CompressedProperties']['StateNumber'],5.25*math.pi/4)
	else:	#no medium or low temperature recuperators
		LTRecuperators=False

		if HTRecuperator:
			#make the low pressure outlet of the high temperature recuperator show up on the cycle plot
			CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties']['StateNumber']=10
			CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties'],CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties']['StateNumber'],-1*math.pi/4,ArrowAngleTP=3*math.pi/4)
			#shouldn't need any more states because the precompressor and recompressor points should be overlapped with the main compressor for this scenario

#might want to look into a better way of defining the states so it is not as hard to figure out what to do for each variation of what heat exchangers are used.


	#############################################################################################################################################
	#end recuperators
	#############################################################################################################################################


	#compute the net work
	CycleParameters['SpecificNetWork']=CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']-CycleParameters['TotalSpecificWorkInput_TotalMassFlow']
	if CycleParameters['SpecificNetWork']<0.0:
		PrintWarning('compressors use more power than turbines produce, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	#see if any heat was even added to the system
	if CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']<0.0:
		PrintWarning('no heat was added to the system, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	#compute the back work ratio
	CycleParameters['BackWorkRatio']=CycleParameters['TotalSpecificWorkInput_TotalMassFlow']/CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']

	#compute work fraction
#note!!!!!!!!!!!!!!, this name NetWorkFraction is incorrect. it should be called TotalWorkFraction. the PowerTurbineWorkFraction below should be called NetWorkFraction instead since CycleParameters['PowerTurbine']['SpecificWorkOutput_TotalMassFlow'] should be the same as CycleParameters['SpecificNetWork']
	CycleParameters['MainCompressorTurbine']['NetWorkFraction']=CycleParameters['MainCompressorTurbine']['SpecificWorkOutput_TotalMassFlow']/CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']
	CycleParameters['PreCompressorTurbine']['NetWorkFraction']=CycleParameters['PreCompressorTurbine']['SpecificWorkOutput_TotalMassFlow']/CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']
	CycleParameters['ReCompressorTurbine']['NetWorkFraction']=CycleParameters['ReCompressorTurbine']['SpecificWorkOutput_TotalMassFlow']/CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']
	CycleParameters['PowerTurbine']['NetWorkFraction']=CycleParameters['PowerTurbine']['SpecificWorkOutput_TotalMassFlow']/CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']

	#compute power turbine work fraction
	CycleParameters['MainCompressorTurbine']['PowerTurbineWorkFraction']=CycleParameters['MainCompressorTurbine']['SpecificWorkOutput_TotalMassFlow']/CycleParameters['PowerTurbine']['SpecificWorkOutput_TotalMassFlow']
	CycleParameters['PreCompressorTurbine']['PowerTurbineWorkFraction']=CycleParameters['PreCompressorTurbine']['SpecificWorkOutput_TotalMassFlow']/CycleParameters['PowerTurbine']['SpecificWorkOutput_TotalMassFlow']
	CycleParameters['ReCompressorTurbine']['PowerTurbineWorkFraction']=CycleParameters['ReCompressorTurbine']['SpecificWorkOutput_TotalMassFlow']/CycleParameters['PowerTurbine']['SpecificWorkOutput_TotalMassFlow']



	#also compare the heat recuperated in the second low temperature recuperator compared to the precompressor work used to allow that to be recuperated
	if LTRecuperators:
		CycleParameters['PreCompressor']['PowerInputvsRecuperatedHeatFraction']=CycleParameters['PreCompressor']['SpecificWorkInput_TotalMassFlow']*CycleInputParameters['LTRecuperator']['MainFraction']['LowPressure']['MassFraction']/CycleParameters['LTRecuperator']['MainFraction']['SpecificHeatRecuperated_TotalMassFlow']

	#compute the cycle efficiency
	CycleParameters['CycleRealEfficiency']=CycleParameters['SpecificNetWork']/CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']

	#calculate the exergy efficiency
	CycleParameters['CycleExergyEfficiency']=CycleParameters['CycleRealEfficiency']/CycleParameters['CycleCarnotEfficiency']

#do a couple more efficiency calculations to make sure they all match up?


	#do some checks to make sure the result is meaningful.
	#note, these error checks used to be in CyclePermutationWrapper, which allowed them to be raised seperate of other errors that were caught,
	#which helps to identify unclassified problems that were able to make it this far in the function without being caught by a more specific error check.
	#but hadn't had major problems in a while now that the code is fairly robust and when problems did happen, didn't want to have everything crash because
	#they were rare and it would have been better to just ignore that case and let the run complete, especially since now doing some very long runs.

	if CycleParameters['CycleRealEfficiency']>CycleParameters['CycleCarnotEfficiency']:
		#print values
		PrintKeysAndValues("Cycle Input Parameters",CycleInputParameters)
		PrintKeysAndValues("Cycle Outputs",CycleParameters)
		raise ValueError('CycleRealEfficiency='+str(round(CycleParameters['CycleRealEfficiency'],3))+'      CycleCarnotEfficiency='+str(round(CycleParameters['CycleCarnotEfficiency'],3)))
	elif (CycleParameters['CycleRealEfficiency']>CycleParameters['CycleCarnotEfficiency']*CycleInputParameters['PowerTurbine']['IsentropicEfficiency']):
		#do another sanity check because efficiency should always be less than carnot efficiency times power turbine efficiency

		#print values
		PrintKeysAndValues("Cycle Input Parameters",CycleInputParameters)
		PrintKeysAndValues("Cycle Outputs",CycleParameters)
		raise ValueError('CycleRealEfficiency='+str(round(CycleParameters['CycleRealEfficiency'],3))+'      CycleCarnotEfficiency*PowerTurbineEfficiency='+str(round(CycleParameters['CycleCarnotEfficiency']*CycleInputParameters['PowerTurbine']['IsentropicEfficiency'],3)))








	return CycleParameters

























#simple cycle with no recuperation
def SimpleCycle(CycleInputParameters):
	CycleParameters=SmartDictionary()

	CycleParameters['Fluid']=FluidProperties.REFPROP.FluidName			#should currently be air

	#compute the carnot cycle efficiency for reference, now rather than later in case the cycle can't run because of too high heat exchanger pressure drops
	CycleParameters['CycleCarnotEfficiency']=1-(CycleInputParameters['StartingProperties']['Temperature'])/(CycleInputParameters['MaximumTemperature'])

	CycleParameters['TotalSpecificWorkInput_TotalMassFlow']=0
	CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']=0
	CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']=0


	#main compressor
	CurrentProperties=GetFluidProperties(Pressure=CycleInputParameters['MainCompressor']['InletPressure'],Temperature=CycleInputParameters['StartingProperties']['Temperature'])

	if (CycleInputParameters['CombinedFuelCellAndCombustor']['FuelCellFuelUtilization']=={}) or (CycleInputParameters['CombinedFuelCellAndCombustor']['FuelCellFuelUtilization']==0):
		#running with pure air and external heating, so the main flow is everything.
		CycleInputParameters['MainCompressor']['MassFraction']=1.0
	else:
		CycleInputParameters['MainCompressor']['MassFraction']=ComputeMassOfAirToTotalMassRatio(PercentExcessOxygen=CycleInputParameters['CombinedFuelCellAndCombustor']['PercentExcessOxygen'])

		#also set a higher total fraction cooler temperature because REFPROP can't handle lower temperatures with water vapour condensing
		CycleInputParameters['TotalFractionCooler']['MinimumTemperature']=273+70

	CycleParameters['MainCompressor']=RealCompressor(CurrentProperties,CycleInputParameters['MainCompressor'])
	CycleParameters['TotalSpecificWorkInput_TotalMassFlow']+=CycleParameters['MainCompressor']['SpecificWorkInput_TotalMassFlow']
	CycleParameters['MainCompressor']['StartingProperties']['StateNumber']=1
	CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['MainCompressor']['StartingProperties']['StateNumber'],5*math.pi/4,ArrowAngleTP=-math.pi/6)

	if (CycleInputParameters['CombinedFuelCellAndCombustor']['FuelCellFuelUtilization']=={}) or (CycleInputParameters['CombinedFuelCellAndCombustor']['FuelCellFuelUtilization']==0):
		#running without a fuel cell and with idealized heating and pure air in the heater, turbine, and exhaust heat exchanger.

		#second and third heat input on the high pressure side includes both recuporator and heat input
		CurrentProperties=CycleParameters['MainCompressor']['CompressedProperties']
		CycleParameters['SecondPlusThirdHeating']=Heater(CurrentProperties,CycleInputParameters['SecondPlusThirdHeating'])
		CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']+=CycleParameters['SecondPlusThirdHeating']['SpecificHeatAdded_TotalMassFlow']
		CycleParameters['SecondPlusThirdHeating']['StartingProperties']['StateNumber']=4
		CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['SecondPlusThirdHeating']['StartingProperties']['StateNumber'],3*math.pi/4,ArrowAngleTP=math.pi/4)
		CurrentProperties=CycleParameters['SecondPlusThirdHeating']['HeatedProperties']

	else:
		#running with fuel cell, fuel, and chemistry considered

		#fuel compressor
		SetupFluid('methane')
		CurrentProperties=GetFluidProperties(Pressure=CycleInputParameters['MainCompressor']['InletPressure'],Temperature=CycleInputParameters['StartingProperties']['Temperature'],ExtendedProperties=True)	#use the same inlet pressure as the main compressor, although it will actually be a little higher in the gas supply line. get ExtentedProperties so that if need to do extrapolation, have specific heat values to start from.
		CycleInputParameters['FuelCompressor']['MassFraction']=ComputeMassOfFuelToTotalMassRatio(PercentExcessOxygen=CycleInputParameters['CombinedFuelCellAndCombustor']['PercentExcessOxygen'])
		CycleParameters['FuelCompressor']=RealCompressor(CurrentProperties,CycleInputParameters['FuelCompressor'])
		CycleParameters['TotalSpecificWorkInput_TotalMassFlow']+=CycleParameters['FuelCompressor']['SpecificWorkInput_TotalMassFlow']

	#skip plotting the fuel compression because it will be confusing and it is a small amount of work anyway and because
	#don't currently calculate temperature or entropy with the methane property extrapolation method in use to get to the higher temperatures needed
	#	CycleParameters['FuelCompressor']['StartingProperties']['StateNumber']=111
	#	CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['FuelCompressor']['StartingProperties']['StateNumber'],5*math.pi/4,ArrowAngleTP=-math.pi/6)


		#fuel cell and combustor
		#fuel cell function converts fluid over to CombustionProducts
		CurrentProperties=CycleParameters['MainCompressor']['CompressedProperties']
		CycleParameters['CombinedFuelCellAndCombustor']=CombinedFuelCellAndCombustor(CurrentProperties,CycleParameters['FuelCompressor']['CompressedProperties'],CycleInputParameters['CombinedFuelCellAndCombustor'])
		CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']+=CycleParameters['CombinedFuelCellAndCombustor']['SpecificWorkOutput_TotalMassFlow']
		CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']+=CycleParameters['CombinedFuelCellAndCombustor']['SpecificEnergyAdded_TotalMassFlow']
		CycleParameters['CombinedFuelCellAndCombustor']['StartingProperties']['StateNumber']=4
		CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['CombinedFuelCellAndCombustor']['StartingProperties']['StateNumber'],3*math.pi/4,ArrowAngleTP=math.pi/4)
		CurrentProperties=CycleParameters['CombinedFuelCellAndCombustor']['HeatedProperties']




	#this is actually a little overly conservative maybe because it assumes a pressure drop exists for the heat that doesn't actually get used by any of the CO2 engines.
	#actually, currently have the pressure drop set to zero for this engine, which isn't realistic
	#also, for right now have it set at a fixed minimum temperature of 70C for the cooler because of issues with REFPROP and water vapour, so the over conservativeness wouldn't be that terrible
	#if a pressure drop were re-introduced, but it really isn't the best way for all this to be right now

	#power turbine
	#need to iteratively solve for the power turbine pressure ratio
	#define the convergence parameters
	ConvergenceCriteria=1.0e-6
	SecondaryConvergenceCriteria=3.0e-3
	MaxIterations=20

	#first guess is based on no pressure drop in the heat exchangers
	PressureRatioOld=CurrentProperties['Pressure']/(CycleParameters['MainCompressor']['StartingProperties']['Pressure'])	#warning, this is starting/final, instead of final/starting like the rest of the code
	#preallocate all so they are defined, so they can all be deleted without having to check for existence
	PressureRatioOldOld=PressureRatioOldOldOld=0

	if PressureRatioOld<1.0:
		PrintWarning('pressure drop during heating too high and turbine inlet pressure is below the minimum cycle pressure, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	for count in arange(0,MaxIterations):
		#run the turbine with the guessed pressure ratio
		CycleParameters['PowerTurbine']=RealTurbine(CurrentProperties,CycleInputParameters['PowerTurbine'],PressureRatio=PressureRatioOld)

		#once a temperature is calculated for the power turbine exit, calculate the pressure drop accross the heat exchangers
		CycleParameters['TotalFractionCooler']=Cooler(CycleParameters['PowerTurbine']['ExpandedProperties'],CycleInputParameters['TotalFractionCooler'])
		#then calculate a new power turbine pressure ratio for the next iteration
		PressureRatio=(CycleParameters['PowerTurbine']['StartingProperties']['Pressure']/CycleParameters['MainCompressor']['StartingProperties']['Pressure'])*CycleParameters['TotalFractionCooler']['PressureRatio']		#warning, this is starting/final, instead of final/starting like the rest of the code

		PrintWarning("power turbine Pressure Ratio: "+str(PressureRatio))

		if PressureRatio<0.25:
			#if pressure ratio is far less than 1, don't even try any more because it is probably not a running engine and other functions may error out because fluid properties are out of range
			break

		#check for convergence
		#first see if the residual is really low
		#note, in this search (the turbine), the first guess may be right, whereas, in the heat exchangers, the first guess was never right because the temperature AND pressure were unknown
		PressureRatioResidual=abs(1-PressureRatio/PressureRatioOld)
		PrintWarning("power turbine PressureRatioResidual: "+str(PressureRatioResidual))
		if PressureRatioResidual<ConvergenceCriteria:
			break
		#next, see if even if the residual is not low, is it oscillating around a fixed value?
		if count>0:
			if CheckPercentage(PressureRatio,PressureRatioOldOld,1.0e-13) or (count>1 and CheckPercentage(PressureRatio,PressureRatioOldOldOld,1.0e-13)):
				if PressureRatioResidual<SecondaryConvergenceCriteria:
					PrintWarning("power turbine Presure ratio residuals stopped changing but primary convergence criteria not yet met. secondary convergence criteria met.")
					break
				elif count==(MaxIterations-1):
					print("power turbine pressure did not converge in "+str(MaxIterations)+" iterations. residuals stopped changing but primary and secondary convergence criteria not met.")
					break
		#did not converge
		if count==(MaxIterations-1):
			raise Exception("pressure did not converge in "+str(MaxIterations)+" iterations. residuals did not stop changing")

		#save values for the next iteration to test convergence
		if count>0:
			PressureRatioOldOldOld=PressureRatioOldOld
		PressureRatioOldOld=PressureRatioOld
		PressureRatioOld=PressureRatio

	if PressureRatio<1.00000001:					#require it to be slightly over 1 because if roundoff error allows it to be greater than one it will allow for a non-running engine.
		PrintWarning('pressure drops in heat exchangers too high, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	#get rid of some variables since this same code is used for the power turbine pressure ratio, and it isn't placed in a function
	del(count,PressureRatioResidual,PressureRatio,PressureRatioOld,PressureRatioOldOld,PressureRatioOldOldOld)

	#now that the correct power turbine pressure ratio has been found, assign some values
	CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']+=CycleParameters['PowerTurbine']['SpecificWorkOutput_TotalMassFlow']
	CycleParameters['PowerTurbine']['StartingProperties']['StateNumber']=8
	CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['PowerTurbine']['StartingProperties']['StateNumber'],2*math.pi/4)
	#also add the state point for the power turbine exit since there is no recuperator in the simple cycle assigning this point.
	CycleParameters['PowerTurbine']['ExpandedProperties']['StateNumber']=9
	CurrentProperties=CycleParameters['PowerTurbine']['ExpandedProperties']
	CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['PowerTurbine']['ExpandedProperties']['StateNumber'],-2*math.pi/4,ArrowAngleTP=math.pi)



	#compute the net work
	CycleParameters['SpecificNetWork']=CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']-CycleParameters['TotalSpecificWorkInput_TotalMassFlow']
	if CycleParameters['SpecificNetWork']<0.0:
		PrintWarning('compressors use more power than turbines produce, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	#see if any heat was even added to the system
	if CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']<0.0:
		PrintWarning('no heat was added to the system, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	#compute the back work ratio
	CycleParameters['BackWorkRatio']=CycleParameters['TotalSpecificWorkInput_TotalMassFlow']/CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']

	#compute the cycle efficiency
	CycleParameters['CycleRealEfficiency']=CycleParameters['SpecificNetWork']/CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']

	#calculate the exergy efficiency
	CycleParameters['CycleExergyEfficiency']=CycleParameters['CycleRealEfficiency']/CycleParameters['CycleCarnotEfficiency']


	return CycleParameters
















































def ConstantVolumeCycle(CycleInputParameters):
	CycleParameters=SmartDictionary()

	CycleParameters['Fluid']=FluidProperties.REFPROP.FluidName

	CycleParameters['TotalSpecificWorkInput_TotalMassFlow']=0
	CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']=0
	CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']=0


	CurrentProperties=GetFluidProperties(Pressure=CycleInputParameters['MinPressure'],Temperature=CycleInputParameters['StartingProperties']['Temperature'])

	#second and third heat input on the high pressure side includes both recuporator and heat input
	CycleParameters['SecondPlusThirdHeating']=ConstantVolumeHeater(CurrentProperties,CycleInputParameters['SecondPlusThirdHeating'])
	CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']+=CycleParameters['SecondPlusThirdHeating']['SpecificHeatAdded_TotalMassFlow']
	CycleParameters['SecondPlusThirdHeating']['StartingProperties']['StateNumber']=CycleParameters['ReCompressor']['CompressedProperties']['StateNumber']=1
	CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['SecondPlusThirdHeating']['StartingProperties']['StateNumber'],3*math.pi/4,ArrowAngleTP=math.pi)
	CurrentProperties=CycleParameters['SecondPlusThirdHeating']['HeatedProperties']

	#compute the carnot cycle efficiency for reference, now rather than later in case the cycle can't run because of too high heat exchanger pressure drops
	CycleParameters['CycleCarnotEfficiency']=1-(CycleInputParameters['StartingProperties']['Temperature'])/(CycleParameters['SecondPlusThirdHeating']['HeatedProperties']['Temperature'])


	print 'heater exit pressure after outflow pressure loss: ' + str(CurrentProperties['Pressure']/10.**6.)



	#expander
	#need to iteratively solve for the expander pressure ratio
	#define the convergence parameters
	ConvergenceCriteria=1.0e-6
	SecondaryConvergenceCriteria=3.0e-3
	MaxIterations=20

	#first guess is based on no pressure drop in the heat exchangers
	PressureRatioOld=CurrentProperties['Pressure']/(CycleParameters['SecondPlusThirdHeating']['StartingProperties']['Pressure'])	#warning, this is starting/final, instead of final/starting like the rest of the code
	#preallocate all so they are defined, so they can all be deleted without having to check for existence
	PressureRatioOldOld=PressureRatioOldOldOld=0

	if PressureRatioOld<1.0:
		#don't know that this case will ever occur for this cycle, but still leaving this check in here.
		PrintWarning('pressure drop during heating too high and piston inlet pressure is below the minimum cycle pressure, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	for count in arange(0,MaxIterations):
		#run the piston with the guessed pressure ratio
		CycleParameters['Piston']=RealPiston(CurrentProperties,CycleInputParameters['Piston'],PressureRatio=PressureRatioOld)

		#once a temperature is calculated for the piston exit, calculate the pressure drop accross the heat exchangers
		CycleParameters['TotalFractionCooler']=Cooler(CycleParameters['Piston']['ExpandedProperties'],CycleInputParameters['TotalFractionCooler'])
		#then calculate a new piston pressure ratio for the next iteration
		PressureRatio=(CycleParameters['Piston']['StartingProperties']['Pressure']/CycleParameters['SecondPlusThirdHeating']['StartingProperties']['Pressure'])*CycleParameters['TotalFractionCooler']['PressureRatio']		#warning, this is starting/final, instead of final/starting like the rest of the code

		PrintWarning("piston Pressure Ratio: "+str(PressureRatio))

		if PressureRatio<0.25:
			#if pressure ratio is far less than 1, don't even try any more because it is probably not a running engine and other functions may error out because fluid properties are out of range
			break

		#check for convergence
		#first see if the residual is really low
		#note, in this search (the piston), the first guess may be right, whereas, in the heat exchangers, the first guess was never right because the temperature AND pressure were unknown
		PressureRatioResidual=abs(1-PressureRatio/PressureRatioOld)
		PrintWarning("piston PressureRatioResidual: "+str(PressureRatioResidual))
		if PressureRatioResidual<ConvergenceCriteria:
			break
		#next, see if even if the residual is not low, is it oscillating around a fixed value?
		if count>0:
			if CheckPercentage(PressureRatio,PressureRatioOldOld,1.0e-13) or (count>1 and CheckPercentage(PressureRatio,PressureRatioOldOldOld,1.0e-13)):
				if PressureRatioResidual<SecondaryConvergenceCriteria:
					PrintWarning("piston Presure ratio residuals stopped changing but primary convergence criteria not yet met. secondary convergence criteria met.")
					break
				elif count==(MaxIterations-1):
					print("piston pressure did not converge in "+str(MaxIterations)+" iterations. residuals stopped changing but primary and secondary convergence criteria not met.")
					break
		#did not converge
		if count==(MaxIterations-1):
			raise Exception("pressure did not converge in "+str(MaxIterations)+" iterations. residuals did not stop changing")

		#save values for the next iteration to test convergence
		if count>0:
			PressureRatioOldOldOld=PressureRatioOldOld
		PressureRatioOldOld=PressureRatioOld
		PressureRatioOld=PressureRatio

	if PressureRatio<1.00000001:					#require it to be slightly over 1 because if roundoff error allows it to be greater than one it will allow for a non-running engine.
		PrintWarning('pressure drops in heat exchangers too high, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters


	#now that the correct pressure ratio has been found, assign some values
	CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']+=CycleParameters['Piston']['SpecificWorkOutput_TotalMassFlow']
	CycleParameters['Piston']['StartingProperties']['StateNumber']=3
	CycleParameters['States']=AddState(CycleParameters['States'],CurrentProperties,CycleParameters['Piston']['StartingProperties']['StateNumber'],2*math.pi/4)
	CurrentProperties=CycleParameters['Piston']['ExpandedProperties']

	#take into account the work needed to compress at constant pressure while cooling
	CycleParameters['TotalSpecificWorkInput_TotalMassFlow']+=CycleParameters['TotalFractionCooler']['SpecificWorkCooling_TotalMassFlow']			#note, this lumps the work of the recuperator cooling and the heat rejection cooling


	if CycleInputParameters['NoRecuperator']!=True:			#default to having a recuperator if CycleInputParameters['NoRecuperator'] is not set or set to False, otherwise if set to True, then skip the recuperator and it is a standard Lenoir cycle

		#############################################################################################################################################
		#recuperators
		#############################################################################################################################################
		#high temperature recuperator
		CycleParameters['HTRecuperator']['LowPressure']['StartingProperties']=CycleParameters['Piston']['ExpandedProperties']
		CycleParameters['HTRecuperator']['HighPressure']['StartingProperties']=CycleParameters['SecondPlusThirdHeating']['StartingProperties']
		CycleParameters['HTRecuperator']=GeneralRealRecuperator(CycleParameters['HTRecuperator'],CycleInputParameters['HTRecuperator'])

		CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']-=CycleParameters['HTRecuperator']['SpecificHeatRecuperated_TotalMassFlow']

		CycleParameters['HTRecuperator']['LowPressure']['StartingProperties']['StateNumber']=4
		CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['HTRecuperator']['LowPressure']['StartingProperties'],CycleParameters['HTRecuperator']['LowPressure']['StartingProperties']['StateNumber'],-2*math.pi/4,ArrowAngleTP=math.pi)
		CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties']['StateNumber']=2
		CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties'],CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties']['StateNumber'],3*math.pi/4,ArrowAngleTP=math.pi)

		#make the low pressure outlet of the high temperature recuperator show up on the cycle plot
		CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties']['StateNumber']=5
		CycleParameters['States']=AddState(CycleParameters['States'],CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties'],CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties']['StateNumber'],-1*math.pi/4,ArrowAngleTP=3*math.pi/4)

		CurrentProperties=CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties']


		#############################################################################################################################################
		#end recuperators
		#############################################################################################################################################


	#compute the net work
	CycleParameters['SpecificNetWork']=CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']-CycleParameters['TotalSpecificWorkInput_TotalMassFlow']
	if CycleParameters['SpecificNetWork']<0.0:
		PrintWarning('compressors use more power than produced, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	#see if any heat was even added to the system
	if CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']<0.0:
		PrintWarning('no heat was added to the system, engine cannot run')
		CycleParameters['SpecificNetWork']=0
		CycleParameters['CycleRealEfficiency']=0
		CycleParameters['CycleExergyEfficiency']=0
		return CycleParameters

	#compute the back work ratio
	CycleParameters['BackWorkRatio']=CycleParameters['TotalSpecificWorkInput_TotalMassFlow']/CycleParameters['TotalSpecificWorkOutput_TotalMassFlow']
	print "bwr="+str(CycleParameters['BackWorkRatio'])

	#compute the cycle efficiency
	CycleParameters['CycleRealEfficiency']=CycleParameters['SpecificNetWork']/CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']
#probably also want to calculate the efficiency based on 1-heatrejected/heatadded in order to double check everything

	#calculate the exergy efficiency
	CycleParameters['CycleExergyEfficiency']=CycleParameters['CycleRealEfficiency']/CycleParameters['CycleCarnotEfficiency']


	return CycleParameters




