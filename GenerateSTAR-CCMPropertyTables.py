###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


import numpy
import FluidProperties		#all this is used for is to know where to put the output files relative to.
from FluidProperties.REFPROP import CriticalTemperature,SmartDirname,EnthalpyFromTemperaturePressureREFPROPdirect,DensityFromTemperaturePressure,SpeedOfSoundFromTemperaturePressure,DynamicViscocityFromTemperatureDensity,ThermalConductivityFromTemperatureDensity
from os.path import isdir
from os import makedirs


#might want to re-look at the CycleCode's data table point distribution after doing this CFD grid dependency study








##################################################################
#choose a temperature and pressure range to run by uncommenting
##################################################################


#used for main CFD cases

#allows for 3 grid levels, but don't care about "nice" round numbers here.
#MinTemperature=CriticalTemperature+.1	#note, it seems to crash right on the critical point, so add .1K to the critical point to get a little bit away from there.
#MaxTemperature=500
#MaxTemperatureGridPoints=3001


#note, these values are tuned to make there be "nice" round pressure levels that should match closely to CFD simulation boundary conditions (at least for the fine grid)
#while providing 3 grid levels.
#MinPressure=4.4*10**6
#MaxPressure=26*10**6
#MaxPressureGridPoints=217

#AdditionalGridLevelText=''



##################################################################


#used for the low pressure high temperature CFD case

MinTemperature=600-10		#make it a little lower than the boundary condition since the boundary condition is a total temperature and also the solver will dip down a little more too while converging.
MaxTemperature=700+10
MaxTemperatureGridPoints=3001

MinPressure=1*10**6
MaxPressure=5*10**6
MaxPressureGridPoints=217

AdditionalGridLevelText='LowPressure'


##################################################################






#compute the point locations for each independent variable for the fine grid
Pressures=numpy.linspace(MinPressure,MaxPressure,MaxPressureGridPoints)
Temperatures=numpy.linspace(MinTemperature,MaxTemperature,MaxTemperatureGridPoints)




for GridLevel in range(3):
	#note, got a little differnet values (15th? decimal place) after re-running with this newly created script. don't think there anything wrong/changed with the code and think previously ran on the
	#"compressor" (opensuse) workstation to create those slightly different values. re-running on the same machine (laptop) seems to always reproduce the exact same data, so not sure why roundoff error is exactly
	#the same every time on the same machine but different on another. not sure if it is a difference in the operating system, CPU, compiler, or python distribution. would have thought that
	#roundoff error would be consistently random if it is going to be an issue.

	#generate the independent variables grid for the current grid level
	(PressuresGrid,TemperaturesGrid)=numpy.meshgrid(Pressures[::2**GridLevel],Temperatures[::2**GridLevel],indexing='ij')

	#compute the fluid properties for the grid
	EnthalpiesGrid=EnthalpyFromTemperaturePressureREFPROPdirect(TemperaturesGrid,PressuresGrid)
	DensitiesGrid=DensityFromTemperaturePressure(TemperaturesGrid,PressuresGrid)
	SpeedOfSoundsGrid=SpeedOfSoundFromTemperaturePressure(TemperaturesGrid,PressuresGrid)
	DynamicViscocitiesGrid=DynamicViscocityFromTemperatureDensity(TemperaturesGrid,DensitiesGrid)
	ThermalConductivitiesGrid=ThermalConductivityFromTemperatureDensity(TemperaturesGrid,DensitiesGrid)


	#flatten data

	#independent variables
	TemperatureData=TemperaturesGrid.flatten()
	PressureData=PressuresGrid.flatten()
	#dependent variables
	EnthalpyData=EnthalpiesGrid.flatten()
	DensityData=DensitiesGrid.flatten()
	SpeedOfSoundData=SpeedOfSoundsGrid.flatten()
	DynamicViscocityData=DynamicViscocitiesGrid.flatten()
	ThermalConductivityData=ThermalConductivitiesGrid.flatten()


	#export data to a csv file

	GridLevelText=AdditionalGridLevelText+2*str(GridLevel)

	#setup output directory
	SaveDirectory=SmartDirname(FluidProperties.__file__)+'/FluidPropertyTables/'+GridLevelText+'/'
	#check to see if the folder exists and if not, make it
	if not isdir(SaveDirectory):
		makedirs(SaveDirectory)

	#note, savetxt defaults to fmt='%.18e', not sure where the extra precision comes from???????????
	numpy.savetxt(SaveDirectory+GridLevelText+'-Enthalpy.csv', numpy.hstack((EnthalpyData[numpy.newaxis].T,TemperatureData[numpy.newaxis].T,PressureData[numpy.newaxis].T)), delimiter=',',comments='',header='Enthalpy,Temperature,Pressure')
	numpy.savetxt(SaveDirectory+GridLevelText+'-Density.csv', numpy.hstack((DensityData[numpy.newaxis].T,TemperatureData[numpy.newaxis].T,PressureData[numpy.newaxis].T)), delimiter=',',comments='',header='Density,Temperature,Pressure')
	numpy.savetxt(SaveDirectory+GridLevelText+'-SpeedOfSound.csv', numpy.hstack((SpeedOfSoundData[numpy.newaxis].T,TemperatureData[numpy.newaxis].T,PressureData[numpy.newaxis].T)), delimiter=',',comments='',header='SpeedOfSound,Temperature,Pressure')
	numpy.savetxt(SaveDirectory+GridLevelText+'-DynamicViscocity.csv', numpy.hstack((DynamicViscocityData[numpy.newaxis].T,TemperatureData[numpy.newaxis].T,PressureData[numpy.newaxis].T)), delimiter=',',comments='',header='DynamicViscocity,Temperature,Pressure')
	numpy.savetxt(SaveDirectory+GridLevelText+'-ThermalConductivity.csv', numpy.hstack((ThermalConductivityData[numpy.newaxis].T,TemperatureData[numpy.newaxis].T,PressureData[numpy.newaxis].T)), delimiter=',',comments='',header='ThermalConductivity,Temperature,Pressure')

	print "exported GridLevel "+GridLevelText+", "+str(PressuresGrid.size)+" grid points"









