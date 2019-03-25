###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


from numpy import abs
from FluidProperties.REFPROP import TemperatureFromEnthalpyPressureREFPROPdirect, cpFromTemperaturePressure, EnthalpyFromTemperaturePressureREFPROPdirect
from helpers import RoundAndPadToString
from Plotters import CreateFigure,AddSecondVerticalAxis,AddASubPlotBelow,SaveTheFigure,AddMultiAxisLegend
from matplotlib.ticker import MaxNLocator
import HeatExchangerCFDPostProcessFunctions
from HeatExchangerCFDPostProcessFunctions import *
import itertools



HeatExchangerCFDPostProcessFunctions.BaseDirectory='/tmp/'
OutputDirectory='/tmp/'


#warning, need to use "data on vertices" option in starccm+, if not, won't get points right on the boundary in either the presentation grid derived part mode or the original grid.
#also need to realize that number of divisions in the gridder is actually a cell count not a grid point count.
#note, in order to get heat flux, needed to use the actual wall boundary and not a derived part (for some reason starccm does not realize it was on a wall... or could this be fixed using the "data on vertices" option?),
#which does not allow you to choose the point distribution, but instead uses the actual grid point locations.



BaseName='StraightEqualHeightChannels'

#case names and grid levels, etc.
Cases=[
	[
		'Re10L',			#case name
		[0,1,2],			#geometry grid levels
		[0,1,2],			#property grid levels
		'',				#suffix
		[
			(2609,1,4),		#00 wall grid points
			(1305,1,4),		#11 wall grid points
			(653,1,4),		#22 wall grid points
		],
		(401,51,12),	#regularly spaced channel points. doesn't need to be specific to the grid level since a presentation grid is used at regular points that are interpolated already by starccm. see notes on roundoff error issues when not using original grid points.
		[
			5e6,			#TopHalfChannelReferencePressure
			25e6,			#BottomHalfChannelReferencePressure
		],
		150,				#heat flux vertical axis limit
		200,				#heat transfer coefficient vertical axis limit
		15,				#Nu vertical axis limit
	],
	[
		'Re50L',
		[0],
		[0],
		'',
		[
			(2609,1,4),		#00 wall grid points
			(1305,1,4),		#11 wall grid points
			(653,1,4),		#22 wall grid points
		],
		(401,51,12),	#regularly spaced channel points. doesn't need to be specific to the grid level since a presentation grid is used at regular points that are interpolated already by starccm. see notes on roundoff error issues when not using original grid points.
		[
			5e6,			#TopHalfChannelReferencePressure
			25e6,			#BottomHalfChannelReferencePressure
		],
		600,
		200,
		15,
	],
	[
		'Re3000T',
		[0],
		[0],
		'',
		[
			(2609,1,4),		#00 wall grid points
		],
		(401,51,12),	#regularly spaced channel points. doesn't need to be specific to the grid level since a presentation grid is used at regular points that are interpolated already by starccm. see notes on roundoff error issues when not using original grid points.
		[
			5e6,			#TopHalfChannelReferencePressure
			25e6,			#BottomHalfChannelReferencePressure
		],
		25000,
		1000,
		150,
	],
	[
		'Re4000T',
		[0],
		[0],
		'',
		[
			(2609,1,4),		#00 wall grid points
		],
		(401,51,12),	#regularly spaced channel points. doesn't need to be specific to the grid level since a presentation grid is used at regular points that are interpolated already by starccm. see notes on roundoff error issues when not using original grid points.
		[
			5e6,			#TopHalfChannelReferencePressure
			25e6,			#BottomHalfChannelReferencePressure
		],
		25000,
		1000,
		150,
	],
	[

		'10m-Re3000T',
		[0,1,2],
		[0,1,2],
		'',
		[
			(2609,1,4),		#00 wall grid points
			(1305,1,4),		#11 wall grid points
			(653,1,4),		#22 wall grid points
		],
		(4001,51,12),	#regularly spaced channel points. doesn't need to be specific to the grid level since a presentation grid is used at regular points that are interpolated already by starccm. see notes on roundoff error issues when not using original grid points.
		[
			5e6,			#TopHalfChannelReferencePressure
			25e6,			#BottomHalfChannelReferencePressure
		],
		3500,
		1000,
		150,
	],
	[
		'10m-Re3000T',
		[0],
		[0],
		'_LowPressure',
		[
			(2609,1,4),		#00 wall grid points
		],
		(4001,51,12),	#regularly spaced channel points. doesn't need to be specific to the grid level since a presentation grid is used at regular points that are interpolated already by starccm. see notes on roundoff error issues when not using original grid points.
		[
			1e6,			#TopHalfChannelReferencePressure
			5e6,			#BottomHalfChannelReferencePressure
		],
		600,
		200,
		50,
	],
]


MarkersToUse=('H','>', '+', 'p', 'o', '*','^','s','d')
ColorsToUse=('b','g','r','c','m','#FFFF00','k','#FF8C00','#B8860B')





for Case in Cases:

	GridDependencyMarker=itertools.cycle(MarkersToUse)
	GridDependencyColor=itertools.cycle(ColorsToUse)

	TopHalfChannelReferencePressure=Case[6][0]
	BottomHalfChannelReferencePressure=Case[6][1]

	Effectiveness=zeros((len(Case[1]),len(Case[2])))
	TheGridDependencyStudyEffectivenessFigure,TheGridDependencyStudyEffectivenessPlot,TheGridDependencyStudyEffectivenessLines=CreateFigure(TitleTEXT='Heat Exchanger Effectiveness vs Fluid Property Grid Level',HorizontalAxisTEXT=r'Fluid Property Grid Level',VerticalAxisTEXT=r'Heat Exchanger Effectiveness [%]',FontScaling=200)
	TheGridDependencyStudyEffectivenessPlot.xaxis.set_major_locator(MaxNLocator(2))

	TheGridDependencyStudyDeltaTFigure,TheGridDependencyStudyDeltaTPlot,TheGridDependencyStudyDeltaTLines=CreateFigure(TitleTEXT='Temperature Difference, Low Pressure Channel to High Pressure Channel',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'Low Pressure Temperature - High Pressure Temperature [$K$]',MaxNLocatorY=20,AspectRatio=float(1920)/1080)
	TheGridDependencyStudyDeltaT2Figure,TheGridDependencyStudyDeltaT2Plot,TheGridDependencyStudyDeltaT2Lines=CreateFigure(TitleTEXT='Temperature Difference, Low Pressure Channel to High Pressure Channel',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'Low Pressure Temperature - High Pressure Temperature Normalized by Highest Resolution Case',MaxNLocatorY=20,AspectRatio=float(1920)/1080)

#	TheGridDependencyStudyDeltaT3Figure,TheGridDependencyStudyDeltaT3Plot,TheGridDependencyStudyDeltaT3Lines=CreateFigure(TitleTEXT='Temperature Difference, Low Pressure Channel to High Pressure Channel',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'Low Pressure Temperature - High Pressure Temperature Normalized by Highest Resolution Case Low Temperature Delta T',MaxNLocatorY=20,AspectRatio=float(1920)/1080)
#	TheGridDependencyStudyDeltaT4Figure,TheGridDependencyStudyDeltaT4Plot,TheGridDependencyStudyDeltaT4Lines=CreateFigure(TitleTEXT='Temperature Difference, Low Pressure Channel to High Pressure Channel',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'Low Pressure Temperature - High Pressure Temperature Normalized by Low Temperature',MaxNLocatorY=20,AspectRatio=float(1920)/1080)

	if '10m-Re3000T' in Case[0]:	#only do this case for now since the export files for the Re3000T and Re4000T cases seem to have been setup for regularly spaced grid points and they aren't grid dependency studies anyway. if want to look at them, it will probably be easiest to redo the starccm file and then re-export the data on grid points so it matches all the others.
		TheGridDependencyStudyLowPressureyPlusFigure,TheGridDependencyStudyLowPressureyPlusPlot,TheGridDependencyStudyLowPressureyPlusLines=CreateFigure(TitleTEXT='Low Pressure Side',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'y+ Value at the First Grid Point From the Wall',MaxNLocatorY=20,AspectRatio=float(1920)/1080)
		TheGridDependencyStudyHighPressureyPlusFigure,TheGridDependencyStudyHighPressureyPlusPlot,TheGridDependencyStudyHighPressureyPlusLines=CreateFigure(TitleTEXT='High Pressure Side',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'y+ Value at the First Grid Point From the Wall',MaxNLocatorY=20,AspectRatio=float(1920)/1080)

	for GeometryGridLevel in Case[1]:
		for PropertyGridLevel in Case[2]:

			RunName=BaseName+'-'+Case[0]+'_G'+2*str(GeometryGridLevel)+'R_P'+2*str(PropertyGridLevel)+Case[3]

			ShortRunName=BaseName+'-'+Case[0]+Case[3]


			BottomHalfChannelData=ReadStarCCMDataFile(RunName,'Bottom',Case[5])
			TopHalfChannelData=ReadStarCCMDataFile(RunName,'Top',Case[5])

			XValues,BottomHalfChannelAveragedTotalEnthalpies=ComputeAverage('TotalEnthalpy',BottomHalfChannelData)
			XValues,TopHalfChannelAveragedTotalEnthalpies=ComputeAverage('TotalEnthalpy',TopHalfChannelData)

			XValues,BottomHalfChannelAveragedGaugeTotalPressures=ComputeAverage('GaugeTotalPressure',BottomHalfChannelData)
			XValues,TopHalfChannelAveragedGaugeTotalPressures=ComputeAverage('GaugeTotalPressure',TopHalfChannelData)

			XValues,BottomHalfChannelAveragedGaugeStaticPressures=ComputeAverage('GaugeStaticPressure',BottomHalfChannelData)
			XValues,TopHalfChannelAveragedGaugeStaticPressures=ComputeAverage('GaugeStaticPressure',TopHalfChannelData)

			XValues,BottomHalfChannelAveragedDensity=ComputeAverage('Density',BottomHalfChannelData)
			XValues,TopHalfChannelAveragedDensity=ComputeAverage('Density',TopHalfChannelData)


			BottomWallData=ReadAndInterpolateRegularHeatFluxValues(RunName,'Bottom',Case[4][GeometryGridLevel],XValues)
			TopWallData=ReadAndInterpolateRegularHeatFluxValues(RunName,'Top',Case[4][GeometryGridLevel],XValues)

			BottomHalfChannelTotalEnthalpyWeightedTemperature=TemperatureFromEnthalpyPressureREFPROPdirect(BottomHalfChannelAveragedTotalEnthalpies,BottomHalfChannelAveragedGaugeTotalPressures+BottomHalfChannelReferencePressure)
			TopHalfChannelTotalEnthalpyWeightedTemperature=TemperatureFromEnthalpyPressureREFPROPdirect(TopHalfChannelAveragedTotalEnthalpies,TopHalfChannelAveragedGaugeTotalPressures+TopHalfChannelReferencePressure)






			XValues,BottomChannelReValues,BottomChannelDynamicViscosityWeightedByStaticTemperatureAndPressure,BottomChannelHydraulicDiameter,BottomChannelThermalConductivityWeightedByStaticTemperatureAndPressure,BottomChannelAveragedMassFlux=ComputeReValues(BottomHalfChannelData,BottomHalfChannelReferencePressure)
			XValues,TopChannelReValues,TopChannelDynamicViscosityWeightedByStaticTemperatureAndPressure,TopChannelHydraulicDiameter,TopChannelThermalConductivityWeightedByStaticTemperatureAndPressure,TopChannelAveragedMassFlux=ComputeReValues(TopHalfChannelData,TopHalfChannelReferencePressure)


			#setup some parameters for line styles
			markevery=len(XValues)/20+(1+GeometryGridLevel)*(1+PropertyGridLevel)**2			#show about 20 line markers for the 00 case, less for coarser cases so that the markers can be distinguished
			CurrentLineMarker=GridDependencyMarker.next()
			CurrentLineColor=GridDependencyColor.next()


			BottomChannelMaxHeatRecuperated=(EnthalpyFromTemperaturePressureREFPROPdirect(TopHalfChannelTotalEnthalpyWeightedTemperature[-1],BottomHalfChannelAveragedGaugeTotalPressures[0]+BottomHalfChannelReferencePressure)-BottomHalfChannelAveragedTotalEnthalpies[0])*BottomChannelAveragedMassFlux[0]
			TopChannelMaxHeatRecuperated=(TopHalfChannelAveragedTotalEnthalpies[-1]-EnthalpyFromTemperaturePressureREFPROPdirect(BottomHalfChannelTotalEnthalpyWeightedTemperature[0],TopHalfChannelAveragedGaugeTotalPressures[-1]+TopHalfChannelReferencePressure))*TopChannelAveragedMassFlux[-1]
			ActualHeatRecuperated=(TopHalfChannelAveragedTotalEnthalpies[-1]-TopHalfChannelAveragedTotalEnthalpies[0])*TopChannelAveragedMassFlux[-1]

			Effectiveness[GeometryGridLevel,PropertyGridLevel]=ActualHeatRecuperated/min(BottomChannelMaxHeatRecuperated,TopChannelMaxHeatRecuperated)
			DeltaT=TopHalfChannelTotalEnthalpyWeightedTemperature-BottomHalfChannelTotalEnthalpyWeightedTemperature


			print
			print RunName
			print "Effectiveness: "+RoundAndPadToString(Effectiveness[GeometryGridLevel,PropertyGridLevel]*100,6)+'%'
			print "MinDeltaT:     "+RoundAndPadToString(DeltaT.min(),2)
			print "MaxRe:         "+str(TopChannelReValues.max())




			if (GeometryGridLevel==0) and (PropertyGridLevel==0):
				HighestResolutionDeltaT=DeltaT


				#only plot the fine grid cases

				TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT='Temperature Difference, Low Pressure Channel to High Pressure Channel',HorizontalAxisTEXT=r'Temperature, Low Pressure/Cooled/Top Channel [$K$]',VerticalAxisTEXT=r'Low Pressure Temperature - High Pressure Temperature [$K$]',AspectRatio=float(4)/3,FontScaling=200)
				TheLines+=ThePlot.plot(TopHalfChannelTotalEnthalpyWeightedTemperature,DeltaT,label=r'$\Delta T$ - 2-D CFD')

				#using the now known minimum delta T, re-solve using the 0-D model and then plot.
				SimplifiedRecuperator=RecuperatorSimplifier(LowTemperature=BottomHalfChannelTotalEnthalpyWeightedTemperature[0],HighTemperature=TopHalfChannelTotalEnthalpyWeightedTemperature[-1],LowPressure=TopHalfChannelReferencePressure,HighPressure=BottomHalfChannelReferencePressure,MassFraction=BottomChannelAveragedMassFlux[0]/TopChannelAveragedMassFlux[-1],MinimumDeltaT=DeltaT.min())
				TheLines+=ThePlot.plot(SimplifiedRecuperator['LowPressure']['ActualTemperatures'],SimplifiedRecuperator['ActualDeltaTs'],label=r'$\Delta T$ - 0-D')

				AddMultiAxisLegend(ThePlot,TheLines)

				TheSubPlot,TheSubPlotLines=AddASubPlotBelow(TheFigure,ThePlot,HorizontalAxisTEXT=None,VerticalAxisTEXT=r'Specific Heat [$J/(kg*K)$]')
				TheSubPlotLines+=TheSubPlot.plot(TopHalfChannelTotalEnthalpyWeightedTemperature,cpFromTemperaturePressure(ComputeAverage('StaticTemperature',TopHalfChannelData)[1],ComputeAverage('GaugeStaticPressure',TopHalfChannelData)[1]+TopHalfChannelReferencePressure),label='Low Pressure Channel')
				TheSubPlotLines+=TheSubPlot.plot(TopHalfChannelTotalEnthalpyWeightedTemperature,cpFromTemperaturePressure(ComputeAverage('StaticTemperature',BottomHalfChannelData)[1],ComputeAverage('GaugeStaticPressure',BottomHalfChannelData)[1]+BottomHalfChannelReferencePressure),label='High Pressure Channel')
				AddMultiAxisLegend(TheSubPlot,TheSubPlotLines)

				SaveTheFigure(TheFigure,FileName=OutputDirectory+RunName+'-DeltaT.pdf')




				TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT='Local Reynolds Number and Dynamic Viscosity',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'$Re_{D_h}$',AspectRatio=float(4)/3,FontScaling=200)
				TheSubPlot,TheSubPlotLines=AddASubPlotBelow(TheFigure,ThePlot,HorizontalAxisTEXT=None,VerticalAxisTEXT=r'Dynamic Viscosity [$\mu Pa * s$]')

				TheLines+=ThePlot.plot(XValues,TopChannelReValues,label=r'Low Pressure Channel $Re_{D_h}$',color='blue')
				TheSubPlotLines+=TheSubPlot.plot(XValues,TopChannelDynamicViscosityWeightedByStaticTemperatureAndPressure*1e6,label=r'Low Pressure Channel Viscosity',marker='o',markersize=4,color='blue',markevery=markevery)
				TheSubPlotLines+=TheSubPlot.plot(XValues,SutherlandLaw(Temperature=ComputeAverage('StaticTemperature',TopHalfChannelData)[1])*1e6,label=r'Low Pressure Channel Viscosity - Sutherland',marker='x',markersize=4,color='blue',markevery=markevery)

				TheLines+=ThePlot.plot(XValues,BottomChannelReValues,label=r'High Pressure Channel $Re_{D_h}$',color='red')
				TheSubPlotLines+=TheSubPlot.plot(XValues,BottomChannelDynamicViscosityWeightedByStaticTemperatureAndPressure*1e6,label=r'High Pressure Channel Viscosity',marker='o',markersize=4,color='red',markevery=markevery)
				TheSubPlotLines+=TheSubPlot.plot(XValues,SutherlandLaw(Temperature=ComputeAverage('StaticTemperature',BottomHalfChannelData)[1])*1e6,label=r'High Pressure Channel Viscosity - Sutherland',marker='x',markersize=4,color='red',markevery=markevery)


				AddMultiAxisLegend(ThePlot,TheLines,loc=6)
				AddMultiAxisLegend(TheSubPlot,TheSubPlotLines)
				SaveTheFigure(TheFigure,FileName=OutputDirectory+RunName+'-Re.pdf')




				TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT='Temperatures',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'Temperature [$K$]',MaxNLocatorY=20,AspectRatio=float(1920)/1080)

				TheLines+=ThePlot.plot(XValues,TopHalfChannelData[:,-1,ChannelIndices['TotalTemperature']],label=r'Low Pressure Channel Centerline Total Temperature',color='blue',marker='x',markevery=markevery)
				TheLines+=ThePlot.plot(XValues,TopHalfChannelTotalEnthalpyWeightedTemperature,label=r'Low Pressure Channel Enthalpy Weighted Average Total Temperature',color='blue',linewidth=.25)
				TheLines+=ThePlot.plot(XValues,TopHalfChannelData[:,0,ChannelIndices['TotalTemperature']],label=r'Low Pressure Channel Wall Total Temperature',color='blue',linestyle=':')

				TheLines+=ThePlot.plot(XValues,BottomHalfChannelData[:,0,ChannelIndices['TotalTemperature']],label=r'High Pressure Channel Centerline Total Temperature',color='red',marker='x',markevery=markevery)
				TheLines+=ThePlot.plot(XValues,BottomHalfChannelTotalEnthalpyWeightedTemperature,label=r'High Pressure Channel Enthalpy Weighted Average Total Temperature',color='red',linewidth=.25)
				TheLines+=ThePlot.plot(XValues,BottomHalfChannelData[:,-1,ChannelIndices['TotalTemperature']],label=r'High Pressure Channel Wall Total Temperature',color='red',linestyle=':')

				AddMultiAxisLegend(ThePlot,TheLines)
				SaveTheFigure(TheFigure,FileName=OutputDirectory+RunName+'-Temperatures.pdf')













				TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT='Wall Heat Flux Magnitude',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'$W/m^2$',VerticalAxisMin=0,VerticalAxisMax=Case[7])

				TheLines+=ThePlot.plot(XValues,abs(TopWallData[:,0,WallIndices['HeatFlux']]),label=r'Low Pressure Channel',color='blue')
				TheLines+=ThePlot.plot(XValues,abs(BottomWallData[:,0,WallIndices['HeatFlux']]),label=r'High Pressure Channel',color='red')

				AddMultiAxisLegend(ThePlot,TheLines)
				SaveTheFigure(TheFigure,FileName=OutputDirectory+RunName+'-HeatFlux.pdf')








				BottomWallh=BottomWallData[:,0,WallIndices['HeatFlux']]/(BottomHalfChannelData[:,-1,ChannelIndices['TotalTemperature']]-BottomHalfChannelTotalEnthalpyWeightedTemperature)
				TopWallh=TopWallData[:,0,WallIndices['HeatFlux']]/(TopHalfChannelData[:,0,ChannelIndices['TotalTemperature']]-TopHalfChannelTotalEnthalpyWeightedTemperature)

				BottomWallNu=BottomWallh*BottomChannelHydraulicDiameter/BottomChannelThermalConductivityWeightedByStaticTemperatureAndPressure
				TopWallNu=TopWallh*TopChannelHydraulicDiameter/TopChannelThermalConductivityWeightedByStaticTemperatureAndPressure

				TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT='Heat Transfer Coefficient and Thermal Conductivity',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'$W/(m^2*K)$',VerticalAxisMin=0,VerticalAxisMax=Case[8],AspectRatio=float(4)/3,FontScaling=200)

				TheLines+=ThePlot.plot(XValues,TopWallh,label=r'$h$ - Low Pressure Channel',color='blue')
				TheLines+=ThePlot.plot(XValues,BottomWallh,label=r'$h$ - High Pressure Channel',color='red')

				ThePlot_SecondVerticalAxis=AddSecondVerticalAxis(TheFigure,ThePlot,r'$Nu$',VerticalAxisMin=6,VerticalAxisMax=Case[9])
				TheLines+=ThePlot_SecondVerticalAxis.plot(XValues,TopWallNu,label=r'$Nu$ - Low Pressure Channel',color='blue',marker='o',markevery=markevery)
				TheLines+=ThePlot_SecondVerticalAxis.plot(XValues,BottomWallNu,label=r'$Nu$ - High Pressure Channel',color='red',marker='o',markevery=markevery)


				TheSubPlot,TheSubPlotLines=AddASubPlotBelow(TheFigure,ThePlot,HorizontalAxisTEXT=None,VerticalAxisTEXT=r'Thermal Conductivity [$W/(m*K)$]',TheOtherPlotSecondVerticalAxis=ThePlot_SecondVerticalAxis)

				TheSubPlotLines+=TheSubPlot.plot(XValues,TopChannelThermalConductivityWeightedByStaticTemperatureAndPressure,label='Low Pressure Channel')
				TheSubPlotLines+=TheSubPlot.plot(XValues,BottomChannelThermalConductivityWeightedByStaticTemperatureAndPressure,label='High Pressure Channel')


				AddMultiAxisLegend(ThePlot,TheLines)
				AddMultiAxisLegend(TheSubPlot,TheSubPlotLines)
				SaveTheFigure(TheFigure,FileName=OutputDirectory+RunName+'-Nu.pdf')






				TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT='Fluid Density',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'Density [$kg/m^3$]')

				TheLines+=ThePlot.plot(XValues,TopHalfChannelAveragedDensity,label=r'Low Pressure Channel',color='blue')
				TheLines+=ThePlot.plot(XValues,IdealGasDensity(Temperature=ComputeAverage('StaticTemperature',TopHalfChannelData)[1],Pressure=ComputeAverage('GaugeStaticPressure',TopHalfChannelData)[1]+TopHalfChannelReferencePressure),label=r'Low Pressure Channel - Ideal Gas',marker='x',markevery=markevery,color='blue')

				TheLines+=ThePlot.plot(XValues,BottomHalfChannelAveragedDensity,label=r'High Pressure Channel',color='red')
				TheLines+=ThePlot.plot(XValues,IdealGasDensity(Temperature=ComputeAverage('StaticTemperature',BottomHalfChannelData)[1],Pressure=ComputeAverage('GaugeStaticPressure',BottomHalfChannelData)[1]+BottomHalfChannelReferencePressure),label=r'High Pressure Channel - Ideal Gas',marker='x',markevery=markevery,color='red')

				AddMultiAxisLegend(ThePlot,TheLines)
				SaveTheFigure(TheFigure,FileName=OutputDirectory+RunName+'-Density.pdf')



				TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT='Gauge Total Pressure',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'Gauge Total Pressure [$Pa$]')

				TheLines+=ThePlot.plot(XValues,TopHalfChannelAveragedGaugeTotalPressures,label=r'Low Pressure Channel',color='blue')
				TheLines+=ThePlot.plot(XValues,BottomHalfChannelAveragedGaugeTotalPressures,label=r'High Pressure Channel',color='red')

				AddMultiAxisLegend(ThePlot,TheLines)
				SaveTheFigure(TheFigure,FileName=OutputDirectory+RunName+'-GaugeTotalPressure.pdf')


				TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT='Gauge Static Pressure',HorizontalAxisTEXT=r'Position [$m$]',VerticalAxisTEXT=r'Gauge Static Pressure [$Pa$]')

				TheLines+=ThePlot.plot(XValues,TopHalfChannelAveragedGaugeStaticPressures,label=r'Low Pressure Channel',color='blue')
				TheLines+=ThePlot.plot(XValues,BottomHalfChannelAveragedGaugeStaticPressures,label=r'High Pressure Channel',color='red')

				AddMultiAxisLegend(ThePlot,TheLines)
				SaveTheFigure(TheFigure,FileName=OutputDirectory+RunName+'-GaugeStaticPressure.pdf')



			TheCurrentLabel=2*str(GeometryGridLevel)+' Geometry Grid Level, '+2*str(PropertyGridLevel)+' Fluid Property Grid Level'

			TheGridDependencyStudyDeltaTLines+=TheGridDependencyStudyDeltaTPlot.plot(XValues,DeltaT,label=TheCurrentLabel,color=CurrentLineColor,marker=CurrentLineMarker,markevery=markevery)

			if not ((GeometryGridLevel==0) and (PropertyGridLevel==0)):	#don't plot a horizontal line
				TheGridDependencyStudyDeltaT2Lines+=TheGridDependencyStudyDeltaT2Plot.plot(XValues,DeltaT/HighestResolutionDeltaT,label=TheCurrentLabel,color=CurrentLineColor,marker=CurrentLineMarker,markevery=markevery)


#			TheGridDependencyStudyDeltaT3Lines+=TheGridDependencyStudyDeltaT3Plot.plot(XValues,DeltaT/HighestResolutionDeltaT[0],label=TheCurrentLabel)
#			TheGridDependencyStudyDeltaT4Lines+=TheGridDependencyStudyDeltaT4Plot.plot(XValues,DeltaT/BottomHalfChannelTotalEnthalpyWeightedTemperature[0],label=TheCurrentLabel)

			if '10m-Re3000T' in Case[0]:	#only do this case for now since the export files for the Re3000T and Re4000T cases seem to have been setup for regularly spaced grid points and they aren't grid dependency studies anyway. if want to look at them, it will probably be easiest to redo the starccm file and then re-export the data on grid points so it matches all the others.
				yPlusData=ReadStarCCMDataFile(RunName,'y+',Case[4][GeometryGridLevel],Type2='')

				TheGridDependencyStudyLowPressureyPlusLines+=TheGridDependencyStudyLowPressureyPlusPlot.plot(yPlusData[:,0,2],yPlusData[:,0,3],label=TheCurrentLabel,color=CurrentLineColor,marker=CurrentLineMarker,markevery=markevery)
				print TheCurrentLabel+' low pressure y+ max: '+str(yPlusData[:,0,3].max())

				TheGridDependencyStudyHighPressureyPlusLines+=TheGridDependencyStudyHighPressureyPlusPlot.plot(yPlusData[:,0,0],yPlusData[:,0,1],label=TheCurrentLabel,color=CurrentLineColor,marker=CurrentLineMarker,markevery=markevery)
				print TheCurrentLabel+' high pressure y+ max: '+str(yPlusData[:,0,1].max())

			print
			print

		TheGridDependencyStudyEffectivenessLines+=TheGridDependencyStudyEffectivenessPlot.plot(Case[2],100*Effectiveness[GeometryGridLevel,:],label=2*str(GeometryGridLevel)+' Geometry Grid Level',marker='x')



	if (len(Case[1])>1) or (len(Case[2])>1):		#only if a grid dependency study has been conducted
		AddMultiAxisLegend(TheGridDependencyStudyEffectivenessPlot,TheGridDependencyStudyEffectivenessLines)
		SaveTheFigure(TheGridDependencyStudyEffectivenessFigure,FileName=OutputDirectory+ShortRunName+'-EffectivenessVsPropertyGridLevels.pdf')

		AddMultiAxisLegend(TheGridDependencyStudyDeltaTPlot,TheGridDependencyStudyDeltaTLines)
		SaveTheFigure(TheGridDependencyStudyDeltaTFigure,FileName=OutputDirectory+ShortRunName+'-DeltaT.pdf')

		AddMultiAxisLegend(TheGridDependencyStudyDeltaT2Plot,TheGridDependencyStudyDeltaT2Lines)
		SaveTheFigure(TheGridDependencyStudyDeltaT2Figure,FileName=OutputDirectory+ShortRunName+'-DeltaT2.pdf')

#		AddMultiAxisLegend(TheGridDependencyStudyDeltaT3Plot,TheGridDependencyStudyDeltaT3Lines)
#		SaveTheFigure(TheGridDependencyStudyDeltaT3Figure,FileName=OutputDirectory+ShortRunName+'-DeltaT3.pdf')

#		AddMultiAxisLegend(TheGridDependencyStudyDeltaT4Plot,TheGridDependencyStudyDeltaT4Lines)
#		SaveTheFigure(TheGridDependencyStudyDeltaT4Figure,FileName=OutputDirectory+ShortRunName+'-DeltaT4.pdf')

		if '10m-Re3000T' in Case[0]:	#only do this case for now since the export files for the Re3000T and Re4000T cases seem to have been setup for regularly spaced grid points and they aren't grid dependency studies anyway. if want to look at them, it will probably be easiest to redo the starccm file and then re-export the data on grid points so it matches all the others.
			AddMultiAxisLegend(TheGridDependencyStudyLowPressureyPlusPlot,TheGridDependencyStudyLowPressureyPlusLines)
			SaveTheFigure(TheGridDependencyStudyLowPressureyPlusFigure,FileName=OutputDirectory+ShortRunName+'-LowPressureyPlus.pdf')

			AddMultiAxisLegend(TheGridDependencyStudyHighPressureyPlusPlot,TheGridDependencyStudyHighPressureyPlusLines)
			SaveTheFigure(TheGridDependencyStudyHighPressureyPlusFigure,FileName=OutputDirectory+ShortRunName+'-HighPressureyPlus.pdf')


		TheGridDependencyStudyEffectivenessFigure,TheGridDependencyStudyEffectivenessPlot,TheGridDependencyStudyEffectivenessLines=CreateFigure(TitleTEXT='Heat Exchanger Effectiveness vs Geometry Grid Level',HorizontalAxisTEXT=r'Geometry Grid Level',VerticalAxisTEXT=r'Heat Exchanger Effectiveness [%]',FontScaling=200)
		TheGridDependencyStudyEffectivenessPlot.xaxis.set_major_locator(MaxNLocator(2))
		for PropertyGridLevel in Case[2]:
			TheGridDependencyStudyEffectivenessLines+=TheGridDependencyStudyEffectivenessPlot.plot(Case[2],100*Effectiveness[:,PropertyGridLevel],label=2*str(PropertyGridLevel)+' Fluid Property Grid Level',marker='x')
			AddMultiAxisLegend(TheGridDependencyStudyEffectivenessPlot,TheGridDependencyStudyEffectivenessLines)
		SaveTheFigure(TheGridDependencyStudyEffectivenessFigure,FileName=OutputDirectory+ShortRunName+'-EffectivenessVsGeometryGridLevels.pdf')













#LATER TO DO:

#- calculate friction factor
#- find friction factor information for channels
#- find historical turbulent channel flow correlations





