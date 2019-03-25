###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


from helpers import SmartDictionary
from FluidProperties.REFPROP import GetFluidProperties
import math







#compute static properties given stagnation properties and a velocity
def GetStaticProperties(StagnationProperties,Velocity):
	StaticProperties=SmartDictionary()
	StaticProperties['Enthalpy']=StagnationProperties['Enthalpy']-(Velocity**2)/2
	StaticProperties['Entropy']=StagnationProperties['Entropy']
	StaticProperties=GetFluidProperties(Enthalpy=StaticProperties['Enthalpy'], Entropy=StaticProperties['Entropy'],ExtendedProperties=True)
#right now the above function doesn't seem to work for the main compressor with refprop. probably want to use an interpolation table method instead to increase reliability.
	StaticProperties['Mach']=Velocity/StaticProperties['SpeedOfSound']
	return StaticProperties



#compute piping static properties and geometry given stagnation properties and a velocity
def ComputePiping(MassFlowRate,StagnationProperties,Parameters):
	Piping=SmartDictionary()
	Piping['StaticProperties']=GetStaticProperties(StagnationProperties,Parameters['Velocity'])
	Piping['Geometry']['Area']=MassFlowRate/(Piping['StaticProperties']['Density']*Parameters['Velocity'])
	Piping['Geometry']['Diameter_mm']=((Piping['Geometry']['Area']/math.pi)**.5)*2*1000
	Piping['ReD']=Piping['StaticProperties']['Density']*Parameters['Velocity']*Piping['Geometry']['Diameter_mm']/1000/Piping['StaticProperties']['DynamicViscocity']
	return Piping

#compute IGV piping static properties and geometry and rotor speed given stagnation properties and a velocity and metal tip mach number
#note, this has a few lines of code the same/redundant as ComputePiping, but is separated so you can run if not all values are known/defined
def ComputeCompressorParameters(MassFlowRate,CompressorParameters,CompressorInputParameters):
	#populate some more properties that are not normally fetched.
	CompressorParameters['StartingProperties']=GetFluidProperties(Temperature=CompressorParameters['StartingProperties']['Temperature'],Pressure=CompressorParameters['StartingProperties']['Pressure'],ExtendedProperties=True)

	CompressorParameters['InletPiping']=ComputePiping(MassFlowRate,CompressorParameters['StartingProperties'],CompressorInputParameters['InletPiping'])

	CompressorParameters['Mach_based']['IGVStaticProperties']=GetStaticProperties(CompressorParameters['StartingProperties'],CompressorInputParameters['IGVVelocity'])
	CompressorParameters['Mach_based']['IGVArea']=MassFlowRate/(CompressorParameters['Mach_based']['IGVStaticProperties']['Density']*CompressorInputParameters['IGVVelocity'])
	CompressorParameters['Mach_based']['TipMetalMach']=CompressorInputParameters['RotorTipMetalVelocity']/CompressorParameters['StartingProperties']['SpeedOfSound']
	CompressorParameters['Mach_based']['IGVTipRadius']=(CompressorParameters['Mach_based']['IGVArea']/(math.pi*(1-CompressorInputParameters['HubToTipRatio']**2)))**.5
	CompressorParameters['Mach_based']['IGVDiameter_mm']=CompressorParameters['Mach_based']['IGVTipRadius']*2*1000
	CompressorParameters['Mach_based']['Speed_RPM']=(CompressorInputParameters['RotorTipMetalVelocity']/CompressorParameters['Mach_based']['IGVTipRadius'])*60/(2*math.pi)
	return CompressorParameters

def ComputeTurbomachineryParameters(MassFlowRate,ComponentParameters,ComponentInputParameters):
	ComponentParameters['Cordier_based']=SmartDictionary()

	#populate some more properties that are not normally fetched.
	ComponentParameters['StartingProperties']=GetFluidProperties(Temperature=ComponentParameters['StartingProperties']['Temperature'],Pressure=ComponentParameters['StartingProperties']['Pressure'],ExtendedProperties=True)


	Ds=2.84*ComponentInputParameters['Ns']**(-.476)
	VolumetricFlowRate=MassFlowRate/ComponentParameters['StartingProperties']['Density']

	if 'CompressedProperties' in ComponentParameters:
		#it is a compressor
		ExitKey='CompressedProperties'
	elif 'ExpandedProperties' in ComponentParameters:
		#it is a turbine
		ExitKey='ExpandedProperties'

	if VolumetricFlowRate!=0:
		ComponentParameters['deltah']=ComponentParameters['StartingProperties']['Enthalpy']-ComponentParameters[ExitKey]['Enthalpy']
		ComponentParameters['Stage_deltah']=ComponentParameters['deltah']/ComponentInputParameters['StageCount']
		if ComponentParameters['Stage_deltah']!=0:
			ComponentParameters['Cordier_based']['Omega']=((((ComponentInputParameters['Ns'])**2)*(math.fabs(ComponentParameters['Stage_deltah']))**(3.0/2.0))/VolumetricFlowRate)**.5
			ComponentParameters['Cordier_based']['Omega_RPM']=ComponentParameters['Cordier_based']['Omega']*60/(2*math.pi)

			ComponentParameters['Cordier_based']['D']=((Ds*VolumetricFlowRate)/(math.fabs(ComponentParameters['Stage_deltah']))**.5)**.5

	return ComponentParameters


