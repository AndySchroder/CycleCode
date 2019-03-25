###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


from Cycles import ConstantVolumeCycle
from Plotters import CreateFigure,AddSecondVerticalAxis,AddASubPlotBelow,AddMultiAxisLegend,SaveTheFigure
from numpy import linspace,zeros_like

import helpers
helpers.PrintWarningMessages=False			#for some reason have to do it this way because if just import PrintWarningMessages, and then set it, python must think you are overwritting the imported PrintWarningMessages object with a new local one and so the module PrintWarningMessages is not changed.




#since the constant volume cycle is very fast and only has one parameter to adjust, sweep it in serial and don't bother getting any of the other parallel run methods to work with this function..


MinPressures=linspace(2,8.5,200)*10**6
#MinPressures=linspace(2,9.4,200)*10**6			#this should work for 49MPa peak pressure

MaxPressures=zeros_like(MinPressures)
PressureRatios=zeros_like(MinPressures)
MaxTemperatures=zeros_like(MinPressures)
Efficiencies=zeros_like(MinPressures)
ExergyEfficiencies=zeros_like(MinPressures)
OptimalMinPressure=None

for counter in range(len(MinPressures)):

	#set some input values that have been commented out in the main input file.
	CycleInputParameters=helpers.SmartDictionary()

	CycleInputParameters['MinPressure']=MinPressures[counter]

	#choose the input parameters file
	execfile('./InputParameters/InputParameters-ConstantVolumeCO2.py')



	CycleParameters=ConstantVolumeCycle(CycleInputParameters)

	MaxPressures[counter]=CycleParameters['SecondPlusThirdHeating']['HeatedProperties']['Pressure']
	MaxTemperatures[counter]=CycleParameters['SecondPlusThirdHeating']['HeatedProperties']['Temperature']
	Efficiencies[counter]=CycleParameters['CycleRealEfficiency']
	if (counter>0) and (Efficiencies[counter]<Efficiencies[counter-1]) and (OptimalMinPressure is None):
		OptimalMinPressure=MinPressures[counter-1]

	ExergyEfficiencies[counter]=CycleParameters['CycleExergyEfficiency']

	print 'Minimum Pressure: '+str(MinPressures[counter])
	print 'Real Cycle:   '+str(CycleParameters['CycleRealEfficiency'])
	print


print
print
print 'Optimal Min Pressure: '+str(OptimalMinPressure)


PressureRatios=MaxPressures/MinPressures









#setup a much simpler plotter for the serial constant volume cycle parameter sweep

TheFigure,ThePlot,TheLines=CreateFigure(TitleTEXT='Maximum Thermal Efficiency='+helpers.RoundAndPadToString(Efficiencies.max()*100,2)+'%, Maximum Exergy Efficiency='+helpers.RoundAndPadToString(ExergyEfficiencies.max()*100,2)+'%',HorizontalAxisTEXT=r'Minimum Pressure [MPa]',VerticalAxisTEXT=r'Efficiency [%]',AspectRatio=float(4)/3,FontScaling=200)
TheLines+=ThePlot.plot(MinPressures*10**-6,Efficiencies*100,label=r'Thermal Efficiency',color='blue')
TheLines+=ThePlot.plot(MinPressures*10**-6,ExergyEfficiencies*100,label=r'Exergy Efficiency',color='green')

ThePlot_SecondVerticalAxis=AddSecondVerticalAxis(TheFigure,ThePlot,r'Temperature [K]')
TheLines+=ThePlot_SecondVerticalAxis.plot(MinPressures*10**-6,MaxTemperatures,label=r'Maximum Temperature',color='red',marker='o',markevery=len(MinPressures)/20)

TheSubPlot,TheSubPlotLines=AddASubPlotBelow(TheFigure,ThePlot,HorizontalAxisTEXT=None,VerticalAxisTEXT=r'Maximum Presure [MPa]',TheOtherPlotSecondVerticalAxis=ThePlot_SecondVerticalAxis)
TheSubPlotLines+=TheSubPlot.plot(MinPressures*10**-6,MaxPressures*10**-6,label='Maximum Pressure',color='blue',linewidth=5)

TheSubPlot_SecondVerticalAxis=AddSecondVerticalAxis(TheFigure,TheSubPlot,r'Pressure Ratio')
TheSubPlotLines+=TheSubPlot_SecondVerticalAxis.plot(MinPressures*10**-6,PressureRatios,label=r'Pressure Ratio',color='red',marker='o',markevery=len(MinPressures)/20)


AddMultiAxisLegend(ThePlot,TheLines,loc=6)
AddMultiAxisLegend(TheSubPlot,TheSubPlotLines,loc=2)

BaseOutputFilePath='scratch/'

SaveTheFigure(TheFigure,FileName=BaseOutputFilePath+'/'+'ConstantVolumeMinimumPressureSweep35MPa.pdf')







