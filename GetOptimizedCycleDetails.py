###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


from helpers import SmartDictionary,RoundAndPadToString
import cPickle
BaseInputFilePath='outputs/'
CaseName='CO2Cycle-Optimized'
CycleParameters=cPickle.load(open(BaseInputFilePath+'/'+CaseName+'/Results.p', 'rb'))[0]


print "CycleParameters['PreCompressor']['PressureRatio']:               "+RoundAndPadToString(CycleParameters['PreCompressor']['PressureRatio'],1)
print "CycleParameters['MainCompressor']['PressureRatio']:              "+RoundAndPadToString(CycleParameters['MainCompressor']['PressureRatio'],1)
print "RecompressionFraction:                                           "+RoundAndPadToString(CycleParameters['ReCompressor']['MassFraction']*100,1)+'%'
print "main compressor outlet pressure:                                 "+RoundAndPadToString(CycleParameters['MainCompressor']['CompressedProperties']['Pressure']/1e6,1)+'MPa'
print
print "CycleParameters['ReCompressor']['PressureRatio']:                "+RoundAndPadToString(CycleParameters['ReCompressor']['PressureRatio'],1)
print "CycleParameters['VirtualTurbine']['PressureRatio']:              "+RoundAndPadToString(CycleParameters['VirtualTurbine']['PressureRatio'],1)
print "CycleParameters['PowerTurbine']['PressureRatio']:                "+RoundAndPadToString(CycleParameters['PowerTurbine']['PressureRatio'],1)




#as mentioned in a comment in Cycles.py, the following should be called TotalWorkFraction instead of NetWorkFraction
print "MainCompressorTurbine back work ratio:                           "+RoundAndPadToString(CycleParameters['MainCompressorTurbine']['NetWorkFraction']*100,1)+'%'
print "PreCompressorTurbine back work ratio:                            "+RoundAndPadToString(CycleParameters['PreCompressorTurbine']['NetWorkFraction']*100,1)+'%'
print "ReCompressorTurbine back work ratio:                             "+RoundAndPadToString(CycleParameters['ReCompressorTurbine']['NetWorkFraction']*100,1)+'%'
print "BackWorkRatio:                                                   "+RoundAndPadToString(CycleParameters['BackWorkRatio']*100,1)+'%'

print "CycleParameters['MTRecuperator']['Effectiveness']:               "+RoundAndPadToString(CycleParameters['MTRecuperator']['Effectiveness']*100,1)+'%'
print "CycleParameters['MTRecuperator']['phi']:                         "+RoundAndPadToString(CycleParameters['MTRecuperator']['phi']*100,1)+'%'

print "CycleParameters['HTRecuperator']['Effectiveness']:               "+RoundAndPadToString(CycleParameters['HTRecuperator']['Effectiveness']*100,1)+'%'
print "CycleParameters['HTRecuperator']['phi']:                         "+RoundAndPadToString(CycleParameters['HTRecuperator']['phi']*100,1)+'%'



RecuperatedHeat=CycleParameters['HTRecuperator']['SpecificHeatRecuperated_TotalMassFlow']+CycleParameters['MTRecuperator']['SpecificHeatRecuperated_TotalMassFlow']
HeatAdded=CycleParameters['TotalSpecificHeatAdded_TotalMassFlow']

print "MTR heating power:                                               "+RoundAndPadToString(CycleParameters['MTRecuperator']['SpecificHeatRecuperated_TotalMassFlow']/HeatAdded*100,1)+'%'
print "HTR heating power:                                               "+RoundAndPadToString(CycleParameters['HTRecuperator']['SpecificHeatRecuperated_TotalMassFlow']/HeatAdded*100,1)+'%'
print "HTR+MTR heating power:                                           "+RoundAndPadToString(RecuperatedHeat/HeatAdded*100,1)+'%'

print "SpecificNetWork:                                                 "+RoundAndPadToString(CycleParameters['SpecificNetWork']/1000,1)+'kJ/kg'







print
print 'not currently checking low temperature recuperators'

print
print 'medium temperature recuperator'
for HeaterOrCooler in [CycleParameters['MTRecuperator']['HighPressure']['StartingProperties']['HeatAdded_TotalMassFlow'],CycleParameters['MTRecuperator']['HighPressure']['RecuperatedProperties']['HeatAdded_TotalMassFlow'],CycleParameters['MTRecuperator']['LowPressure']['StartingProperties']['HeatRejected_TotalMassFlow'],CycleParameters['MTRecuperator']['LowPressure']['RecuperatedProperties']['HeatRejected_TotalMassFlow']]:
	if abs(HeaterOrCooler)>5:
		print 'heater or cooler exists'
	else:
		print 'heater or cooler is effectively non-existent'

print
print 'high temperature recuperator'
for HeaterOrCooler in [CycleParameters['HTRecuperator']['HighPressure']['StartingProperties']['HeatAdded_TotalMassFlow'],CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties']['HeatAdded_TotalMassFlow'],CycleParameters['HTRecuperator']['LowPressure']['StartingProperties']['HeatRejected_TotalMassFlow'],CycleParameters['HTRecuperator']['LowPressure']['RecuperatedProperties']['HeatRejected_TotalMassFlow']]:
	if abs(HeaterOrCooler)>5:
		print 'heater or cooler exists'
	else:
		print 'heater or cooler is effectively non-existent'








