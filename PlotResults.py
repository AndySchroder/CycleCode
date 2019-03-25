###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


from Plotters import CreateFigure,SaveTheFigure,ComputeLevels,AddMultiAxisLegend,PlotParameterSweep,PlotCycle
from helpers import SmartDictionary,WriteBinaryData
import cPickle

BaseInputFilePath='outputs/'



















#single cycle

BaseOutputFilePath='/tmp/'


CaseName='CO2Cycle-NotOptimizedParameterSweep-PowerTurbineEfficiency'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')


CaseName='CO2Cycle-OptimizedParameterSweep-MaxPressure'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')


CaseName='CO2Cycle-OptimizedParameterSweep-MaxPressure-ExtendedRange'

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Overall Pressure Ratio')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalOverallPressureRatio.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Main Compressor Pressure Ratio')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalMainCompressorPressureRatio.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='PreCompressor Pressure Ratio')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalPreCompressorPressureRatio.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Recompression Fraction')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalRecompressionFraction.pdf')


CaseName='CO2Cycle-OptimizedParameterSweep-RecompressionFraction'

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Overall Pressure Ratio')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalOverallPressureRatio.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Main Compressor Pressure Ratio')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalMainCompressorPressureRatio.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='PreCompressor Pressure Ratio')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalPreCompressorPressureRatio.pdf')





CaseName='CO2Cycle-OptimizedParameterSweep-ReHeat'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',HorizontalAxisLabel='Number of ReHeat Stages',VerticalAxisMin=46,VerticalAxisMax=51.5)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

CaseName='CO2Cycle-OptimizedParameterSweep-ReHeat-ElectricalMainCompressor'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',HorizontalAxisLabel='Number of ReHeat Stages',VerticalAxisMin=46,VerticalAxisMax=51.5)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')



CaseName='CO2Cycle-OptimizedParameterSweep-PressureRatios'

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',ContourLevelMin=30,ContourLevelMax=51)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',PlotSecondAxisAsLines=True)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-Lines.pdf')


CaseName='CO2Cycle-OptimizedParameterSweep-PressureRatios-SlightlyHigherPreCompressorPressureRatio'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',ContourLevelMin=30,ContourLevelMax=51)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Recompression Fraction',ContourLevelRoundTo=.1)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalRecompressionFraction-Contour.pdf')









CaseName='CO2Cycle-OptimizedParameterSweep-PressureRatios-WithZeroMinDeltaT'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',ContourLevelMin=30,ContourLevelMax=51)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

CaseName='CO2Cycle-OptimizedParameterSweep-PressureRatios-WithZeroMinDeltaT-SlightlyHigherPreCompressorPressureRatio'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',ContourLevelMin=30,ContourLevelMax=51)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')




CaseName='CO2Cycle-OptimizedParameterSweep-RegularAndElectricalMainCompressorEfficiency'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',PlotSecondAxisAsLines=True,SecondAxisLineLabel=['Dedicated Turbine Powered','Power Turbine/Electrically Powered'])
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Recompression Fraction',PlotSecondAxisAsLines=True,SecondAxisLineLabel=['Dedicated Turbine Powered','Power Turbine/Electrically Powered'])
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalRecompressionFraction.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Main Compressor Pressure Ratio',PlotSecondAxisAsLines=True,SecondAxisLineLabel=['Dedicated Turbine Powered','Power Turbine/Electrically Powered'])
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalMainCompressorPressureRatio.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='PreCompressor Pressure Ratio',PlotSecondAxisAsLines=True,SecondAxisLineLabel=['Dedicated Turbine Powered','Power Turbine/Electrically Powered'])
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalPreCompressorPressureRatio.pdf')






CaseName='CO2Cycle-OptimizedParameterSweep-MinDeltaTAndPressureDrop'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',PlotSecondAxisAsLines=True,SecondAxisLineLabelSuffix='Pa/K')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-Lines.pdf')

CaseName='CO2Cycle-OptimizedParameterSweep-MinDeltaTAndPressureDrop-RefinedLowDeltaT'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',PlotSecondAxisAsLines=True,SecondAxisLineLabelSuffix='Pa/K')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-Lines.pdf')

CaseName='CO2Cycle-OptimizedParameterSweep-MinDeltaTAndPressureDrop-RefinedLowDeltaT-WithAnotherLowPressureDrop'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',PlotSecondAxisAsLines=True,SecondAxisLineLabelSuffix='Pa/K')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-Lines.pdf')



#this plot is not very interesting, so decided not to use it
#CaseName='CO2Cycle-OptimizedParameterSweep-MinDeltaTAndPressureDrop'
#TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',PlotSecondAxisAsLines=False)
#SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-Contour.pdf')



CaseName='CO2Cycle-Optimized'
CycleParameters=cPickle.load(open(BaseInputFilePath+'/'+CaseName+'/Results.p', 'rb'))[0]

WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel=None,HorizontalAxisMaxOverride=3100,VerticalAxisMaxOverride=1100,ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CycleTs.pdf')
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='cp',ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CycleTscp.pdf')
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='Density',ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CycleTsrho.pdf')
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='gamma',ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CycleTsgamma.pdf')
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='CompressibilityFactor',ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CycleTsCompressibilityFactor.pdf')
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='Enthalpy',ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CycleTsEnthalpy.pdf')
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Enthalpy',ContourLevel='Temperature',ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CyclehsT.pdf')
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='SpecificVolume',VerticalAxis='Pressure',ContourLevel='cp',ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CyclePvcp.pdf')
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='SpecificVolume',VerticalAxis='Pressure',ContourLevel='Entropy',ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CyclePvs.pdf')
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='SpecificVolume',VerticalAxis='Pressure',ContourLevel='Temperature',ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CyclePvT.pdf')
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Pressure',VerticalAxis='Temperature',ContourLevel='cp',ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CycleTPcp.pdf')







CaseName='CO2Cycle-Optimized-ReHeat-0'
CycleParameters=cPickle.load(open(BaseInputFilePath+'/'+CaseName+'/Results.p', 'rb'))[0]
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel=None,HorizontalAxisMaxOverride=3100,VerticalAxisMaxOverride=1100,ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CycleTs.pdf')

CaseName='CO2Cycle-Optimized-ReHeat-3'
CycleParameters=cPickle.load(open(BaseInputFilePath+'/'+CaseName+'/Results.p', 'rb'))[0]
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel=None,HorizontalAxisMaxOverride=3100,VerticalAxisMaxOverride=1100,ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CycleTs.pdf')

CaseName='CO2Cycle-Optimized-ReHeat-6'
CycleParameters=cPickle.load(open(BaseInputFilePath+'/'+CaseName+'/Results.p', 'rb'))[0]
WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel=None,HorizontalAxisMaxOverride=3100,VerticalAxisMaxOverride=1100,ImageFileType='pdf'),BaseOutputFilePath+'/'+CaseName+'-CycleTs.pdf')











CaseName='CO2Cycle-OptimizedParameterSweep-MaxMinTemperatures'

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',PlotSecondAxisAsLines=True,SecondAxisLineLabelSuffix='K')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-Lines.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Exergy Efficiency [%]',PlotSecondAxisAsLines=True,SecondAxisLineLabelSuffix='K')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-ExergyEfficiency-Lines.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',ContourLevelRoundTo=1)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-Contour.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Recompression Fraction',ContourLevelRoundTo=.1)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalRecompressionFraction-Contour.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Main Compressor Outlet Pressure [Pa]',ContourLevelRoundTo=.1)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-OptimalMainCompressorOutletPressure-Contour.pdf')



























############################
#combined cycle
############################
#note, these cases are all commented out since they were added to the paper and don't want to overwrite that with some slightly different plots
#when this script is re-run to create the rest of the plots specified in it, if some changes are made to the plotting functions.

#note, this folder path has also been changed slightly after the creation of these plots has been commented out.
#BaseOutputFilePath='/tmp/'


#CaseName='CombinedCycle-OptimizedParameterSweep-GasTurbineCompressorIsentropicEfficiency'
#TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',HorizontalAxisMin=0.8,HorizontalAxisMax=0.9)
#SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

#CaseName='CombinedCycle-OptimizedParameterSweep-MaxCO2CyclePressure'
#TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]')
#SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

#CaseName='CombinedCycle-OptimizedParameterSweep-NumberOfEngines'
#TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]')
#SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

#CaseName='CombinedCycle-OptimizedParameterSweep-MaxTemperature'
#TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]')
#SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')
############################



BaseOutputFilePath='/tmp/'

CaseName='CombinedCycle-OptimizedParameterSweep-MaxMinTemperatures'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',PlotSecondAxisAsLines=True,SecondAxisLineLabelSuffix='K')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-Lines.pdf')

TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Exergy Efficiency [%]',PlotSecondAxisAsLines=True,SecondAxisLineLabelSuffix='K')
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'-ExergyEfficiency-Lines.pdf')











#fuel cell combined cycle

#BaseOutputFilePath='./scratch/'
#decided to not actually include this one in the dissertation


#CaseName='FuelCellCombinedCycle-OptimizedParameterSweep-FuelUtilization'
#TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]')
#SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')
#need to make horizontal axis multiplied by 100 or take away the % unit












BaseOutputFilePath='/tmp/'


CaseName='FuelCellCombinedCycle-OptimizerTolerance-OldData'
TheFigure,ThePlot,TheLines=PlotParameterSweep(BaseInputFilePath,CaseName,PlotMagnitudeDescription='Cycle Efficiency [%]',ContourLevelRoundTo=.05)
SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+CaseName+'.pdf')






