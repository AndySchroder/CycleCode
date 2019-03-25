###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


from numpy import loadtxt, lexsort, reshape, zeros, ones_like, around, abs
from scipy.integrate import simps
from scipy.interpolate import interp1d
from FluidProperties.REFPROP import DensityFromTemperaturePressure,DynamicViscocityFromTemperatureDensity,ThermalConductivityFromTemperatureDensity,MolecularWeight	#note, make sure don't use SetupFluid with another fluid because MolecularWeight may get changed and below it's assumed to be for CO2
from helpers import SmartDictionary
from HeatExchangers import GeneralRealRecuperator





ChannelIndices={}
ChannelIndices['Density']=0
ChannelIndices['DynamicViscocity']=1
ChannelIndices['ThermalConductivity']=2
ChannelIndices['StaticTemperature']=3
ChannelIndices['TotalTemperature']=4
ChannelIndices['TotalEnthalpy']=5
ChannelIndices['GaugeStaticPressure']=6
ChannelIndices['GaugeTotalPressure']=7
ChannelIndices['AxialVelocity']=8
ChannelIndices['X']=9
ChannelIndices['Y']=10

WallIndices={}
WallIndices['HeatFlux']=0
WallIndices['X']=1
WallIndices['Y']=2






def ReadStarCCMDataFile(RunName,Type,PointCounts,Type2='HalfChannel'):
	FileName=BaseDirectory+'/'+RunName+'-'+Type+Type2+'.csv'

	RawData=loadtxt(FileName,skiprows=1,delimiter=',')		#read in the data file

	if Type2=='':	#assume it is a y+ file and no sorting is needed
		SortedData=RawData
	else:

#for some reason lots of round off error in the data export from starccm+ when using the original grid and not a presentation grid derived part.
#also, there was a huge spike for some reason in temperature and don't understand why
#some other cases with presentation grid had some small spikes, but they weren't as terrible
#anyway, need to round data to get the sort to work properly
#note, this rounding mode is not the best because doesn't just truncate floating precision, but the fixed precision.
#		RawData[:,-3]=around(RawData[:,-3],decimals=11)

		SortedData=RawData[lexsort((RawData[:,-2],RawData[:,-3]))]	#for some reason starccm+ does not sort the output, so do that.


	Data=reshape(SortedData,PointCounts)				#reshape to [x,y,parameter]

	return Data


def ReadAndInterpolateRegularHeatFluxValues(RunName,Type,PointCounts,XValues):

	Data=ReadStarCCMDataFile(RunName,Type,PointCounts,'Wall')

	#fudge some values so they don't give out or range errors
#don't think this is needed if "data on vertices" is selected during export
#	Data[0,0,WallIndices['X']]=XValues[0]
#	Data[-1,0,WallIndices['X']]=XValues[-1]

	HeatFluxInterpolator=interp1d(Data[:,0,WallIndices['X']],Data[:,0,WallIndices['HeatFlux']])		#for some reason LinearNDInterpolator requires 2D data, so using the less general 

	RegularData=zeros((XValues.size,Data.shape[1],Data.shape[2]))

	RegularData[:,0,WallIndices['X']]=XValues
	#just leave the y and z values as zero for now because they aren't even used anyway
	RegularData[:,0,WallIndices['HeatFlux']]=HeatFluxInterpolator(XValues)

	return RegularData



def ComputeAverage(Parameter,Data):

#seems to be about 0.1% error created with this averaging technique, and not really sure why......maybe this was a grid or "data on vertices" issue that has now been resolved???

	#normal vector to the exiting side of the plane is 1,0,0
	#z component of velocitiy is not only zero but also meaningless in an averaging sense because there is no component of the normal vector in that direction
	#y component of velocity is not zero but it is also meaning less because there is no component of the normal vector in that direction
	MassFlux=Data[:,:,ChannelIndices['Density']]*Data[:,:,ChannelIndices['AxialVelocity']]

	if Parameter == 'MassFlux':
		#do a surface average for mass flux because it doesn't really make sense to weight it by itself
		ParameterToAverage=MassFlux
		ParameterToWeight=ones_like(Data[:,:,0])
	else:
		#for every thing else, weight by mass flux
		ParameterToAverage=Data[:,:,ChannelIndices[Parameter]]
		ParameterToWeight=MassFlux


	xPoints,yPoints,_=Data.shape

	AveragedData=zeros(xPoints)

	for xPoint in range(xPoints):
		#since no values are dependent upon the z direction, pretty much skipping those parts of the integral because it just cancels out.
		#simps function nomenclature/use of x is actually y in this geometry
		AveragedData[xPoint]=simps(
						y=(
							ParameterToWeight[xPoint,:]*ParameterToAverage[xPoint,:]
						),
						x=Data[xPoint,:,ChannelIndices['Y']]
						)/simps(
						y=(
							ParameterToWeight[xPoint,:]
						),
						x=Data[xPoint,:,ChannelIndices['Y']]
						)

	XValues=Data[:,0,ChannelIndices['X']]		#x values are the same for all y, so just use point 0

	return XValues,AveragedData



def ComputeIntegral(Parameter,Data):

	if Parameter == 'MassFlux':
		#also, as noted above, assumes axial velocity is normal to the plane
		ParameterToIntegrate=Data[:,:,ChannelIndices['Density']]*Data[:,:,ChannelIndices['AxialVelocity']]
	elif Parameter == 1:
		ParameterToIntegrate=ones_like(Data[:,:,0])
	else:
		ParameterToIntegrate=Data[:,:,ChannelIndices[Parameter]]


	xPoints,yPoints,_=Data.shape

	IntegratedData=zeros(xPoints)

	for xPoint in range(xPoints):
		#as noted above,
		#since no values are dependent upon the z direction, pretty much skipping those parts of the integral because it just cancels out.
		#simps function nomenclature/use of x is actually y in this geometry
		IntegratedData[xPoint]=simps(y=(ParameterToIntegrate[xPoint,:]),x=Data[xPoint,:,ChannelIndices['Y']])

	XValues=Data[:,0,ChannelIndices['X']]		#x values are the same for all y, so just use point 0

	return XValues,IntegratedData


def ComputeReValues(Data,ReferencePressure):
	XValues,AveragedStaticTemperature=ComputeAverage('StaticTemperature',Data)
	XValues,AveragedGaugeStaticPressures=ComputeAverage('GaugeStaticPressure',Data)
	DensityWeightedByStaticTemperatureAndPressure=DensityFromTemperaturePressure(AveragedStaticTemperature,AveragedGaugeStaticPressures+ReferencePressure)
	DynamicViscocityWeightedByStaticTemperatureAndPressure=DynamicViscocityFromTemperatureDensity(AveragedStaticTemperature,DensityWeightedByStaticTemperatureAndPressure)

	#also calculate thermal conductivity since it's also needed later for Nu calculations
	ThermalConductivityWeightedByStaticTemperatureAndPressure=ThermalConductivityFromTemperatureDensity(AveragedStaticTemperature,DensityWeightedByStaticTemperatureAndPressure)

	AveragedMassFlux=abs(ComputeAverage('MassFlux',Data)[1])		#this should be a constant

	HalfChannelCrossSectionalArea=1*ComputeIntegral(1,Data)[1]		#this should be a constant
	ChannelHydraulicDiameter=2*(2*HalfChannelCrossSectionalArea/1)		#this should be a constant


	ChannelReValues=AveragedMassFlux*ChannelHydraulicDiameter/DynamicViscocityWeightedByStaticTemperatureAndPressure

	return XValues,ChannelReValues,DynamicViscocityWeightedByStaticTemperatureAndPressure,ChannelHydraulicDiameter,ThermalConductivityWeightedByStaticTemperatureAndPressure,AveragedMassFlux		#also return DynamicViscocityWeightedByStaticTemperatureAndPressure and some other stuff that are needed later for other things


def RecuperatorSimplifier(LowTemperature,HighTemperature,LowPressure,HighPressure,MassFraction,MinimumDeltaT):

	Recuperator=SmartDictionary()
	RecuperatorInputParameters=SmartDictionary()
	RecuperatorInputParameters['LowPressure']['MassFraction']=1.0
	RecuperatorInputParameters['HighPressure']['MassFraction']=MassFraction
	RecuperatorInputParameters['NumberofTemperatures']=200
	Recuperator['LowPressure']['StartingProperties']['Temperature']=HighTemperature
	Recuperator['LowPressure']['StartingProperties']['Pressure']=LowPressure
	Recuperator['HighPressure']['StartingProperties']['Temperature']=LowTemperature
	Recuperator['HighPressure']['StartingProperties']['Pressure']=HighPressure

	RecuperatorInputParameters['MinimumDeltaT']=MinimumDeltaT
	RecuperatorInputParameters['DeltaPPerDeltaT']=0

	return GeneralRealRecuperator(Recuperator,RecuperatorInputParameters)








def SutherlandLaw(Temperature=273.,Fluid='CO2'):

	#setup this function to be general for any fluid, but actually only have constants for CO2 populated
	Constants={
			'CO2':{
				'ReferenceTemperature':		273.,
				'ReferenceDynamicViscosity':	1.370*10**(-5),
				'SutherlandConstant':		222.,
				},
		}

	DynamicViscosity=Constants[Fluid]['ReferenceDynamicViscosity']*((Temperature/Constants[Fluid]['ReferenceTemperature'])**(3./2.))*(Constants[Fluid]['ReferenceTemperature']+Constants[Fluid]['SutherlandConstant'])/(Temperature+Constants[Fluid]['SutherlandConstant'])

	return DynamicViscosity



def IdealGasDensity(Temperature,Pressure,Fluid='CO2'):

	R=8.3144598					#J/(mol*K), http://physics.nist.gov/cgi-bin/cuu/Value?r

	#setup this function to be general for any fluid, but actually only have molar mass for CO2 populated
	MolarMass={'CO2':MolecularWeight}		#g/mole, see note above about MolecularWeight and SetupFluid

	Rspecific=R/(MolarMass[Fluid]/1000)		#J/(kg*k)

	Density=Pressure/(Temperature*Rspecific)	#kg/m^3

	return Density




