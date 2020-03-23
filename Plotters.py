###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


#import some things
import matplotlib
matplotlib.use('Agg',warn=False)		#needed to allow for a non-x11 renderer to be used in batch mode.
import matplotlib.pyplot as plt			#although already imported matplotlib, do it again so pyplot can be accessed more briefly. this needs to be performed after matplotlib.use('Agg') for some reason
from matplotlib.ticker import MaxNLocator 
from mpl_toolkits.axes_grid1 import host_subplot
import cStringIO				#allows for sort of a virtual file that can be printed to?

import time					#used for timing how long things take
from helpers import RoundAndPadToString,Celsius,WriteBinaryData,nearestMultiple,FindSubString,CheckPercentage
from numpy import linspace,ceil,concatenate,clip,arange,array,floor,meshgrid,load	#may want to eliminate ceil and floor and replace their uses with the new nearestMultiple function?
from copy import copy
import math
from FluidProperties.REFPROP import *






def thousands(x, position):		#don't need position (so it is ignored in this function), but still passed to the function, so have to have it in there, otherwise will error out saying an extra variable was passed.
	#this function could may be eliminated by just doing FuncFormatter('{:,.0f}'.format), but keeping it here so know a way to do more complex things if want to later
	return '{:,.0f}'.format(float(x))		#don't know why float is needed because it works without it in regular python and ipython but not sage



#warning, this function was copied and pasted from PlotContoursPlottingFunctions.py. need to restructure files so it can be imported instead of copy/paste
def ComputeLevels(TheMatrix,NumberofLevels=101):
	#create levels since matplotlib doesn't seem to have an easy way to do it
	return linspace(TheMatrix.min(),TheMatrix.max(),NumberofLevels)



def PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='Enthalpy',HorizontalAxisMaxOverride=None,VerticalAxisMaxOverride=None,AdditionalAnnotations=True,LineColor='black',ImageFileType='png',TheFigure=None,ThePlot=None):
	tic=time.time()				#set a reference time for the start of the function for tracking CPU time of parts of the code


	#figure out if a constant volume cycle or not
	if not CycleParameters['HTRecuperator']['HighPressure']['ConstantVolume']:
		PowerExtractor='PowerTurbine'
	else:
		PowerExtractor='Piston'

	#define the max temperature (min temperature is defined in REFPROPWrappers)
	MaxTemperature=CycleParameters[PowerExtractor]['StartingProperties']['Temperature']+100
	#define the min and max entropy for ContourPlot1
	ContourPlot1EntropyMin=875
	ContourPlot1EntropyMax=3000

	MinDensity=0
	MaxDensity=1300


	#define the maximum pressure
	#round up to the next 5MPa interval above the maximum pressure (which is the main compressor compressed pressure or the constant volume heated pressure for the constant volume cycle), with 20MPa as a minimum, and then add 5MPa.
	MaxPressure=20e6
	if 'MainCompressor' in CycleParameters:		#this will fail if doing the constant volume cycle, so don't even try if there is no main compressor
		MaxPressure=max(MaxPressure,nearestMultiple(CycleParameters['MainCompressor']['CompressedProperties']['Pressure'],5e6,direction='up'))
	if 'SecondPlusThirdHeating' in CycleParameters:
		MaxPressure=max(MaxPressure,nearestMultiple(CycleParameters['SecondPlusThirdHeating']['HeatedProperties']['Pressure'],5e6,direction='up'))
	if 'CombinedFuelCellAndCombustor:' in CycleParameters:
		MaxPressure=max(MaxPressure,nearestMultiple(CycleParameters['CombinedFuelCellAndCombustor:']['HeatedProperties']['Pressure'],5e6,direction='up'))
	MaxPressure+=5e6


	if CycleParameters['Fluid']=='air':
		#if air, don't plot any levels or additional annoations (critical point, critical point label, or saturation line)
		#becuase they will be wrong since ChangeFluid doesn't work on the functions or static values used by those right now
#also don't plot state numbers and arrows and constant pressure lines, although may want to change this for the non-combined cycle individual simple cycle plot ?????????????
		ContourLevel=None
		AdditionalAnnotations=False
		EntropyOffset=-6000
	else:
		EntropyOffset=0

		#create some points for plotting critical temperature at various pressures
		CriticalTemperaturePressures1=linspace(1,CriticalPressure,101)			#don't set the minimum to 0 because it may give zero densities for some calculations.
		CriticalTemperaturePressures2=linspace(CriticalPressure,MaxPressure,101)
		CriticalTemperatures=linspace(CriticalTemperature,CriticalTemperature,101)

		#create some points for plotting critical pressure at various temperatures above the critical temperature
		CriticalPressureTemperatures=linspace(CriticalTemperature+.01,MaxTemperature,101)
		CriticalPressures=linspace(CriticalPressure,CriticalPressure,101)


		#initialize some values
		SupercriticalFluidLabelCoordinates=()
		LiquidLabelCoordinates=()
		GasLabelCoordinates=()
		VaporLabelCoordinates=()
		LiquidVaporLabelCoordinates=()


	#assign the horizontal axis values and set the limits of the axes and define the axis lables, etc.
	if HorizontalAxis=='Entropy':
		HorizontalAxisLabel='Entropy [J/(kg*K)]'
		HorizontalAxisName='Entropy'
		ArrowAngle='ArrowAngle'
		HorizontalAxisScaling=1.0

		if AdditionalAnnotations:
			CriticalPointHorizontal=(CriticalEntropy+EntropyOffset)*HorizontalAxisScaling
			CriticalTemperatureHorizontalAxisValues1=(EntropyFromTemperaturePressure(CriticalTemperatures+.01,CriticalTemperaturePressures1)+EntropyOffset)*HorizontalAxisScaling			#don't need to use REFPROPdirect here because the function is already direct and there is no data table created for this one.
			CriticalTemperatureHorizontalAxisValues2=(EntropyFromTemperaturePressure(CriticalTemperatures+.01,CriticalTemperaturePressures2)+EntropyOffset)*HorizontalAxisScaling			#don't need to use REFPROPdirect here because the function is already direct and there is no data table created for this one.

			CriticalPressureHorizontalAxisValues=(EntropyFromTemperaturePressure(CriticalPressureTemperatures,CriticalPressures)+EntropyOffset)*HorizontalAxisScaling				#don't need to use REFPROPdirect here because the function is already direct and there is no data table created for this one.

			SaturationLineHorizontalAxis=(SaturationLineEntropies+EntropyOffset)*HorizontalAxisScaling

			SupercriticalFluidLabelCoordinates+=((CriticalEntropy+EntropyOffset)*HorizontalAxisScaling,)
			LiquidLabelCoordinates+=((CriticalEntropy+EntropyOffset)*HorizontalAxisScaling,)
			GasLabelCoordinates+=((CriticalEntropy+EntropyOffset)*HorizontalAxisScaling,)
			VaporLabelCoordinates+=((CriticalEntropy+EntropyOffset)*HorizontalAxisScaling,)
			LiquidVaporLabelCoordinates+=((CriticalEntropy+EntropyOffset)*HorizontalAxisScaling,)

		#HorizontalAxisMin=SaturationLineEntropies.min()
		HorizontalAxisMin=(ContourPlot1EntropyMin)*HorizontalAxisScaling		#ContourPlot2 and the saturation line actually has a lower min entropy, but it looks stupid to show it because there is a blank area where ContourPlot1 doesn't have data
		HorizontalAxisMax=ceil((CycleParameters[PowerExtractor]['ExpandedProperties']['Entropy']+EntropyOffset)/1000)*1000

	elif (HorizontalAxis=='Density') and (VerticalAxis!='Density'):
		HorizontalAxisLabel=r'Density [kg/m$^3$]'
		HorizontalAxisName='Density'
		ArrowAngle='ArrowAngle'
		HorizontalAxisScaling=1.0

		if AdditionalAnnotations:
			CriticalPointHorizontal=CriticalDensity*HorizontalAxisScaling
			CriticalTemperatureHorizontalAxisValues1=DensityFromTemperaturePressure(CriticalTemperatures+.01,CriticalTemperaturePressures1)*HorizontalAxisScaling			#don't need to use REFPROPdirect here because the function is already direct and there is no data table created for this one.
			CriticalTemperatureHorizontalAxisValues2=DensityFromTemperaturePressure(CriticalTemperatures+.01,CriticalTemperaturePressures2)*HorizontalAxisScaling			#don't need to use REFPROPdirect here because the function is already direct and there is no data table created for this one.

			CriticalPressureHorizontalAxisValues=DensityFromTemperaturePressure(CriticalPressureTemperatures,CriticalPressures)*HorizontalAxisScaling				#don't need to use REFPROPdirect here because the function is already direct and there is no data table created for this one.

			SaturationLineHorizontalAxis=SaturationLineDensities*HorizontalAxisScaling

			SupercriticalFluidLabelCoordinates+=(CriticalDensity*HorizontalAxisScaling,)
			LiquidLabelCoordinates+=(CriticalDensity*HorizontalAxisScaling,)
			GasLabelCoordinates+=(CriticalDensity*HorizontalAxisScaling,)
			VaporLabelCoordinates+=(CriticalDensity*HorizontalAxisScaling,)
			LiquidVaporLabelCoordinates+=(CriticalDensity*HorizontalAxisScaling,)

		HorizontalAxisMin=MinDensity*HorizontalAxisScaling
		HorizontalAxisMax=MaxDensity*HorizontalAxisScaling

	elif (HorizontalAxis=='SpecificVolume') and (VerticalAxis!='SpecificVolume'):
		HorizontalAxisLabel=r'Specific Volume [L/kg]'
		HorizontalAxisName='SpecificVolume'
		ArrowAngle='ArrowAngle'
		HorizontalAxisScaling=1000.0

		if AdditionalAnnotations:
			CriticalPointHorizontal=(1/CriticalDensity)*HorizontalAxisScaling
			CriticalTemperatureHorizontalAxisValues1=(1/DensityFromTemperaturePressure(CriticalTemperatures+.01,CriticalTemperaturePressures1))*HorizontalAxisScaling			#don't need to use REFPROPdirect here because the function is already direct and there is no data table created for this one.
			CriticalTemperatureHorizontalAxisValues2=(1/DensityFromTemperaturePressure(CriticalTemperatures+.01,CriticalTemperaturePressures2))*HorizontalAxisScaling			#don't need to use REFPROPdirect here because the function is already direct and there is no data table created for this one.

			CriticalPressureHorizontalAxisValues=(1/DensityFromTemperaturePressure(CriticalPressureTemperatures,CriticalPressures))*HorizontalAxisScaling					#don't need to use REFPROPdirect here because the function is already direct and there is no data table created for this one.

			SaturationLineHorizontalAxis=(1/SaturationLineDensities)*HorizontalAxisScaling

			SupercriticalFluidLabelCoordinates+=(25,)
			LiquidLabelCoordinates+=(1/CriticalDensity,)
			GasLabelCoordinates+=(30,)
			VaporLabelCoordinates+=(30,)
			LiquidVaporLabelCoordinates+=(4.5,)

		HorizontalAxisMin=(1/MaxDensity)*HorizontalAxisScaling
		HorizontalAxisMax=0.04*HorizontalAxisScaling

	else:	#only other option right now is pressure
		HorizontalAxisLabel='Pressure [MPa]'
		HorizontalAxisName='Pressure'
		ArrowAngle='ArrowAngleTP'
		HorizontalAxisScaling=1.0/(10**6)

		if AdditionalAnnotations:
			CriticalPointHorizontal=CriticalPressure*HorizontalAxisScaling
			CriticalTemperatureHorizontalAxisValues1=CriticalTemperaturePressures1*HorizontalAxisScaling
			CriticalTemperatureHorizontalAxisValues2=CriticalTemperaturePressures2*HorizontalAxisScaling

			CriticalPressureHorizontalAxisValues=CriticalPressures*HorizontalAxisScaling

			#just using this same process for T-P diagram so don't have to deal with refprop returning two identical solutions at once, but there are still duplicate values in this result,
			#just organized differently. note, this may cause the line to appear unexpectedly if plotted vs temperature (but not enthalpy), especially if using dashed
			#lines because there will be two lines on top of each other.
			#also, if a more complex fluid is used, may actually have different temperatures at the beginning and end of the liquid vapour mixture, so it may
			#actually not have duplicates, but different values.

			SaturationLineHorizontalAxis=SaturationLinePressures*HorizontalAxisScaling

			SupercriticalFluidLabelCoordinates+=(20,)
			LiquidLabelCoordinates+=(22.5,)
			GasLabelCoordinates+=(2.5,)
			VaporLabelCoordinates+=(1.5,)
			LiquidVaporLabelCoordinates+=(4,)

		HorizontalAxisMin=0
		HorizontalAxisMax=MaxPressure*HorizontalAxisScaling

	#assign the vertical axis values and set the limits of the axes and define the axis lables, etc.
	if VerticalAxis=='Temperature':
		VerticalAxisLabel='Temperature [K]'
		VerticalAxisName='Temperature'					#used later when critical point and state points are plotted
		VerticalAxisScaling=1

		if AdditionalAnnotations:
			CriticalPointVertical=CriticalTemperature*VerticalAxisScaling	#used later when critical point and state points are plotted
			CriticalTemperatureVerticalAxisValues1=CriticalTemperatures*VerticalAxisScaling
			CriticalTemperatureVerticalAxisValues2=CriticalTemperatures*VerticalAxisScaling

			CriticalPressureVerticalAxisValues=CriticalPressureTemperatures*VerticalAxisScaling

			SaturationLineVerticalAxis=SaturationLineTemperatures*VerticalAxisScaling

			SupercriticalFluidLabelCoordinates+=(550,)
			LiquidLabelCoordinates+=(250,)
			GasLabelCoordinates+=(850,)
			VaporLabelCoordinates+=(275,)
			LiquidVaporLabelCoordinates+=(340,)

		VerticalAxisMin=MinTemperature*VerticalAxisScaling
		VerticalAxisMax=MaxTemperature*VerticalAxisScaling

		VerticalAxisMinC=Celsius(MinTemperature)*VerticalAxisScaling
		VerticalAxisMaxC=Celsius(MaxTemperature)*VerticalAxisScaling

	elif VerticalAxis=='Pressure':
		VerticalAxisLabel='Pressure [MPa]'
		VerticalAxisName='Pressure'					#used later when critical point and state points are plotted------not sure if this one is actually really used??????
		VerticalAxisScaling=1.0/(10**6)

		if AdditionalAnnotations:
			CriticalPointVertical=CriticalPressure*VerticalAxisScaling	#used later when critical point and state points are plotted------not sure if this one is actually really used??????
			CriticalTemperatureVerticalAxisValues1=CriticalTemperaturePressures1*VerticalAxisScaling
			CriticalTemperatureVerticalAxisValues2=CriticalTemperaturePressures2*VerticalAxisScaling

			CriticalPressureVerticalAxisValues=CriticalPressures*VerticalAxisScaling

			SaturationLineVerticalAxis=SaturationLinePressures*VerticalAxisScaling

			SupercriticalFluidLabelCoordinates+=(20,)
			LiquidLabelCoordinates+=(22.5,)
			GasLabelCoordinates+=(2.5,)
			VaporLabelCoordinates+=(1.5,)
			LiquidVaporLabelCoordinates+=(4,)

		VerticalAxisMin=0
		VerticalAxisMax=MaxPressure*VerticalAxisScaling

	else:	#only other option right now is enthalpy
		VerticalAxisLabel='Enthalpy [kJ/kg]'
		VerticalAxisName='Enthalpy'						#used later when critical point and state points are plotted
		VerticalAxisScaling=1.0/1000.0						#note, decimal point is needed becuase the result will come out to zero otherwise

		if AdditionalAnnotations:
			CriticalPointVertical=CriticalEnthalpy*VerticalAxisScaling		#used later when critical point and state points are plotted
			CriticalTemperatureVerticalAxisValues1=EnthalpyFromTemperaturePressureREFPROPdirect(CriticalTemperatures+.01,CriticalTemperaturePressures1)*VerticalAxisScaling		#note, this seems to crash right on the critical point, so add .01K to the critical point and then it works and noone is going to be able to see that anyway
			CriticalTemperatureVerticalAxisValues2=EnthalpyFromTemperaturePressureREFPROPdirect(CriticalTemperatures+.01,CriticalTemperaturePressures2)*VerticalAxisScaling		#note, this seems to crash right on the critical point, so add .01K to the critical point and then it works and noone is going to be able to see that anyway

			CriticalPressureVerticalAxisValues=EnthalpyFromTemperaturePressureREFPROPdirect(CriticalPressureTemperatures,CriticalPressures)*VerticalAxisScaling

			SaturationLineVerticalAxis=EnthalpyFromTemperatureEntropy(SaturationLineTemperatures,SaturationLineEntropies)*VerticalAxisScaling					#note, refprop saturation line function only returns temperature and pressure, so need to do it this way

			SupercriticalFluidLabelCoordinates+=(550,)
			LiquidLabelCoordinates+=(175,)
			GasLabelCoordinates+=(850,)
			VaporLabelCoordinates+=(460,)
			LiquidVaporLabelCoordinates+=(340,)

		VerticalAxisMin=None
		VerticalAxisMax=None



	#define functions for easy plotting of multiple components
#should this really be re-defined every time the function is called? if so, probably will have to define more variables explicitely??
#same with other functions?
	def PlotComponent(ThePlot,StartingProperties,ExitProperties,MassFraction=1,LineColor='black',FluidEndChoice='Exit',ComponentType=None):
		NumberOfPoints=50

		#remember the default fluid assigned to this plot (pretty sure copy is needed)
		OldFluidName=copy(FluidName)
		OldPercentExcessOxygen=copy(CurrentPercentExcessOxygen)

		#figure out which end the fluid type should be taken from
		#this is useful if have a component that has a different fluid at the inlet and outlet
		#such as a fuel cell+combustor
		#the function can be run twice and get a constant pressure line for each fluid
		#which is confusing because it has two lines, but at least better than having a gap,
		#at least for now until, some more advanced function is created that calculates species
		#concentrations of a reacting flow as it reacts, as a function of temperature and entropy.
		if FluidEndChoice=='Exit':
			NewFluidName=ExitProperties['FluidName']
			NewFluidPercentExcessOxygen=ExitProperties['PercentExcessOxygen']
		else:
			#anything else results in using the inlet
			NewFluidName=StartingProperties['FluidName']
			NewFluidPercentExcessOxygen=StartingProperties['PercentExcessOxygen']

		#temporarily change the fluid to the fluid of this component.
		SetupFluid(NewFluidName,PercentExcessOxygen=NewFluidPercentExcessOxygen)

		#recompute points since not too concerned about speed of plotting and all functions didn't always save the points or compute them at all
		Temperatures=linspace(StartingProperties['Temperature'],ExitProperties['Temperature'],NumberOfPoints)

		#figure out what kind of device it is and what relationship to use to compute the intermediate pressures
		if ComponentType=='TurbinePistonOrCompressor':
			#asssume temperature is linearly related to entropy. it may not be exactly, but it's pretty close, good enough for plotting purposes, especially since the turbomachinery has not been designed and polytropic effciencies are not in use.
			Entropies=linspace(StartingProperties['Entropy'],ExitProperties['Entropy'],NumberOfPoints)
			Pressures=PressureFromTemperatureEntropy(Temperatures,Entropies)

		else:
			#it's a heater or cooler of some kind

			if CheckPercentage(StartingProperties['Density'],ExitProperties['Density'],.01):			#allow a little error because of REFPROP doing weird stuff sometimes. probably should have saved in the component saying whether it was constant volume to avoid this uncertainty, but didn't, so just doing it this way for now.
				#constant volume heater
				Pressures=PressureFromTemperatureDensity(Temperatures,StartingProperties['Density'])		#as checked above, starting density is the same as the exit density

			else:
				#nearly constant pressure heater or cooler
				#linear relationship between temperature and pressure
				Pressures=linspace(StartingProperties['Pressure'],ExitProperties['Pressure'],NumberOfPoints)	#note, this only works because using DeltaPPerDeltaT to be constant for now

		if VerticalAxis=='Temperature':
			VerticalAxisValues=Temperatures*VerticalAxisScaling
		elif VerticalAxis=='Pressure':
			VerticalAxisValues=Pressures*VerticalAxisScaling
		else:	#only other option right now is enthalpy
			VerticalAxisValues=EnthalpyFromTemperaturePressure(Temperatures,Pressures)*VerticalAxisScaling

		#assign the horizontal axis values
		if HorizontalAxis=='Entropy':
			HorizontalAxisValues=(EntropyFromTemperaturePressure(Temperatures,Pressures)+EntropyOffset)*HorizontalAxisScaling
		elif (HorizontalAxis=='Density') and (VerticalAxis!='Density'):
			HorizontalAxisValues=DensityFromTemperaturePressure(Temperatures,Pressures)*HorizontalAxisScaling
		elif (HorizontalAxis=='SpecificVolume') and (VerticalAxis!='SpecificVolume'):
			HorizontalAxisValues=(1/DensityFromTemperaturePressure(Temperatures,Pressures))*HorizontalAxisScaling
		else:	#only other option right now is pressure
			HorizontalAxisValues=Pressures*HorizontalAxisScaling

		ThePlot.plot(HorizontalAxisValues,VerticalAxisValues,color=LineColor,linewidth=1.5*MassFraction)

		#plot a constant pressure line for both the high and low pressure, as a reference of the pressure drop
		if AdditionalAnnotations and (ComponentType!='TurbinePistonOrCompressor') and (HorizontalAxis!='Pressure') and (VerticalAxis!='Pressure'):		#only plot constant pressure lines if an axis is not pressure
			MeanTemperature=(StartingProperties['Temperature']+ExitProperties['Temperature'])/2
			StartingPressureTemperatures=linspace(StartingProperties['Temperature'],MeanTemperature,round(NumberOfPoints/2))
			ExitPressureTemperatures=linspace(MeanTemperature,ExitProperties['Temperature'],round(NumberOfPoints/2))

			if VerticalAxis=='Temperature':
				StartingPressureVerticalAxis=StartingPressureTemperatures*VerticalAxisScaling
				ExitPressureVerticalAxis=ExitPressureTemperatures*VerticalAxisScaling
			else:	#only other option right now is enthalpy
				StartingPressureVerticalAxis=EnthalpyFromTemperaturePressure(StartingPressureTemperatures,StartingProperties['Pressure'])*VerticalAxisScaling
				ExitPressureVerticalAxis=EnthalpyFromTemperaturePressure(ExitPressureTemperatures,ExitProperties['Pressure'])*VerticalAxisScaling

			#inlet temperature up to the MeanTemperature
			ThePlot.plot((EntropyFromTemperaturePressure(StartingPressureTemperatures,StartingProperties['Pressure'])+EntropyOffset)*HorizontalAxisScaling,StartingPressureVerticalAxis,linewidth=.25,label=RoundAndPadToString(StartingProperties['Pressure']/(10**6),2)+'MPa')
			#MeanTemperature up to the exit
			ThePlot.plot((EntropyFromTemperaturePressure(ExitPressureTemperatures,ExitProperties['Pressure'])+EntropyOffset)*HorizontalAxisScaling,ExitPressureVerticalAxis,linewidth=.25,label=RoundAndPadToString(ExitProperties['Pressure']/(10**6),2)+'MPa')

		#change back to the default fluid for this plot
		SetupFluid(OldFluidName,PercentExcessOxygen=OldPercentExcessOxygen)




	#setup the figure object if it is not passed
	if TheFigure==None:
		TheFigure=plt.figure()
	#setup the plot object if it is not passed (should always be when the figure object is also not passed, for now)
	#basically takes the settings below for the first call with ThePlot==None, but they can be overridden manually later if needed.
	if ThePlot==None:
		#do this instead of ThePlot=TheFigure.add_subplot(111) because otherwise, grid lines for the second axis vertical axis (if it exists) will be draw on top of things (critical point text box and legend) from the first axis.
		#for some reason this way the second vertical axis grid lines still are on top of the plotted lines, but that doesn't look too bad, so not worring about it, and actually, it looks like all
		#grid lines (regardless of if there is a secondary vertical axis) are that way because they wouldn't ever show up for contour plots and other things that are solid. so, it looks like the drawing order is lines, gridlines, and then annotations.
		#note, host_subplot doesn't allow using a specific figure object, it just uses the current figure, which in this case it should be TheFigure since it was the last one just created
		#host_subplot doesn't have very good documentation so needed to look at the source code of it to learn that it used the current figure.
		#may want to look into using host_subplot for the heat exchanger plotting to make that simpler, but it is working for now, so just leaving it as is.
		ThePlot=host_subplot(111)

		PlotTitleTEXT='Cycle Thermal Efficiency: '+RoundAndPadToString(CycleParameters['CycleRealEfficiency']*100,2)+'%, Cycle Exergy Efficiency: '+RoundAndPadToString(CycleParameters['CycleExergyEfficiency']*100,2)+'%'
		if 'CombinedFuelCellAndCombustor' in CycleParameters:
			#show HHV and LHV efficiencies
			PlotTitleTEXT+=' (HHV),   '+RoundAndPadToString(CycleParameters['CycleRealEfficiency']*100*MethaneHHVoverLHV,2)+'% (LHV)'
		elif CycleParameters['Fluid']=='CO2':
			PlotTitleTEXT+='\nLine widths scaled by mass fraction.'

		TheFigure.suptitle(PlotTitleTEXT,fontsize=12)

		#set format the axes labels
		ThePlot.xaxis.set_major_formatter(plt.FuncFormatter(thousands))
		ThePlot.yaxis.set_major_formatter(plt.FuncFormatter(thousands))

		#and set the axis limits if don't want to keep the default auto ranging
		if HorizontalAxisMaxOverride is not None:
			HorizontalAxisMax=HorizontalAxisMaxOverride
		if VerticalAxisMaxOverride is not None:
			VerticalAxisMax=VerticalAxisMaxOverride

		if (HorizontalAxisMin is not None) and (HorizontalAxisMax is not None):
			ThePlot.set_xlim(left=HorizontalAxisMin,right=HorizontalAxisMax)
		if (VerticalAxisMin is not None) and (VerticalAxisMax is not None):
			ThePlot.set_ylim(bottom=VerticalAxisMin,top=VerticalAxisMax)

		#add a second scale that has Celsius if vertical axis is temperature
		if VerticalAxis=='Temperature':
			if VerticalAxisMaxOverride is not None:
				VerticalAxisMaxC=Celsius(VerticalAxisMaxOverride)		#assumes VerticalAxisScaling=1
			ThePlot_SecondVerticalAxis=ThePlot.twinx()
			ThePlot_SecondVerticalAxis.set_ylabel('Temperature [C]')
			ThePlot_SecondVerticalAxis.set_ylim(VerticalAxisMinC,VerticalAxisMaxC)
			ThePlot_SecondVerticalAxis.yaxis.set_major_locator(MaxNLocator(10))
			#and add gridlines
			ThePlot_SecondVerticalAxis.grid(True)
		else:
			#use gridlines matching the left vertical axis only if not doing the celsiuis scale on the right vertical axis
			ThePlot.grid(True)

		#label the plot
		ThePlot.set_xlabel(HorizontalAxisLabel)
		ThePlot.set_ylabel(VerticalAxisLabel)

		#make the margins smaller
		if ContourLevel!=None:
			TheFigure.subplots_adjust(left=.1,right=.97)
		else:
			#although tighter margins look nicer, seems to require different values for contour level and haven't had time to figure out what is best without contour level.
			pass

	else:
		#force to False if the plot object is passed because there is no reason to re draw annotations a second time
		AdditionalAnnotations=False






	#create the curves to be plotted and add to the plot

#may be able to remove the not CycleParameters['HTRecuperator']['HighPressure']['ConstantVolume'] part of the if statements because the other test probably works for both simple cycle and constant volume

	if not CycleParameters['HTRecuperator']['HighPressure']['ConstantVolume'] and 'MainFractionCooler' in CycleParameters:		#don't plot if constant volume or simple cycle
		PlotComponent(ThePlot,CycleParameters['MainFractionCooler']['StartingProperties'],CycleParameters['MainFractionCooler']['CooledProperties'],MassFraction=CycleParameters['MainFractionCooler']['MassFraction'],LineColor=LineColor)

	if 'MainCompressor' in CycleParameters:
		PlotComponent(ThePlot,CycleParameters['MainCompressor']['StartingProperties'],CycleParameters['MainCompressor']['CompressedProperties'],MassFraction=CycleParameters['MainCompressor']['MassFraction'],ComponentType='TurbinePistonOrCompressor',LineColor=LineColor)

	if not CycleParameters['HTRecuperator']['HighPressure']['ConstantVolume'] and 'FirstHPHeating' in CycleParameters:		#don't plot if constant volume or simple cycle
		PlotComponent(ThePlot,CycleParameters['FirstHPHeating']['StartingProperties'],CycleParameters['FirstHPHeating']['HeatedProperties'],MassFraction=CycleParameters['FirstHPHeating']['MassFraction'],LineColor=LineColor)

	if 'SecondPlusThirdHeating' in CycleParameters:
		PlotComponent(ThePlot,CycleParameters['SecondPlusThirdHeating']['StartingProperties'],CycleParameters['SecondPlusThirdHeating']['HeatedProperties'],MassFraction=CycleParameters['SecondPlusThirdHeating']['MassFraction'],LineColor=LineColor)

	if 'CombinedFuelCellAndCombustor' in CycleParameters:
		PlotComponent(ThePlot,CycleParameters['CombinedFuelCellAndCombustor']['StartingProperties']['Air'],CycleParameters['CombinedFuelCellAndCombustor']['HeatedProperties'],MassFraction=CycleParameters['CombinedFuelCellAndCombustor']['MassFraction'],LineColor=LineColor)
		PlotComponent(ThePlot,CycleParameters['CombinedFuelCellAndCombustor']['StartingProperties']['Air'],CycleParameters['CombinedFuelCellAndCombustor']['HeatedProperties'],MassFraction=CycleParameters['CombinedFuelCellAndCombustor']['MassFraction'],LineColor=LineColor,FluidEndChoice='Inlet')

	if not CycleParameters['HTRecuperator']['HighPressure']['ConstantVolume'] and 'VirtualTurbine' in CycleParameters:		#don't plot if constant volume or simple cycle
		PlotComponent(ThePlot,CycleParameters['VirtualTurbine']['StartingProperties'],CycleParameters['VirtualTurbine']['ExpandedProperties'],MassFraction=CycleParameters['VirtualTurbine']['MassFraction'],ComponentType='TurbinePistonOrCompressor',LineColor=LineColor)
		if 'ReHeat' in CycleParameters:
			for CurrentReHeat in CycleParameters['ReHeat']['Stages']:
				PlotComponent(ThePlot,CurrentReHeat['StartingProperties'],CurrentReHeat['HeatedProperties'],MassFraction=CurrentReHeat['MassFraction'],LineColor=LineColor)

	if 'Stages' in CycleParameters[PowerExtractor]:
		for CurrentPowerExtractorStage in CycleParameters[PowerExtractor]['Stages']:
			PlotComponent(ThePlot,CurrentPowerExtractorStage['StartingProperties'],CurrentPowerExtractorStage['ExpandedProperties'],MassFraction=CurrentPowerExtractorStage['MassFraction'],ComponentType='TurbinePistonOrCompressor',LineColor=LineColor)
	else:		#constant volume or simple cycle
		PlotComponent(ThePlot,CycleParameters[PowerExtractor]['StartingProperties'],CycleParameters[PowerExtractor]['ExpandedProperties'],MassFraction=CycleParameters[PowerExtractor]['MassFraction'],ComponentType='TurbinePistonOrCompressor',LineColor=LineColor)


#	if 'TotalFractionCooler' in CycleParameters:		#don't plot if simple cycle
#not sure why the abov test was there? simple cycle should have the total fraction cooler???????
	if True:
		PlotComponent(ThePlot,CycleParameters['TotalFractionCooler']['StartingProperties'],CycleParameters['TotalFractionCooler']['CooledProperties'],MassFraction=CycleParameters['TotalFractionCooler']['MassFraction'],LineColor=LineColor)



	if not CycleParameters['HTRecuperator']['HighPressure']['ConstantVolume'] and 'PreCompressor' in CycleParameters:		#don't plot if constant volume or simple cycle
		PlotComponent(ThePlot,CycleParameters['PreCompressor']['StartingProperties'],CycleParameters['PreCompressor']['CompressedProperties'],MassFraction=CycleParameters['PreCompressor']['MassFraction'],ComponentType='TurbinePistonOrCompressor',LineColor=LineColor)
		PlotComponent(ThePlot,CycleParameters['ReCompressor']['StartingProperties'],CycleParameters['ReCompressor']['CompressedProperties'],MassFraction=CycleParameters['ReCompressor']['MassFraction'],ComponentType='TurbinePistonOrCompressor',LineColor=LineColor)





	#now make a contour plot
	if ContourLevel!=None:
		#first patch
		#setup the data for the bottom based on an entropy and temperature range
		ContourPlot1Entropies=linspace(ContourPlot1EntropyMin,ContourPlot1EntropyMax,100)
		ContourPlot1Temperatures=linspace(MinTemperature,CriticalTemperature,100)		#go up to the critical temperature because that is about where the next case starts to have problems
		(ContourPlot1EntropiesGrid,ContourPlot1TemperaturesGrid)=meshgrid(ContourPlot1Entropies,ContourPlot1Temperatures,indexing='ij')


		#second patch
		#setup the data for the rest of the plot based on a temperature and pressure range
		ContourPlot2Pressures=concatenate((linspace(PressureFromTemperatureEntropy(CriticalTemperature,ContourPlot1EntropyMax),12*10**6,50),linspace(12*10**6,250*10**6,50)[1:]))		#concatenate is used to cluster crudely points better around critical region
		ContourPlot2Temperatures=concatenate((linspace(CriticalTemperature,400,50),linspace(400,MaxTemperature,50)[1:]))	#concatenate is used to cluster crudely points better around critical region
		(ContourPlot2PressuresGrid,ContourPlot2TemperaturesGrid)=meshgrid(ContourPlot2Pressures,ContourPlot2Temperatures,indexing='ij')


		#both patches
		#save some processing time if value isn't actually used(since recalculating everything on the fly right now)
		if (HorizontalAxis=='Pressure') or (ContourLevel=='Pressure') or (VerticalAxis=='Pressure'):
			ContourPlot1PressuresGrid=PressureFromTemperatureEntropy(ContourPlot1TemperaturesGrid,ContourPlot1EntropiesGrid)
		if (HorizontalAxis=='Entropy') or (ContourLevel=='Entropy'):
			ContourPlot2EntropiesGrid=EntropyFromTemperaturePressure(ContourPlot2TemperaturesGrid,ContourPlot2PressuresGrid)
		if (VerticalAxis=='Enthalpy') or (ContourLevel=='Enthalpy'):
			ContourPlot1EnthalpiesGrid=EnthalpyFromTemperatureEntropy(ContourPlot1TemperaturesGrid,ContourPlot1EntropiesGrid)
			ContourPlot2EnthalpiesGrid=EnthalpyFromTemperaturePressureREFPROPdirect(ContourPlot2TemperaturesGrid,ContourPlot2PressuresGrid)
		if (ContourLevel=='Density') or (HorizontalAxis=='Density') or (HorizontalAxis=='SpecificVolume') or (ContourLevel=='CompressibilityFactor'):
			ContourPlot1DensitiesGrid=DensityFromTemperatureEntropy(ContourPlot1TemperaturesGrid,ContourPlot1EntropiesGrid)			#note, even though x and y are swapped here, it doesn't really matter because the shape of x and y axis variables is really what matters
			ContourPlot2DensitiesGrid=DensityFromTemperaturePressure(ContourPlot2TemperaturesGrid,ContourPlot2PressuresGrid)

		#assign the vertical axis values
		if VerticalAxis=='Temperature':
			ContourPlot1VerticalAxisGrid=ContourPlot1TemperaturesGrid*VerticalAxisScaling
			ContourPlot2VerticalAxisGrid=ContourPlot2TemperaturesGrid*VerticalAxisScaling
		elif VerticalAxis=='Pressure':
			ContourPlot1VerticalAxisGrid=ContourPlot1PressuresGrid*VerticalAxisScaling
			ContourPlot2VerticalAxisGrid=ContourPlot2PressuresGrid*VerticalAxisScaling
		else:	#only other option right now is enthalpy
			ContourPlot1VerticalAxisGrid=ContourPlot1EnthalpiesGrid*VerticalAxisScaling
			ContourPlot2VerticalAxisGrid=ContourPlot2EnthalpiesGrid*VerticalAxisScaling

		#assign the horizontal axis values
		if HorizontalAxis=='Entropy':
			ContourPlot1HorizontalAxisGrid=(ContourPlot1EntropiesGrid+EntropyOffset)*HorizontalAxisScaling
			ContourPlot2HorizontalAxisGrid=(ContourPlot2EntropiesGrid+EntropyOffset)*HorizontalAxisScaling
		elif (HorizontalAxis=='Density') and (VerticalAxis!='Density'):
			ContourPlot1HorizontalAxisGrid=ContourPlot1DensitiesGrid*HorizontalAxisScaling
			ContourPlot2HorizontalAxisGrid=ContourPlot2DensitiesGrid*HorizontalAxisScaling
		elif (HorizontalAxis=='SpecificVolume') and (VerticalAxis!='SpecificVolume'):
			ContourPlot1HorizontalAxisGrid=1/ContourPlot1DensitiesGrid*HorizontalAxisScaling
			ContourPlot2HorizontalAxisGrid=1/ContourPlot2DensitiesGrid*HorizontalAxisScaling
		else:	#only other option right now is pressure
			ContourPlot1HorizontalAxisGrid=ContourPlot1PressuresGrid*HorizontalAxisScaling
			ContourPlot2HorizontalAxisGrid=ContourPlot2PressuresGrid*HorizontalAxisScaling

#		import ipdb; ipdb.set_trace()

		#calculate level values if not done so already and assign level colorbar tick mark values and range
		#hardcode a colorbar range range because the actual range is sometimes really large and not very meaningful to look at.
		#also, note, the number of values here use used to set the number of ticks in the colorbar and ComputeLevels function later actually
		#causes a lot more levels in the contour plot to be used by default
		if ContourLevel=='Temperature':
			ContourLevelLabel='Temperature [K]'
			ContourPlot1LevelsGrid=ContourPlot1TemperaturesGrid
			ContourPlot2LevelsGrid=ContourPlot2TemperaturesGrid
			ContourPlotColorLabels=linspace(min(ContourPlot1LevelsGrid.min(),ContourPlot2LevelsGrid.min()),max(ContourPlot1LevelsGrid.max(),ContourPlot2LevelsGrid.max()),11)
			ContourPlotLevelLines=[]
		elif ContourLevel=='Pressure':
			ContourLevelLabel='Pressure [MPa]'
			ContourPlot1LevelsGrid=ContourPlot1PressuresGrid/(10**6)
			ContourPlot2LevelsGrid=ContourPlot2PressuresGrid/(10**6)
			ContourPlotColorLabels=linspace(min(ContourPlot1LevelsGrid.min(),ContourPlot2LevelsGrid.min()),max(ContourPlot1LevelsGrid.max(),ContourPlot2LevelsGrid.max()),11)
			ContourPlotLevelLines=[]
		elif ContourLevel=='Enthalpy':
			ContourLevelLabel='Enthalpy [kJ/kg]'
			ContourPlot1LevelsGrid=ContourPlot1EnthalpiesGrid/1000
			ContourPlot2LevelsGrid=ContourPlot2EnthalpiesGrid/1000
			ContourPlotColorLabels=linspace(min(ContourPlot1LevelsGrid.min(),ContourPlot2LevelsGrid.min()),max(ContourPlot1LevelsGrid.max(),ContourPlot2LevelsGrid.max()),11)
			ContourPlotLevelLines=[]
		elif ContourLevel=='Entropy':
			ContourLevelLabel='Entropy [J/(kg*K)]'
			ContourPlot1LevelsGrid=ContourPlot1EntropiesGrid
			ContourPlot2LevelsGrid=ContourPlot2EntropiesGrid
			ContourPlotColorLabels=linspace(ContourPlot1LevelsGrid.min(),3000,11)
			ContourPlotLevelLines=[]
		elif ContourLevel=='Density':
			ContourLevelLabel=r'Density [kg/m$^3$]'
			ContourPlot1LevelsGrid=ContourPlot1DensitiesGrid
			ContourPlot2LevelsGrid=ContourPlot2DensitiesGrid
			ContourPlotColorLabels=arange(MinDensity,MaxDensity+100,100)
			ContourPlotLevelLines=[25,50,300,700,1000]
		elif ContourLevel=='CompressibilityFactor':
			ContourLevelLabel='Compressibility Factor, Z'
			ContourPlot1LevelsGrid=CompressiblityFactorFromTemperatureDensity(ContourPlot1TemperaturesGrid,ContourPlot1DensitiesGrid)
			ContourPlot2LevelsGrid=CompressiblityFactorFromTemperatureDensity(ContourPlot2TemperaturesGrid,ContourPlot2DensitiesGrid)
			ContourPlotColorLabels=linspace(0,2,11)
			ContourPlotLevelLines=[0.8,1.0,1.2]
		elif ContourLevel=='cp':
			ContourLevelLabel=r'$c_p$, Specific Heat at Constant Pressure [J/(kg*K)]'
			ContourPlot1LevelsGrid=cpFromTemperatureEntropy(ContourPlot1TemperaturesGrid,ContourPlot1EntropiesGrid)
			ContourPlot2LevelsGrid=cpFromTemperaturePressureREFPROPdirect(ContourPlot2TemperaturesGrid,ContourPlot2PressuresGrid)
			ContourPlotColorLabels=ContourPlotRange=linspace(800,5000,11)
			#ContourPlotLevelLines=arange(500,2500,500)
			ContourPlotLevelLines=[]
		elif ContourLevel=='gamma':
			ContourLevelLabel=r'$\gamma,$ $c_p/c_v$'
			ContourPlot1LevelsGrid=gammaFromTemperatureEntropy(ContourPlot1TemperaturesGrid,ContourPlot1EntropiesGrid)
			ContourPlot2LevelsGrid=gammaFromTemperaturePressure(ContourPlot2TemperaturesGrid,ContourPlot2PressuresGrid)
			ContourPlotColorLabels=ContourPlotRange=linspace(min(ContourPlot1LevelsGrid.min(),ContourPlot2LevelsGrid.min()),4,11)
			ContourPlotLevelLines=[1.1,1.2,1.225,1.25,1.3,1.4,1.5]


	#save a couple ranges for now until positive didn't actually need them
	#	ContourPlotRange=linspace(min(ContourPlot1EntropiesGrid.min(),ContourPlot2EntropiesGrid.min()),max(ContourPlot1EntropiesGrid.max(),ContourPlot2EntropiesGrid.max()),11)
	#	ContourPlotRange=linspace(750,4300,11)


		#note, looks like don't actually need to transpose data when sending it to contour function (as did in PlotContoursPlottingFunctions.py) unless the x and y values are 1-D instead of 2-D
		#because the results look fine. as long as the shape matches, then it must really not actually matter.
		TheContourPlot1=ThePlot.contourf(ContourPlot1HorizontalAxisGrid,ContourPlot1VerticalAxisGrid,clip(ContourPlot1LevelsGrid,ContourPlotColorLabels.min(),ContourPlotColorLabels.max()),ComputeLevels(ContourPlotColorLabels))
		TheContourPlot2=ThePlot.contourf(ContourPlot2HorizontalAxisGrid,ContourPlot2VerticalAxisGrid,clip(ContourPlot2LevelsGrid,ContourPlotColorLabels.min(),ContourPlotColorLabels.max()),ComputeLevels(ContourPlotColorLabels))

		#if a set of specific contour lines has been defined, plot them too.
		if ContourPlotLevelLines!=[]:
			TheContourPlot1b=ThePlot.contour(ContourPlot1HorizontalAxisGrid,ContourPlot1VerticalAxisGrid,ContourPlot1LevelsGrid,ContourPlotLevelLines,colors='black')
			plt.clabel(TheContourPlot1b, fontsize=9, inline=1)		#add a level lable on the contour lines
			TheContourPlot2b=ThePlot.contour(ContourPlot2HorizontalAxisGrid,ContourPlot2VerticalAxisGrid,ContourPlot2LevelsGrid,ContourPlotLevelLines,colors='black')
			plt.clabel(TheContourPlot2b, fontsize=9, inline=1)		#add a level lable on the contour lines

		#make room for the contour level AND the second vertical axis
		if VerticalAxis=='Temperature':
			pad=0.12
		else:
			pad=0.05

		#don't know what object to call this specifically from. just passing TheContourPlot2 since assigning the same levels to both plots
		if abs(ContourPlotColorLabels[0]-ContourPlotColorLabels[1])>=1:		#decimal places aren't needed if the tick spacing is greater than or equal to 1, and commas should be added as a thousands separator
			#add the FuncFormatter here because TheColorBar.ax.yaxis.set_major_formatter(plt.FuncFormatter(thousands)) doesn't work for some reason
			TheColorBar=plt.colorbar(TheContourPlot2,format=plt.FuncFormatter(thousands),pad=pad)
		else:	#otherwise, use the default formatting (whatever that is)
			TheColorBar=plt.colorbar(TheContourPlot2,pad=pad)
		TheColorBar.set_ticks(ContourPlotColorLabels)
		TheColorBar.set_label(ContourLevelLabel,fontsize=12)






	#now do some additional plotting and annotations.

	if AdditionalAnnotations:
#note, above AdditionalAnnotations is set to False for AIR to force these not being displayed since they aren't calculated properly for air right now.
		#now plot the saturation line
		ThePlot.plot(SaturationLineHorizontalAxis,SaturationLineVerticalAxis,color='black',linestyle='--',dashes=(2,2))

		#plot the critical point. for some reason this has to be after contour plotting to show up.
		ThePlot.scatter(CriticalPointHorizontal,CriticalPointVertical,marker='x',color='black',s=15)

	ArrowLength=30		#points?

	#now plot the state points
	#but first adjust the horizontal axis if it is entropy and there was an offset defined.
	#may not be the most consistent way to do offsets based on the way entropy offsets are done in the rest of the code, but okay for now
	if HorizontalAxis=='Entropy':
		HorizontalAxisOffset=EntropyOffset
	else:
		HorizontalAxisOffset=0
#can scatter plot be moved up or down and consolidate the if statement or was there some reason for the order because of something being written over top of?
	ThePlot.scatter((CycleParameters['States'][HorizontalAxisName]+HorizontalAxisOffset)*HorizontalAxisScaling,CycleParameters['States'][VerticalAxisName]*VerticalAxisScaling,marker='o',s=8)	#using "marker='o',s=8" instead of "marker='.'" as a temporary workaround because current version of matplotlib on local worstation (not sage, not the actual server) is too old to support it. also just not caring about the blue center to the circle.
	if AdditionalAnnotations:
		for label, angle, x, y in zip(CycleParameters['States']['StateNumber'],CycleParameters['States'][ArrowAngle],(CycleParameters['States'][HorizontalAxisName]+HorizontalAxisOffset)*HorizontalAxisScaling,CycleParameters['States'][VerticalAxisName]*VerticalAxisScaling):
			ThePlot.annotate(label,xy = (x, y), xytext = (ArrowLength*math.cos(angle), ArrowLength*math.sin(angle)),textcoords = 'offset points',size=8, ha = 'center', va = 'center', arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))	#note, couldn't figure out how to reduce the gab between the arrow tail and the lable text

		#now draw some annotations that are specific to each type of plot.
		if HorizontalAxis=='Entropy':

			#also add a legend if constant pressure lines were plotted, which is only done if entropy is the horizontal axis
			TheLegend=ThePlot.legend(loc=2,prop={'size':8},title='Constant\nPressure\nLines')
			TheLegend.get_title().set_fontsize('8')		#can't seem to find a parameter to set the legend title font size in the original legend creation

			if ContourLevel!=None:		#don't display the critical point if no contour level background because it's probably supposed to be a clean looking plot and critical point is labeled on so many others and it also is less interesting to see without the contour level background anyway.
				#make the dialog box that displays the critical temperature and pressure.
				#note, not doing this for other horizontal axes because those plots are more cluttered and because people can always look at this one instead and
				#because T-P plot for example has the information very obvious in the plot itself.
				if VerticalAxis=='Temperature':
					CriticalPointTextBoxVerticalPosition=135
				elif VerticalAxis=='Pressure':
					CriticalPointTextBoxVerticalPosition=135
				else:	#only other option right now is enthalpy
					CriticalPointTextBoxVerticalPosition=100

				#lable the critical point for case where entropy is on the horizontal axis
				ThePlot.annotate('Critical Temperature: '+RoundAndPadToString(CriticalTemperature,2)+'K\nCritical Pressure: '+RoundAndPadToString(CriticalPressure/(10**6))+'MPa',
							xy = (CriticalPointHorizontal, CriticalPointVertical), 
							xytext = (-20, CriticalPointTextBoxVerticalPosition),
							textcoords = 'offset points',
							size=8,
							ha = 'center',
							va = 'center',
							arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=.3'),
							bbox = dict(boxstyle = 'square,pad=0.5', fc = 'white', alpha = 1.0),				#see http://matplotlib.org/api/patches_api.html#matplotlib.patches.Rectangle for bbox dict options
						)

		else:

			#not consolidating the following above with the plotting of the saturation line because don't want to clutter the plot any more when entropy is the horizontal axis.

			#plot the distinction between gas and supercritical fluid (the critical pressure line, above the critical temperature). is this correct for the enthalpy case? yes, it is.
			ThePlot.plot(CriticalPressureHorizontalAxisValues,CriticalPressureVerticalAxisValues,color='black',linestyle='--',dashes=(2,2))

			#plot the distinction between vapour and gas (the critical temperature below the critical pressure)
			ThePlot.plot(CriticalTemperatureHorizontalAxisValues1,CriticalTemperatureVerticalAxisValues1,color='gray',linestyle='--',dashes=(2,2))

			#plot the distinction between liquid and supercritical fluid (the critical temperature above the critical pressure)
			ThePlot.plot(CriticalTemperatureHorizontalAxisValues2,CriticalTemperatureVerticalAxisValues2,color='black',linestyle='--',dashes=(2,2))

			#plot the supercritical fluid boundaries and lable the regions for the case when pressure is on the horizontal axis
			ThePlot.annotate('Supercritical Fluid',		xy=SupercriticalFluidLabelCoordinates,		ha = 'center', va = 'center')
			ThePlot.annotate('Liquid',			xy=LiquidLabelCoordinates,			ha = 'center', va = 'center')
			ThePlot.annotate('Gas',				xy=GasLabelCoordinates,				ha = 'center', va = 'center')
			ThePlot.annotate('Vapor',			xy=VaporLabelCoordinates,			ha = 'center', va = 'center', size=8)		

			if VerticalAxis=='Temperature':
				#Liquid+Vapor region is collapsed on this plot, so can't annotate it
				pass

			else:	#all(?) other will have the Liquid+Vapor region visible
				ThePlot.annotate('Liquid+Vapor',	xy=LiquidVaporLabelCoordinates,			ha = 'center', va = 'center', size=8)


	if ImageFileType=='object':
		return TheFigure,ThePlot
	else:
		#save the image
		image_data = cStringIO.StringIO()					#setup the file handle
		TheFigure.savefig(image_data,format=ImageFileType)			#make the image file

		plt.close('all')							#releases all the RAM that is never released automatically

		return image_data.getvalue()

















def PlotHeatExchanger(Recuperator,RecuperatorInputParameters,ImageFileType='png',DeltaTVerticalAxisMax=None,cpRatioAxisMax=None):

	if DeltaTVerticalAxisMax is None:
		DeltaTVerticalAxisMax=nearestMultiple(Recuperator['ActualDeltaTs'].max(),10,direction='up')
	if cpRatioAxisMax is None:
		cpRatioAxisMax=nearestMultiple(Recuperator['ActualSpecificHeatRatios'].max(),1,direction='up')

	#first setup the plot title as a variable since it is so long
	PlotTitle=(
		'Cooled Side Inlet: Temperature='+RoundAndPadToString(Recuperator['LowPressure']['ActualStartingProperties']['Temperature'],1)+'K, Pressure='+RoundAndPadToString(Recuperator['LowPressure']['ActualStartingProperties']['Pressure']/10**6,1)+'MPa, Mass Fraction='+RoundAndPadToString(RecuperatorInputParameters['LowPressure']['MassFraction'],2)+'\n'
		+'Heated Side Inlet: Temperature='+RoundAndPadToString(Recuperator['HighPressure']['ActualStartingProperties']['Temperature'],1)+'K, Pressure='+RoundAndPadToString(Recuperator['HighPressure']['ActualStartingProperties']['Pressure']/10**6,1)+'MPa, Mass Fraction='+RoundAndPadToString(RecuperatorInputParameters['HighPressure']['MassFraction'],4)+'\n'
		+r'$\Delta T_{min}$='+RoundAndPadToString(RecuperatorInputParameters['MinimumDeltaT'],1)+' K'
		+', Pressure Drop='+RoundAndPadToString(RecuperatorInputParameters['DeltaPPerDeltaT'],0)+' Pa/K'
		+', Inlet Pressure Ratio='+RoundAndPadToString(Recuperator['HighPressure']['ActualStartingProperties']['Pressure']/Recuperator['LowPressure']['ActualStartingProperties']['Pressure'],1)
		+r', $\phi$='+RoundAndPadToString(Recuperator['phi'],2)
		+r', $\varepsilon$='+RoundAndPadToString(Recuperator['Effectiveness'],2)
		)

	#setup the figure with two subfigures side by side
	TheFigure,(Plot1,Plot2)=plt.subplots(nrows=1, ncols=2,figsize=(14,8))
	TheFigure.subplots_adjust(left=.075,right=.93)	#adust the spacing
	TheFigure.suptitle(PlotTitle,fontsize=12)

	#only show about 20 markers on the plots because if there are too many data points then the lines aren't distinguishable
	#all lines have the same number of data points, so assign this variable for shorter plot calls
	markevery=len(Recuperator['LowPressure']['ActualTemperatures'])/20


	#left figure

	#plot the specific heats
	Plot1.plot(Recuperator['LowPressure']['ActualTemperatures'],Recuperator['LowPressure']['ActualSpecificHeats'],marker='o',markersize=4,markevery=markevery,linestyle='-',color='black',label=r'$c_{p,Cooled}$')
	Plot1.plot(Recuperator['LowPressure']['ActualTemperatures'],Recuperator['HighPressure']['ActualSpecificHeats'],marker='o',markersize=4,markevery=markevery,linestyle='-',color='green',label=r'$c_{p,Heated}$')
	Plot1.plot(Recuperator['LowPressure']['ActualTemperatures'],Recuperator['LowPressure']['ActualSpecificHeats']*RecuperatorInputParameters['LowPressure']['MassFraction'],marker='x',markersize=8,markevery=markevery,linestyle='-',color='black',label=r'$C_{Cooled}$')
	Plot1.plot(Recuperator['LowPressure']['ActualTemperatures'],Recuperator['HighPressure']['ActualSpecificHeats']*RecuperatorInputParameters['HighPressure']['MassFraction'],marker='x',markersize=8,markevery=markevery,linestyle='-',color='green',label=r'$C_{Heated}$')

	#probably want to add a second vertical axis here and plot the pressure drop as a pressure ratio for both high and low pressure sides.


	#label the plot
	Plot1.set_xlabel('Temperature, Cooled Side, [K]')
	Plot1.set_xlim(floor(Recuperator['HighPressure']['ActualStartingProperties']['Temperature']/10)*10,ceil(Recuperator['LowPressure']['ActualStartingProperties']['Temperature']/10)*10)
#note, kg$_{LowPressure}$ is not really right if low pressure mass fraction is not 1
	Plot1.set_ylabel(r'$c_{p}$, [J/(kg*K)] and C, [J/(kg$_{Cooled}$*K)]')
	Plot1.set_ylim(0,ceil(max((Recuperator['LowPressure']['ActualSpecificHeats']).max(),(Recuperator['HighPressure']['ActualSpecificHeats']).max(),(Recuperator['LowPressure']['ActualSpecificHeats']*RecuperatorInputParameters['LowPressure']['MassFraction']).max(),(Recuperator['HighPressure']['ActualSpecificHeats']*RecuperatorInputParameters['HighPressure']['MassFraction']).max())/1000)*1000)
	Plot1.grid(True)
	Plot1.legend()


	#right figure

	#now plot the temperature difference and SpecificHeat ratio
	line1=Plot2.plot(Recuperator['LowPressure']['ActualTemperatures'],Recuperator['ActualDeltaTs'],marker='o',markersize=4,markevery=markevery,linestyle='-',color='black',label=r'$\Delta T$')

	Plot2.set_ylim(0,DeltaTVerticalAxisMax)

	#now, setup a second vertical axis
	Plot2_SecondVerticalAxis = Plot2.twinx()
	#plot the SpecificHeat ratios
	line3=Plot2_SecondVerticalAxis.plot(Recuperator['LowPressure']['ActualTemperatures'],Recuperator['ActualSpecificHeatRatios'],marker='o',markersize=4,markevery=markevery,linestyle='-',color='red',label=r'$C_{Heated}/C_{Cooled}$')
	#draw a horizontal line at 1 so it is easy to see where the specific heat ratio crosses 1
	line4=Plot2_SecondVerticalAxis.axhline(1,color='green',label='1')

#########warning, still confused which SpecificHeatRatios to actually plot. currently plotting the one based on extreme temperatures and not the actual SpecificHeat ratios in the node################
#actually, now no longer doing this. SpecificHeatRatiosOriginal is deactivated in the above function, and now using ActualSpecificHeatRatios because of the fact that now have heaters and coolers optional
#also, the other thing is that turned off the iterating for SpecificHeatRatios (currently just doing 1 iteration), so think ActualSpecificHeatRatiosOriginal wouldn't really be any different
#if it were actually defined in some way

	#draw the average SpecificHeat ratio so can see when it crosses 1
#	line4=plt.axhline(Recuperator['ActualSpecificHeatRatios'].mean())


	#set the titles and labels
	Plot2.set_xlabel('Temperature, Cooled Side, [K]')
	Plot2.set_ylabel(r'$\Delta T = T_{Cooled} - T_{Heated}$, [K]')
	Plot2_SecondVerticalAxis.set_ylabel(r'Heat Capacity Ratio, $C_{Heated}/C_{Cooled}$')
	Plot2_SecondVerticalAxis.set_ylim(0,cpRatioAxisMax)
	Plot2.set_xlim(floor(round(Recuperator['HighPressure']['ActualStartingProperties']['Temperature'],5)/10)*10,ceil(Recuperator['LowPressure']['ActualStartingProperties']['Temperature']/10)*10)		#round first to 5 decimal places because there seems to be some roundoff error that accumulated sometimes and don't want to round by 10K for something that can't even be seen
	Plot2.grid(True)

	#add the legend
	#need to manually build the legend here because it spand multiple axes
	#concatenate the line objects into one list
	AllLines=line1+line3+[line4]	#for some reason axhline objects aren't in a list, so put them in one so they can be concatenated
	#get all the lables in the form of a new list
	Lables=[l.get_label() for l in AllLines]
	#create the legend with the list of line objects and the corresponding list of line lables
	Plot2.legend(AllLines,Lables,loc='upper left')


	#save the image
	image_data = cStringIO.StringIO()					#setup the file handle
	TheFigure.savefig(image_data,format=ImageFileType)			#make the image file

	plt.close('all')							#releases all the RAM that is never released automatically

	return image_data.getvalue()






















#create some mildly general helper functions to simplify syntax for making *some* of the plots.


def CreateFigure(TitleTEXT,HorizontalAxisTEXT,VerticalAxisTEXT,HorizontalAxisMin=None,HorizontalAxisMax=None,VerticalAxisMin=None,VerticalAxisMax=None,MaxNLocatorY=10,AspectRatio=1,ResolutionMultiplier=1,FontScaling=250):

	TheFigure=plt.figure()

	#set the size and shape of the figure
	DotsPerInch=FontScaling*ResolutionMultiplier				#FontScaling controls the font and line width scaling (larger value means larger fonts). ResolutionMultiplier controls the resolution without changing the font scaling (no real effect for pdf output). Larger value means higher resolution.
	ImageDimensions={}
	ImageDimensions['width']=1800*ResolutionMultiplier/DotsPerInch		#don't know where 1800 came from, but seems like it is a good number to start with relative to FontScaling=250
	ImageDimensions['height']=ImageDimensions['width']*AspectRatio		#don't need to scale this by the resolution because width already was

	TheFigure.set_size_inches(ImageDimensions['width'],ImageDimensions['height'])
	TheFigure.set_dpi(DotsPerInch)


	ThePlot=TheFigure.add_subplot(111)	#see PlotCycle for some notes on why host_subplot may want to be used

	TheFigure.suptitle(TitleTEXT,fontsize=12)

	#set format the axes labels
#	ThePlot.xaxis.set_major_formatter(plt.FuncFormatter(thousands))
#	ThePlot.yaxis.set_major_formatter(plt.FuncFormatter(thousands))

	ThePlot.yaxis.set_major_locator(MaxNLocator(MaxNLocatorY))


	#and set the axis limits if don't want to keep the default auto ranging
	if (HorizontalAxisMin is not None) and (HorizontalAxisMax is not None):
		ThePlot.set_xlim(left=HorizontalAxisMin,right=HorizontalAxisMax)
	if (VerticalAxisMin is not None) and (VerticalAxisMax is not None):
		ThePlot.set_ylim(bottom=VerticalAxisMin,top=VerticalAxisMax)

	ThePlot.grid(True)

	#label the plot
	ThePlot.set_xlabel(HorizontalAxisTEXT)
	ThePlot.set_ylabel(VerticalAxisTEXT)

	TheFigure.subplots_adjust(left=.125,right=.92)

	TheLines=[]	#initialize this value

	return TheFigure,ThePlot,TheLines





def AddSecondVerticalAxis(TheFigure,ThePlot,VerticalAxisTEXT,VerticalAxisMin=None,VerticalAxisMax=None):

	ThePlot_SecondVerticalAxis=ThePlot.twinx()
	ThePlot_SecondVerticalAxis.set_ylabel(VerticalAxisTEXT)

	ThePlot_SecondVerticalAxis.yaxis.set_major_locator(MaxNLocator(10))
	#and add gridlines
#	ThePlot_SecondVerticalAxis.grid(True)

	#and remove grid lines for the other axis
#	ThePlot.grid(False)


	if (VerticalAxisMin is not None) and (VerticalAxisMax is not None):
		ThePlot_SecondVerticalAxis.set_ylim(bottom=VerticalAxisMin,top=VerticalAxisMax)

	#also, re-tweak the subplot layout
	TheFigure.subplots_adjust(right=.90)

	return ThePlot_SecondVerticalAxis

def AddMultiAxisLegend(ThePlot,TheLines,loc=0):
	#get all the lables in the form of a new list
	Lables=[l.get_label() for l in TheLines]
	#create the legend with the list of line objects and the corresponding list of line lables
	ThePlot.legend(TheLines,Lables,fontsize='x-small',loc=loc)



def AddASubPlotBelow(TheFigure,TheOtherPlot,HorizontalAxisTEXT,VerticalAxisTEXT,TheOtherPlotSecondVerticalAxis=None,HorizontalAxisMin=None,HorizontalAxisMax=None,VerticalAxisMin=None,VerticalAxisMax=None,MaxNLocatorY=10):
	TheOtherPlot.change_geometry(2,1,1)
	if TheOtherPlotSecondVerticalAxis is not None:
		TheOtherPlotSecondVerticalAxis.change_geometry(2,1,1)
	if HorizontalAxisTEXT is None:
		sharex=TheOtherPlot
		plt.setp(TheOtherPlot.get_xticklabels(),visible=False)
	else:
		sharex=None

	TheSubPlot=TheFigure.add_subplot(2,1,2,sharex=sharex)

	#set format the axes labels
#	TheSubPlot.xaxis.set_major_formatter(plt.FuncFormatter(thousands))
#	TheSubPlot.yaxis.set_major_formatter(plt.FuncFormatter(thousands))

	TheSubPlot.yaxis.set_major_locator(MaxNLocator(MaxNLocatorY))

	#and set the axis limits if don't want to keep the default auto ranging
	if (HorizontalAxisMin is not None) and (HorizontalAxisMax is not None) and (HorizontalAxisTEXT is not None):
		TheSubPlot.set_xlim(left=HorizontalAxisMin,right=HorizontalAxisMax)
	if (VerticalAxisMin is not None) and (VerticalAxisMax is not None):
		TheSubPlot.set_ylim(bottom=VerticalAxisMin,top=VerticalAxisMax)

	TheSubPlot.grid(True)

	#label the rest of the plot
	TheSubPlot.set_ylabel(VerticalAxisTEXT)
	if HorizontalAxisTEXT is None:
		TheSubPlot.set_xlabel(TheOtherPlot.get_xlabel())
		TheOtherPlot.set_xlabel('')
	else:
		TheSubPlot.set_xlabel(HorizontalAxisTEXT)


	TheSubPlotLines=[]	#initialize this value

	return TheSubPlot,TheSubPlotLines



def SaveTheFigure(TheFigure,FileName=None,ImageFileType='pdf'):

	#save the image
	image_data = cStringIO.StringIO()					#setup the file handle
	TheFigure.savefig(image_data,format=ImageFileType)			#make the image file

	plt.close('all')							#releases all the RAM that is never released automatically. note, this statement currently limits working on more than one figure simultaneously (which you can do). may want to improve it to just close the current figure (TheFigure).

	#actually write the image
	if FileName is None:
		return image_data.getvalue()
	else:
		WriteBinaryData(image_data.getvalue(),FileName)















def PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription,TheFigure=None,ThePlot=None,TheLines=None,HorizontalAxisMin=None,HorizontalAxisMax=None,HorizontalAxisLabel=None,VerticalAxisMin=None,VerticalAxisMax=None,VerticalAxisLabel=None,ContourLevelMin=None,ContourLevelMax=None,ContourLevelRoundTo=1,PlotSecondAxisAsLines=False,SecondAxisLineLabelSuffix='',SecondAxisLineLabel=None):
	Folder=BaseInputFilePath+'/'+CaseName+'/'

	#as noted below, these SWEPT independent variables are at the end of the group (either NonCO2CycleIndependentVariable or the end of everything)
	IndependentVariableValuesGrid=load(Folder+'IndependentVariableValues.npz')['IndependentVariableValuesGrid']

	#note, IndependentVariableLabels referes to more than just the swept values in IndependentVariableValuesGrid
	IndependentVariableLabels=load(Folder+'IndependentVariableValues.npz')['IndependentVariableLabels']

	try:	#might want to do this more specifically to see if the file exists rather than some other type of error.
		NonCO2CycleIndependentVariableLabels=cPickle.load(open(Folder+'NonCO2CycleIndependentVariableLabels.p', 'rb'))
		ValueCount=cPickle.load(open(Folder+'ValueCount.p', 'rb'))
	except:
		NonCO2CycleIndependentVariableLabels=()
		ValueCount=(0,0,0,0)

	Results=load(Folder+'OptimizationResults.npz')['Results']

	if PlotMagnitudeDescription=='Cycle Efficiency [%]':
		plotdata=Results[0]*100.

		TitleTEXT='Maximum Thermal Efficiency='+RoundAndPadToString(plotdata.max(),2)+'%'

	elif PlotMagnitudeDescription=='Cycle Exergy Efficiency [%]':
		TEMPplotdata=Results[0]
		#more setup for this case will be done below

	else:
		#plot an optimized parameter

		###################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		#the following works since optimized values are always first in the IndependentVariableLabels and the script is currently not setup to work if NonCO2CycleIndependentVariableLabels is not ()
		#and this script is not setup to work with multiple swept values.
		###################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

		if PlotMagnitudeDescription == 'Overall Pressure Ratio':
			ParameterToPlotIndex1=FindSubString(IndependentVariableLabels,'PreCompressor Pressure Ratio')[0][0]+1		#need to offset by 1 because the efficiency is the first element in the Results object
			ParameterToPlotIndex2=FindSubString(IndependentVariableLabels,'Main Compressor Pressure Ratio')[0][0]+1		#need to offset by 1 because the efficiency is the first element in the Results object
			plotdata=Results[ParameterToPlotIndex1]*Results[ParameterToPlotIndex2]
		else:
			ParameterToPlotIndex=FindSubString(IndependentVariableLabels,PlotMagnitudeDescription)[0][0]+1		#need to offset by 1 because the efficiency is the first element in the Results object
			plotdata=Results[ParameterToPlotIndex]

		TitleTEXT=''

	IndependentVariableLabels=NonCO2CycleIndependentVariableLabels+tuple(IndependentVariableLabels)

	#set the horizontal axis
	HorizontalAxis=IndependentVariableValuesGrid[0]


	#figure out how to find the axis labels
	#the swept values are placed at the end of the group (either NonCO2CycleIndependentVariable or the end of everything)
	if ValueCount[3]==2:
		VerticalAxisIndex=len(NonCO2CycleIndependentVariableLabels)-1
		HorizontalAxisIndex=VerticalAxisIndex-1
	elif ValueCount[3]==1:
		VerticalAxisIndex=-1
		HorizontalAxisIndex=len(NonCO2CycleIndependentVariableLabels)-1
	else:
		VerticalAxisIndex=-1
		HorizontalAxisIndex=VerticalAxisIndex-1


	if HorizontalAxisLabel is None:
		HorizontalAxisLabel=IndependentVariableLabels[HorizontalAxisIndex]


	Log2YScale=False
	if (PlotMagnitudeDescription=='Cycle Efficiency [%]') and (HorizontalAxisLabel=='Optimizer Population Size'):
		#do some special things for this case

		plotdata=plotdata-plotdata.min()

		#most of the following could have been accomplishd outside of this function (before writing to a file), but just putting them in here since there already has to be a special modification of the plotdata variable
		Log2YScale=True
		TitleTEXT=''
		PlotMagnitudeDescription='Cycle Efficiency Percentage Point Increase Relative to Lowest Case'


	#do some more things for the exergy efficiency calculation
	if PlotMagnitudeDescription=='Cycle Exergy Efficiency [%]':
		if (
			((HorizontalAxisLabel=='Maximum Temperature [K]') and (IndependentVariableLabels[VerticalAxisIndex]=='Minimum Temperature [K]')) or
			((HorizontalAxisLabel=='Gas Turbine Rotor Inlet Temperature [K]') and (IndependentVariableLabels[VerticalAxisIndex]=='Ambient Temperature [K]'))
			):
			plotdata=TEMPplotdata*100/(1-IndependentVariableValuesGrid[1]/HorizontalAxis)
			TitleTEXT='Maximum Exergy Efficiency='+RoundAndPadToString(plotdata.max(),2)+'%'
		else:
			raise Exception ('exergy efficiency plotting right now only works for a very limited configuration')


	if ContourLevelMax is None:
		ContourLevelMax=nearestMultiple(plotdata.max(),ContourLevelRoundTo,direction='up')
	else:
		print 'contour level limited to '+str(ContourLevelMax) + ' and Max value is '+str(plotdata.max())

	if ContourLevelMin is None:
		ContourLevelMin=nearestMultiple(plotdata.min(),ContourLevelRoundTo,direction='down')
	else:
		print 'contour level limited to '+str(ContourLevelMin) + ' and Min value is '+str(plotdata.min())

	plotrange=linspace(ContourLevelMin,ContourLevelMax,11)


	if plotdata.shape[1]==1 or PlotSecondAxisAsLines:				#if the second axis has a size of one then that means it has no data, so the plot should be a line plot.

		if VerticalAxisLabel is None:
			VerticalAxisLabel=PlotMagnitudeDescription

		if TheFigure is None:
			TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT=TitleTEXT,HorizontalAxisTEXT=HorizontalAxisLabel,VerticalAxisTEXT=VerticalAxisLabel,HorizontalAxisMin=HorizontalAxisMin,HorizontalAxisMax=HorizontalAxisMax,VerticalAxisMin=VerticalAxisMin,VerticalAxisMax=VerticalAxisMax)

		for ValueNumber in range(plotdata.shape[1]):
			VerticalAxis=plotdata[:,ValueNumber]
			if SecondAxisLineLabel is not None:
				label=SecondAxisLineLabel[ValueNumber]
			else:
				label=str(IndependentVariableValuesGrid[1][0,ValueNumber])+' '+SecondAxisLineLabelSuffix
			TheLines+=ThePlot.plot(HorizontalAxis[:,ValueNumber],VerticalAxis,marker='o',markersize=2,linestyle='-',label=label)

		if PlotSecondAxisAsLines:
			AddMultiAxisLegend(ThePlot,TheLines)

	else:
		VerticalAxis=IndependentVariableValuesGrid[1]

		if VerticalAxisLabel is None:
			VerticalAxisLabel=IndependentVariableLabels[VerticalAxisIndex]

		if TheFigure is None:
			TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT=TitleTEXT,HorizontalAxisTEXT=HorizontalAxisLabel,VerticalAxisTEXT=VerticalAxisLabel,HorizontalAxisMin=HorizontalAxisMin,HorizontalAxisMax=HorizontalAxisMax,VerticalAxisMin=VerticalAxisMin,VerticalAxisMax=VerticalAxisMax)

		#plot the grid points
		ThePlot.plot(HorizontalAxis,VerticalAxis,marker='o',markersize=1,linestyle='none',color='black')
		#plot the contour level
		TheContourPlot=ThePlot.contourf(HorizontalAxis,VerticalAxis,plotdata,ComputeLevels(plotrange))
		TheColorBar=TheFigure.colorbar(TheContourPlot)		#don't know that TheFigure is needed here. maybe plt can just be used instead????
		TheColorBar.set_label(PlotMagnitudeDescription,fontsize=12)
		TheColorBar.set_ticks(plotrange)

	if Log2YScale == True:
		ThePlot.set_yscale('log',basey=2)
		ThePlot.grid(False)		#turn off the grid lines for logarithmic plot because the grid points ploted above are likely going to be in the same place on the vertical axis.

	return TheFigure,ThePlot,TheLines
