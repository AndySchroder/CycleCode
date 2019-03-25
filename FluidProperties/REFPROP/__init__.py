###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


#import some needed packages and functions
import time,numpy
import cPickle
from os.path import isfile
import PyREFPROP.python2x.refprop as PyREFPROP
import FluidProperties					#not sure that this does anything at the moment other than give a point to reference the fluid properties from with the __file__ object


#define some standard enthalpies of formation becaues refprop does not do enthalpies of formation

EnthalpiesOfFormation={}

#standard enthalpies of formation at
ReferencePressure=101325.	#Pa, 1 atm

ReferenceTemperature1=298.15	#K
EnthalpiesOfFormation[ReferenceTemperature1]={}
EnthalpiesOfFormation[ReferenceTemperature1]['entropy']=198.59724118621799		#don't think this is actually used for anything right now.

#appendix A
EnthalpiesOfFormation[ReferenceTemperature1]['water']		= -241845.		#kJ/kmole
EnthalpiesOfFormation[ReferenceTemperature1]['nitrogen']	= 0.			#kJ/kmole
EnthalpiesOfFormation[ReferenceTemperature1]['oxygen']		= 0.			#kJ/kmole
EnthalpiesOfFormation[ReferenceTemperature1]['CO2']		= -393546.		#kJ/kmole

#appendix b1
EnthalpiesOfFormation[ReferenceTemperature1]['methane']		= -74831.		#kJ/kmole
MethaneHHV							= 55.528e6		#J/kg fuel, not an enthalpy of formation, but also in appendix b1
MethaneLHV							= 50.016e6		#J/kg fuel, not an enthalpy of formation, but also in appendix b1
MethaneHHVoverLHV						= MethaneHHV/MethaneLHV


ReferenceTemperature2=400.	#K, needed because REFPROP is unstable below 333K with the mixture concentrations of combustion currently being used because of the water vapour condensing.
EnthalpiesOfFormation[ReferenceTemperature2]={}
EnthalpiesOfFormation[ReferenceTemperature2]['entropy']=207.21132890132012

#appendix A

#not exactly an enthalpy of formation because it includes the heat of vaporization, but it should be what REFPROP needs to make everything work out correctly.
#really though, this assumes that the partial pressure of water in the exhaust gases is high enough that all of the water will condense by the time the
#gases return back to ambient temperature at the end of the cycle.
#if not, then need to remove the latent heat of vaporization below and then switch to a lower heating value.
#not sure how to do this automatically in a general way though.
EnthalpiesOfFormation[ReferenceTemperature2]['water']		= -242858.+44010.	#kJ/kmole

EnthalpiesOfFormation[ReferenceTemperature2]['nitrogen']	= 0.			#kJ/kmole
EnthalpiesOfFormation[ReferenceTemperature2]['oxygen']		= 0.			#kJ/kmole
EnthalpiesOfFormation[ReferenceTemperature2]['CO2']		= -393617.		#kJ/kmole

#manually calculated from the values above and REFPROP. the main inconsistency is REFPROP may have used a different latent heat of vaporization for the water, but it should be pretty close.
#also note that this calculation used REFPROP's enthalpy of vaporization of water which may have actually been a little lower than the value used above.
EnthalpiesOfFormation[ReferenceTemperature2]['methane']		= -77590.236		#kJ/kmole

#all from An Introduction to Combustion, Third Edition, by Steven Turns.




#define this regardless because need to know what the air composition was for determining the combustion byproducts
MolesAir=[79.,21.]


#define some molecular weights that were manually obtained from REFPROP.
#could dynamically get them from REFPROP, but they never change and also it would be unnecessarily complicated.
#note, these are only used for the computation of stoichiometric air to fuel mass ratio and also the moles of oxygen per mole of fuel and also the reference entropy.
#all other computations that use the molecular weight use the dynamically obtained one from REFPROP

MolecularWeight_Nitrogen	= 28.01348		#g/mole
MolecularWeight_Oxygen		= 31.9988		#g/mole
MolecularWeight_Methane		= 16.0428		#g/mole
MolecularWeight_Air		= 28.8503972		#g/mole

#assign default fluid to use
#this variable is also used in some additional if statements that may be best if they are restructured or renamed a little bit.
DefaultFluidSimpleName='CO2'




#################################
#probably should move this function to helpers.py
#################################
#os.path.dirname doesn't seem to do a ./ for the current directory, so force it to so still works if there is no subfolder in the path returned by os.path.dirname
#and want to also add another subfolder to the path returned by os.path.dirname. note, don't always want to add a ./ to everything in case the path returned by 
#os.path.dirname is an absolute one.
def SmartDirname(TheFile):
	import os
	if os.path.dirname(TheFile)=='':
		return '.'
	else:
		return os.path.dirname(TheFile)
#################################


def ComputeCombinedEnthalpyOfFormation(FluidNames,MoleFractions,ReferenceTemperature):
	EnthalpyOfFormation=0
	for CurrentFluidName,MoleFraction in zip(FluidNames,MoleFractions):
		EnthalpyOfFormation+=MoleFraction*EnthalpiesOfFormation[ReferenceTemperature][CurrentFluidName]
	return EnthalpyOfFormation				#J/molemix

def ComputeMoleFractions(Moles):
	Moles=numpy.array(Moles)
	return list(Moles/Moles.sum())

def ComputeEquivalenceRatio(PercentExcessOxygen):	#percent excess oxygen is the same as percent excess air.
	return 1./((PercentExcessOxygen/100.)+1.)

def ComputeStoichiometricMassOfAirToMassOfFuelRatio():														#for methane, CH4
	return 2*(MolecularWeight_Oxygen+(MolesAir[0]/MolesAir[1])*MolecularWeight_Nitrogen)/MolecularWeight_Methane						#StoichiometricMassOfAirToMassOfFuelRatio=(A/F)stoic=17.1=(mair/mfuel)stoic

def ComputeMassOfAirToMassOfFuelRatio(EquivalenceRatio,StoichiometricMassOfAirToMassOfFuelRatio):
	return StoichiometricMassOfAirToMassOfFuelRatio/EquivalenceRatio

def ComputeMolesOfOxygenPerMoleOfFuel(ActualMassOfAirToMassOfFuelRatio):											#for methane, CH4
	#ActualMassOfAirToMassOfFuelRatio=(A/F)=(mair/mfuel)=MolesOfOxygenPerMoleOfFuel*(MolecularWeight_Oxygen+(MolesAir[0]/MolesAir[1])*MolecularWeight_Nitrogen)/MolecularWeight_Methane, so
	return ActualMassOfAirToMassOfFuelRatio/((MolecularWeight_Oxygen+(MolesAir[0]/MolesAir[1])*MolecularWeight_Nitrogen)/MolecularWeight_Methane)		#MolesOfOxygenPerMoleOfFuel

def ComputeMassOfFuelToTotalMassRatio(PercentExcessOxygen=0):													#for methane, CH4
	MassOfAirToMassOfFuelRatio=ComputeMassOfAirToMassOfFuelRatio(ComputeEquivalenceRatio(PercentExcessOxygen),ComputeStoichiometricMassOfAirToMassOfFuelRatio())
	return (1/(MassOfAirToMassOfFuelRatio+1))

def ComputeMassOfAirToTotalMassRatio(PercentExcessOxygen=0):													#for methane, CH4
	MassOfAirToMassOfFuelRatio=ComputeMassOfAirToMassOfFuelRatio(ComputeEquivalenceRatio(PercentExcessOxygen),ComputeStoichiometricMassOfAirToMassOfFuelRatio())
	return (MassOfAirToMassOfFuelRatio/(MassOfAirToMassOfFuelRatio+1))

def SetupFluid(FluidSimpleName,PercentExcessOxygen=None):		#methane, CH4
#see warnings below about how this currently has limited result when running after initial importation.

	#note, refprop psuedo pure fluids basically treat a mixture as a pure fluid. i guess they have done testing of those mixtures specifically or use a different (possibly less general) model. the main advantage is psuedo pure fluids are faster to compute.
	#don't know why the u prefix (unicode formating syntax?) is needed with REFPROP functions

	#not using mole fractions defined by predefined mixtures. instead just passing the mixture components explictely and then manually
	#calculating the mole fractions (since mole fractions aren't returned at all when passing mixture components explicitely).
	#the species concentration in the mixture files is pretty much a reference that they will just read for you.
	#apparently the fortran code does not persist this information, so the mole fractions in the predefined mixtures have to be manually stored and passed later after initially setting the mixture.
	#most likely, the mole fractions were added to the mixture files much later in the code developement and
	#they were too lazy to make that option persist as the species themselves do.
	#also, pure fluids don't return a mole fraction either. so that case has to be handled as well because you still need to pass a mole fraction
	#for pure fluids to most functions.

	#make some variables global so they will persist after each run without having to catch them and set them each time the function is run.
	global MoleFractions, MolecularWeight, CriticalPressure, CriticalTemperature, CriticalDensity, CriticalEntropy, CriticalEnthalpy, FluidName, CurrentPercentExcessOxygen

	FluidName=FluidSimpleName
	CurrentPercentExcessOxygen=PercentExcessOxygen

	#make some smarter shortcuts so don't have to remember every common mixture used species', concentrations, etc..
	if FluidSimpleName == 'air':
		FluidNames=[u'nitrogen',u'oxygen']
		Moles=MolesAir
	elif FluidSimpleName == 'CombustionProducts':
		FluidNames=[u'CO2',u'water',u'oxygen',u'nitrogen']
		# general reaction for complete lean combustion of methane with no Argon assumed in the air:
		# CH4+a(O2+(79/21)N2)-->CO2+2H2O+bO2+(79/21)aN2
		# 2b=2a-4, and b=a-2 and for stoichiometric, a=2
		if PercentExcessOxygen is None:
			raise Exception('PercentExcessOxygen must be defined')
		MolesOfOxygenPerMoleOfFuel=ComputeMolesOfOxygenPerMoleOfFuel(ComputeMassOfAirToMassOfFuelRatio(ComputeEquivalenceRatio(PercentExcessOxygen),ComputeStoichiometricMassOfAirToMassOfFuelRatio()))
		Moles=[1.,2.,MolesOfOxygenPerMoleOfFuel-2,MolesAir[0]/MolesAir[1]*MolesOfOxygenPerMoleOfFuel]
	elif FluidSimpleName == 'methane':
		FluidNames=[u'methane']
		Moles=[1.]
	elif FluidSimpleName == 'CO2':
		FluidNames=[u'CO2']
		Moles=[1.]
	else:
		raise Exception('no matching fluid shortcut defined')


	#assign the fluid and then get fluid properties

	FluidSetup=PyREFPROP.setup(u'def',FluidNames)				#don't know why the u is needed. 'def' is Default reference state as specified in fluid file is applied to each pure component. you have to specify a reference state. it isn't smart enough to use the default as the default.

	MoleFractions=ComputeMoleFractions(Moles)
	EnthalpyOfFormation={}
	EnthalpyOfFormation[ReferenceTemperature1]=ComputeCombinedEnthalpyOfFormation(FluidNames,MoleFractions,ReferenceTemperature1)			#J/molemix, don't think this one is actually used for anything????
	EnthalpyOfFormation[ReferenceTemperature2]=ComputeCombinedEnthalpyOfFormation(FluidNames,MoleFractions,ReferenceTemperature2)			#J/molemix
	
	#get the mixture [average] molecular weight so can later do unit conversions (or is it really molecular mass?)
	MolecularWeight=PyREFPROP.wmol(MoleFractions)['wmix']		#[g/molmix]

	#set the reference enthalpy to the enthalpy of formation so that chemical reactions can be done easily
	if FluidSimpleName != 'CO2':		#don't mess with pure CO2, because all the plot axis ranges will have to be redone and it isn't used for any reactions.
		PyREFPROP.setref(hrf=u'OTH', ixflag=2, x0=MoleFractions, h0=EnthalpyOfFormation[ReferenceTemperature2], s0=EnthalpiesOfFormation[ReferenceTemperature2]['entropy']*MolecularWeight/MolecularWeight_Air, t0=ReferenceTemperature2, p0=ReferencePressure/1000)		#entropy reference value is the same as the standard for air in refprop at the reference temperature and pressure

	if FluidSimpleName == 'CombustionProducts':
		#REFPROP can't seem to find the critical point of this mixture????


		pass


#need to clear these variables out?????



	else:
		#get the critical temperature and pressure. note info() above (actually, info is no longer used anymore in the script) does return critical temperature, but there is a bug and it doesn't return critical pressure, but the following does, so just using it instead of fixing the bug
		CriticalPressure=float((PyREFPROP.critp(MoleFractions)['pcrit'])*1000)
		#note, just calling this twice instead of calling once, assigning a variable, and then defining the two separately.
		#can't find a good way to extract a subset of a dictionary in one line of code. best thing found was http://stackoverflow.com/questions/5352546/best-way-to-extract-subset-of-key-value-pairs-from-python-dictionary-object, but it
		#still would make double call or require a definition of a separate variable anyway.
		CriticalTemperature=float(PyREFPROP.critp(MoleFractions)['tcrit'])
		#calculate the entropy at the critical point using the density at the critical point because that is more stable since it is one of the primitive variables?
		#don't know why critp() doesn't return this already?
		CriticalDensity=float((PyREFPROP.critp(MoleFractions)['Dcrit'])*MolecularWeight)
		CriticalEntropy=float((PyREFPROP.flsh(u'TD',float(CriticalTemperature),CriticalDensity/MolecularWeight,MoleFractions)['s'])*1000/MolecularWeight)	#again, not a real efficient way to do this, but it is only done once
		CriticalEnthalpy=float((PyREFPROP.flsh(u'TD',float(CriticalTemperature),CriticalDensity/MolecularWeight,MoleFractions)['h'])*1000/MolecularWeight)	#again, not a real efficient way to do this, but it is only done once

		##print out some reference information
		#print "Molecular Weight :     "+str(MolecularWeight)
		#print "Critical Pressure :    "+str(CriticalPressure)
		#print "Critical Temperature : "+str(CriticalTemperature)


	return


tic=time.time()
print "importing REFPROP functions and setting up fluid to be "+DefaultFluidSimpleName
SetupFluid(DefaultFluidSimpleName)
print "finished importing REFPROP functions and setting up fluid: "+str(time.time()-tic)


#setup wrapper functions for processing arrays of inputs and outputs.
#only need a few so not bothering to define every one that could be.
#is there a better way to do this all in one function definition instead of defining a function and then passing in through vectorize?
def cpFromTemperaturePressureSimple(Temperature,Pressure): return float((PyREFPROP.flsh(u'TP',float(Temperature),float(Pressure/1000),MoleFractions)['cp'])*1000/MolecularWeight)
cpFromTemperaturePressure=numpy.vectorize(cpFromTemperaturePressureSimple)

def cpFromTemperatureEntropySimple(Temperature,Entropy): return float((PyREFPROP.flsh(u'TS',float(Temperature),float(Entropy*MolecularWeight/1000),MoleFractions)['cp'])*1000/MolecularWeight)
cpFromTemperatureEntropy=numpy.vectorize(cpFromTemperatureEntropySimple)

def cvFromTemperaturePressureSimple(Temperature,Pressure): return float((PyREFPROP.flsh(u'TP',float(Temperature),float(Pressure/1000),MoleFractions)['cv'])*1000/MolecularWeight)
cvFromTemperaturePressure=numpy.vectorize(cvFromTemperaturePressureSimple)

def cvFromTemperatureEntropySimple(Temperature,Entropy): return float((PyREFPROP.flsh(u'TS',float(Temperature),float(Entropy*MolecularWeight/1000),MoleFractions)['cv'])*1000/MolecularWeight)
cvFromTemperatureEntropy=numpy.vectorize(cvFromTemperatureEntropySimple)

def PressureFromTemperatureEntropySimple(Temperature,Entropy): return float((PyREFPROP.flsh(u'TS',float(Temperature),float(Entropy*MolecularWeight/1000),MoleFractions)['p'])*1000)
PressureFromTemperatureEntropy=numpy.vectorize(PressureFromTemperatureEntropySimple)

def PressureFromTemperatureDensitySimple(Temperature,Density): return float((PyREFPROP.flsh(u'TD',float(Temperature),float(Density/MolecularWeight),MoleFractions)['p'])*1000)
PressureFromTemperatureDensity=numpy.vectorize(PressureFromTemperatureDensitySimple)

def EnthalpyFromTemperatureDensitySimple(Temperature,Density): return float((PyREFPROP.flsh(u'TD',float(Temperature),float(Density/MolecularWeight),MoleFractions)['h'])*1000/MolecularWeight)
EnthalpyFromTemperatureDensity=numpy.vectorize(EnthalpyFromTemperatureDensitySimple)

def EnthalpyFromTemperaturePressureSimple(Temperature,Pressure): return float((PyREFPROP.flsh(u'TP',float(Temperature),float(Pressure/1000),MoleFractions)['h'])*1000/MolecularWeight)
EnthalpyFromTemperaturePressure=numpy.vectorize(EnthalpyFromTemperaturePressureSimple)

def InternalEnergyFromTemperaturePressureSimple(Temperature,Pressure): return float((PyREFPROP.flsh(u'TP',float(Temperature),float(Pressure/1000),MoleFractions)['e'])*1000/MolecularWeight)
InternalEnergyFromTemperaturePressure=numpy.vectorize(InternalEnergyFromTemperaturePressureSimple)

def EnthalpyFromTemperatureEntropySimple(Temperature,Entropy): return float((PyREFPROP.flsh(u'TS',float(Temperature),float(Entropy*MolecularWeight/1000),MoleFractions)['h'])*1000/MolecularWeight)
EnthalpyFromTemperatureEntropy=numpy.vectorize(EnthalpyFromTemperatureEntropySimple)

def EntropyFromTemperaturePressureSimple(Temperature,Pressure): return float((PyREFPROP.flsh(u'TP',float(Temperature),float(Pressure/1000),MoleFractions)['s'])*1000/MolecularWeight)
EntropyFromTemperaturePressure=numpy.vectorize(EntropyFromTemperaturePressureSimple)

def DensityFromTemperaturePressureSimple(Temperature,Pressure): return float((PyREFPROP.flsh(u'TP',float(Temperature),float(Pressure/1000),MoleFractions)['D'])*MolecularWeight)
DensityFromTemperaturePressure=numpy.vectorize(DensityFromTemperaturePressureSimple)

def TemperatureFromEnthalpyPressureSimple(Enthalpy,Pressure): return float(PyREFPROP.flsh(u'PH',float(Pressure/1000),float(Enthalpy*MolecularWeight/1000),MoleFractions)['t'])
TemperatureFromEnthalpyPressure=numpy.vectorize(TemperatureFromEnthalpyPressureSimple)

def TemperatureFromInternalEnergyPressureSimple(InternalEnergy,Pressure): return float(PyREFPROP.flsh(u'PE',float(Pressure/1000),float(InternalEnergy*MolecularWeight/1000),MoleFractions)['t'])
TemperatureFromInternalEnergyPressure=numpy.vectorize(TemperatureFromInternalEnergyPressureSimple)


def gammaFromTemperaturePressureSimple(Temperature,Pressure):
	PropertiesFromREFPROP=PyREFPROP.flsh(u'TP',float(Temperature),float(Pressure/1000),MoleFractions)
	return float(PropertiesFromREFPROP['cp']/PropertiesFromREFPROP['cv'])
gammaFromTemperaturePressure=numpy.vectorize(gammaFromTemperaturePressureSimple)

def gammaFromTemperatureEntropySimple(Temperature,Entropy):
	PropertiesFromREFPROP=PyREFPROP.flsh(u'TS',float(Temperature),float(Entropy*MolecularWeight/1000),MoleFractions)
	return float(PropertiesFromREFPROP['cp']/PropertiesFromREFPROP['cv'])
gammaFromTemperatureEntropy=numpy.vectorize(gammaFromTemperatureEntropySimple)


def SaturationTemperatureFromEntropySimple(Entropy): return float(PyREFPROP.sats(float(Entropy*MolecularWeight/1000),MoleFractions,kph=int(0))['t1'])				#not sure if kph=0 and t1 are always the best to use?
SaturationTemperatureFromEntropy=numpy.vectorize(SaturationTemperatureFromEntropySimple)

def SaturationPressureFromEntropySimple(Entropy): return float((PyREFPROP.sats(float(Entropy*MolecularWeight/1000),MoleFractions,kph=int(0))['p1'])*1000)				#not sure if kph=0 and p1 are always the best to use?
SaturationPressureFromEntropy=numpy.vectorize(SaturationPressureFromEntropySimple)

def SaturationDensityFromEntropySimple(Entropy): return float((PyREFPROP.sats(float(Entropy*MolecularWeight/1000),MoleFractions,kph=int(0))['D1'])*MolecularWeight)				#not sure if kph=0 and p1 are always the best to use?
SaturationDensityFromEntropy=numpy.vectorize(SaturationDensityFromEntropySimple)


#can only get compressibility factor with temperature and density inputs (at least how things are setup right now), so make a way to percalculate them
#not sure why, but these functions have to be used as an extra step to get compressibility factor, but maybe they should be wrapped up into specific compressibility factor functions?
def DensityFromTemperatureEntropySimple(Temperature,Entropy): return float((PyREFPROP.flsh(u'TS',float(Temperature),float(Entropy*MolecularWeight/1000),MoleFractions)['D'])*MolecularWeight)
DensityFromTemperatureEntropy=numpy.vectorize(DensityFromTemperatureEntropySimple)

def DensityFromEnthalpyEntropySimple(Enthalpy,Entropy): return float((PyREFPROP.flsh(u'HS',float(Enthalpy*MolecularWeight/1000),float(Entropy*MolecularWeight/1000),MoleFractions)['D'])*MolecularWeight)
DensityFromEnthalpyEntropy=numpy.vectorize(DensityFromEnthalpyEntropySimple)

def TemperatureFromEnthalpyEntropySimple(Enthalpy,Entropy): return float((PyREFPROP.flsh(u'HS',float(Enthalpy*MolecularWeight/1000),float(Entropy*MolecularWeight/1000),MoleFractions)['t']))
TemperatureFromEnthalpyEntropy=numpy.vectorize(TemperatureFromEnthalpyEntropySimple)

#now get the compressibility factor
def CompressiblityFactorFromTemperatureDensitySimple(Temperature,Density): return float(PyREFPROP.therm2(float(Temperature),float(Density/MolecularWeight),MoleFractions)['Z'])
CompressiblityFactorFromTemperatureDensity=numpy.vectorize(CompressiblityFactorFromTemperatureDensitySimple)







#now get the SpeedOfSound
def SpeedOfSoundFromTemperaturePressureSimple(Temperature,Pressure): return float((PyREFPROP.flsh(u'TP',float(Temperature),float(Pressure/1000),MoleFractions)['w']))
SpeedOfSoundFromTemperaturePressure=numpy.vectorize(SpeedOfSoundFromTemperaturePressureSimple)

#now get the dynamic viscocity
def DynamicViscocityFromTemperatureDensitySimple(Temperature,Density): return float(PyREFPROP.trnprp(float(Temperature),float(Density/MolecularWeight),MoleFractions)['eta']/1e6)
DynamicViscocityFromTemperatureDensity=numpy.vectorize(DynamicViscocityFromTemperatureDensitySimple)

#now get the thermal conductivity
def ThermalConductivityFromTemperatureDensitySimple(Temperature,Density): return float(PyREFPROP.trnprp(float(Temperature),float(Density/MolecularWeight),MoleFractions)['tcx'])
ThermalConductivityFromTemperatureDensity=numpy.vectorize(ThermalConductivityFromTemperatureDensitySimple)








if DefaultFluidSimpleName == 'CO2':

#warning, SetupFluid does not re-do this section if run after the inital import.

	#compute the liquid vapor saturation line for plotting and finding the minimum temperature
	SaturationLineEntropies=numpy.linspace(750,2125,50)							#problems with refprop crashing, so limited to this range until get it fixed

	SaturationLineDensities=SaturationDensityFromEntropy(SaturationLineEntropies)
	SaturationLinePressures=SaturationPressureFromEntropy(SaturationLineEntropies)
	SaturationLineTemperatures=SaturationTemperatureFromEntropy(SaturationLineEntropies)

	#define the min temperatures that will be computed
	MinTemperature=SaturationLineTemperatures.min()

else:
#need to make this entropy range not hard coded so it works with mutliple fluids
	pass


#define a max enthalpy to saturate to (if selected), as a workaround so bad heat exchanger solutions don't error out, but just realize they are bad and try a different technique
MaxEnthalpy=2.5*10**6


if DefaultFluidSimpleName == 'CO2':		#right now, don't make data tables if not doing CO2. if not doing CO2, probably doing just a simple air cycle with no heat exchangers, which doesn't take very long at all.

#warning, SetupFluid does not re-do this section if run after the inital import.



	#now, use table lookup/interpolation for some commonly accessed dependent and independent values to speed things up,
	#but limit to only what is needed for faster startup and reduced RAM compared to old
	#table only lookup which just put everything into RAM
	#also use a hybrid and smart range so that the entire liquid, liquid+vapour mixture,vapour,gas, and supercticial
	#regions will be included and they will also have a appropriate and efficient resolution
	#hybrid smart range is similiar to that which is used in CycleFunctions.PlotResults and may want to combine the two more
	#in the future somehow. check that function for more comments on the rationale behind everything.
	#sometimes refprop is not very stable either (for example TemperatureFromInternalEnergyPressure), so this also eliminates issues with that too

	if not (										#if any of the pickled files don't already exist, recreate them all, so just need to delete one of them to force them all to be recreated and for this part of the code to be run
			isfile(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/cpFromTemperaturePressureInterpolant.p')
			and
			isfile(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/EnthalpyFromTemperaturePressureInterpolant.p')
			and
			isfile(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/TemperatureFromInternalEnergyPressureInterpolant.p')
			and
			isfile(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/TemperatureFromEnthalpyPressureInterpolant.p')
		):

		print "recreating cpFromTemperaturePressure, EnthalpyFromTemperaturePressure, TemperatureFromInternalEnergyPressure, and TemperatureFromEnthalpyPressure Interpolants and saving to a pickled file for future runs"

		#import and define some needed functions
		from scipy.interpolate import LinearNDInterpolator

		#first calculate some values from already defined REFPROP functions and some ranges that were inspired by old ranges from NIST webook and from making CycleFunctions.PlotResults

		REFPROPMaxTemperature=1100							#max temperature can do in refprop without having any problems
		REFPROPMaxPressure=50*10**6							#max pressure want to do in REFPROP (mainly to limit speedown/memory consumption)
	#make sure this is compatiple with plotting data??? or will never use these functions when plotting data?


#not sure why this if statement is here since this whole section is already skipped if not CO2, other than was planning to take that if statement away later????
		if DefaultFluidSimpleName == 'CO2':
			MiddleTemperature=CriticalTemperature
		else:
			MiddleTemperature=15+273			#make it a little lower than ambient. CO2 will condense at this point, but other fluid's (such as air) critical temperature may be much lower than ambient and don't want to show these very cold temperatures


		#region 1
	#	Entropies1=numpy.linspace(875,3000,100)
	#	Temperatures1=numpy.linspace(MinTemperature,CriticalTemperature,100)
	#	(Entropies1Grid,Temperatures1Grid)=numpy.meshgrid(Entropies1,Temperatures1,indexing='ij')
	#	Pressures1Grid=PressureFromTemperatureEntropy(Temperatures1Grid,Entropies1Grid)
	#	InternalEnergies1Grid=InternalEnergyFromTemperatureEntropy(Temperatures1Grid,Entropies1Grid)
	#	Enthalpies1Grid=EnthalpyFromTemperatureEntropy(Temperatures1Grid,Entropies1Grid)
	#	cps1Grid=cpFromTemperatureEntropy(Temperatures1Grid,Entropies1Grid)

		#region 2
		Pressures2=numpy.concatenate((numpy.linspace(.1*10**6,12*10**6,120),numpy.linspace(12*10**6,REFPROPMaxPressure,381)[1:]))
		Temperatures2=numpy.concatenate((numpy.linspace(MiddleTemperature,400,193),numpy.linspace(400,REFPROPMaxTemperature,1401)[1:]))
		(Pressures2Grid,Temperatures2Grid)=numpy.meshgrid(Pressures2,Temperatures2,indexing='ij')
		Entropies2Grid=EntropyFromTemperaturePressure(Temperatures2Grid,Pressures2Grid)
		InternalEnergies2Grid=InternalEnergyFromTemperaturePressure(Temperatures2Grid,Pressures2Grid)
		Enthalpies2Grid=EnthalpyFromTemperaturePressure(Temperatures2Grid,Pressures2Grid)
		cps2Grid=cpFromTemperaturePressure(Temperatures2Grid,Pressures2Grid)

	#	#next flatten and combine values from both regions
	#	EntropyData=numpy.concatenate((Entropies1Grid.flatten(),Entropies2Grid.flatten()))
	#	TemperatureData=numpy.concatenate((Temperatures1Grid.flatten(),Temperatures2Grid.flatten()))
	#	PressureData=numpy.concatenate((Pressures1Grid.flatten(),Pressures2Grid.flatten()))
	#	InternalEnergyData=numpy.concatenate((InternalEnergies1Grid.flatten(),InternalEnergies2Grid.flatten()))
	#	EnthalpyData=numpy.concatenate((Enthalpies1Grid.flatten(),Enthalpies2Grid.flatten()))
	#	cpData=numpy.concatenate((cps1Grid.flatten(),cps2Grid.flatten()))

		EntropyData=Entropies2Grid.flatten()
		TemperatureData=Temperatures2Grid.flatten()
		PressureData=Pressures2Grid.flatten()
		InternalEnergyData=InternalEnergies2Grid.flatten()
		EnthalpyData=Enthalpies2Grid.flatten()
		cpData=cps2Grid.flatten()


		#next combine independent variable pairs into one object because that is what the interpolator functions are expecting
		EnthalpyEntropyData=numpy.hstack((EnthalpyData[numpy.newaxis].T,EntropyData[numpy.newaxis].T))
		TemperaturePressureData=numpy.hstack((TemperatureData[numpy.newaxis].T,PressureData[numpy.newaxis].T))
		EntropyPressureData=numpy.hstack((EntropyData[numpy.newaxis].T,PressureData[numpy.newaxis].T))
		InternalEnergyPressureData=numpy.hstack((InternalEnergyData[numpy.newaxis].T,PressureData[numpy.newaxis].T))
		EnthalpyPressureData=numpy.hstack((EnthalpyData[numpy.newaxis].T,PressureData[numpy.newaxis].T))

	#######are these all the right combinations needed? can some be eliminated??????

		#then create the interpolator functions, later overwriting previously defined vectorized functions that used REFPROP every time a variable was requested (which was slow)
	#is it is okay if there are duplicate points????

		#specifically, the following will be redefined that are used in the cycle (and not the plot of the cycle) so it is faster
		cpFromTemperaturePressureInterpolant=LinearNDInterpolator(TemperaturePressureData,cpData)
		EnthalpyFromTemperaturePressureInterpolant=LinearNDInterpolator(TemperaturePressureData,EnthalpyData)
		TemperatureFromInternalEnergyPressureInterpolant=LinearNDInterpolator(InternalEnergyPressureData,TemperatureData,TemperatureData.max())		#warning, there is an out of range value here that assumes out of range is always a high internal energy
		TemperatureFromEnthalpyPressureInterpolant=LinearNDInterpolator(EnthalpyPressureData,TemperatureData,TemperatureData.max())			#warning, there is an out of range value here that assumes out of range is always a high enthalpy

		#dump the Interpolants created to a pickle file for faster startup next time
		cPickle.dump(cpFromTemperaturePressureInterpolant,open(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/cpFromTemperaturePressureInterpolant.p','wb'))
		cPickle.dump(EnthalpyFromTemperaturePressureInterpolant,open(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/EnthalpyFromTemperaturePressureInterpolant.p','wb'))
		cPickle.dump(TemperatureFromInternalEnergyPressureInterpolant,open(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/TemperatureFromInternalEnergyPressureInterpolant.p','wb'))
		cPickle.dump(TemperatureFromEnthalpyPressureInterpolant,open(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/TemperatureFromEnthalpyPressureInterpolant.p','wb'))

	#skip other cases for now that are only used in the cycle plot and not the cycle
	#if aren't going to make table lookups for everything below, is there anything that should be removed above to speed things up?


	else:
		print "loading cpFromTemperaturePressure, EnthalpyFromTemperaturePressure, TemperatureFromInternalEnergyPressure, and TemperatureFromEnthalpyPressure Interpolants from a pickled file"
		print "if having problems with interpolants, try deleting the files so that they are recreated because they may not work if used with a different version of numpy/scipy"
		cpFromTemperaturePressureInterpolant=cPickle.load(open(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/cpFromTemperaturePressureInterpolant.p', 'rb'))
		EnthalpyFromTemperaturePressureInterpolant=cPickle.load(open(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/EnthalpyFromTemperaturePressureInterpolant.p', 'rb'))
		TemperatureFromInternalEnergyPressureInterpolant=cPickle.load(open(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/TemperatureFromInternalEnergyPressureInterpolant.p', 'rb'))
		TemperatureFromEnthalpyPressureInterpolant=cPickle.load(open(SmartDirname(FluidProperties.__file__)+'/FluidPropertyCache/TemperatureFromEnthalpyPressureInterpolant.p', 'rb'))


	#can't seem to pickle this function so have to put it here and then define the higher level functions that overwrite the direct refprop ones (with Interpolant functions). this extra step is not that big of a deal because this is really fast to run.
	#define a function that checks for out of range values for each interpolation function
	##copied and pasted from DataTables.py##
	def InterpolateDataAndCheckValues(InterpolantName,Values):
		exec('InterpolatedValues='+InterpolantName+'Interpolant(Values)')
		if numpy.isnan(InterpolatedValues).any():
			raise Exception('interpolated value(s) out of range, InterpolantName: '+InterpolantName+', values: '+str(Values)+', InterpolatedValues: '+str(InterpolatedValues))
		else:
			return InterpolatedValues

	#assign a new name to a few objects before they are overwritten so can access REFPROP data directly if want to if need to get data outside of the range
	#established above for the interpolants (such as by the CycleFunctions.PlotResults function that creates a background of fluid properties over a much larger range than the cycle is ever solved for)
	cpFromTemperaturePressureREFPROPdirect=cpFromTemperaturePressure
	EnthalpyFromTemperaturePressureREFPROPdirect=EnthalpyFromTemperaturePressure
	TemperatureFromInternalEnergyPressureREFPROPdirect=TemperatureFromInternalEnergyPressure
	TemperatureFromEnthalpyPressureREFPROPdirect=TemperatureFromEnthalpyPressure

	#now assign new objects to the original names
	def cpFromTemperaturePressure(*Values): return InterpolateDataAndCheckValues('cpFromTemperaturePressure',Values)
	def EnthalpyFromTemperaturePressure(*Values): return InterpolateDataAndCheckValues('EnthalpyFromTemperaturePressure',Values)
	def TemperatureFromInternalEnergyPressure(*Values): return InterpolateDataAndCheckValues('TemperatureFromInternalEnergyPressure',Values)
	def TemperatureFromEnthalpyPressure(*Values): return InterpolateDataAndCheckValues('TemperatureFromEnthalpyPressure',Values)


	#then delete variables (to free up memory) that are no longer needed now that the interpolator functions have been created
	#del asdfadsf
	#maybe doesn't matter since it doesn't use much ram since just doing a few variables into interpolator functions.









#run the interpolating function with the appropriate arguments and then put the desired results into a dictionary of the same form as if were using the data lookup tables.
def GetFluidProperties(Pressure=None,Temperature=None,Enthalpy=None,InternalEnergy=None,Entropy=None,Density=None,ExtendedProperties=False,TransportProperties=True,SaturateEnthalpy=False):	#all properties must be provided in base SI units. not really interpolating here but keeping the name for now for compatibility with table lookups.

	Properties={}

	#remember what the fluid is for future activities like plotting
	#note, need to decide when is best to read from CycleInputParameters and when is best to use this value
	Properties['FluidName']=FluidName
	Properties['PercentExcessOxygen']=CurrentPercentExcessOxygen

	#first get the properties, converting units as necessary to work with refprop which deals in mols and sometimes kilo, micro, units or grams instead of kg. (what does sometimes kilo, micro units mean?????????????)
	#assume only two things are defined. if more than two are defined then the first combination that the logic below gets to is used. don't know why more than two would ever be provided though.
	if (Enthalpy is not None) and (Entropy is not None):
		PropertiesFromREFPROP=PyREFPROP.flsh(u'HS',float(Enthalpy*MolecularWeight/1000),float(Entropy*MolecularWeight/1000),MoleFractions)			#don't know why u is needed. don't know why MoleFractions is needed for pure fluids. also may want to look into other flsh functions.
	elif (Pressure is not None) and (Temperature is not None):
		PropertiesFromREFPROP=PyREFPROP.flsh(u'TP',float(Temperature),float(Pressure/1000),MoleFractions)							#same notes as above
	elif (Pressure is not None) and (Entropy is not None):
		PropertiesFromREFPROP=PyREFPROP.flsh(u'PS',float(Pressure/1000),float(Entropy*MolecularWeight/1000),MoleFractions)					#same notes as above
	elif (Pressure is not None) and (Density is not None):
		PropertiesFromREFPROP=PyREFPROP.flsh(u'PD',float(Pressure/1000),float(Density/MolecularWeight),MoleFractions)						#same notes as above
	elif (Temperature is not None) and (Density is not None):
		PropertiesFromREFPROP=PyREFPROP.flsh(u'TD',float(Temperature),float(Density/MolecularWeight),MoleFractions)						#same notes as above
	elif (Pressure is not None) and (InternalEnergy is not None):
#should the internal energy be saturated like the enthalpy is??????
		PropertiesFromREFPROP=PyREFPROP.flsh(u'PE',float(Pressure/1000),float(InternalEnergy*MolecularWeight/1000),MoleFractions)				#same notes as above
	elif (Pressure is not None) and (Enthalpy is not None):
		if (SaturateEnthalpy) and (Enthalpy>MaxEnthalpy):	#saturate enthalpy to value defined above, as a workaround so bad heat exchanger solutions don't error out, but just realize they are bad and try a different technique
			Enthalpy=MaxEnthalpy
		PropertiesFromREFPROP=PyREFPROP.flsh(u'PH',float(Pressure/1000),float(Enthalpy*MolecularWeight/1000),MoleFractions)					#same notes as above
	else:
		raise Exception('need temperature or entropy or enthalpy given a certain pressure or enthalpy and entropy')

	#then convert units and populate the Properties dictionary and determine dynamic viscocity and thermal conductivity
	Properties['Temperature']=float(PropertiesFromREFPROP['t'])
	Properties['Pressure']=float(PropertiesFromREFPROP['p']*1000)
	Properties['Enthalpy']=float(PropertiesFromREFPROP['h']*1000/MolecularWeight)
	Properties['Entropy']=float(PropertiesFromREFPROP['s']*1000/MolecularWeight)
	Properties['InternalEnergy']=float(PropertiesFromREFPROP['e']*1000/MolecularWeight)
	Properties['Density']=float(PropertiesFromREFPROP['D']*MolecularWeight)
	if ExtendedProperties:
		Properties['SpeedOfSound']=float(PropertiesFromREFPROP['w'])
		Properties['cp']=float(PropertiesFromREFPROP['cp']*1000/MolecularWeight)
		Properties['cv']=float(PropertiesFromREFPROP['cv']*1000/MolecularWeight)

		#compute the derived quantity, gamma, the ratio of specific heats
		Properties['gamma']=float(PropertiesFromREFPROP['cp']/PropertiesFromREFPROP['cv'])

		if TransportProperties:		#make a way to skip transport properties if explicitly told to because they don't seem to be possible with mixtures of water, but default to getting transport properties with extended properties.
			#need to run another function to get dynamic viscocity and thermal conductivity.
			TransportPropertiesFromREFPROP=PyREFPROP.trnprp(PropertiesFromREFPROP['t'],PropertiesFromREFPROP['D'],MoleFractions)
			#convert units and populate Properties dictionary
			Properties['DynamicViscocity']=float(TransportPropertiesFromREFPROP['eta']/1e6)
			Properties['ThermalConductivity']=float(TransportPropertiesFromREFPROP['tcx'])

		#need to run another function to get the dimensionless compressibility factor, Z
		Properties['Z']=float(PyREFPROP.therm2(PropertiesFromREFPROP['t'],PropertiesFromREFPROP['D'],MoleFractions)['Z'])



	return Properties		#all properties are returned in base SI units.


print "finished setting remaining functions: "+str(time.time()-tic)

