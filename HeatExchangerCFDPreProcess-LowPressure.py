###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


from FluidProperties.REFPROP import GetFluidProperties
from helpers import SmartDictionary,RoundAndPadToString
from numpy import array

ChannelHalfHeight=1.5e-3


HeatExchanger=SmartDictionary()

HeatExchanger['HighPressure']['StartingProperties']['Pressure']=5e6
HeatExchanger['HighPressure']['StartingProperties']['Temperature']=600
HeatExchanger['HighPressure']['StartingReDHs']=array([3000])
HeatExchanger['HighPressure']['MassFraction']=1				#kg/kg_LowPressure

HeatExchanger['LowPressure']['StartingProperties']['Pressure']=1e6
HeatExchanger['LowPressure']['StartingProperties']['Temperature']=700





HeatExchanger['HighPressure']['EstimatedRecuperatedProperties']['Pressure']=HeatExchanger['HighPressure']['StartingProperties']['Pressure']
HeatExchanger['HighPressure']['EstimatedRecuperatedProperties']['Temperature']=HeatExchanger['LowPressure']['StartingProperties']['Temperature']

HeatExchanger['LowPressure']['EstimatedRecuperatedProperties']['Pressure']=HeatExchanger['LowPressure']['StartingProperties']['Pressure']
HeatExchanger['LowPressure']['EstimatedRecuperatedProperties']['Temperature']=HeatExchanger['HighPressure']['StartingProperties']['Temperature']

ChannelHeight=2*ChannelHalfHeight
HydraulicDiameter=2*ChannelHeight

HeatExchanger['HighPressure']['StartingProperties']=GetFluidProperties(Temperature=HeatExchanger['HighPressure']['StartingProperties']['Temperature'],Pressure=HeatExchanger['HighPressure']['StartingProperties']['Pressure'],ExtendedProperties=True)
HeatExchanger['HighPressure']['EstimatedRecuperatedProperties']=GetFluidProperties(Temperature=HeatExchanger['HighPressure']['EstimatedRecuperatedProperties']['Temperature'],Pressure=HeatExchanger['HighPressure']['EstimatedRecuperatedProperties']['Pressure'],ExtendedProperties=True)
HeatExchanger['HighPressure']['MassFluxes']=HeatExchanger['HighPressure']['StartingReDHs']*HeatExchanger['HighPressure']['StartingProperties']['DynamicViscocity']/HydraulicDiameter
HeatExchanger['HighPressure']['EstimatedRecuperatedReDHs']=HeatExchanger['HighPressure']['MassFluxes']*HydraulicDiameter/HeatExchanger['HighPressure']['EstimatedRecuperatedProperties']['DynamicViscocity']


HeatExchanger['LowPressure']['StartingProperties']=GetFluidProperties(Temperature=HeatExchanger['LowPressure']['StartingProperties']['Temperature'],Pressure=HeatExchanger['LowPressure']['StartingProperties']['Pressure'],ExtendedProperties=True)
HeatExchanger['LowPressure']['EstimatedRecuperatedProperties']=GetFluidProperties(Temperature=HeatExchanger['LowPressure']['EstimatedRecuperatedProperties']['Temperature'],Pressure=HeatExchanger['LowPressure']['EstimatedRecuperatedProperties']['Pressure'],ExtendedProperties=True)
HeatExchanger['LowPressure']['MassFluxes']=HeatExchanger['HighPressure']['MassFluxes']/HeatExchanger['HighPressure']['MassFraction']

HeatExchanger['LowPressure']['StartingReDHs']=HeatExchanger['LowPressure']['MassFluxes']*HydraulicDiameter/HeatExchanger['LowPressure']['StartingProperties']['DynamicViscocity']
HeatExchanger['LowPressure']['EstimatedRecuperatedReDHs']=HeatExchanger['LowPressure']['MassFluxes']*HydraulicDiameter/HeatExchanger['LowPressure']['EstimatedRecuperatedProperties']['DynamicViscocity']




if __name__ == '__main__':

	print "High Pressure Inlet : Temperature="+str(HeatExchanger['HighPressure']['StartingProperties']['Temperature'])+" K, Pressure="+RoundAndPadToString(HeatExchanger['HighPressure']['StartingProperties']['Pressure'],DecimalPlaces=0,LeftPad=8)+" Pa, Mass Fraction="+RoundAndPadToString(HeatExchanger['HighPressure']['MassFraction'],DecimalPlaces=3)
	print "Low Pressure Inlet  : Temperature="+str(HeatExchanger['LowPressure']['StartingProperties']['Temperature'])+" K, Pressure="+RoundAndPadToString(HeatExchanger['LowPressure']['StartingProperties']['Pressure'],DecimalPlaces=0,LeftPad=8)+" Pa, Mass Fraction=1.000"

	print str(HeatExchanger['HighPressure']['StartingReDHs'].size)+" cases"

	for CaseNumber in range(HeatExchanger['HighPressure']['StartingReDHs'].size):
		print	("High Pressure: Inlet Reynolds Number="+RoundAndPadToString(HeatExchanger['HighPressure']['StartingReDHs'][CaseNumber],DecimalPlaces=0,LeftPad=6)+" , Estimated Outlet Reynolds Number="+RoundAndPadToString(HeatExchanger['HighPressure']['EstimatedRecuperatedReDHs'][CaseNumber],DecimalPlaces=0,LeftPad=6)+" , Mass Flux="+RoundAndPadToString(HeatExchanger['HighPressure']['MassFluxes'][CaseNumber],DecimalPlaces=5,LeftPad=3)+" kg/s/m^2"
			+"   |   "
			+"Low Pressure: Inlet Reynolds Number="+ RoundAndPadToString(HeatExchanger['LowPressure']['StartingReDHs'][CaseNumber],DecimalPlaces=0,LeftPad=6)+ " , Estimated Outlet Reynolds Number="+RoundAndPadToString(HeatExchanger['LowPressure']['EstimatedRecuperatedReDHs'][CaseNumber],DecimalPlaces=0,LeftPad=6)+ " , Mass Flux="+RoundAndPadToString(HeatExchanger['LowPressure']['MassFluxes'][CaseNumber], DecimalPlaces=5,LeftPad=3)+" kg/s/m^2"
			)