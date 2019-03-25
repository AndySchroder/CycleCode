###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


#import packages needed by functions defined in this file
from scipy.optimize import root
from FluidProperties.REFPROP import *
from numpy import arange,linspace,diff,gradient,zeros_like,isnan,argmin
from helpers import PrintWarning,SmartDictionary,CheckPercentage,PrintKeysAndValues
from copy import deepcopy		#import because regular python doesn't automatically have deepcopy imported like sage does




#solve the recuperator and also find the unknown pressure drops which are a function of the tempererature drop, assuming the solution converges rather than diverges from the initial guess.
def GeneralRealRecuperator(Recuperator,RecuperatorInputParameters):

	#define the convergence parameters
#	ConvergenceCriteria=1.0e-6
	ConvergenceCriteria=1.0e-5
	SecondaryConvergenceCriteria=3.0e-3
	MaxIterations=20
#may want to add a relaxation factor to be able to get these convergence criteria to be lowered


	#keep in mind that the resolution of the data being interpolated is the real upper limit on the usefulness of this value
	NumberofTemperatures=RecuperatorInputParameters['NumberofTemperatures']


	#first define the initial guess, which is a pressure drop based on no temperature difference at the exit of the high and low pressure sides and no heaters and coolers.
	TestRecuperator=deepcopy(Recuperator)
	#might want to make this smarter if the recuperated values are defined? including the pressures which already may be calculated in the cycle.

	TestRecuperator['HighPressure']['RecuperatedProperties']['Temperature']=Recuperator['LowPressure']['StartingProperties']['Temperature']
	TestRecuperator['LowPressure']['RecuperatedProperties']['Temperature']=Recuperator['HighPressure']['StartingProperties']['Temperature']

	TestRecuperator['HighPressure']['ActualRecuperatedProperties']['Temperature']=Recuperator['LowPressure']['StartingProperties']['Temperature']
	TestRecuperator['LowPressure']['ActualRecuperatedProperties']['Temperature']=Recuperator['HighPressure']['StartingProperties']['Temperature']

	TestRecuperator['LowPressure']['ActualStartingProperties']['Temperature']=Recuperator['LowPressure']['StartingProperties']['Temperature']
	TestRecuperator['HighPressure']['ActualStartingProperties']['Temperature']=Recuperator['HighPressure']['StartingProperties']['Temperature']



	for count in arange(0,MaxIterations):
		#calculate the recuperated pressures from the currently guessed recuperated temperature

		HighPressureDeltaT=TestRecuperator['HighPressure']['RecuperatedProperties']['Temperature']-TestRecuperator['HighPressure']['StartingProperties']['Temperature']
		HighPressureActualDeltaT=TestRecuperator['HighPressure']['ActualRecuperatedProperties']['Temperature']-TestRecuperator['HighPressure']['ActualStartingProperties']['Temperature']
		HighPressureLowerDeltaT=TestRecuperator['HighPressure']['ActualStartingProperties']['Temperature']-TestRecuperator['HighPressure']['StartingProperties']['Temperature']
		#don't care about HighPressureUpperDeltaT because if the others are correct, then it will be, and the properties needed below can be calculated without it.

		LowPressureDeltaT=TestRecuperator['LowPressure']['StartingProperties']['Temperature']-TestRecuperator['LowPressure']['RecuperatedProperties']['Temperature']
		LowPressureActualDeltaT=TestRecuperator['LowPressure']['ActualStartingProperties']['Temperature']-TestRecuperator['LowPressure']['ActualRecuperatedProperties']['Temperature']
		LowPressureUpperDeltaT=TestRecuperator['LowPressure']['StartingProperties']['Temperature']-TestRecuperator['LowPressure']['ActualStartingProperties']['Temperature']
		#don't care about LowPressureLowerDeltaT because if the others are correct, then it will be, and the properties needed below can be calculated without it.

		LowPressureRatio=1-LowPressureDeltaT*RecuperatorInputParameters['DeltaPPerDeltaT']/TestRecuperator['LowPressure']['StartingProperties']['Pressure']
		LowPressureUpperPressureRatio=1-LowPressureUpperDeltaT*RecuperatorInputParameters['DeltaPPerDeltaT']/TestRecuperator['LowPressure']['StartingProperties']['Pressure']
		Recuperator['LowPressure']['ActualStartingProperties']['Pressure']=LowPressureUpperPressureRatio*TestRecuperator['LowPressure']['StartingProperties']['Pressure']
		LowPressureActualPressureRatio=1-LowPressureActualDeltaT*RecuperatorInputParameters['DeltaPPerDeltaT']/Recuperator['LowPressure']['ActualStartingProperties']['Pressure']
		#don't care about LowPressureLowerPressureRatio because if the others are correct, then it will be, and the properties needed below can be calculated without it.

		Recuperator['LowPressure']['RecuperatedProperties']['Pressure']=Recuperator['LowPressure']['StartingProperties']['Pressure']*LowPressureRatio
		Recuperator['LowPressure']['ActualRecuperatedProperties']['Pressure']=Recuperator['LowPressure']['ActualStartingProperties']['Pressure']*LowPressureActualPressureRatio

		if RecuperatorInputParameters['HighPressure']['ConstantVolume'] is True:
			#there is constant volume heat addition and the pressure rises instead of drops in the heat exchanger high pressure side.

			EstimatedActualTemperatures=linspace(
								TestRecuperator['HighPressure']['ActualStartingProperties']['Temperature'],
								TestRecuperator['LowPressure']['ActualStartingProperties']['Temperature'],
								NumberofTemperatures
								)

			#need to calculate the pressure as a function of temperature and the fixed density

			#get the density
			TestRecuperator['HighPressure']['StartingProperties']=GetFluidProperties(
														Temperature		= TestRecuperator['HighPressure']['StartingProperties']['Temperature'],
														Pressure		= TestRecuperator['HighPressure']['StartingProperties']['Pressure'],
														ExtendedProperties	= True
													)

			#calculate pressure using the constant density and the guessed temperature
			TestRecuperator['HighPressure']['ActualStartingProperties']=GetFluidProperties(
														Temperature		= TestRecuperator['HighPressure']['ActualStartingProperties']['Temperature'],
														Density			= TestRecuperator['HighPressure']['StartingProperties']['Density'],
														ExtendedProperties	= True
													)

			#calculate pressure using the constant density and the guessed temperature
			TestRecuperator['HighPressure']['ActualRecuperatedProperties']=GetFluidProperties(
														Temperature		= TestRecuperator['HighPressure']['ActualRecuperatedProperties']['Temperature'],
														Density			= TestRecuperator['HighPressure']['ActualStartingProperties']['Density'],
														ExtendedProperties	= True
													)

			#calcuate pressure using the constant density and the guessed temperature
			TestRecuperator['HighPressure']['RecuperatedProperties']=GetFluidProperties(
														Temperature		= TestRecuperator['HighPressure']['RecuperatedProperties']['Temperature'],
														Density			= TestRecuperator['HighPressure']['ActualRecuperatedProperties']['Density'],
														ExtendedProperties	= True
													)

			#calculate the pressure ratios
			HighPressureRatio=TestRecuperator['HighPressure']['RecuperatedProperties']['Pressure']/TestRecuperator['HighPressure']['StartingProperties']['Pressure']
			HighPressureLowerPressureRatio=TestRecuperator['HighPressure']['ActualStartingProperties']['Pressure']/TestRecuperator['HighPressure']['StartingProperties']['Pressure']
			HighPressureActualPressureRatio=TestRecuperator['HighPressure']['ActualRecuperatedProperties']['Pressure']/TestRecuperator['HighPressure']['ActualStartingProperties']['Pressure']

			#calculate the pressure for each temperature using the constant density
			Recuperator['HighPressure']['ActualPressures']=PressureFromTemperatureDensity(
										EstimatedActualTemperatures,
										TestRecuperator['HighPressure']['ActualStartingProperties']['Density']
										)

			#assign pressure only, and not everything else, because if temperature is defined, then other parts of the logic think it is an explicit value and not an initial guess and those parts aren't setup for the constant volume case.
			Recuperator['HighPressure']['StartingProperties']['Pressure']=TestRecuperator['HighPressure']['StartingProperties']['Pressure']
			Recuperator['HighPressure']['ActualStartingProperties']['Pressure']=TestRecuperator['HighPressure']['ActualStartingProperties']['Pressure']
			Recuperator['HighPressure']['ActualRecuperatedProperties']['Pressure']=TestRecuperator['HighPressure']['ActualRecuperatedProperties']['Pressure']
			Recuperator['HighPressure']['RecuperatedProperties']['Pressure']=TestRecuperator['HighPressure']['RecuperatedProperties']['Pressure']

#still need to consider some pressure loss during the inflow and outflow phases somehow



		else:
			#constant pressure on both the high and low pressure sides

			HighPressureRatio=1-HighPressureDeltaT*RecuperatorInputParameters['DeltaPPerDeltaT']/TestRecuperator['HighPressure']['StartingProperties']['Pressure']
			HighPressureLowerPressureRatio=1-HighPressureLowerDeltaT*RecuperatorInputParameters['DeltaPPerDeltaT']/TestRecuperator['HighPressure']['StartingProperties']['Pressure']

			Recuperator['HighPressure']['ActualStartingProperties']['Pressure']=HighPressureLowerPressureRatio*TestRecuperator['HighPressure']['StartingProperties']['Pressure']
			HighPressureActualPressureRatio=1-HighPressureActualDeltaT*RecuperatorInputParameters['DeltaPPerDeltaT']/Recuperator['HighPressure']['ActualStartingProperties']['Pressure']
			#don't care about HighPressureUpperPressureRatio because if the others are correct, then it will be, and the properties needed below can be calculated without it.

			Recuperator['HighPressure']['RecuperatedProperties']['Pressure']=Recuperator['HighPressure']['StartingProperties']['Pressure']*HighPressureRatio
			Recuperator['HighPressure']['ActualRecuperatedProperties']['Pressure']=Recuperator['HighPressure']['ActualStartingProperties']['Pressure']*HighPressureActualPressureRatio

			#normal heat exchanger with a linear pressure drop that occurs during the heat exchanger
			Recuperator['HighPressure']['ActualPressures']=linspace(
											Recuperator['HighPressure']['ActualStartingProperties']['Pressure'],
											Recuperator['HighPressure']['ActualRecuperatedProperties']['Pressure'],
											NumberofTemperatures
										)



		if count==0:
			#limit the initial guess to .5 because it seems to be way off sometimes and causes the property data to go out of range
			if HighPressureRatio<.5:
				HighPressureRatio=.5
				HighPressureActualPressureRatio=.5	#on the first iteration these are going to be the same so don't need to test this one in the if statement
			if LowPressureRatio<.5:
				LowPressureRatio=.5
				LowPressureActualPressureRatio=.5	#on the first iteration these are going to be the same so don't need to test this one in the if statement

		#print out some indication of the convergence process for debugging
		PrintWarning("Pressure Ratio Iteration: "+str(count))
		PrintWarning("HighPressureRatio: "+str(HighPressureRatio)+", HighPressureLowerPressureRatio: "+str(HighPressureLowerPressureRatio)+", HighPressureActualPressureRatio: "+str(HighPressureActualPressureRatio))
		PrintWarning("LowPressureRatio: "+str(LowPressureRatio)+", LowPressureUpperPressureRatio: "+str(LowPressureUpperPressureRatio)+", LowPressureActualPressureRatio: "+str(LowPressureActualPressureRatio))

		#perform the iteration
		TestRecuperator=RealRecuperatorWithHeatOrCool(Recuperator,RecuperatorInputParameters)

		#check each pressure for convergence

		#first see if the residual is really low
		if count!=0:		#not going to get it on the first iteration and TestRecuperatorOld is also not defined yet
			HighPressureResidual=abs(1-TestRecuperator['HighPressure']['RecuperatedProperties']['Pressure']/TestRecuperatorOld['HighPressure']['RecuperatedProperties']['Pressure'])
			HighPressureActualRecuperatedPressureResidual=abs(1-TestRecuperator['HighPressure']['ActualRecuperatedProperties']['Pressure']/TestRecuperatorOld['HighPressure']['ActualRecuperatedProperties']['Pressure'])
			HighPressureActualStartingPressureResidual=abs(1-TestRecuperator['HighPressure']['ActualStartingProperties']['Pressure']/TestRecuperatorOld['HighPressure']['ActualStartingProperties']['Pressure'])
			PrintWarning("high pressure residual: "+str(HighPressureResidual)+", HighPressureActualRecuperatedPressureResidual: "+str(HighPressureActualRecuperatedPressureResidual)+", HighPressureActualStartingPressureResidual: "+str(HighPressureActualStartingPressureResidual))

			LowPressureResidual=abs(1-TestRecuperator['LowPressure']['RecuperatedProperties']['Pressure']/TestRecuperatorOld['LowPressure']['RecuperatedProperties']['Pressure'])
			LowPressureActualRecuperatedPressureResidual=abs(1-TestRecuperator['LowPressure']['ActualRecuperatedProperties']['Pressure']/TestRecuperatorOld['LowPressure']['ActualRecuperatedProperties']['Pressure'])
			LowPressureActualStartingPressureResidual=abs(1-TestRecuperator['LowPressure']['ActualStartingProperties']['Pressure']/TestRecuperatorOld['LowPressure']['ActualStartingProperties']['Pressure'])
			PrintWarning("low pressure residual: "+str(LowPressureResidual)+", LowPressureActualRecuperatedPressureResidual: "+str(LowPressureActualRecuperatedPressureResidual)+", LowPressureActualStartingPressureResidual: "+str(LowPressureActualStartingPressureResidual))

			if	(
				(HighPressureResidual<ConvergenceCriteria)				and
				(HighPressureActualRecuperatedPressureResidual<ConvergenceCriteria)	and
				(HighPressureActualStartingPressureResidual<ConvergenceCriteria)	and
				(LowPressureResidual<ConvergenceCriteria)				and
				(LowPressureActualRecuperatedPressureResidual<ConvergenceCriteria)	and
				(LowPressureActualStartingPressureResidual<ConvergenceCriteria)
				):
				return TestRecuperator

		#next, see if even if the residual is not low, is it oscillating around a fixed value?
		if count>1:
			if	(
				#need to use CheckPercentage because == wasn't working, apparently due to roundoff errors?
					(
						#are the last and third last iteration the same?
						(CheckPercentage(TestRecuperator['HighPressure']['RecuperatedProperties']['Pressure'],		TestRecuperatorOldOld['HighPressure']['RecuperatedProperties']['Pressure'],		1.0e-13)) and
						(CheckPercentage(TestRecuperator['HighPressure']['ActualRecuperatedProperties']['Pressure'],	TestRecuperatorOldOld['HighPressure']['ActualRecuperatedProperties']['Pressure'],	1.0e-13)) and
						(CheckPercentage(TestRecuperator['HighPressure']['ActualStartingProperties']['Pressure'],	TestRecuperatorOldOld['HighPressure']['ActualStartingProperties']['Pressure'],		1.0e-13)) and
						(CheckPercentage(TestRecuperator['LowPressure']['RecuperatedProperties']['Pressure'],		TestRecuperatorOldOld['LowPressure']['RecuperatedProperties']['Pressure'],		1.0e-13)) and
						(CheckPercentage(TestRecuperator['LowPressure']['ActualRecuperatedProperties']['Pressure'],	TestRecuperatorOldOld['LowPressure']['ActualRecuperatedProperties']['Pressure'],	1.0e-13)) and
						(CheckPercentage(TestRecuperator['LowPressure']['ActualStartingProperties']['Pressure'],	TestRecuperatorOldOld['LowPressure']['ActualStartingProperties']['Pressure'],		1.0e-13))
					)
					or
					(
						#are the last and fourth last iteration the same?
						(count>2)
						and
						(
							(CheckPercentage(TestRecuperator['HighPressure']['RecuperatedProperties']['Pressure'],		TestRecuperatorOldOldOld['HighPressure']['RecuperatedProperties']['Pressure'],		1.0e-13)) and
							(CheckPercentage(TestRecuperator['HighPressure']['ActualRecuperatedProperties']['Pressure'],	TestRecuperatorOldOldOld['HighPressure']['ActualRecuperatedProperties']['Pressure'],	1.0e-13)) and
							(CheckPercentage(TestRecuperator['HighPressure']['ActualStartingProperties']['Pressure'],	TestRecuperatorOldOldOld['HighPressure']['ActualStartingProperties']['Pressure'],		1.0e-13)) and
							(CheckPercentage(TestRecuperator['LowPressure']['RecuperatedProperties']['Pressure'],		TestRecuperatorOldOldOld['LowPressure']['RecuperatedProperties']['Pressure'],		1.0e-13)) and
							(CheckPercentage(TestRecuperator['LowPressure']['ActualRecuperatedProperties']['Pressure'],	TestRecuperatorOldOldOld['LowPressure']['ActualRecuperatedProperties']['Pressure'],	1.0e-13)) and
							(CheckPercentage(TestRecuperator['LowPressure']['ActualStartingProperties']['Pressure'],	TestRecuperatorOldOldOld['LowPressure']['ActualStartingProperties']['Pressure'],		1.0e-13))
						)
					#add another period length here
					)
				):

				if	(
						(HighPressureResidual<SecondaryConvergenceCriteria)				and
						(HighPressureActualRecuperatedPressureResidual<SecondaryConvergenceCriteria)	and
						(HighPressureActualStartingPressureResidual<SecondaryConvergenceCriteria)	and
						(LowPressureResidual<SecondaryConvergenceCriteria)				and
						(LowPressureActualRecuperatedPressureResidual<SecondaryConvergenceCriteria)	and
						(LowPressureActualStartingPressureResidual<SecondaryConvergenceCriteria)
					):
					PrintWarning("residuals stopped changing but primary convergence criteria not yet met. secondary convergence criteria met.")
					return TestRecuperator
				elif count==(MaxIterations-1):
					print("pressure(s) did not converge in "+str(MaxIterations)+" iterations. residuals stopped changing but primary and secondary convergence criteria not met.")
					return TestRecuperator
					#raise Exception("pressure(s) did not converge in "+str(MaxIterations)+" iterations")

		#save values for the next iteration to test convergence
		if count!=0:
			if count!=1:
				TestRecuperatorOldOldOld=TestRecuperatorOldOld
			TestRecuperatorOldOld=TestRecuperatorOld
		TestRecuperatorOld=TestRecuperator

	if count==(MaxIterations-1):
		raise Exception("pressure(s) did not converge in "+str(MaxIterations)+" iterations. residuals did not stop changing")




#make a higher level function that chooses to use this function or the other heat exchanger function and the third boundary condition will kindof be ignored by the other heat exchanger function
#maybe change the function name?
def RealRecuperatorWithHeatOrCool(Recuperator,RecuperatorInputParameters):
	#################################
	#about this function
	#################################
	#this heat exchanger function takes high and low side pressures, and two, three, or four temperatures and calculates the unknown temperatures. at least two of the inputs given must be an inlet
	#temperature. if an input is required which is not an inlet temperature, then a third [and fourth] input temperature, which is an inlet, must be defined. however, this third [and fourth] 
	#inlet temperature can be considered a limit (which may be relevant if the heat exchanger is adding heat or taking away heat from the cycle, and not just transferring heat within the cycle).
	#with more than two input temperatures given, a heater or cooler may be needed to account for the difference between the boundary conditions desired and that of a heat exchanger
	#(because the problem is over constrained with more than two inputs). the heating and cooling needed is calculated. if the third [and fourth] boundary conditions are considered a limit
	#then the heating and cooling can be ignored.
	#in short, this function represents a heat exchanger, and if over constrained, a heat exchanger and heaters and coolers that can accomodate for the overconstraint
	#################################
	#this function accepts dictionaries as inputs
	#################################


	################################
	#ACTUAL values are the conditions at the inlet and outlet of the recuperator.
	#NON ACTUAL values are the inlet and outlet of the heaters and coolers that may be placed before or after the recuperator, in this special combined recuperator+heaters+coolers, which is described above.
	#if ACTUAL and non-ACTUAL values are the same, there is not a heater or cooler at that end of the recuperator.
	################################

	#note, think all of the logic and restrictions here would still be the same even if a more general heat exchanger formulation were utilized.
	#does condensing cycles work?

	########################
	#areas for improvement and notes
	########################
	#want to think about the option of mixing fluid streams that merge (which is for the cases where the outlet boundary streams must be defined) in order to eliminate the
	#heaters and coolers from the cycle. this may be an iterative process with the entire cycle. how does the mixing process entropy production compare to the heating or cooling entropy production?

	#another thing to think about is the possibility of having only heaters or only coolers, but this would be complicated because it would require details of
	#neighboring heat exchangers to be already known, which could be an iterative process. it may be better to not do low temperature heating from an entropy production standpoint.

	#also, just thinking, if there is any low temperature heating, the mass flow rate will probably always be very low on the heat rejection side in order to keep the pinching on
	#the low temperature end such that the heated sides outlet temperature is correct. and a similiar phenomenon for the coolers.
	########################


	TemperaturePercentError=0.001


	#need to check for LowPressureInletTemperature and HighPressureInletTemperature being defined. can't run without these, even if they are just acting as a maximum or minimum (which
	#if both outlets are given, is just needed to figure out where pinching occurs(?)).
	if ('Temperature' not in Recuperator['LowPressure']['StartingProperties']) or ('Temperature' not in Recuperator['HighPressure']['StartingProperties']):
		raise Exception("Recuperator['LowPressure']['StartingProperties']['Temperature'] or Recuperator['HighPressure']['StartingProperties']['Temperature'] not given and required for at least setting limits")


	#first, call the heat exchanger function so can know if need heating or cooling and where in order to maintain boundary conditions imposed.
	RecuperatorTrial=RealRecuperator(
						LowPressureInletTemperature		= Recuperator['LowPressure']['StartingProperties']['Temperature'],
						LowPressureInletPressure		= Recuperator['LowPressure']['StartingProperties']['Pressure'],
						ActualLowPressureOutletPressure		= Recuperator['LowPressure']['ActualRecuperatedProperties']['Pressure'],
						LowPressureMassFraction			= RecuperatorInputParameters['LowPressure']['MassFraction'],
						HighPressureInletTemperature		= Recuperator['HighPressure']['StartingProperties']['Temperature'],
						HighPressureInletPressure		= Recuperator['HighPressure']['StartingProperties']['Pressure'],
						ActualHighPressureOutletPressure	= Recuperator['HighPressure']['ActualRecuperatedProperties']['Pressure'],
						HighPressureMassFraction		= RecuperatorInputParameters['HighPressure']['MassFraction'],
						ActualHighPressures			= Recuperator['HighPressure']['ActualPressures'],
						MinimumDeltaT				= RecuperatorInputParameters['MinimumDeltaT'],
					)

	#now check to see if some heating or cooling needs actually needs to happen to happen and rerun the heat exchanger function if necessary
	#note, cases currently implemented have only heating on the high pressure side and only cooling on the low pressure side. case with 4 constraints may not be this way?
	if ('Temperature' not in Recuperator['LowPressure']['RecuperatedProperties']) and ('Temperature' not in Recuperator['HighPressure']['RecuperatedProperties']):
		#not really anything to do. original outputs obtained above are correct, so the dictionary can be set the the correct variable name
		Recuperator=RecuperatorTrial

	elif ('Temperature' in Recuperator['LowPressure']['RecuperatedProperties']) and ('Temperature' in Recuperator['HighPressure']['RecuperatedProperties']):
		#case where all 4 boundaries are constrained and there can be heating or cooling on the high and low pressure side.
		raise Exception("4 boundary conditions not yet implemented in this function (but should be setup in the RealRecuperator function, so it can be done)")

	elif ('Temperature' in Recuperator['HighPressure']['RecuperatedProperties']):

#don't think the following two cases work with constant volume
		if	(
				(RecuperatorTrial['HighPressure']['RecuperatedProperties']['Temperature']<Recuperator['HighPressure']['RecuperatedProperties']['Temperature']) and
				not CheckPercentage(RecuperatorTrial['HighPressure']['RecuperatedProperties']['Temperature'],Recuperator['HighPressure']['RecuperatedProperties']['Temperature'],TemperaturePercentError)		#CheckPercentage is needed because of small errors
			):

			PrintWarning("need to HEAT up the HIGH pressure side at the EXIT.")
			#set the correct recuperated properties (they are initially the same as the ACTUAL values)
			RecuperatorTrial['HighPressure']['RecuperatedProperties']=GetFluidProperties(
														Temperature	= Recuperator['HighPressure']['RecuperatedProperties']['Temperature'],
														Pressure	= Recuperator['HighPressure']['StartingProperties']['Pressure']
													)

			#once the correct recuperated properties has been set, the dictionary can be set the the correct variable name now
			Recuperator=RecuperatorTrial

			#recalculate the heat added at the high temperature end (defaults to 0)
			Recuperator['HighPressure']['RecuperatedProperties']['HeatAdded_TotalMassFlow']=(
														(
														Recuperator['HighPressure']['RecuperatedProperties']['Enthalpy']
														-Recuperator['HighPressure']['ActualRecuperatedProperties']['Enthalpy']
														)*RecuperatorInputParameters['HighPressure']['MassFraction']
													)

		elif	(
				(RecuperatorTrial['HighPressure']['RecuperatedProperties']['Temperature']>Recuperator['HighPressure']['RecuperatedProperties']['Temperature']) and
				not CheckPercentage(RecuperatorTrial['HighPressure']['RecuperatedProperties']['Temperature'],Recuperator['HighPressure']['RecuperatedProperties']['Temperature'],TemperaturePercentError)		#CheckPercentage is needed because of small errors
			):

			PrintWarning("need to rerun with a third boundary condition set on the heat exchanger")
			#see some additional notes on the accuracy of the heat exchanger function, in the heat exchanger function that may impact this section
			PrintWarning("LOW pressure side will be COOLED at the INLET")

			Recuperator['HighPressure']['ActualRecuperatedProperties']['Temperature']=Recuperator['HighPressure']['RecuperatedProperties']['Temperature']

			Recuperator=RealRecuperator(
							ActualHighPressureOutletTemperature		= Recuperator['HighPressure']['ActualRecuperatedProperties']['Temperature'],
							LowPressureInletTemperature			= Recuperator['LowPressure']['StartingProperties']['Temperature'],
							LowPressureInletPressure			= Recuperator['LowPressure']['StartingProperties']['Pressure'],
							ActualLowPressureInletPressure			= Recuperator['LowPressure']['ActualStartingProperties']['Pressure'],
							ActualLowPressureOutletPressure			= Recuperator['LowPressure']['ActualRecuperatedProperties']['Pressure'],
							LowPressureMassFraction				= RecuperatorInputParameters['LowPressure']['MassFraction'],
							HighPressureInletTemperature			= Recuperator['HighPressure']['StartingProperties']['Temperature'],
							HighPressureInletPressure			= Recuperator['HighPressure']['StartingProperties']['Pressure'],
							ActualHighPressureOutletPressure		= Recuperator['HighPressure']['ActualRecuperatedProperties']['Pressure'],
							HighPressureMassFraction			= RecuperatorInputParameters['HighPressure']['MassFraction'],
							ActualHighPressures				= Recuperator['HighPressure']['ActualPressures'],
							MinimumDeltaT					= RecuperatorInputParameters['MinimumDeltaT'],
						)

		else:	#pretty rare that this case that actually did exist!
			#although high pressure recuperated temperature was defined, it was exactly the same as if no heating or cooling were performed
			#actually, this seems to be possible for some reason. the CheckPercentage function test is needed to correctly trigger it though.
			Recuperator=RecuperatorTrial

	elif ('Temperature' in Recuperator['LowPressure']['RecuperatedProperties']):

#don't think the following two cases work with constant volume
		if	(
				(RecuperatorTrial['LowPressure']['RecuperatedProperties']['Temperature']>Recuperator['LowPressure']['RecuperatedProperties']['Temperature']) and
				not CheckPercentage(RecuperatorTrial['LowPressure']['RecuperatedProperties']['Temperature'],Recuperator['LowPressure']['RecuperatedProperties']['Temperature'],TemperaturePercentError)		#CheckPercentage is needed because of small errors
			):

			PrintWarning("need to COOL LOW pressure side down more at the EXIT")
			#set the correct recuperated properties (they are initially the same as the ACTUAL values)
			RecuperatorTrial['LowPressure']['RecuperatedProperties']=GetFluidProperties(
														Temperature	= Recuperator['LowPressure']['RecuperatedProperties']['Temperature'],
														Pressure	= Recuperator['LowPressure']['StartingProperties']['Pressure']
													)

			#once the correct recuperated properties has been set, the dictionary can be set the the correct variable name now
			Recuperator=RecuperatorTrial
			
			#recalculate the heat rejected at the low temperature end (defaults to 0)
			Recuperator['LowPressure']['RecuperatedProperties']['HeatRejected_TotalMassFlow']=(
														(Recuperator['LowPressure']['ActualRecuperatedProperties']['Enthalpy']
														-Recuperator['LowPressure']['RecuperatedProperties']['Enthalpy']
														)*RecuperatorInputParameters['LowPressure']['MassFraction']
													)

		elif	(
				(RecuperatorTrial['LowPressure']['RecuperatedProperties']['Temperature']<Recuperator['LowPressure']['RecuperatedProperties']['Temperature']) and
				not CheckPercentage(RecuperatorTrial['LowPressure']['RecuperatedProperties']['Temperature'],Recuperator['LowPressure']['RecuperatedProperties']['Temperature'],TemperaturePercentError)		#CheckPercentage is needed because of small errors
			):

			PrintWarning("need to rerun with a third boundary condition set on the heat exchanger")
			PrintWarning("HIGH pressure side will be HEATED at the INLET")

			Recuperator['LowPressure']['ActualRecuperatedProperties']['Temperature']=Recuperator['LowPressure']['RecuperatedProperties']['Temperature']

			Recuperator=RealRecuperator(
							ActualLowPressureOutletTemperature		= Recuperator['LowPressure']['ActualRecuperatedProperties']['Temperature'],
							LowPressureInletTemperature			= Recuperator['LowPressure']['StartingProperties']['Temperature'],
							LowPressureInletPressure			= Recuperator['LowPressure']['StartingProperties']['Pressure'],
							ActualLowPressureOutletPressure			= Recuperator['LowPressure']['ActualRecuperatedProperties']['Pressure'],
							LowPressureMassFraction				= RecuperatorInputParameters['LowPressure']['MassFraction'],
							HighPressureInletTemperature			= Recuperator['HighPressure']['StartingProperties']['Temperature'],
							HighPressureInletPressure			= Recuperator['HighPressure']['StartingProperties']['Pressure'],
							ActualHighPressureInletPressure			= Recuperator['HighPressure']['ActualStartingProperties']['Pressure'],
							ActualHighPressureOutletPressure		= Recuperator['HighPressure']['ActualRecuperatedProperties']['Pressure'],
							HighPressureMassFraction			= RecuperatorInputParameters['HighPressure']['MassFraction'],
							ActualHighPressures				= Recuperator['HighPressure']['ActualPressures'],
							MinimumDeltaT					= RecuperatorInputParameters['MinimumDeltaT'],
						)

		else:	#pretty rare that this case that actually did exist!
			#although low pressure recuperated temperature was defined, it was exactly the same as if no heating or cooling were performed
			#actually, this seems to be possible for some reason. the CheckPercentage function test is needed to correctly trigger it though.
			Recuperator=RecuperatorTrial

	else: #don't think else is even possible given the above inputs, but just check to be safe
		raise Exception("unknown permutation of inputs given")

	#########
	#more notes and todo
	#########

	#how to add the heating and cooling to the ts diagram states numbers? .... probably want to add an extra number for each possible and then make it appear or dissappear?
	#	- do this in the main cycle because need to hard code state numbers
	#make every heat exchanger always have these heaters or coolers and they will just be set to zero if not used?
	#can the existing (meant original???) heater function be used or modified for this?

	#it is possible to just specify the temperatures on one side (needed for the future when calculating the temperatures in the coolant and heater flows)
	#but will need to at least specify a minimum temperature on the side that is
	#receiving the heat (in the case of recuperators, the high pressure side, in the case of coolers or heates, the much lower pressure side)
	#or in the case where the temperatures are known on only the side receiving the heat, the other side will need to know the maximum temperature
	#so actually, the answer is really no. in the case where the max or min has to be defined, it is the same as the case where the outlet temperatures
	#are defined, except you can just ignore the heat added or subtracted by the heater or cooler and take the heater or cooler outlet temperatures as
	#the answer for the single sided cases, and then the RealRecuperator function can just be kept the same

	#???????
	#there will be some cases where the boundary condition can't be met based on the given max or min and in those cases an error will have to be given
	#case where the only the outlets are defined is similiar in that it needs a max and min for both the inlets defined, so it pretty much makes sense to also use this same
	#approach in order to keep generality

	#actually, making the RealRecuperator function accept 3 inputs, but still need to use this function in order to make sure that the case that is sent to the RealRecuperator function
	#is always one in which heat has to be cooled on the low pressure inlet side.
	#doing it the other way wasn't going to work because cps aren't constant so think calculating the temperature for the required enthalpy change on the low pressure side may not have worked
	#????????????
	#############





	#if debugging, uncomment the following line to see the result of the recuperator
#	PrintKeysAndValues("Recuperator",Recuperator)


	return Recuperator





#iterate the RealRecuperatorIteration function until the residual in SpecificHeatRatios is low
#actually though, looks like this function is not needed. based running with several iterations, the solution does not work out if SpecificHeatRatios is updated from the guess
#also, when just one iteration is run and swept through different values, the solution process appears to be stable accross the sweep, so the SpecificHeatRatios apparently should
#be based on the extreme temperatures and not the actual temperatures. still not positive this works for every situation though so leaving this iteration process in here
#just in case. if it is later proven that it is definitely not needed and/or a commit has been made to save this iteration process, the code can be simplified to not include iterations.
def RealRecuperator(
			LowPressureInletTemperature			= None,
			ActualLowPressureOutletTemperature		= None,
			LowPressureInletPressure			= None,
			ActualLowPressureInletPressure			= None,
			ActualLowPressureOutletPressure			= None,
			LowPressureMassFraction				= None,
			HighPressureInletTemperature			= None,
			ActualHighPressureOutletTemperature		= None,
			HighPressureInletPressure			= None,
			ActualHighPressureInletPressure			= None,
			ActualHighPressureOutletPressure		= None,
			HighPressureMassFraction			= None,
			SpecificHeatRatios				= None,
			ActualHighPressures				= None,
			MinimumDeltaT					= 0,
		):	#=None set for all because of "non-default argument follows default argument" error. maybe could have reordered, but didn't want to mess anything up.


	SpecificHeatRatios=None		#for the first iteration, the SpecificHeatRatio is not known
	for iteration in arange(0,1):		#do at most xxx iterations
		PrintWarning("RealRecuperatorIteration: "+str(iteration))
		Recuperator=RealRecuperatorIteration(
							LowPressureInletTemperature,
							ActualLowPressureOutletTemperature,
							LowPressureInletPressure,
							ActualLowPressureInletPressure,
							ActualLowPressureOutletPressure,
							LowPressureMassFraction,
							HighPressureInletTemperature,
							ActualHighPressureOutletTemperature,
							HighPressureInletPressure,
							ActualHighPressureInletPressure,
							ActualHighPressureOutletPressure,
							HighPressureMassFraction,
							SpecificHeatRatios,
							ActualHighPressures,
							MinimumDeltaT,
						)
		if Recuperator['SpecificHeatRatiosMaxResidual']<1.0:		#if the maximum residual is less than 1% then it is good enough
			break
		else:							#if the maximum residual is greater than 1% then pass the latest value of SpecificHeatRatios in as an initial guess
			SpecificHeatRatios=Recuperator['SpecificHeatRatios']
	return Recuperator


def SolveRecuperator(Guess, ActualLowPressureInletTemperature, ActualLowPressureOutletTemperature, ActualLowPressures, ActualHighPressureInletTemperature, ActualHighPressureOutletTemperature, ActualHighPressures, LowPressureMassFraction, HighPressureMassFraction, HighPressureEnergy, MinimumDeltaT=0, StartEnd='LowTemperature', AssignedSide='LowPressure'):
	#note, need to pass the ActualLowPressureOutletTemperature instead of ActualLowPressureOutlet because the optimizer can't work with a dictionary
	#calculate the temperatures within the heat exchanger based on a guessed Low Pressure Outlet Temperature, which is guessed based on the heuristics above that are based on comparing specific heats on the high and low pressure sides.

	PrintWarning("Starting Heat Exchanger Root Finding Iteration")

	#figure out what is the guessed value
	Mode='CheckGuess'	#set the mode, but it may be overridden if no variable to Guess is set
	if ActualLowPressureInletTemperature is 'Guess':
		ActualLowPressureInletTemperature=Guess
	elif ActualLowPressureOutletTemperature is 'Guess':
		ActualLowPressureOutletTemperature=Guess
	elif ActualHighPressureInletTemperature is 'Guess':
		ActualHighPressureInletTemperature=Guess
	else:
		if Guess is not None:
			raise Exception('improper input combination')

		Mode='Calculate'

#note, there is also another variable that is set to 'Solve'. although that value is ignored and the only reason to check for it would be to make sure the inputs are not overconstrained
#actually, maybe could use this variable to eliminate AssignedSide variable, but it will require more logic, so just skipping that for now


	#figure out which end to start solving from
	if StartEnd is 'LowTemperature':
		PrintWarning('start end is low temperature end')

		StartIndex=0
		CountDirection=1

		if AssignedSide is 'LowPressure':
			PrintWarning('assigned side is low pressure side')
			StartTemperature=ActualHighPressureInletTemperature
		elif AssignedSide is 'HighPressure':
			PrintWarning('assigned side is high pressure side')
			StartTemperature=ActualLowPressureOutletTemperature

	elif StartEnd is 'HighTemperature':
		PrintWarning('start end is high temperature end')

		StartIndex=-1
		CountDirection=-1

		if AssignedSide is 'LowPressure':
			PrintWarning('assigned side is low pressure side')
			StartTemperature=ActualHighPressureOutletTemperature
		elif AssignedSide is 'HighPressure':
			PrintWarning('assigned side is high pressure side')
			StartTemperature=ActualLowPressureInletTemperature

	else:
		raise Exception('improper input combination')


	#first ASSIGN temperatures
	NumberofTemperatures=len(ActualLowPressures)				#calculate this so don't need to pass another parameter


	#figure out which side the temperatures are assigned and which side they are calculated
	if AssignedSide is 'LowPressure':
		ActualLowPressureTemperatures=linspace(ActualLowPressureOutletTemperature,ActualLowPressureInletTemperature,NumberofTemperatures)

		#calculate the enthalpies at all of those tempeatures and pressures
		ActualLowPressureEnthalpies=EnthalpyFromTemperaturePressure(ActualLowPressureTemperatures,ActualLowPressures)

		#preallocate the array of unknown values
		ActualHighPressureEnergies=zeros_like(ActualLowPressureEnthalpies)


		#now solve for the high pressure side. can this be made more general so it isn't mostly copied and pasted below???
		ActualHighPressureEnergies[StartIndex]=GetFluidProperties(Temperature=StartTemperature,Pressure=ActualHighPressures[StartIndex])[HighPressureEnergy]		#assign a known value
		#then calculate unknown energy on the high pressure side that correspond to the temperatures assigned on the low pressure side
		for node in arange(0,ActualLowPressureEnthalpies.size)[::CountDirection][:-1]:
			ActualHighPressureEnergies[node+CountDirection]=ActualHighPressureEnergies[node]+(LowPressureMassFraction/HighPressureMassFraction)*(ActualLowPressureEnthalpies[node+CountDirection]-ActualLowPressureEnthalpies[node])


		#now that the energies are known, calcuate the temperatures
		if HighPressureEnergy=='InternalEnergy':
			#there is constant volume heat addition so use internal energy
			ActualHighPressureTemperatures=TemperatureFromInternalEnergyPressure(ActualHighPressureEnergies,ActualHighPressures)
		else:
			#normal heat exchanger with a nearly constant pressure
			ActualHighPressureTemperatures=TemperatureFromEnthalpyPressure(ActualHighPressureEnergies,ActualHighPressures)


	elif AssignedSide is 'HighPressure':
		ActualHighPressureTemperatures=linspace(ActualHighPressureInletTemperature,ActualHighPressureOutletTemperature,NumberofTemperatures)

		#calculate the energies at all of those tempeatures and pressures
		if HighPressureEnergy=='InternalEnergy':
			#there is constant volume heat addition so use internal energy
			ActualHighPressureEnergies=InternalEnergyFromTemperaturePressure(ActualHighPressureTemperatures,ActualHighPressures)
		else:
			#normal heat exchanger with a nearly constant pressure
			ActualHighPressureEnergies=EnthalpyFromTemperaturePressure(ActualHighPressureTemperatures,ActualHighPressures)

		#preallocate the array of unknown values
		ActualLowPressureEnthalpies=zeros_like(ActualHighPressureEnergies)

		#now solve for the low pressure side
		ActualLowPressureEnthalpies[StartIndex]=GetFluidProperties(Temperature=StartTemperature,Pressure=ActualLowPressures[StartIndex])[HighPressureEnergy]		#assign a known value
		#then calculate unknown energy on the low pressure side that correspond to the temperatures assigned on the high pressure side
		for node in arange(0,ActualHighPressureEnergies.size)[::CountDirection][:-1]:
			ActualLowPressureEnthalpies[node+CountDirection]=ActualLowPressureEnthalpies[node]+(HighPressureMassFraction/LowPressureMassFraction)*(ActualHighPressureEnergies[node+CountDirection]-ActualHighPressureEnergies[node])

		#now that the enthalpies are known, calcuate the temperatures
		ActualLowPressureTemperatures=TemperatureFromEnthalpyPressure(ActualLowPressureEnthalpies,ActualLowPressures)

	else:
		raise Exception('improper input combination')



	#calculate the delta t everywhere now that the temperatures are known
	ActualDeltaTs=ActualLowPressureTemperatures-ActualHighPressureTemperatures

	if Mode=='CheckGuess':
		PrintWarning(ActualDeltaTs.min())
		return ActualDeltaTs.min()-MinimumDeltaT
	elif Mode=='Calculate':

		#determine the SpecificHeats and outlet properties for the high pressure side now that the temperatures are known on the high pressure side
		if HighPressureEnergy=='InternalEnergy':
			#there is constant volume heat addition and want to return cv instead of cp for the high pressure side
			ActualHighPressureSpecificHeats=cvFromTemperaturePressure(ActualHighPressureTemperatures,ActualHighPressures)

			#calculate all values at the inlet and outlet
			ActualHighPressureInlet=GetFluidProperties(ActualHighPressures[0],InternalEnergy=ActualHighPressureEnergies[0])
			ActualHighPressureOutlet=GetFluidProperties(ActualHighPressures[-1],InternalEnergy=ActualHighPressureEnergies[-1])
		else:
			#normal heat exchanger with a nearly constant pressure
			ActualHighPressureSpecificHeats=cpFromTemperaturePressure(ActualHighPressureTemperatures,ActualHighPressures)

			#calculate all values at the inlet and outlet
			ActualHighPressureInlet=GetFluidProperties(ActualHighPressures[0],Enthalpy=ActualHighPressureEnergies[0])
			ActualHighPressureOutlet=GetFluidProperties(ActualHighPressures[-1],Enthalpy=ActualHighPressureEnergies[-1])

		#calculate the SpecificHeats on the low pressure side based on the assigned temperatures on the low pressure side. (could have been done above, but doing here to consolidate SpecificHeat calculations)
		ActualLowPressureSpecificHeats=cpFromTemperaturePressure(ActualLowPressureTemperatures,ActualLowPressures)		#note, at the beginning of this function, just one temperature was used for both the high and low pressure side, now a specific temperature is used

		#calculate all values at the low pressure inlet and outlet
		ActualLowPressureInlet=GetFluidProperties(ActualLowPressures[-1],Enthalpy=ActualLowPressureEnthalpies[-1])
		ActualLowPressureOutlet=GetFluidProperties(ActualLowPressures[0],Enthalpy=ActualLowPressureEnthalpies[0])

		ActualSpecificHeatRatios=(ActualHighPressureSpecificHeats*HighPressureMassFraction)/(LowPressureMassFraction*ActualLowPressureSpecificHeats)		#need to take the ratio of the specific heats multiplied by their mass fractions because that determines the relative specific heat ratio when there are different mass flow rates

		#do some checks

		PrintWarning('minimum DeltaT: '+str(ActualDeltaTs.min()))
		if isnan(ActualDeltaTs.min()):
			print ""
			PrintKeysAndValues("Recuperator",Recuperator)
			print ""
			raise Exception("there is some problem with the heat exchanger logic")

		#double check the additional knowns are the same
#why would this be an issue other than interpolation error stackup???????
		ActualHighPressureEnergyError=(ActualHighPressureEnergies[-1]-ActualHighPressureOutlet[HighPressureEnergy])/ActualHighPressureOutlet[HighPressureEnergy]
		PrintWarning('high pressure recuperated energy error='+str(ActualHighPressureEnergyError))
		if isnan(ActualHighPressureEnergyError):		#not sure why this isn't checked in more detail other than other checks will probably also fail if this fails
			print ""
			PrintKeysAndValues("Recuperator",Recuperator)
			print ""
			raise Exception("there is some problem with the heat exchanger logic")

		#return the current solution
		return ActualLowPressureTemperatures,ActualHighPressureTemperatures,ActualDeltaTs,ActualHighPressureSpecificHeats,ActualLowPressureSpecificHeats,ActualSpecificHeatRatios,ActualLowPressureInlet,ActualLowPressureOutlet,ActualHighPressureInlet,ActualHighPressureOutlet
	else:
		raise Exception("don't understand Mode")












def RealRecuperatorIteration(
				LowPressureInletTemperature			= None,
				ActualLowPressureOutletTemperature		= None,
				LowPressureInletPressure			= None,
				ActualLowPressureInletPressure			= None,		#actual value has to be set because it can't be calculated
				ActualLowPressureOutletPressure			= None,
				LowPressureMassFraction				= None,
				HighPressureInletTemperature			= None,
				ActualHighPressureOutletTemperature		= None,
				HighPressureInletPressure			= None,
				ActualHighPressureInletPressure			= None,		#actual value has to be set because it can't be calculated
				ActualHighPressureOutletPressure		= None,
				HighPressureMassFraction			= None,
				SpecificHeatRatios				= None,
				ActualHighPressures				= None,
				MinimumDeltaT					= 0,
			):	#=None set for all because of "non-default argument follows default argument" error. maybe could have reordered, but didn't want to mess anything up.




	#################################
	#about this function
	#################################
	#this function takes heat exchanger high and low side pressures, and inlet temperatures, and calculates the outlet temperatures.
	#if outlet temperatures are defined, then the inlet temperatures (on the same pressure as the outlet temperature is defined) are taken to be limits (and
	#not boundaries, so this function does not allow for overconstraining the boundaries) and new inlet temperature(s) is(are) computed (the ACTUAL values)
	#(and then the amount of heating or cooling required at the inlets is calculated between the limit and the ACTUAL value????)
	#note, before calling with outlet temperatures defined, need to verify that the outlet temperatures given will work within the inlet temperature limits given
	#note, the energy equation is solved only (never allowing an entropy reduction of course), and perfect convective and conductive heat transfer is assumed
	#within the heat exchanger.
	#################################
	#this function accepts values as inputs, but returns a dictionary. it doesn't accept a dictionary as an input because many times a custom dictionary would
	#have to be constructed anyway, and because all the expressions below would be very long/confusing to read with a dictionary that would probably want to
	#deconstruct the dictionary immediately in this function anyway
	#################################


	#need an option for different fluids on both sides so can use for heaters and coolers when modeling those too
	#change terminology so that high pressure side just means the side receiving the heat and the low pressure side just means the side rejecting the heat.
	#this is needed because coolers will pretty much always be lower pressure.
	
	#keep in mind that the resolution of the data being interpolated is the real upper limit on the usefulness of this value
	NumberofTemperatures=len(ActualHighPressures)

	#define a tolerance for errors in the enthalies interpolated
	EnergyTolerance=.15	#%


	#set these variable so they can be used for more consistent comparisons. or are the comparisons consitent enough already??
	LowPressureOutletTemperature=ActualLowPressureOutletTemperature
	HighPressureOutletTemperature=ActualHighPressureOutletTemperature

	#in case this function is not called by GeneralRealRecuperator, also
	#check for LowPressureInletTemperature and HighPressureInletTemperature being defined. can't run without these, even if they are just acting as a maximum or minimum.
	if (LowPressureInletTemperature is None) or (HighPressureInletTemperature is None):
		raise Exception("LowPressureInletTemperature or HighPressureInletTemperature not given and required for at least setting limits")

	#make sure inlet temperatures given make sense
	elif LowPressureInletTemperature<HighPressureInletTemperature:
		raise Exception("LowPressureInletTemperature<HighPressureInletTemperature")
	elif (LowPressureInletTemperature<HighPressureOutletTemperature) and (HighPressureOutletTemperature is not None):
		raise Exception("LowPressureInletTemperature<HighPressureOutletTemperature")
	elif (HighPressureInletTemperature>LowPressureOutletTemperature) and (LowPressureOutletTemperature is not None):
		raise Exception("HighPressureInletTemperature>LowPressureOutletTemperature")

	#check for Actual Pressures
	if ((ActualLowPressureInletPressure == {}) or (ActualLowPressureInletPressure is None)):	#don't know why "is" doesn't work instead of "==" ?
		ActualLowPressureInletPressure=LowPressureInletPressure
		if (HighPressureOutletTemperature is not None):
			PrintWarning("HighPressureOutletTemperature is defined but ActualLowPressureInletPressure is not defined, so setting ActualLowPressureInletPressure=LowPressureInletPressure as an approximation")
		#if HighPressureOutletTemperature is None, don't want to do a warning because setting ActualLowPressureInletPressure=LowPressureInletPressure is just done so ActualPressures can be defined more neatly below
	elif (LowPressureOutletTemperature is not None):
		raise Exception("ActualLowPressureInletPressure defined and LowPressureOutletTemperature defined. there may be a problem with the input combination used")

	if ((ActualHighPressureInletPressure == {}) or (ActualHighPressureInletPressure is None)):	#don't know why "is" doesn't work instead of "==" ?
		ActualHighPressureInletPressure=HighPressureInletPressure
		if (LowPressureOutletTemperature is not None):
			PrintWarning("LowPressureOutletTemperature is defined but ActualHighPressureInletPressure is not defined, so setting ActualHighPressureInletPressure=HighPressureInletPressure as an approximation")
		#if LowPressureOutletTemperature is None, don't want to do a warning because setting ActualHighPressureInletPressure=HighPressureInletPressure is just done so ActualPressures can be defined more neatly below
	elif (HighPressureOutletTemperature is not None):
		raise Exception("ActualHighPressureInletPressure defined and HighPressureOutletTemperature defined. there may be a problem with the input combination used")

	#define the dictionary that is populated by this function
	Recuperator=SmartDictionary()

	LowPressureInlet=GetFluidProperties(LowPressureInletPressure,LowPressureInletTemperature)
	LowPressures=linspace(ActualLowPressureOutletPressure,LowPressureInletPressure,NumberofTemperatures)				#note, LowPressureOutlet=ActualLowPressureOutlet below, so using ActualLowPressureOutletPressure is correct
	ActualLowPressures=linspace(ActualLowPressureOutletPressure,ActualLowPressureInletPressure,NumberofTemperatures)
	LowPressureOutletMin=GetFluidProperties(ActualLowPressureOutletPressure,HighPressureInletTemperature)				#same note as above

	Temperatures=linspace(LowPressureOutletMin['Temperature'],LowPressureInlet['Temperature'],NumberofTemperatures)

	if ActualHighPressureOutletPressure>HighPressureInletPressure:
		#there is constant volume heat addition and the pressure rises instead of drops in the heat exchanger high pressure side.
#if this happens then there is a pressure drop that should be considered before and after the heat exchange (although it actually is not modeled yet).
#this issue is also mentioned in the constant volume heater function

		HighPressureEnergy='InternalEnergy'

		#need to calculate the pressure as a function of temperature and the fixed density
		HighPressures=PressureFromTemperatureDensity(Temperatures,GetFluidProperties(Temperature=HighPressureInletTemperature,Pressure=HighPressureInletPressure,ExtendedProperties=True)['Density'])						#every property for ActualHighPressureOutlet isn't know yet because temperature may not be known, but the density is and is the same as the inlet, so just fetch it from the inlet state.

		#set in the result so can reference elsewhere in CycleParameters in results processing to distinquish from constant pressure cases.
		Recuperator['HighPressure']['ConstantVolume']=True

	else:
		#normal heat exchanger with a pressure drop that occurs during the heat exchange

		HighPressureEnergy='Enthalpy'

		HighPressures=linspace(HighPressureInletPressure,ActualHighPressureOutletPressure,NumberofTemperatures)				#note, HighPressureOutlet=ActualHighPressureOutlet below, so using ActualHighPressureOutletPressure is correct

		#set in the result so can reference elsewhere in CycleParameters in results processing to distinquish from constant volume cases.
		Recuperator['HighPressure']['ConstantVolume']=False



	HighPressureInlet=GetFluidProperties(HighPressureInletPressure,HighPressureInletTemperature)
	HighPressureOutletMax=GetFluidProperties(ActualHighPressureOutletPressure,LowPressureInletTemperature)					#same note as above



	#if the first iteration then make a guess for the specific heat ratios
	#note, this logic proves to not do anything positive at present but just leaving it in here in case it is useful in the future for some reason
	#it was assumed that the proper SpecificHeatRatio was based on the actual SpecificHeatRatio of the control volume (different temperatures) and not the SpecificHeatRatio at
	#the same temperature on the high and low pressure sides. there still could be some truth to this (which could be why the trial and error fallback is needed)
	#and what was done below could have not been implemented all the way correctly. the cases the logic does work using common temperatures could have something to do
	#with the fact that the for a lot of the cases when SpecificHeatRatio is near 1 the temperatures are a lot of times similiar or equal
	#this issue is most significant for large delta T at the outlet/inlet?
	#another case of concern is where the pinching occurs near the exit, but not at the exit.
	if SpecificHeatRatios is None:
		#print "guessing SpecificHeatRatios"

		if HighPressureEnergy=='InternalEnergy':
			#there is constant volume heat addition and want to return cv instead of cp for the high pressure side
			HighPressureSpecificHeats=cvFromTemperaturePressure(Temperatures,HighPressures)
		else:
			#normal heat exchanger with a nearly constant pressure
			HighPressureSpecificHeats=cpFromTemperaturePressure(Temperatures,HighPressures)

		LowPressureSpecificHeats=cpFromTemperaturePressure(Temperatures,LowPressures)

		SpecificHeatRatios=(HighPressureSpecificHeats*HighPressureMassFraction)/(LowPressureMassFraction*LowPressureSpecificHeats)		#need to take the ratio of the specific heats multiplied by their mass fractions because that determines the relative specific heat ratio when there are different mass flow rates
		SpecificHeatRatiosOriginal=SpecificHeatRatios.copy()


	OneCrossings=abs(diff(1*(SpecificHeatRatios>1)))	#locate where the specific heat ratio crosses 1
	NumberOfOneCrossings=sum(OneCrossings)	#count the number of times the specific heat ratio crosses 1

	#if more than one specific heat ratio crossing of 1, find the index of the specific heat ratio crossing closest 1 at the highest temperature
	#or lowest temperature, based on a guess of which one it should be based on inspecting the concavity of SpecificHeatRatios
	#note, originally had index=argmin(abs(SpecificHeatRatios-1)) but it assumes there is only one ones crossing
	if NumberOfOneCrossings>0:
		HighestTemperatureOneCrossingIndex=OneCrossings.nonzero()[0].max()
		LowestTemperatureOneCrossingIndex=OneCrossings.nonzero()[0].min()
		SpecificHeatRatiosDeviationFromOne=abs(SpecificHeatRatios-1)

		Previousindex=None

		SpecificHeatRatiosSecondDerivative=gradient(gradient(SpecificHeatRatios))
		if SpecificHeatRatiosSecondDerivative.mean()>=0:		#can't use all(SpecificHeatRatiosSecondDerivative>=0) because too noisy data so not all concavities come out right, and there might be a small region with a change in concavity
			#concave up
			index=HighestTemperatureOneCrossingIndex+SpecificHeatRatiosDeviationFromOne[[HighestTemperatureOneCrossingIndex,HighestTemperatureOneCrossingIndex+1]].argmin()
		elif SpecificHeatRatiosSecondDerivative.mean()<=0:		#can't use all(SpecificHeatRatiosSecondDerivative<=0) because too noisy data so not all concavities come out right, and there might be a small region with a change in concavity
			#concave down
			index=LowestTemperatureOneCrossingIndex+SpecificHeatRatiosDeviationFromOne[[LowestTemperatureOneCrossingIndex,LowestTemperatureOneCrossingIndex+1]].argmin()
		else:
			raise Exception("don't don't understand the curvature of SpecificHeatRatios")
	else:
		Previousindex=0	#don't know that this is actually needed, but added it in here. the case where it did cause a problem ended up being another problem that caused the code to get somewhere it shouldn't have even been.
		index=0		#there are no ones crossings so set to 0 so that there is some value

	###############################################################################################################################
	#first go through all the assumed conditions and behaviour. if the condition is understood indicate how calculate unknowns (which will be done later)
	#note, this is done instead of a general (and slower?) discretization and solving the nonlinear function technique that could have been used.
	#there could have been a lot of stability issues with the general nonlinear function solving technique due to the property variations and accuracy of the property data
	#and not sure if could have done all the combinations of boundary conditions that way?
	CalculationType=None
	if NumberOfOneCrossings>1:
		PrintWarning("warning: SpecificHeatRatio crosses one more than once")
		pass

	#check to see if the ratio of specific heats changes within the heat exchanger from less than 1 to greater than 1 or vice versa
	if index!=0 and index!=SpecificHeatRatios.shape[0] and SpecificHeatRatios.max()>1 and SpecificHeatRatios.min()<1:	#not sure if there are any cases where triggers the wrong case and causes it to go into trial and error mode
		if gradient(SpecificHeatRatios).max()>0 and gradient(SpecificHeatRatios).min()<0:	#skipping the deltaT part of this condition because just checking sign so it doesn't matter
			#can't just search for a zero because the discretization may miss it, so check if it crosses zero
			PrintWarning("note, SpecificHeatRatios slope changes sign.")
			pass

		if gradient(SpecificHeatRatios).mean()<0:
			#skipping the deltaT part of this condition because just checking sign so it doesn't matter. note, used to have gradient(SpecificHeatRatios).max()<0,
			#but that didn't seem to work for a lot of cases (error in the interpolation(?) and causing a(n artificial) or real local minimum, for example)
			#case where all SpecificHeatRatios are always decreasing
			PrintWarning("SpecificHeat ratio decreasing")

			if SpecificHeatRatios.mean()>1:
				#assuming same as SpecificHeatRatios always greater than 1 case.
				#if not, a trial and error fallback method will result
				CalculationType='LowTemperaturePinch'
			elif SpecificHeatRatios.mean()<1:
				if SpecificHeatRatiosSecondDerivative.mean()>=0 and index>argmin(SpecificHeatRatios):		#see above concavity check for why all(SpecificHeatRatiosSecondDerivative>=0) is not used
					#if the average slope is decreasing and the SpecificHeatRatios average is less than 1 and the concavity is up and the chosen index is greater than the minimum SpecificHeatRatio
					CalculationType='MiddlePinch'
				else:
					#assuming same as SpecificHeatRatios always less than 1 case
					#if not, a trial and error fallback method will result
					CalculationType='HighTemperaturePinch'
			else:
				#very rare case (partially due to computer precision) where SpecificHeatRatios.mean() is exactly 1, is always decreasing, and crosses 1
				#pinching occurs at both ends, which is a kindof neat phenomenon
				CalculationType='HighLowTemperaturePinch'

		elif gradient(SpecificHeatRatios).mean()>0:
			#skipping the deltaT part of this condition because just checking sign so it doesn't matter. note, used to have gradient(SpecificHeatRatios).min()>0,
			#but that didn't seem to work for a lot of cases (error in the interpolation(?) and causing a(n artificial) or real local maximum, for example)
			#maybe elif is redundant compared to else?
			#case where all SpecificHeatRatios are always increasing
			#pinch is in the middle
			PrintWarning("SpecificHeat ratio increasing")

			CalculationType='MiddlePinch'


	elif (SpecificHeatRatios.max()>1 and SpecificHeatRatios.min()>1) or (SpecificHeatRatios.max()>1 and SpecificHeatRatios.max()!=SpecificHeatRatios[index] and (index==0 or index==SpecificHeatRatios.shape[0])):
		#SpecificHeat ratio is [almost] always greater than 1. one control volume needed. pinch occurs at high pressure inlet/low pressure outlet (low temperature)
		CalculationType='LowTemperaturePinch'
	elif (SpecificHeatRatios.max()<1 and SpecificHeatRatios.min()<1) or (SpecificHeatRatios.min()<1 and SpecificHeatRatios.min()!=SpecificHeatRatios[index] and (index==0 or index==SpecificHeatRatios.shape[0])):
		#SpecificHeat ratio is [almost] always less than 1. one control volume needed. pinch occurs at low pressure inlet/high pressure outlet (high temperature)
		CalculationType='HighTemperaturePinch'
	elif NumberOfOneCrossings==0:
		#there are no specific heat ratio crossings of 1, specific heat ratios are never always less than 1 or greater than 1.
		#this is the case of constant and equal specific heats where the heat exchanger is pinched everywhere
		CalculationType='HighLowTemperaturePinch'
	else:
		#pinch occured between an end point and 1 point away from the end???
		raise Exception("don't know why all other cases didn't match. need a finer resolution to resolve?")
	###############################################################################################################################

	###############################################################################################################################
	#now do calculation for cases
	#separated here because multiple conditions could require the same calculation.
	#cases where only one condition required a certain calculation were still placed here just to keep the calculations consolidated
	#may have been able to avoid this step but wanted to keep things separate so different cases are more clearly differentiated, partially for documentation and understanding purposes
	#but also in case it turns out they actually aren't common the rework is easier.

	#do up to 4 trials in case all the logic above didn't actually identify the correct calculation method
	PreviousCalculationType=None
	for trial in arange(0,4):
		PrintWarning('CalculationType:'+CalculationType)
		#set some values, but if they are overridden, then that is okay
		ActualLowPressureInlet=LowPressureInlet
		ActualHighPressureInlet=HighPressureInlet

		if CalculationType is 'LowTemperaturePinch':
			PrintWarning("SpecificHeat greater than 1")

			#note, cooling at the outlets is handled by the higher level function, so don't care if the outlet is defined here and there isn't any logic to take care of it.

			if ActualLowPressureOutletTemperature is not None:
				#high pressure side is heated at the inlet
				#note, if ActualHighPressureOutletTemperature is not None (below), then there will be both heating and cooling and the configuration will be very inefficient. dont think the calling function will ever constrain both outlets at once though.
				#change the ActualHighPressureInlet so that some heating happens
				ActualHighPressureInlet=GetFluidProperties(ActualHighPressureInletPressure,ActualLowPressureOutletTemperature-MinimumDeltaT)

			#if pinching occurs at the low temperature then the low pressure outlet temperature is the same as the high pressure inlet temperature plus the MinimumDeltaT
			#note, not just using ActualLowPressureOutletTemperature here because it may be set to None and don't want to make an else statement above that sets it because some logic below will be messed up.
			ActualLowPressureOutlet=GetFluidProperties(ActualLowPressureOutletPressure,ActualHighPressureInlet['Temperature']+MinimumDeltaT)

			#check to see if an alternate boundary condition is specified
			if ActualHighPressureOutletTemperature is not None:	#ActualLowPressureInlet is unknown. there may be some cooling at the low pressure inlet
				ActualHighPressureOutlet=GetFluidProperties(ActualHighPressureOutletPressure,ActualHighPressureOutletTemperature)	#get rest of the properties if the temperature is known

				#check the quality of the interpolated enthalpies or internal energies
				if (ActualHighPressureOutlet[HighPressureEnergy]<ActualHighPressureInlet[HighPressureEnergy]):
					if CheckPercentage(ActualHighPressureOutlet[HighPressureEnergy],ActualHighPressureInlet[HighPressureEnergy],EnergyTolerance):
						#close enough, so just set them to be equal because there was probably supposed to be 0 enthalpy or internal energy based on the inputs
						ActualHighPressureOutlet[HighPressureEnergy]=ActualHighPressureInlet[HighPressureEnergy]
						PrintWarning("warning, ActualHighPressureOutlet[HighPressureEnergy]<ActualHighPressureInlet[HighPressureEnergy] but within "+str(EnergyTolerance)+"%, setting ActualHighPressureOutlet[HighPressureEnergy]=ActualHighPressureInlet[HighPressureEnergy]")
					else:
						raise Exception('too much error in interopolated enthalpies or internal energies')

				#note, constant volume cooling on the low pressure side is not implemented
				ActualLowPressureInletEnthalpy=(ActualHighPressureOutlet[HighPressureEnergy]-ActualHighPressureInlet[HighPressureEnergy])*(HighPressureMassFraction/LowPressureMassFraction)+ActualLowPressureOutlet['Enthalpy']	#calculate the other enthalpy
				ActualLowPressureInlet=GetFluidProperties(ActualLowPressureInletPressure,Enthalpy=ActualLowPressureInletEnthalpy)													#get rest of the properties once the enthalpy is known
			else:	#HighPressureOutlet is unknown. there is no cooling at the low pressure inlet.

				#check the quality of the interpolated enthalpies
				if (ActualLowPressureInlet['Enthalpy']<ActualLowPressureOutlet['Enthalpy']):		#note LowPressureOutlet=ActualLowPressureOutlet, but LowPressureOutlet has not yet been defined.
					if CheckPercentage(ActualLowPressureInlet['Enthalpy'],ActualLowPressureOutlet['Enthalpy'],EnergyTolerance):
						#close enough, so just set them to be equal because there was probably supposed to be 0 enthalpy based on the inputs
						ActualLowPressureOutlet['Enthalpy']=ActualLowPressureInlet['Enthalpy']
						PrintWarning("warning, ActualLowPressureInlet['Enthalpy']<ActualLowPressureOutlet['Enthalpy'] but within "+str(EnergyTolerance)+"%, setting ActualLowPressureOutlet['Enthalpy']=ActualLowPressureInlet['Enthalpy']")
					else:
						raise Exception('too much error in interopolated enthalpies')

				ActualHighPressureOutletEnergy=(LowPressureMassFraction/HighPressureMassFraction)*(ActualLowPressureInlet['Enthalpy']-ActualLowPressureOutlet['Enthalpy'])+ActualHighPressureInlet[HighPressureEnergy]	#calculate the other enthalpy or internal energy

				if HighPressureEnergy=='InternalEnergy':
					#there is constant volume heat addition so use internal energy
					ActualHighPressureOutlet=GetFluidProperties(ActualHighPressureOutletPressure,InternalEnergy=ActualHighPressureOutletEnergy)					#get the rest of the properties once internal energy is known
				else:
					#normal heat exchanger with a nearly constant pressure
					ActualHighPressureOutlet=GetFluidProperties(ActualHighPressureOutletPressure,Enthalpy=ActualHighPressureOutletEnergy,SaturateEnthalpy=True)			#get the rest of the properties once enthalpy is known


		elif CalculationType is 'HighTemperaturePinch':
			PrintWarning("SpecificHeat less than 1")

			#note, cooling at the outlets is handled by the higher level function, so don't care if the outlet is defined here and there isn't any logic to take care of it.

			if ActualHighPressureOutletTemperature is not None:
				#low pressure side is cooled at the inlet
				#note, if ActualLowPressureOutletTemperature is not None (below), then there will be both heating and cooling and the configuration will be very inefficient. dont think the calling function will ever constrain both outlets at once though.
				#change the ActualLowPressureInlet so that some cooling happens
				ActualLowPressureInlet=GetFluidProperties(ActualLowPressureInletPressure,ActualHighPressureOutletTemperature+MinimumDeltaT)

			#if the pinching is at the high temperature then the high pressure outlet temperature is the same as the low pressure inlet temperature minus the MinimumDeltaT
			#note, not just using ActualHighPressureOutletTemperature here because it may be set to None and don't want to make an else statement above that sets it because some logic below will be messed up.
			ActualHighPressureOutlet=GetFluidProperties(ActualHighPressureOutletPressure,ActualLowPressureInlet['Temperature']-MinimumDeltaT)

			#check to see if an alternate boundary condition is specified
			if ActualLowPressureOutletTemperature is not None:	#ActualHighPressureInlet is unknown. there may be some heating at the high pressure inlet.

				#note, constant volume cooling on the low pressure side is not implemented
				ActualLowPressureOutlet=GetFluidProperties(ActualLowPressureOutletPressure,ActualLowPressureOutletTemperature)	#get rest of the properties if the temperature is known

				#check the quality of the interpolated enthalpies
				if (ActualLowPressureInlet['Enthalpy']<ActualLowPressureOutlet['Enthalpy']):		#note LowPressureOutlet=ActualLowPressureOutlet, but LowPressureOutlet has not yet been defined.
					if CheckPercentage(ActualLowPressureInlet['Enthalpy'],ActualLowPressureOutlet['Enthalpy'],EnergyTolerance):
						#close enough, so just set them to be equal because there was probably supposed to be 0 enthalpy based on the inputs
						ActualLowPressureOutlet['Enthalpy']=ActualLowPressureInlet['Enthalpy']
						PrintWarning("warning, ActualLowPressureInlet['Enthalpy']<ActualLowPressureOutlet['Enthalpy'] but within "+str(EnergyTolerance)+"%, setting ActualLowPressureOutlet['Enthalpy']=ActualLowPressureInlet['Enthalpy']")
					else:
						raise Exception('too much error in interopolated enthalpies')

				ActualHighPressureInletEnergy=ActualHighPressureOutlet[HighPressureEnergy]-(ActualLowPressureInlet['Enthalpy']-ActualLowPressureOutlet['Enthalpy'])*(LowPressureMassFraction/HighPressureMassFraction)	#calculate the other enthalpy or internal energy

				if HighPressureEnergy=='InternalEnergy':
					#there is constant volume heat addition so use internal energy
					ActualHighPressureInlet=GetFluidProperties(ActualHighPressureInletPressure,InternalEnergy=ActualHighPressureInletEnergy)		#get rest of the properties once the internal energy is known
				else:
					#normal heat exchanger with a nearly constant pressure
					ActualHighPressureInlet=GetFluidProperties(ActualHighPressureInletPressure,Enthalpy=ActualHighPressureInletEnergy)			#get rest of the properties once the enthalpy is known

			else:	#ActualLowPressureOutlet is unknown. there is no heating at the high pressure inlet.

				#check the quality of the interpolated enthalpies or internal energies
				if (ActualHighPressureOutlet[HighPressureEnergy]<ActualHighPressureInlet[HighPressureEnergy]):
					if CheckPercentage(ActualHighPressureOutlet[HighPressureEnergy],ActualHighPressureInlet[HighPressureEnergy],EnergyTolerance):
						#close enough, so just set them to be equal because there was probably supposed to be 0 enthalpy or internal energy based on the inputs
						ActualHighPressureOutlet[HighPressureEnergy]=ActualHighPressureInlet[HighPressureEnergy]
						PrintWarning("warning, ActualHighPressureOutlet[HighPressureEnergy]<ActualHighPressureInlet[HighPressureEnergy] but within "+str(EnergyTolerance)+"%, setting ActualHighPressureOutlet[HighPressureEnergy]=ActualHighPressureInlet[HighPressureEnergy]")
					else:
						raise Exception('too much error in interopolated enthalpies or internal energies')

				#note, constant volume cooling on the low pressure side is not implemented
				ActualLowPressureOutletEnthalpy=LowPressureInlet['Enthalpy']-(HighPressureMassFraction/LowPressureMassFraction)*(ActualHighPressureOutlet[HighPressureEnergy]-ActualHighPressureInlet[HighPressureEnergy])	#calculate the other enthalpy
				ActualLowPressureOutlet=GetFluidProperties(ActualLowPressureOutletPressure,Enthalpy=ActualLowPressureOutletEnthalpy)												#get the rest of the properties once enthalpy is known
			#don't think else is possible given the above conditions that are checked ???????????? is this an old comment???


		elif CalculationType is 'HighLowTemperaturePinch':
			#pinching occurs at both ends

			#note, cooling at the outlets is handled by the higher level function, so don't care if the outlet is defined here and there isn't any logic to take care of it.

			if ActualLowPressureOutletTemperature is not None:
				#high pressure side is heated at the inlet
				#change the ActualHighPressureInlet so that some heating happens
				ActualHighPressureInlet=GetFluidProperties(ActualHighPressureInletPressure,ActualLowPressureOutletTemperature-MinimumDeltaT)

			#if pinching occurs at the low temperature then the low pressure outlet temperature is the same as the high pressure inlet temperature plus the MinimumDeltaT
			#note, not just using ActualLowPressureOutletTemperature here because it may be set to None and don't want to make an else statement above that sets it because some logic below will be messed up.
			ActualLowPressureOutlet=GetFluidProperties(ActualLowPressureOutletPressure,ActualHighPressureInlet['Temperature']+MinimumDeltaT)


			if ActualHighPressureOutletTemperature is not None:
				#low pressure side is cooled at the inlet
				#change the ActualLowPressureInlet so that some cooling happens
				ActualLowPressureInlet=GetFluidProperties(ActualLowPressureInletPressure,ActualHighPressureOutletTemperature+MinimumDeltaT)

			#if the pinching is at the high temperature then the high pressure outlet temperature is the same as the low pressure inlet temperature minus the MinimumDeltaT
			#note, not just using ActualHighPressureOutletTemperature here because it may be set to None and don't want to make an else statement above that sets it because some logic below will be messed up.
			ActualHighPressureOutlet=GetFluidProperties(ActualHighPressureOutletPressure,ActualLowPressureInlet['Temperature']-MinimumDeltaT)


		elif CalculationType is 'MiddlePinch':
			#two control volumes needed for pinch in the middle

			#this case is sort of simpler because there is never heating or cooling at the pinch point

			PinchTemperature=Temperatures[index]
#don't know if PinchTemperature should be on the high or low pressure side when MinimumDeltaT is non-zero, but for now just consider it to be the low pressure side.
#it's likely this simpler solution technique trying to find the pinch point may not work well with the MinimumDeltaT non-zero, so not sure that it matters to much
#since the result of all of this logic is likely just going to give a better initial guess to the root solver

			LowPressurePinchPressure=LowPressures[index]
			HighPressurePinchPressure=HighPressures[index]
			PrintWarning("pinch temperature: "+str(PinchTemperature))
			LowPressurePinch=GetFluidProperties(LowPressurePinchPressure,PinchTemperature)				#get rest of the properties once the temperature is known
			HighPressurePinch=GetFluidProperties(HighPressurePinchPressure,PinchTemperature-MinimumDeltaT)		#get rest of the properties once the temperature is known

			#calculate the conditions at the low temperature end
			if ActualLowPressureOutletTemperature is not None:
				ActualLowPressureOutlet=GetFluidProperties(ActualLowPressureOutletPressure,ActualLowPressureOutletTemperature)	#get rest of the properties if the temperature is known
				ActualHighPressureInletEnergy=HighPressurePinch[HighPressureEnergy]-(LowPressurePinch['Enthalpy']-ActualLowPressureOutlet['Enthalpy'])*(LowPressureMassFraction/HighPressureMassFraction)	#calculate the other enthalpy or internal energy

				if HighPressureEnergy=='InternalEnergy':
					#there is constant volume heat addition so use internal energy
					ActualHighPressureInlet=GetFluidProperties(ActualHighPressureInletPressure,InternalEnergy=ActualHighPressureInletEnergy)	#get rest of the properties once the internal energy is known
				else:
					#normal heat exchanger with a nearly constant pressure
					ActualHighPressureInlet=GetFluidProperties(ActualHighPressureInletPressure,Enthalpy=ActualHighPressureInletEnergy)		#get rest of the properties once the enthalpy is known

			else:
				#calculate temperature at the low pressure outlet (not dependent at all on the high pressure outlet calcuation)
				ActualLowPressureOutletEnthalpy=LowPressurePinch['Enthalpy']-(HighPressureMassFraction/LowPressureMassFraction)*(HighPressurePinch[HighPressureEnergy]-ActualHighPressureInlet[HighPressureEnergy])	#calculate the other enthalpy
				ActualLowPressureOutlet=GetFluidProperties(ActualLowPressureOutletPressure,Enthalpy=ActualLowPressureOutletEnthalpy)											#get the rest of the properties once enthalpy is known

			#calculate the conditions at the high temperature end
			if ActualHighPressureOutletTemperature is not None:
				ActualHighPressureOutlet=GetFluidProperties(ActualHighPressureOutletPressure,ActualHighPressureOutletTemperature)											#get rest of the properties if the temperature is known
				ActualLowPressureInletEnthalpy=(ActualHighPressureOutlet[HighPressureEnergy]-HighPressurePinch[HighPressureEnergy])*(HighPressureMassFraction/LowPressureMassFraction)+LowPressurePinch['Enthalpy']	#calculate the other enthalpy
				ActualLowPressureInlet=GetFluidProperties(ActualLowPressureInletPressure,Enthalpy=ActualLowPressureInletEnthalpy)											#get rest of the properties once the enthalpy is known
			else:
				#calculate temperature at the high pressure outlet (not dependent at all on the low pressure outlet calcuation)
				ActualHighPressureOutletEnergy=(LowPressureMassFraction/HighPressureMassFraction)*(ActualLowPressureInlet['Enthalpy']-LowPressurePinch['Enthalpy'])+HighPressurePinch[HighPressureEnergy]		#calculate the other enthalpy or internal energy

				if HighPressureEnergy=='InternalEnergy':
					#there is constant volume heat addition so use internal energy
					ActualHighPressureOutlet=GetFluidProperties(ActualHighPressureOutletPressure,InternalEnergy=ActualHighPressureOutletEnergy)			#get the rest of the properties once internal energy is known
#may need to add a SaturateInternalEnergy option in the above call and another call farther above (and the actual function), like the SaturateEnthalpy option used above and below in several places.
				else:
					#normal heat exchanger with a nearly constant pressure
					ActualHighPressureOutlet=GetFluidProperties(ActualHighPressureOutletPressure,Enthalpy=ActualHighPressureOutletEnergy,SaturateEnthalpy=True)	#get the rest of the properties once enthalpy is known

		else:
			raise Exception("shouldn't get here")



		#now  use the root function to check the solution and find a more exact one if the above method failed.
		#but figure out how to call the heat exchanger solver
		#see notes in SolveRecuperator function about  how the 'Solve' assignments are not really necessary, but could be used to eliminate the  AssignSide variable. right now just leaving them in there for clarity only.
		#may be able to not have individual calls in the if statements for the 'Calculate' mode though if the AssignSide variable is used. not taking advantage of this now though, but could have.

		if ActualLowPressureOutletTemperature is not None:
			#unknown: 				low pressure inlet temperature

			if ActualHighPressureOutletTemperature is not None:
				PrintWarning('-combination 1-')

				#unknown, guessed value:	low pressure inlet temperature
				#unknown, solved for:		high pressure inlet temperature
				#known:				low pressure outlet temperature, high pressure outlet temperature
				StartEnd='HighTemperature'
				AssignedSide='LowPressure'
				FirstGuess=ActualLowPressureInlet['Temperature']
#for some reason having stability issues with other methods and 'lm' is the only one that seems to work.
				OptimizedResult=root(SolveRecuperator, FirstGuess, method='lm', args=('Guess', ActualLowPressureOuletTemperature, ActualLowPressures, 'Solve', ActualHighPressureOutletTemperature, ActualHighPressures, LowPressureMassFraction, HighPressureMassFraction, HighPressureEnergy, MinimumDeltaT, StartEnd, AssignedSide))

				if not OptimizedResult.success:
					raise Exception("heat exchanger -root- solver failed. error message is: "+OptimizedResult.message)

				ActualLowPressureInletTemperature=OptimizedResult.x
				ActualLowPressureTemperatures,ActualHighPressureTemperatures,ActualDeltaTs,ActualHighPressureSpecificHeats,ActualLowPressureSpecificHeats,ActualSpecificHeatRatios,ActualLowPressureInlet,ActualLowPressureOutlet,ActualHighPressureInlet,ActualHighPressureOutlet=SolveRecuperator(None,ActualLowPressureInletTemperature, ActualLowPressureOutlet['Temperature'], ActualLowPressures, 'Solve', ActualHighPressureOutlet['Temperature'], ActualHighPressures, LowPressureMassFraction, HighPressureMassFraction, HighPressureEnergy, MinimumDeltaT, StartEnd, AssignedSide)


			else:
				PrintWarning('-combination 2-')

				#unknown, guessed value:	low pressure inlet temperature (although it could be the high pressure outlet, choosing low pressure inlet for more commonality with other cases)
				#unknown, solved for:		high pressure outlet temperature
				#known:				low pressure outlet temperature, high pressure inlet temperature
				StartEnd='LowTemperature'
				AssignedSide='LowPressure'
				FirstGuess=ActualLowPressureInlet['Temperature']
				OptimizedResult=root(SolveRecuperator, FirstGuess, method='lm', args=('Guess', ActualLowPressureOuletTemperature, ActualLowPressures, ActualHighPressureInlet['Temperature'], 'Solve', ActualHighPressures, LowPressureMassFraction, HighPressureMassFraction, HighPressureEnergy, MinimumDeltaT, StartEnd, AssignedSide))

				if not OptimizedResult.success:
					raise Exception("heat exchanger -root- solver failed. error message is: "+OptimizedResult.message)

				ActualLowPressureInletTemperature=OptimizedResult.x
				ActualLowPressureTemperatures,ActualHighPressureTemperatures,ActualDeltaTs,ActualHighPressureSpecificHeats,ActualLowPressureSpecificHeats,ActualSpecificHeatRatios,ActualLowPressureInlet,ActualLowPressureOutlet,ActualHighPressureInlet,ActualHighPressureOutlet=SolveRecuperator(None,ActualLowPressureInletTemperature, ActualLowPressureOutletTemperature, ActualLowPressures, ActualHighPressureInlet['Temperature'], 'Solve', ActualHighPressures, LowPressureMassFraction, HighPressureMassFraction, HighPressureEnergy, MinimumDeltaT, StartEnd, AssignedSide)


		elif ActualHighPressureOutletTemperature is not None:		#low pressure outlet temperature must be unknown because the known case is detected above
			PrintWarning('-combination 3-')

			#unknown, guessed value:		high pressure inlet temperature
			#unknown, solved for:			low pressure outlet temperature
			#known:					low pressure inlet temperature, high pressure outlet temperature
			StartEnd='HighTemperature'
			AssignedSide='HighPressure'
			FirstGuess=ActualHighPressureInlet['Temperature']
			OptimizedResult=root(SolveRecuperator, FirstGuess, method='lm', args=(ActualLowPressureInlet['Temperature'], 'Solve', ActualLowPressures, 'Guess', ActualHighPressureOutletTemperature, ActualHighPressures, LowPressureMassFraction, HighPressureMassFraction, HighPressureEnergy, MinimumDeltaT, StartEnd, AssignedSide))

			if not OptimizedResult.success:
				raise Exception("heat exchanger -root- solver failed. error message is: "+OptimizedResult.message)

			ActualHighPressureInletTemperature=OptimizedResult.x
			ActualLowPressureTemperatures,ActualHighPressureTemperatures,ActualDeltaTs,ActualHighPressureSpecificHeats,ActualLowPressureSpecificHeats,ActualSpecificHeatRatios,ActualLowPressureInlet,ActualLowPressureOutlet,ActualHighPressureInlet,ActualHighPressureOutlet=SolveRecuperator(None,ActualLowPressureInlet['Temperature'], 'Solve', ActualLowPressures, ActualHighPressureInletTemperature, ActualHighPressureOutletTemperature, ActualHighPressures, LowPressureMassFraction, HighPressureMassFraction, HighPressureEnergy, MinimumDeltaT, StartEnd, AssignedSide)


		else:
			PrintWarning('-combination 4 - inlets only defined-')

			#unknown, guessed value:		low pressure outlet temperature
			#unknown, solved for:			high pressure outlet temperature
			#known:					low pressure inlet temperature, high pressure inlet temperature
			StartEnd='LowTemperature'
			AssignedSide='LowPressure'
			FirstGuess=ActualLowPressureOutlet['Temperature']
			OptimizedResult=root(SolveRecuperator, FirstGuess, method='lm', args=(ActualLowPressureInlet['Temperature'], 'Guess', ActualLowPressures, ActualHighPressureInlet['Temperature'], 'Solve', ActualHighPressures, LowPressureMassFraction, HighPressureMassFraction, HighPressureEnergy, MinimumDeltaT, StartEnd, AssignedSide))

			if not OptimizedResult.success:
				raise Exception("heat exchanger -root- solver failed. error message is: "+OptimizedResult.message)

			ActualLowPressureOutletTemperature=OptimizedResult.x
			ActualLowPressureTemperatures,ActualHighPressureTemperatures,ActualDeltaTs,ActualHighPressureSpecificHeats,ActualLowPressureSpecificHeats,ActualSpecificHeatRatios,ActualLowPressureInlet,ActualLowPressureOutlet,ActualHighPressureInlet,ActualHighPressureOutlet=SolveRecuperator(None,ActualLowPressureInlet['Temperature'], ActualLowPressureOutletTemperature, ActualLowPressures, ActualHighPressureInlet['Temperature'], 'Solve', ActualHighPressures, LowPressureMassFraction, HighPressureMassFraction, HighPressureEnergy, MinimumDeltaT, StartEnd, AssignedSide)



		SpecificHeatRatiosOld=SpecificHeatRatios.copy()
		Recuperator['SpecificHeatRatiosMaxResidual']=(ActualSpecificHeatRatios/SpecificHeatRatiosOld).max()*100-100


		###############################################################################################################################


		LowPressureOutlet=ActualLowPressureOutlet
		HighPressureOutlet=ActualHighPressureOutlet
#note, Actual outlet values are the same, and are defined in case the calling function overrides the non-Actual values. maybe should also use actual values above more places then to avoid confusion of their meaning? -- started to, but not sure if everything is cleared up.

		#add some variables to the dictionary returned
		Recuperator['LowPressure']['StartingProperties']=LowPressureInlet
		Recuperator['LowPressure']['RecuperatedProperties']=LowPressureOutlet			#set this value, even if the calling function overrides it (like to add a cooler)

		Recuperator['HighPressure']['StartingProperties']=HighPressureInlet
		Recuperator['HighPressure']['RecuperatedProperties']=HighPressureOutlet			#set this value, even if the calling function overrides it (like to add a heater)

		#add some more variables to the dictionary returned
		Recuperator['LowPressure']['ActualStartingProperties']=ActualLowPressureInlet		#if the inlet was a limit, then define the actual, calculated value
		Recuperator['LowPressure']['ActualRecuperatedProperties']=ActualLowPressureOutlet
		Recuperator['HighPressure']['ActualStartingProperties']=ActualHighPressureInlet		#if the inlet was a limit, then define the actual, calculated value
		Recuperator['HighPressure']['ActualRecuperatedProperties']=ActualHighPressureOutlet

		#set some values, even if there is no attempt to change them anywhere in this function, want to have them defined because they may or may not be set by the calling function
		#note, assume these are only changed in this function below and not above
		#don't know that they are used for anything other than reference???????
		Recuperator['HighPressure']['StartingProperties']['HeatAdded_TotalMassFlow']=0
		Recuperator['HighPressure']['RecuperatedProperties']['HeatAdded_TotalMassFlow']=0
		Recuperator['LowPressure']['StartingProperties']['HeatRejected_TotalMassFlow']=0
		Recuperator['LowPressure']['RecuperatedProperties']['HeatRejected_TotalMassFlow']=0

		###############################################################################################################################





		###############################################################################################################################
		#check to see if the current calculation technique actually worked.
		ActualDeltaTsSmallErrorTolerance=10**-8
		BoundarySmallErrorTolerance	=30*10**-2
#need to figure out why this value is so high!!!!!!!! related to roundoff error, but need to figure out if there is a better way to mitigate than what is done below, because it is obviously not good enough.
#see notes below about effectiveness and phi below giving unphysical values







		#much of the following code is probably not needed since the root function is used above to find a better solution, although just leaving it in here because it doesn't hurt and the additional trials probably won't ever be run
		#so there probably isn't a speed loss just leaving it here. if do ever decide the logic below is really needed, should have it more intelligent and save the solution that was best out of all the trials instead of just
		#erroring out with the last one. also need to change above where the root function failure raises an exception so that it doesn't and tries one of the below methods to give it a better initial condition.
		#may also want to iterate on an error tolerance if having trouble getting a solution so that the cases that don't have a problem will have better solutions and the ones with problems will have a more relaxed tolerance.
		#leaving things as is and relying on the root function rather than searching for a better permutation below may a little slower, but probably not too much slower since the root function doesn't look like it is doing
		#too many iterations and the reliability is much higher and the accuracy is much higher.



#check to see if this case is now fixed
#http://localhost:5000/CO2Cycle/PlotImages/HeatExchanger?HeatedSideMassFraction=0.5&DeltaPPerDeltaT=5000&CooledSideInletTemperature=400.0&CooledSideInletPressure=6.5&HeatedSideInletTemperature=325.0&HeatedSideInletPressure=20.0



		##########check for small errors and give a warning if a small error
		if	(
				(ActualDeltaTs.min()			< MinimumDeltaT) 
				and	(ActualDeltaTs.min()		> MinimumDeltaT-ActualDeltaTsSmallErrorTolerance)
				and	(
					ActualDeltaTs.argmin()		!= 0
					and ActualDeltaTs.argmin()	!= (ActualDeltaTs.size-1)
					)
			):
			#if minimum is at an end and greater than SmallErrorTolerance then that means there was an error due to accuracy of fluid properties.
			#(at least think this is the issue and not the solution technique). might want to do a piecewise solution to the interior above if there is a middle pinch to reduce this?
			#note that the endpoints are checked below in a different way that isn't as dependent on the quality of the fluid property data, so they have a lower tolerance.
			PrintWarning("warning minimum ActualDeltaT is "+str(ActualDeltaTs.min())+", the error is probably an interpolation error because it is greater than -"+str(ActualDeltaTsSmallErrorTolerance))

		#note, if non-Actual values and Actual values are different, then the non-Actual were defined by the function inputs, so don't want to mess with them at all here and
		#non-Actual values should have been tested at the very beginning of the function whether they are appropriate. also don't think there is any use comparing actual
		#and non actual values for errors
		if	(
				(ActualLowPressureInlet['Temperature']							< ActualHighPressureOutlet['Temperature'])
				and ((ActualHighPressureOutlet['Temperature']-ActualLowPressureInlet['Temperature'])	< BoundarySmallErrorTolerance)
			):

			PrintWarning("warning Actual high pressure outlet temperature in heat exchanger was greater than Actual low pressure inlet by less than "+str(BoundarySmallErrorTolerance)+"K. assuming an interpolation error and setting Actual high pressure outlet temperature equal to Actual low pressure inlet temperature")
			ActualHighPressureOutlet=GetFluidProperties(ActualHighPressureOutlet['Pressure'],Temperature=ActualLowPressureInlet['Temperature'])
		if	(
				(ActualLowPressureOutlet['Temperature']							< ActualHighPressureInlet['Temperature'])
				and (ActualHighPressureInlet['Temperature']-ActualLowPressureOutlet['Temperature']	< BoundarySmallErrorTolerance)
			):

			PrintWarning("warning Actual low pressure outlet temperature in heat exchanger was greater than Actual high pressure inlet by less than "+str(BoundarySmallErrorTolerance)+"K. assuming an interpolation error and setting Actual low pressure outlet temperature equal to Actual high pressure inlet temperature")
			ActualLowPressureOutlet=GetFluidProperties(ActualLowPressureOutlet['Pressure'],Temperature=ActualHighPressureInlet['Temperature'])



		#add some variables to the dictionary returned
		Recuperator['LowPressure']['MassFraction']=LowPressureMassFraction
		Recuperator['HighPressure']['MassFraction']=HighPressureMassFraction
		Recuperator['LowPressure']['ActualTemperatures']=ActualLowPressureTemperatures
		Recuperator['LowPressure']['ActualSpecificHeats']=ActualLowPressureSpecificHeats
		Recuperator['HighPressure']['ActualTemperatures']=ActualHighPressureTemperatures
		Recuperator['HighPressure']['ActualSpecificHeats']=ActualHighPressureSpecificHeats
		Recuperator['ActualSpecificHeatRatios']=ActualSpecificHeatRatios
#the following line is commented out because it is confusing and not an Actual value so not sure if it has meaning all the time
#		Recuperator['SpecificHeatRatiosOriginal']=SpecificHeatRatiosOriginal		#right now this is going to error out if doing more than 1 iteration. if doing more than 1 iteration should also decide what SpecificHeatRatios is really the right one to plot when fixing this error.
		Recuperator['ActualDeltaTs']=ActualDeltaTs


		##########check for a large error and try other calculation techniques
		if	(
				(
					ActualDeltaTs.min()<MinimumDeltaT-ActualDeltaTsSmallErrorTolerance
					and (
						ActualDeltaTs.argmin()!=0 
						and 
						ActualDeltaTs.argmin()!=(ActualDeltaTs.size-1))
				)
				or ((ActualHighPressureOutlet['Temperature']	- ActualLowPressureInlet['Temperature'])	> BoundarySmallErrorTolerance)
				or (ActualHighPressureInlet['Temperature']	- ActualLowPressureOutlet['Temperature']	> BoundarySmallErrorTolerance)
			):

			PrintWarning("Low Temperature Error: "+str(ActualHighPressureInlet['Temperature']-ActualLowPressureOutlet['Temperature'])+", High Temperature Error: "+str(ActualHighPressureOutlet['Temperature']-ActualLowPressureInlet['Temperature']))		#is this labled correct? is a negative error fine???
			if trial<3 and (CalculationType is not None):			#change None to something else to force a certain mode for testing
				#if the anticipated solution technique was wrong, try the other two
				#PrintKeysAndValues("Recuperator",Recuperator)
				if CalculationType is 'MiddlePinch' and Previousindex is None:
#this assumes the guessed index is correct, but is it?????????????
					Previousindex=index
					#try the oppposite curvature
					if SpecificHeatRatiosSecondDerivative.mean()<=0:
						#concave up
						index=HighestTemperatureOneCrossingIndex+SpecificHeatRatiosDeviationFromOne[[HighestTemperatureOneCrossingIndex,HighestTemperatureOneCrossingIndex+1]].argmin()
					elif SpecificHeatRatiosSecondDerivative.mean()>=0:
						#concave down
						index=LowestTemperatureOneCrossingIndex+SpecificHeatRatiosDeviationFromOne[[LowestTemperatureOneCrossingIndex,LowestTemperatureOneCrossingIndex+1]].argmin()
					else:
						raise Exception("don't don't understand the curvature of SpecificHeatRatios")
				elif PreviousCalculationType is None:
					if CalculationType is 'MiddlePinch':
						PreviousCalculationType='MiddlePinch'
						CalculationType='LowTemperaturePinch'
					elif CalculationType is 'LowTemperaturePinch':
						PreviousCalculationType='LowTemperaturePinch'
						CalculationType='HighTemperaturePinch'
					elif CalculationType is 'HighTemperaturePinch':
						PreviousCalculationType='HighTemperaturePinch'
						CalculationType='MiddlePinch'
					else:
						raise Exception("shouldn't get here???")
				elif PreviousCalculationType is 'MiddlePinch':
					if CalculationType is 'LowTemperaturePinch':
						PreviousCalculationType='LowTemperaturePinch'
						CalculationType='HighTemperaturePinch'
					else:
						raise Exception("shouldn't get here???")
				elif PreviousCalculationType is 'LowTemperaturePinch':
					if CalculationType is 'HighTemperaturePinch':
						PreviousCalculationType='HighTemperaturePinch'
						CalculationType='MiddlePinch'
				elif PreviousCalculationType is 'HighTemperaturePinch':
					if CalculationType is 'MiddlePinch':
						PreviousCalculationType='MiddlePinch'
						CalculationType='LowTemperaturePinch'
					else:
						raise Exception("shouldn't get here???")
				else:
					raise Exception("shouldn't get here???")
				#may have made the above a lot more complicated than it needs to be but just doing so to make sure actually got all cases covered

			else:
				print CalculationType
				print ActualDeltaTs.min()
				PrintKeysAndValues("Recuperator",Recuperator)
				print ""
				raise Exception("there is some problem with the heat exchanger logic")
				#could this error message be more desciptive (like old logic that was used before had to do the trial and error fallback method)
				#or not since not sure which trial was actually the closest one?
		else:
			break		#the guessed technique was correct





	##########now that the solution was found, check for appropriately constrained outlet boundary conditions

	if (CalculationType is 'LowTemperaturePinch') and (ActualLowPressureOutletTemperature is not None) and ((HighPressureInletTemperature-ActualLowPressureOutletTemperature)>BoundarySmallErrorTolerance):
#ActualLowPressureOutletTemperature is always defined now that the root finding technique is used. not sure if that condition matters that much?
		#if this function was called directly then the inputs given aren't valid. if called by the GeneralRealRecuperator function then it has an invalid case defined
		raise Exception("ActualLowPressureOutletTemperature defined but solution is low temperature pinch and (HighPressureInletTemperature-ActualLowPressureOutletTemperature)>"+str(BoundarySmallErrorTolerance)+"K so the inputs to this function are invalid")

	if (CalculationType is 'HighTemperaturePinch') and (ActualHighPressureOutletTemperature is not None) and ((ActualHighPressureOutletTemperature-LowPressureInletTemperature)>BoundarySmallErrorTolerance):
		#if this function was called directly then the inputs given aren't valid. if called by the GeneralRealRecuperator function then it has an invalid case defined
		raise Exception("ActualHighPressureOutletTemperature defined but solution is high temperature pinch and (ActualHighPressureOutletTemperature-LowPressureInletTemperature)>"+str(BoundarySmallErrorTolerance)+"K so the inputs to this function are invalid")

	if CalculationType is 'HighLowTemperaturePinch':
		if (ActualLowPressureOutletTemperature is not None) and ((HighPressureInletTemperature-ActualLowPressureOutletTemperature)>BoundarySmallErrorTolerance):
			#if this function was called directly then the inputs given aren't valid. if called by the GeneralRealRecuperator function then it has an invalid case defined
			raise Exception("ActualLowPressureOutletTemperature defined but solution is HighLowTemperaturePinch and (HighPressureInletTemperature-ActualLowPressureOutletTemperature)>"+str(BoundarySmallErrorTolerance)+"K so the inputs to this function are invalid")

		if (ActualHighPressureOutletTemperature is not None) and ((ActualHighPressureOutletTemperature-LowPressureInletTemperature)>BoundarySmallErrorTolerance):
			#if this function was called directly then the inputs given aren't valid. if called by the GeneralRealRecuperator function then it has an invalid case defined
			raise Exception("ActualHighPressureOutletTemperature defined but solution is HighLowTemperaturePinch and (ActualHighPressureOutletTemperature-LowPressureInletTemperature)>"+str(BoundarySmallErrorTolerance)+"K so the inputs to this function are invalid")

	if (HighPressureInlet['Temperature']-ActualHighPressureInlet['Temperature'])>BoundarySmallErrorTolerance:
		#don't think will ever get here because check to see if HighPressureInletTemperature>LowPressureOutletTemperature at the beginning of the function,
		#but might if the delta T is high, so just check again anyway. don't think any heater or cooler could fix this situation, right?
		raise Exception('solution resulted in an actual high pressure inlet temperature that was too low')
	if (ActualLowPressureInlet['Temperature']-LowPressureInlet['Temperature'])>BoundarySmallErrorTolerance:
		#don't think will ever get here because check to see if LowPressureInletTemperature<HighPressureOutletTemperature at the beginning of the function,
		#but just do as a safety measure that the rest of the logic is working right
		raise Exception('solution resulted in an actual low pressure inlet temperature that was too high')

	###############################################################################################################################




	#calculate the heat recuperated
	Recuperator['SpecificHeatRecuperated_TotalMassFlow']=(Recuperator['LowPressure']['ActualStartingProperties']['Enthalpy']-Recuperator['LowPressure']['ActualRecuperatedProperties']['Enthalpy'])*LowPressureMassFraction	#should be able to do this same type of calculation on the high pressure side and get the same answer

	#calculate the heat rejected at the low pressure inlet (it is nonzero if the actual low pressure inlet is different than the low pressure inlet)
	Recuperator['LowPressure']['StartingProperties']['HeatRejected_TotalMassFlow']=(LowPressureInlet['Enthalpy']-ActualLowPressureInlet['Enthalpy'])*LowPressureMassFraction
	#calculate the heat added at the high pressure inlet (it is nonzero if the actual high pressure inlet is different than the high pressure inlet)
	Recuperator['HighPressure']['StartingProperties']['HeatAdded_TotalMassFlow']=(HighPressureInlet[HighPressureEnergy]-ActualHighPressureInlet[HighPressureEnergy])*HighPressureMassFraction

	#calculate the heat exchanger effectiveness
	#note, it may be possible to use some of the above calculations to simplify the following, but just redoing it explicitely to be clear and don't feel like generalizing the above, if it would be necessary
	#still don't understand why effectiveness is not maximum at SpecificHeatRatioOriginal average=1 for the SpecificHeatRatio increasing case
	MaxSpecificHeatRecuperatedHighPressure_TotalMassFlow=(HighPressureOutletMax[HighPressureEnergy]-ActualHighPressureInlet[HighPressureEnergy])*HighPressureMassFraction
	MaxSpecificHeatRecuperatedLowPressure_TotalMassFlow=(ActualLowPressureInlet['Enthalpy']-LowPressureOutletMin['Enthalpy'])*LowPressureMassFraction
	Recuperator['phi']=Recuperator['SpecificHeatRecuperated_TotalMassFlow']/max(MaxSpecificHeatRecuperatedHighPressure_TotalMassFlow,MaxSpecificHeatRecuperatedLowPressure_TotalMassFlow)
	Recuperator['Effectiveness']=Recuperator['SpecificHeatRecuperated_TotalMassFlow']/min(MaxSpecificHeatRecuperatedHighPressure_TotalMassFlow,MaxSpecificHeatRecuperatedLowPressure_TotalMassFlow)












#some precision issue must be why the 1.01 is needed, and why can give the wrong value if the mass fraction is really low (the recuperator doesn't really exist). probably want to not even run the recuperator function at all if know the mass fraction is so low. same situation with a really small temperature drop in the heat exchanger.
	if (HighPressureMassFraction>.01) and ((Temperatures.max()-Temperatures.min())>2.5):
		if Recuperator['phi']>=1.01:	#some precision issue must be why the .01 is needed
			PrintKeysAndValues("Recuperator",Recuperator)
			raise Exception("recuperator phi can't be greater than 1")
		elif (Recuperator['Effectiveness']>=1.01):
			PrintKeysAndValues("Recuperator",Recuperator)
			raise Exception("recuperator effectiveness can't be greater than 1")











	return Recuperator








