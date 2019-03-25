###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


#import some necessary functions
from random import shuffle
from joblib._multiprocessing import mp
from joblib import Parallel, delayed
from helpers import partition,SmartDictionary,PrintKeysAndValues,RoundAndPadToString,RoundAndPadArrayToString,irange,Kelvin2CelsiusAndKelvinString,Kelvin2CelsiusAndKelvinString2,WriteBinaryData
import helpers			#for some reason PrintWarningMessages needs to be accessed as helpers.PrintWarningMessages (only if changed after this file is imported????)
from itertools import chain
import cPickle,time,os
from Cycles import PreCompressionReCompressionCycleWithReheat,SimpleCycle
from numpy import arange,savez,shape,reshape,meshgrid,array
from scipy.optimize import minimize
from FluidProperties.REFPROP import GetFluidProperties,SetupFluid,MethaneHHVoverLHV
from Plotters import PlotCycle

import matplotlib
matplotlib.use('Agg',warn=False)		#needed to allow for a non-x11 renderer to be used in batch mode.
import matplotlib.pyplot as plt			#although already imported matplotlib, do it again so pyplot can be accessed more briefly. this needs to be performed after matplotlib.use('Agg') for some reason
import cStringIO				#allows for sort of a virtual file that can be printed to?


#set the number of CPUs to use. whatever imports this module can change this if it wants, after importing.
NumberOfCPUs=1			#default to running in serial mode


def Worker(FunctionName,ProcessPermutationList):
	#work on the assigned permutations
	ProcessTotalPermutations=len(ProcessPermutationList)
#	print('ProcessTotalPermutations='+str(ProcessTotalPermutations))
	ProcessResults=[]									#initialize list to hold the results
	for ProcessPermutationNumber in range(0,ProcessTotalPermutations):			#need to pass the process permuntation number in addition to the actual permutation number to be able to do a per machine status update
		PermutationNumber=ProcessPermutationList[ProcessPermutationNumber]
		ProcessResults.append(FunctionName(PermutationNumber,ProcessPermutationNumber,ProcessTotalPermutations))			#don't know if append slows things down because every iteration it needs to expand the size of the list, but it doesn't seem to be a problem with 20 million iterations of the for loop.

	return ProcessResults


def ParallelRunTool(FunctionName,PermutationList,NumberOfCPUs=-1):		#note, currently only works with one input and one output per function. also, not sure why, but NumberOfCPUs needs to be passed explicitly???
	shuffle(PermutationList)	#shuffle the results so each process gets about the same workload (otherwise easier ranges would tend to certain machines). note there is a numpy version if ever switch permutation list over to a numpy array for more efficiency. http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.shuffle.html

	if NumberOfCPUs==1:
		#just run in serial mode
		Results=Worker(FunctionName,PermutationList)
	elif NumberOfCPUs == 0:
		raise Exception('NumberOfCPUs can not be equal to 0')
	else:
		#run in parallel
		if NumberOfCPUs < 0:				#if using negative synax style described in joblib documentation, pre-figure out the number of CPUs so can figure out how to divide the permutation list up
			NumberOfCPUs = max(mp.cpu_count() + 1 + NumberOfCPUs, 1)
		#need to package up a list of jobs for each CPU because it is not very efficient spawning a new worker for every iteration, particularly when each job runs very quick.
		PackagedPermutationList=partition(PermutationList,NumberOfCPUs)
		print("Average Permutations/Worker: "+str(float(len(PermutationList))/NumberOfCPUs))

		#do the run
		#returns a list of list of lists, where the main list is all the results for each worker and then the first sub list is all the permutation for that worker and then the subsub list (actually, it may really be a tuple)
		#is a list of all values returned by the objective function for that permutation.
#may want to add more variables that are passed to Worker so less global variables need to be used?
		PackagedResults=Parallel(n_jobs=NumberOfCPUs)(delayed(Worker)(FunctionName,i) for i in PackagedPermutationList)

		#need to unpack the results that were returned by each worker (list of lists) and put them into a single list
		Results=list(chain(*PackagedResults))			#note, these results are all in the same order as PermutationList because joblib is smarter than sage parallel was, but actually doesn't matter because PermutationList was randomized for better workload distribution, so still need to resort below.

	#now that results are all computed and unpacked, need to resort since the original permutation list was shuffled
	Results=[Result for (_,Result) in sorted(zip(PermutationList,Results))]

	return Results



def OutputDirectory():
	#assemble the output directory path
	directory='outputs/'+RunName+'/'

	#make sure the path and directory to save to actually exists
	#this is done every time this function is called, but not positive when function will always be run so does't hurt to check more than once.
	if not os.path.exists(directory):
		os.makedirs(directory)		#if the path does not exist, create it

	return directory


def WriteAdditionalObjects(FixedIndependentVariableValues,NonCO2CycleIndependentVariableLabels,ValueCount):
	#save out a few extra objects needed for post processing
	#this is not the best place to put this because this function has to be called explicitly in every input file
	#could make a smart wrapper function that figures out what you are trying to do based on the existence of CO2 and non-CO2 swept values
	#the existenceo of non-CO2 values, etc. in the input file, and then automatically save these objects at that time, but not bothering to do that right now.
	#don't totally need to write objects out for non-sweep runs but want to just because it's good to have a consolidated folder for the outputs of each run
	#in case want to do something with them programatically later. if skiped saving outputs for non-swept runs, could just put this logic into RunParameterSweepPermutations
	#below and if ObjectiveFunction is ParameterSweepAndOptimizeCombinedCycleWrapper, you know it's the combined cycle case. this would avoid the need for an explicit call
	#or a wrapper function mentioned above, but decided not to do it that way

	directory=OutputDirectory()

	#want to save fixed values for both combined cycle and regular cycle for both a simple optimize and a parameter sweep optimize
	cPickle.dump(FixedIndependentVariableValues, open(directory+'FixedIndependentVariableValues.p', 'wb'))

	#if doing a combined cycle, then also save out these parameters
	if NonCO2CycleIndependentVariableLabels is not None:
		cPickle.dump(NonCO2CycleIndependentVariableLabels, open(directory+'NonCO2CycleIndependentVariableLabels.p', 'wb'))
		cPickle.dump(ValueCount, open(directory+'ValueCount.p', 'wb'))

	return

def WriteResultObject(ResultObject):
	#similiar notes as above for WriteAdditionalObjects

	directory=OutputDirectory()

	cPickle.dump(ResultObject, open(directory+'Results.p', 'wb'))

	return







def SetupPermutations():
	#make the grid of all the permutations of variables
	#note, the variable created is a tuple with each element a grid for each dimension
	IndependentVariableValuesGrid=meshgrid(*IndependentVariableValues,indexing='ij')	#the * causes tuple to expand into separate arguments. also, not sure if it is better if IndependentVariableValues is passed as a function input rather than making it be a global that is inherited that has to be defined in advance?

	#setup the inputs for the parallel optimizer

	#setup a variable with the total number of permutations for easier/simpler code
	TotalPermutations=IndependentVariableValuesGrid[0].size
	print "Total Permutations: "+str(TotalPermutations)

	PermutationList=range(0,TotalPermutations)		#may want to switch this to arange for better efficiency, but will need to make a new partition function, amoung other potential issues to deal with numpy arrays instead of lists

	directory=OutputDirectory()

	#save out the independent variable data so it can be used by the web based post processor and when doing other investigations with the finished run data
	savez(directory+'IndependentVariableValues',IndependentVariableValuesGrid=IndependentVariableValuesGrid,IndependentVariableLabels=IndependentVariableLabels)
	#use cPickle for IndependentVariableValues because savez is designed for arrays and it tries to convert the list to an array but it doesn't work if each element of the list doesn't
	#have the same dimensions. not sure how the labels are saved okay with savez though.
	#although this information is redundant in the .p file, just creating it for convenience so don't need to extract it out of the gridded data exported above if want to know what values of each parameter are used.
	cPickle.dump(IndependentVariableValues, open(directory+'IndependentVariableValues.p', 'wb'))
	#also dump the dictionary mappings which will be used to build up the inputs to the cycle function
	cPickle.dump(IndependentVariableMappings, open(directory+'IndependentVariableMappings.p', 'wb'))

	return	PermutationList,TotalPermutations,IndependentVariableValuesGrid,IndependentVariableMappings,directory			#why is IndependentVariableMappings returned if it is already a gobal?




def RunPermutations():
	global IndependentVariableValuesGridFlat

	#generate the permutation list and independent variables
	PermutationList,TotalPermutations,IndependentVariableValuesGrid,IndependentVariableMappings,directory=SetupPermutations()		#don't need any inputs because everything needed is just inhiereted (but have to be defined in the module by whatever is importing the module).

	#flatten the grids. the permutation numbers will refer to the flattened grids
	IndependentVariableValuesGridFlat=()		#initialize the new variable
	for counter in arange(0,len(IndependentVariableValuesGrid)):
		IndependentVariableValuesGridFlat+=(IndependentVariableValuesGrid[counter].flatten(),)

	#create a timer so can track the speed and predict the time remaining.
	global tic
	tic=time.time()										#start up a timer	###############################need to look around because other scripts have used time.clock(). never noticed the difference because the CPU was probably at 100% all the time for other scripts

	#run
	EfficiencyResults=ParallelRunTool(CyclePermutationWrapper,PermutationList,NumberOfCPUs)

	#do some adjustments to the results
	#package up into a list because post processor allows (not totally implimented) for multiple dependent variables to process, but the above/below optimizer functions actually doesn't yet.
#actually, this will not work right if changing the number of values returned by CyclePermutationWrapper
#see RunParameterSweepPermutations for the right way to do this and actually may want to change ParallelRunTool to return an array instead.
#possibly this way is carried over from the old sage optimizer and didn't realize it was wrong for more than one output with joblib???????
#also, can this function be combined with RunParameterSweepPermutations?
	Results=[EfficiencyResults]
	#reshape each output back to the original shape
	for counter in arange(0,len(Results)):				#note, need to use len, instead of size to make it count the number of items in the list, not total number of items
		Results[counter]=reshape(Results[counter],shape(IndependentVariableValuesGrid[0]))
	#save out the data so it can be used by the web based post processor. probably should work on this more and save some more intermediate data from the cycle?
	savez(directory+'OptimizationResults',Results=Results)

	#done running, now print out some summary information

	#print some blank lines to separate the outputs a little bit
	print
	print
	print

	#print some information on the run and its speed
	OptimizationTime=(time.time()-tic)
	print "Optimization Time: "+RoundAndPadToString(OptimizationTime)+" seconds, "+RoundAndPadToString(OptimizationTime/60)+" minutes, "+RoundAndPadToString(OptimizationTime/3600)+" hours, or "+RoundAndPadToString(OptimizationTime/3600/24)+' days'
	print "Total Permutations: "+str(TotalPermutations)
#note, the following doesn't work right now for -1 convention on NumberOfCPUs
	print "Permutations/second/CPU: "+RoundAndPadToString(TotalPermutations/(OptimizationTime*NumberOfCPUs))
	print "Permutations/second: "+RoundAndPadToString(TotalPermutations/(OptimizationTime))


	return Results



def PrepareInputs(PermutationNumber,FinalizeInputs=True):
	#uses flattened grid from IndependentVariableValues items that are each an array of values to explore

	#this variable needs to be set by whatever imports this module (after importing but before running) or set as a global by another function in this module (RunPermutations), so that don't need to be passed around through parallel function calls, since they they are static for all permutations
	global IndependentVariableValuesGridFlat

	CycleInputParameters=SmartDictionary()

	#assign the mappings based on the previously defined mappings to CycleInputParameters
	for counter in arange(0,len(IndependentVariableMappings)):
		if 'CycleInputParameters' in IndependentVariableMappings[counter]:				#skip other values that aren't related to the cycle (like optimizer settings)
			exec(str(IndependentVariableMappings[counter])+"=IndependentVariableValuesGridFlat["+str(counter)+"][PermutationNumber]")

	if FinalizeInputs:		#might want to do this manually, so leave the option to do so.
		#choose the input parameters file
		#note, don't really need to run this for the cases with low pressure ratio that are skipped, but consolidating here because this command is pretty fast and want to be able to use this entire function in multiple places
		execfile('./InputParameters/InputParameters-CO2.py')

	return CycleInputParameters



def PrepareInputs2(IndependentVariableValues,FinalizeInputs=True):
	#uses a set of values passed directly rather than using a permutation number and looking up the values to use in a flattened grid

	CycleInputParameters=SmartDictionary()

	#assign the mappings based on the previously defined mappings to CycleInputParameters
	for counter in arange(0,len(IndependentVariableMappings)):
		exec(str(IndependentVariableMappings[counter])+"=IndependentVariableValues["+str(counter)+"]")


	if FinalizeInputs:		#might want to do this manually, so leave the option to do so.
		#choose the input parameters file
		#note, don't really need to run this for the cases with low pressure ratio that are skipped, but consolidating here because this command is pretty fast and want to be able to use this entire function in multiple places
		execfile('./InputParameters/InputParameters-CO2.py')

	return CycleInputParameters



#define a wrapper function for the PreCompressionReCompressionCycleWithReheat function
def CyclePermutationWrapper(PermutationNumber=-1,ProcessPermutationNumber=0,ProcessTotalPermutations=0,IndependentVariableValues=None,ExtendedResults=False,MinimalPrint=False):

	if PermutationNumber>-1:
		CycleInputParameters=PrepareInputs(PermutationNumber)
	else:
		CycleInputParameters=PrepareInputs2(IndependentVariableValues)

	#actually had another problem with final optimization (not yet identified), and it was at low overall pressure ratio, which isn't
	#really going to happen with real heat exchangers, so just ignore low overall pressure ratios altogether for
	#now (so there currently is actually an additional (unecessary?) bit about low pressure ratios below)

	if (CycleInputParameters['PreCompressor']['PressureRatio']*CycleInputParameters['MainCompressor']['PressureRatio']<1.1):
		CycleParameters={}
		CycleParameters['CycleRealEfficiency']=0
	else:
		try:
#			import ipdb; ipdb.set_trace()
			CycleParameters=PreCompressionReCompressionCycleWithReheat(CycleInputParameters)
		except KeyboardInterrupt:
			raise
		except:
			if not MinimalPrint:
				print "Warning: Could not successfully compute the cycle. Setting efficiency to -1 to mark this permutation for later debugging."
#			raise

			CycleParameters={}
			CycleParameters['CycleRealEfficiency']=-1
		else:

			#print some status output and info about the current permutation

			if ProcessTotalPermutations!=0:		#only print out timing information if running more than one case.
#may want to completely turn this off, update less frequently, or fix number of digits so output comes up in the same spot and it is easier to read without stopping
				AverageTimePerIteration=(time.time()-tic)/(ProcessPermutationNumber+.0000001)
				TimeRemaining=AverageTimePerIteration*(ProcessTotalPermutations-ProcessPermutationNumber)
				FirstStatusMessageText='Permutation: '+str(PermutationNumber)+', Machine Permutation: '+str(ProcessPermutationNumber)+', Percent Complete:  ' + RoundAndPadToString(100.*ProcessPermutationNumber/ProcessTotalPermutations) + '%       '
				if AverageTimePerIteration<5:
					FirstStatusMessageText+='Time Remaining: ' + RoundAndPadToString(TimeRemaining) + ' seconds, ' + RoundAndPadToString(TimeRemaining/60) + ' minutes, ' + RoundAndPadToString(TimeRemaining/3600) + ' hours, or ' + RoundAndPadToString(TimeRemaining/3600/24) + ' days -- AverageTimePerIteration:  '+RoundAndPadToString(AverageTimePerIteration*1000)+' ms'
				else:
					FirstStatusMessageText+='Time Estimate Not Very Accurate - skipping'
				print FirstStatusMessageText
				#note, need to premultiply by 100. because other two are both integers so it will always come out to zero otherwise unless they are manually converted to another variable type (or if the from future import division option is selected at the beginning of the script).
				#second note, this value is accurate to the number of processors divided by the total number of permutations
				#third note, time remaining also looses accuracy because of permutations that are skipped due to the above if statements. and maybe could be improved by a more intelligent process
				#fourth note, the output will be jumbled together from all processors, so it assumes that all processes are working at about the same speed, otherwise there will be lots of variation in what the status message is indicating

			if not MinimalPrint:
				print 'Efficiency: '+RoundAndPadToString(CycleParameters['CycleRealEfficiency'],5)+'	MaxPress (MPa): '+RoundAndPadToString(CycleInputParameters['MainCompressor']['OutletPressure']/(10**6))+ '	Overall PR: ~'+RoundAndPadToString(CycleInputParameters['PreCompressor']['PressureRatio']*CycleInputParameters['MainCompressor']['PressureRatio'])+'	PreComp PR: '+RoundAndPadToString(CycleInputParameters['PreCompressor']['PressureRatio'])+'	MainComp PR: '+RoundAndPadToString(CycleInputParameters['MainCompressor']['PressureRatio'])+'	ReComp MF: '+RoundAndPadToString(CycleInputParameters['RecompressionFraction'])+'	LTR MF HP MF: '+RoundAndPadToString(CycleInputParameters['LTRecuperator']['MainFraction']['HighPressure']['ComponentMassFraction'])

			if helpers.PrintWarningMessages:
				#print values
				PrintKeysAndValues("Cycle Input Parameters",CycleInputParameters)
				PrintKeysAndValues("Cycle Outputs",CycleParameters)

				print 'Carnot Cycle: '+str(CycleParameters['CycleCarnotEfficiency'])
				print 'Real Cycle:   '+str(CycleParameters['CycleRealEfficiency'])

	if ExtendedResults:
		return CycleParameters
	else:
		return CycleParameters['CycleRealEfficiency']







def CycleOptimizationWrapper(IndependentVariableValues,FixedIndependentVariableValues,MinimalPrint):		#note, args used in optimizers below needs to be in the right order because it doesn't allow keywords to specifiy the variables the arguments refer to

	#add the fixed independent values to the rest of the optimized independent values
	#also convert to tuple if not already a tuple (minimize seems to make it into a numpy array for some reason)
	IndependentVariableValues=tuple(IndependentVariableValues)+FixedIndependentVariableValues

	return -CyclePermutationWrapper(IndependentVariableValues=IndependentVariableValues,MinimalPrint=MinimalPrint)





def OptimizeCycle(InitialGuessIndependentVariableValues,IndependentVariableValueLimits,FixedIndependentVariableValues,MinimalPrint=False):

	#convert FixedIndependentVariableValues to a tuple because it may be a list depending on what the calling function needs to do.
	FixedIndependentVariableValues=tuple(FixedIndependentVariableValues)


#	OptimizedResult=minimize(CycleOptimizationWrapper, InitialGuessIndependentVariableValues, args=(FixedIndependentVariableValues,MinimalPrint), bounds=IndependentVariableValueLimits, method='SLSQP')	#method has to be defined because minimize doesn't automatically choose a method that supports bounds (like it says it should). L-BFGS-B and TNC had problems.


	#initialize the variables to some defaults in case they don't get defined
	popsize=200
	tol=2**-8
	polishtol=5e-5		#None is apparently the default for this option (but must have decided this value is more accurate?)
	polishmaxiter=200	#can't figure out what the default for this actually is (documentation is very bad), so set it to something, also note, the actual number of iterations is actually much higher, this must be some higher level function internal to the optimizer that it is talking about.

	#search for the population size and tolerance, and then assign it if found.
	#IndependentVariableMappings contains both variable and fixed independent variables, so need to skip the variable independent variables because never going to
	#be able to optimize an optimizer parameter.
	Offset=len(IndependentVariableValueLimits)
	for ParameterNumber in range(0,len(FixedIndependentVariableValues)):
		if IndependentVariableMappings[ParameterNumber+Offset] in ['popsize','tol','polishtol','polishmaxiter']:
			exec(IndependentVariableMappings[ParameterNumber+Offset]+'=FixedIndependentVariableValues[ParameterNumber]')

	from _differentialevolution import differential_evolution
	OptimizedResult=differential_evolution(CycleOptimizationWrapper, args=(FixedIndependentVariableValues,MinimalPrint), bounds=IndependentVariableValueLimits,maxiter=10**5,popsize=popsize,tol=tol,disp=True,polishmethod='SLSQP',polishtol=polishtol,polishoptions={'maxiter': polishmaxiter})					#requires a newer version of scipy, so have not tested this yet because it is a pain to install and don't want to muck up the linux install and haven't yet got a virtual machine setup to run everything in there.

#	from scipy.optimize import basinhopping
#	OptimizedResult=basinhopping(CycleOptimizationWrapper, InitialGuessIndependentVariableValues, minimizer_kwargs={'bounds':IndependentVariableValueLimits,'args':(FixedIndependentVariableValues,),'method':'SLSQP'})		#has problems because "bounds" doesn't seem to be working. also doesn't seem to have the "success" attribute, so the following test will not work.
#need to figure out difference between *args and **kwargs again. ---- needed for other optimizer types


	if not OptimizedResult.success:
		raise Exception("optimizer failed. error message is: "+OptimizedResult.message)

	OptimizedIndependentVariableValues=tuple(OptimizedResult.x)

	#add the fixed independent values to the rest of the optimized independent values
	OptimizedAndFixedIndependentVariableValues=OptimizedIndependentVariableValues+FixedIndependentVariableValues

	CycleParameters=CyclePermutationWrapper(IndependentVariableValues=OptimizedAndFixedIndependentVariableValues,ExtendedResults=True)

	return CycleParameters,OptimizedIndependentVariableValues			#also return OptimizedIndependentVariableValues so don't have to recreate it from CycleParameters for use as an initial guess for another optimization run with different FixedIndependentVariableValues #may want to get rid of this if never using a gradient optimizer to start off with? no, because this is also used by the parameter sweep mode.




def PrepareInputs3(PermutationNumber,FixedIndependentVariableValues):
	#uses flattened grid from IndependentVariableValues items that are each an array of values to explore, building up SweptIndependentVariableValuesInstance, and then combines that with FixedIndependentVariableValues.
	#note, this does not eliminate the need for using PrepareInputs2.

	#this variable needs to be set by whatever imports this module (after importing but before running) or set as a global by another function in this module (RunPermutations), so that don't need to be passed around through parallel function calls, since they they are static for all permutations
	global IndependentVariableValuesGridFlat

	#initialize SweptIndependentVariableValuesInstance
	SweptIndependentVariableValuesInstance=()

	#extract values for the current permutation number and add them to SweptIndependentVariableValuesInstance
	for counter in arange(0,len(IndependentVariableValuesGridFlat)):
		SweptIndependentVariableValuesInstance+=(IndependentVariableValuesGridFlat[counter][PermutationNumber],)

	#combine FixedIndependentVariableValues and SweptIndependentVariableValuesInstance
	FixedIndependentVariableValues+=SweptIndependentVariableValuesInstance

	#return the combined value
	return FixedIndependentVariableValues



def ParameterSweepAndOptimizeCycleWrapper(PermutationNumber,ProcessPermutationNumber,ProcessTotalPermutations):
	#not using ProcessPermutationNumber and ProcessTotalPermutations for now but accept them anyway because they are passed by "Worker".
	#not using them because not sure if it is worth trying to come up with a time estimate since don't know how long each instance of the optimizer is going to take.

	global InitialGuessIndependentVariableValues, IndependentVariableValueLimits, FixedIndependentVariableValues

	FixedAndSweptIndependentVariableValues=PrepareInputs3(PermutationNumber,FixedIndependentVariableValues)

	print "Starting Parameter Optimization for FixedIndependentVariableValues: "+str(FixedAndSweptIndependentVariableValues)

	CycleParameters,OptimizedIndependentVariableValues=OptimizeCycle(InitialGuessIndependentVariableValues,IndependentVariableValueLimits,FixedAndSweptIndependentVariableValues)

	return (CycleParameters['CycleRealEfficiency'],)+OptimizedIndependentVariableValues




def RunParameterSweepPermutations(ObjectiveFunction):

	global IndependentVariableValuesGridFlat

	#generate the permutation list and independent variables
	PermutationList,TotalPermutations,IndependentVariableValuesGrid,IndependentVariableMappings,directory=SetupPermutations()		#don't need any inputs because everything needed is just inhiereted (but have to be defined in the module by whatever is importing the module).

	#flatten the grids. the permutation numbers will refer to the flattened grids
	IndependentVariableValuesGridFlat=()		#initialize the new variable
	for counter in arange(0,len(IndependentVariableValuesGrid)):
		IndependentVariableValuesGridFlat+=(IndependentVariableValuesGrid[counter].flatten(),)

	#create a timer so can track the speed and predict the time remaining.
	global tic
	tic=time.time()										#start up a timer	###############################need to look around because other scripts have used time.clock(). never noticed the difference because the CPU was probably at 100% all the time for other scripts

	#run
	UnReShapedResults=array(ParallelRunTool(ObjectiveFunction,PermutationList,NumberOfCPUs))		#convert the list of lists to an array so that it can be sliced properly below

	#reshape each output back to the original shape
	Results=[]
	for counter in arange(0,shape(UnReShapedResults)[1]):
		Results+=[reshape(UnReShapedResults[:,counter],shape(IndependentVariableValuesGrid[0])),]		#all values of IndependentVariableValuesGrid have the same shape
	#save out the data so it can be used by the web based post processor. probably should work on this more and save some more intermediate data from the cycle?
	savez(directory+'OptimizationResults',Results=Results)

	#done running, now print out some summary information

	#print some blank lines to separate the outputs a little bit
	print
	print
	print

	#print some information on the run and its speed
	OptimizationTime=(time.time()-tic)
	print "Optimization Time: "+RoundAndPadToString(OptimizationTime)+" seconds, "+RoundAndPadToString(OptimizationTime/60)+" minutes, "+RoundAndPadToString(OptimizationTime/3600)+" hours, or "+RoundAndPadToString(OptimizationTime/3600/24)+' days'
	print "Total Permutations: "+str(TotalPermutations)
#note, the following doesn't work right now for -1 convention on NumberOfCPUs
	print "Permutations/second/CPU: "+RoundAndPadToString(TotalPermutations/(OptimizationTime*NumberOfCPUs))
	print "Permutations/second: "+RoundAndPadToString(TotalPermutations/(OptimizationTime))

	return Results





def PartitionList(List,MaxNumberOfEngines,NonCO2CycleValueCount):
	#break up into a list of tuples of parameters for each engine. air cycle is different, so it has to be more explicitly done.
	return [List[0:NonCO2CycleValueCount],]+partition(List[NonCO2CycleValueCount:],MaxNumberOfEngines-1)


def CombinedCycle(AllEnginesIndependentVariableValues,AllEnginesFixedIndependentVariableValues,ValueCount,LineColors,CombinedOptimization=False,MinimalPrint=False,PrintSummary=False):		#MinimalPrint overrides PrintSummary printing, and plot generation. also note, args used in optimizers below needs to be in the right order because it doesn't allow keywords to specifiy the variables the arguments refer to.
	#NumberOfEngines is a limit to the number of engines, but the actual number may be less (if the efficiency of the remaining engines that could exist is 0).
	#if CombinedOptimization==False then AllEnginesIndependentVariableValues is an initial guess (AllEnginesInitialGuessIndependentVariableValues), except for the air cycle as indicated below

	#break up into a list of tuples of parameters for each engine.
	PartitionedAllEnginesIndependentVariableValues=PartitionList(AllEnginesIndependentVariableValues,ValueCount[0],ValueCount[1])
	PartitionedAllEnginesFixedIndependentVariableValues=PartitionList(AllEnginesFixedIndependentVariableValues,ValueCount[0],ValueCount[2]+ValueCount[3])

	#search for the number of engines parameter, and then assign it.
	for ParameterNumber in range(0,len(NonCO2CycleIndependentVariableMappings)):
		if NonCO2CycleIndependentVariableMappings[ParameterNumber]=='NumberOfEngines':
			NumberOfEngines=(tuple(PartitionedAllEnginesIndependentVariableValues[0])+tuple(PartitionedAllEnginesFixedIndependentVariableValues[0]))[ParameterNumber]

	#no figure created yet on the first loop, but the variable needs to be defined
	TheFigure=None
	ThePlot=None

	#assemble the path where to save images to. note, this directory is assumed to already exist. should be created when SetupPermutations and/or WriteAdditionalObjects are run
	#and don't want to do any more file system things unnecessarily in a function that can be run many many times and also don't feel like creating another if statement to figure out if the current
	#run is going to be writing data or not.
	directory='outputs/'+RunName+'/'

	EnginePowerOutputList=[]
	CascadeCycleParameters=[]
	EngineNumber=1
	for EngineNumber in irange(1,NumberOfEngines):

		if CombinedOptimization or EngineNumber==1:
			#if CombinedOptimization is False, the first engine (the air cycle) is not optimized at all, so no guesses need to be set.
			#if CombinedOptimization is True, no initial guess is set in this function, it will be set in the higher level optimization function
			IndependentVariableValues=PartitionedAllEnginesIndependentVariableValues[EngineNumber-1]
		else:
			#if CombinedOptimization is False, the first CO2 engine (the second engine) gets a defined initial guess, but the remaining engines get their initial guess from the previous engine's solution.
			#hopefully this is a little more efficient than using the same inital guess for every engine.
			if EngineNumber==2:
				InitialGuessIndependentVariableValues=PartitionedAllEnginesIndependentVariableValues[1]		#as mentioned above, AllEnginesInitialGuessIndependentVariableValues is passed to AllEnginesIndependentVariableValues when CombinedOptimization is False
			else:
				#InitialGuessIndependentVariableValues is not needed for Engine 1 (mentioned above)
				#OR
				#InitialGuessIndependentVariableValues is defined by the previous iteration of the loop, so don't overwrite it.
				pass

		#all CO2 engines currently use the same fixed values (they are just copied in ReplicateCombinedCycleInputs), except for the HighInputTemperature which is overridden
		#so, PartitionedAllEnginesFixedIndependentVariableValues, may have been able to be reduced to len 1 and simplified (loosing some generality)
		#was doing this before when CombinedOptimization is False, but decided it was not worth the loss of generality and simplicity, since
		#initial guesses aren't the same in the combined optimization case for each engine in the cascade
		FixedIndependentVariableValues=PartitionedAllEnginesFixedIndependentVariableValues[EngineNumber-1]

		if EngineNumber==1:
			SetupFluid('air')

			#set some input values that have been commented out in the main input file.
			CycleInputParameters=SmartDictionary()

			#add the fixed independent values to the rest of the optimized independent values
			#also convert to tuple if not already a tuple (minimize seems to make IndependentVariableValues into a numpy array for some reason) and FixedIndependentVariableValues is a list sometimes.
			IndependentVariableValues=tuple(IndependentVariableValues)+tuple(FixedIndependentVariableValues)

			#assign the mappings based on the previously defined mappings to CycleInputParameters
			for counter in arange(0,len(NonCO2CycleIndependentVariableMappings)):
				if 'CycleInputParameters' in NonCO2CycleIndependentVariableMappings[counter]:						#skip other values that aren't related to the air cycle
					exec(str(NonCO2CycleIndependentVariableMappings[counter])+"=IndependentVariableValues["+str(counter)+"]")

			if not MinimalPrint:
				print("PressureRatio: "+str(CycleInputParameters['PressureRatio']))

			#choose the input parameters file
			execfile('./InputParameters/InputParameters-SimpleAirCycle.py')

			HighInputTemperature=CycleInputParameters['MaximumTemperature']						#also define HighInputTemperature because that is what is used for printing below.
			LowOutputTemperature=CycleInputParameters['StartingProperties']['Temperature']				#also define LowOutputTemperature because that is what is used for the other cycles below because they are set to None in the input file for combined cycles

			#also define what the exhaust fluid is because it is needed below when calculating heat extracted
			if (CycleInputParameters['CombinedFuelCellAndCombustor']['FuelCellFuelUtilization']=={}) or (CycleInputParameters['CombinedFuelCellAndCombustor']['FuelCellFuelUtilization']==0):
				ExhaustFluid='air'
				PercentExcessOxygen=None
			else:
				ExhaustFluid='CombustionProducts'
				PercentExcessOxygen=CycleInputParameters['CombinedFuelCellAndCombustor']['PercentExcessOxygen']

			CycleParameters=SimpleCycle(CycleInputParameters)	#not optimizing this air cycle right now indivudually (like the CO2 cycle is below if CombinedOptimization=False) so the initial guess is the value if CombinedOptimization=False.

			#change the fluid back to air from combustion products just so the plotter will work okay.
			SetupFluid('air')

			CycleParameters['MassFlowRate']=CycleInputParameters['PowerOutput']/CycleParameters['SpecificNetWork']		#mass flow rate of AIR
			ExhaustProperties=CycleParameters['PowerTurbine']['ExpandedProperties']
			ExhaustMassFlowRate=CycleParameters['MassFlowRate']

			PowerOutput=CycleInputParameters['PowerOutput']
			CurrentEnginePowerOutput=PowerOutput			#also define another variable that's replaced every loop, not added to
			if 'CombinedFuelCellAndCombustor' in CycleParameters:
				FuelCellPowerOutput=CycleParameters['CombinedFuelCellAndCombustor']['SpecificWorkOutput_TotalMassFlow']*CycleParameters['MassFlowRate']
			else:
				#no fuel cell, so just st the value to zero, so that engine number 0 will always be the fuel cell.
				FuelCellPowerOutput=0

			CycleParameters['FuelCellPowerOutput']=FuelCellPowerOutput

			EnginePowerOutputList+=[FuelCellPowerOutput,]
			EnginePowerOutputList+=[PowerOutput-FuelCellPowerOutput,]

			CombinedCycleEfficiency=CycleParameters['CycleRealEfficiency']		#for the first iteration
			ToppingCycleCarnotEfficiency=CycleParameters['CycleCarnotEfficiency']

			if not MinimalPrint:
				print("ActualMaxTemperature:"+str(CycleParameters['PowerTurbine']['StartingProperties']['Temperature']))

			if (CycleParameters['CycleRealEfficiency']<0.01):
				#current engine could not be solved or has less than 1% efficiency, which is really low.
				#not worth even considering this one or any other engine with an even lower efficiency (the next one in the cascade).
				break

			#wait to do this calculation until after figure out if efficiency is greater than 0
			PowerInput=CycleInputParameters['PowerOutput']/CycleParameters['CycleRealEfficiency']

			#initialize this value to zero so the print statement doesn't error out.
			LowInputTemperature=0

		else:
			#don't need to change fluid to CO2 because it is done below at the end of each iteration of the loop

			if EngineNumber==2:
				HighInputTemperature=CycleParameters['PowerTurbine']['ExpandedProperties']['Temperature']
			else:
				HighInputTemperature=CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties']['Temperature']

			#figure out where the minimum and maximum temperature are defined and then override the value of None in the input file with the same value as the topping cycle
			#for the minimum temperature and the appropriate value for the maximum temperature for this engine.
			for ParameterNumber in range(0,len(IndependentVariableMappings)):
				if IndependentVariableMappings[ParameterNumber]=="CycleInputParameters['StartingProperties']['Temperature']":
					FixedIndependentVariableValues[ParameterNumber-len(IndependentVariableValues)]=LowOutputTemperature		#not to be confused with LowInputTemperature, this is the heat rejection tempreature. it is defined this way so you can sweep a common heat rejection temperature for doing a sensitivity study.
				elif IndependentVariableMappings[ParameterNumber]=="CycleInputParameters['MaximumTemperature']":
					FixedIndependentVariableValues[ParameterNumber-len(IndependentVariableValues)]=HighInputTemperature

			if CombinedOptimization:
				#the higher level combined cylcle calling function is doing the optimizing
				CycleParameters=CyclePermutationWrapper(IndependentVariableValues=(tuple(IndependentVariableValues)+tuple(FixedIndependentVariableValues)),ExtendedResults=True,MinimalPrint=MinimalPrint)				#convert to tuple if not already a tuple (minimize seems to make IndependentVariableValues into a numpy array for some reason) and FixedIndependentVariableValues is a list sometimes.
			else:
				#optimize this engine individually
				#note, this doesn't optimize the number of engines (it can't really)
				#also, there is nothing collecting the OptimizedIndependentVariableValues, so this mode also doesn't allow you to save the best result, and isn't setup to be able to really do as good of a restart with a gradient optimizer.
				CycleParameters,InitialGuessIndependentVariableValues=OptimizeCycle(InitialGuessIndependentVariableValues,FixedIndependentVariableValues,MinimalPrint=MinimalPrint)				#this engine's optimized values are the initial guess for the next engine in the cascade

			if (CycleParameters['CycleRealEfficiency']<0.01):
				#current engine could not be solved or has less than 1% efficiency, which is really low.
				#not worth even considering this one or any other engine with an even lower efficiency (the next one in the cascade).
				break

			if 'HTRecuperator' in CycleParameters:
				LowInputTemperature=CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties']['Temperature']
			else:
#why not a check for other recuperators???
#because right now there is no option in the cycle for them if there is no high temperature recuperator.

				#need to be careful about the minimum temperature that heat is extracted to since there are two mass flow rates in the CO2 engine

				if CycleInputParameters['ReCompressor']['MassFraction']<.01 or CycleInputParameters['PreCompressor']['PressureRatio']<1.01:
					#there is nearly all the mass flow through the main compressor
						#the optimizer should really drive it lower than this recompression fraction
					#or the main compressor and recompressor pretty much have the same oulet temperature (they are really the same thing)
						#this currently only works because the main compressor and precompressor are configured to always have the same inlet temperature
					LowInputTemperature=CycleParameters['MainCompressor']['CompressedProperties']['Temperature']
				else:
					if CombinedOptimization:
						#don't want to let the optimizer even consider this case because it's going to print out a stupid looking plot, so pretty much just make this engine not exist so it is less efficient and the optimizer never picks it
						break
					else:
						if CycleInputParameters['ReCompressor']['MassFraction']>.99:
							#there is pretty much no mass flow through the main compressor, so don't even consider it, no matter what the pressure ratio is.
							LowInputTemperature=CycleParameters['ReCompressor']['CompressedProperties']['Temperature']
						else:
							#there is a partial mass flow through the main compressor
							#don't know why the optimizer would ever pick this when there is no recuperation
							#don't want to bother handling it either
							print "optimizer did something weird and this configuration is not currently handled, ignoring this engine"
							break



			SetupFluid(ExhaustFluid,PercentExcessOxygen=PercentExcessOxygen)
			try:
				HeatExtractedFromAir=ExhaustMassFlowRate*(GetFluidProperties(Pressure=ExhaustProperties['Pressure'],Temperature=HighInputTemperature)['Enthalpy']-GetFluidProperties(Pressure=ExhaustProperties['Pressure'],Temperature=LowInputTemperature)['Enthalpy'])
			except:
				#rather than raise an exception, just set this to zero so the script continues to run and this combined cycle configuration won't have any more engines.
				if not MinimalPrint:
					print "LowInputTemperature is probably too low and REFPROP can't calculate the outlet enthalpy."
				HeatExtractedFromAir=0

			SetupFluid('CO2')	#change fluid back to CO2 so cycle plot will work below and so that if run another script afterwards in the same interpreter that assumes the default fluid of CO2, it will work if there is some rare case where there is no bottoming cycle or the script errors out.

			CurrentEnginePowerOutput=HeatExtractedFromAir*CycleParameters['CycleRealEfficiency']

			if (CurrentEnginePowerOutput/PowerInput<.01) or (CurrentEnginePowerOutput/sum(EnginePowerOutputList,CurrentEnginePowerOutput)<.01):
				#current engine has less than 1% work fraction, or 1% marginal gain in combined cycle efficiency, which is really low.
				#not worth even considering this one or any other engine with an even lower efficiency (the next one in the cascade).
				#also, not combining CycleParameters['CycleRealEfficiency']<0.01 case above here because if it is a failed case, not sure if there is any problem populating LowInputTemperature, so don't even want to try
				break

			EnginePowerOutputList+=[CurrentEnginePowerOutput,]

			PowerOutput+=CurrentEnginePowerOutput
			CombinedCycleEfficiency=PowerOutput/PowerInput


#assumes no pressure drop
#assumes no mini heaters in heat exchangers. need to make a warning for this!!!!!!!!!


			#print values
			if helpers.PrintWarningMessages and (not CombinedOptimization):
				PrintKeysAndValues("Cycle Input Parameters",CycleInputParameters)
				PrintKeysAndValues("Cycle Outputs",CycleParameters)


		#keep a copy of each engine's design so can access at anything later that wasn't explicitly printed
		#and also add a few more combined cycle parameters too

		CycleParameters['HighInputTemperature']=HighInputTemperature
		CycleParameters['LowInputTemperature']=LowInputTemperature
		CycleParameters['PowerOutput']=CurrentEnginePowerOutput			#for the engine with fuel cell, this includes the fuel cell and gas turbine. the fuel cell by itself is CycleParameters['FuelCellPowerOutput'], defined above. subtract the two to get just the gas turbine.

		#these assume this is actually the last engine in the cascade.
		CycleParameters['CombinedCycleEfficiency']=CombinedCycleEfficiency
		CycleParameters['CombinedCycleExergyEfficiency']=CombinedCycleEfficiency/ToppingCycleCarnotEfficiency

		CascadeCycleParameters+=[CycleParameters,]



		#plot the cycle if it is greater than 1% and PrintSummary is set in the combined optimization case (like running after combined optimization has finished) or PrintWarningMessages is set during the non-combined optimization case.
		if 	(
				(
					helpers.PrintWarningMessages and 
					(not CombinedOptimization)
				) or
				PrintSummary
			) and (
				not MinimalPrint
#			) and (
#				CycleParameters['CycleRealEfficiency']>0.01
			):

			#write out a detailed plot for this engine
			WriteBinaryData(PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel='cp',ImageFileType='pdf'),directory+'CombinedCycleEngine-'+str(EngineNumber)+'.pdf')
			#add this engine to the combined engine cascade plot
			TheFigure,ThePlot=PlotCycle(CycleParameters,HorizontalAxis='Entropy',VerticalAxis='Temperature',ContourLevel=None,HorizontalAxisMaxOverride=3000,VerticalAxisMaxOverride=CycleInputParameters['MaximumTemperature']+100,AdditionalAnnotations=False,LineColor=LineColors[EngineNumber-1],ImageFileType='object',TheFigure=TheFigure,ThePlot=ThePlot)

		if EngineNumber==1:		#don't need to do this for other engines because they should already reset back to CO2 above after doing their exhaust gas heat extraction calculation.
			#change the fluid back to CO2 so that if run another script afterwards in the same interpreter that assumes the default fluid of CO2, it will work if there is some rare case where there is no bottoming cycle or the script errors out.
			SetupFluid('CO2')

		if (not MinimalPrint) and ((not CombinedOptimization) or PrintSummary):		#print summary for all non CombinedOptimizations or if explicitly indicated (like when run after combined optimization is finished)
			print ''
			print 'Engine Number:                                  ' +					str(EngineNumber)
			print 'Carnot Cycle:                                ' +						RoundAndPadToString(CycleParameters['CycleCarnotEfficiency']*100,DecimalPlaces=1,LeftPad=3)+							'%'
			print 'Real Cycle:                                  ' +						RoundAndPadToString(CycleParameters['CycleRealEfficiency']*100,DecimalPlaces=1,LeftPad=3)+							'%'
			print 'Exergy Efficiency:                           ' +						RoundAndPadToString((CycleParameters['CycleExergyEfficiency'])*100,DecimalPlaces=1,LeftPad=3)+		'%'
			print 'Combined Cycle Efficiency:                   ' +						RoundAndPadToString(CycleParameters['CombinedCycleEfficiency']*100,DecimalPlaces=1,LeftPad=3)+									'%'
			print 'Combined Cycle Exergy Efficiency:            ' +						RoundAndPadToString(CycleParameters['CombinedCycleExergyEfficiency']*100,DecimalPlaces=1,LeftPad=3)+					'%'
			print 'Maximum Temperature:                         ' +						Kelvin2CelsiusAndKelvinString(CycleParameters['HighInputTemperature'],DecimalPlaces=0,LeftPad=3)
			if 'Temperature' in CycleParameters['VirtualTurbine']['ExpandedProperties']:
				print 'Virtual Turbine Exit Temperature:            ' +					Kelvin2CelsiusAndKelvinString(CycleParameters['VirtualTurbine']['ExpandedProperties']['Temperature'],DecimalPlaces=0,LeftPad=3)
			print 'Power Turbine Exit Temperature:              ' +						Kelvin2CelsiusAndKelvinString(CycleParameters['PowerTurbine']['ExpandedProperties']['Temperature'],DecimalPlaces=0,LeftPad=3)
			if 'Temperature' in CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties']:
				print 'HTR High Pressure Side Exit Temperature:     ' +					Kelvin2CelsiusAndKelvinString(CycleParameters['HTRecuperator']['HighPressure']['RecuperatedProperties']['Temperature'],DecimalPlaces=0,LeftPad=3)
			else:
				print '==no HTR=='
			print 'Minimum Exaust Gas Temperature:              ' +						Kelvin2CelsiusAndKelvinString(CycleParameters['LowInputTemperature'],DecimalPlaces=0,LeftPad=3) 	#will be the same as what is printed above if there is a HTR
			print 'Main Compressor Exit Temperature:            ' +						Kelvin2CelsiusAndKelvinString(CycleParameters['MainCompressor']['CompressedProperties']['Temperature'],DecimalPlaces=0,LeftPad=3)
			print 'Power Turbine Pressure Ratio:                ' +						RoundAndPadToString(CycleParameters['PowerTurbine']['PressureRatio'],DecimalPlaces=1,LeftPad=3)
			print 'Back Work Ratio:                             ' +						RoundAndPadToString(CycleParameters['BackWorkRatio']*100,DecimalPlaces=1,LeftPad=3)+								'%'
			print ''



#		if EngineNumber>1 and ((CycleParameters['PowerTurbine']['ExpandedProperties']['Temperature']<CycleParameters['ReCompressor']['CompressedProperties']['Temperature']) or (CycleParameters['CycleRealEfficiency']<0.01)):
#			#no more engines in the cascade, either because the efficiency of this engine is already reall low (less than 1%) or power turbine outlet temperature is less than recompressor outlet temperature
#why the concern about recompressor outlet temperature????
#			break



	#add some extra text to annotations if using combustion products
	if ExhaustFluid=='CombustionProducts':
		ExtraText=' (HHV),   '+RoundAndPadToString(CombinedCycleEfficiency*100*MethaneHHVoverLHV,2)+'% (LHV)'
	else:
		ExtraText=''


	#finish up plotting of the combined cycle and some other summary activities
	if 	(
			(
				helpers.PrintWarningMessages and 
				(not CombinedOptimization)
			) or
			PrintSummary
		) and (
			not MinimalPrint
		):

		#override the title with the combined cycle information
		TheFigure.suptitle('Combined Cycle Efficiency: '+RoundAndPadToString(CombinedCycleEfficiency*100,2)+'%'+ExtraText+'\nLine widths scaled by mass fraction.\nAir cycle entropy reference is arbitrary and does not follow the same conventions as CO2.',fontsize=12)
		TheFigure.subplots_adjust(top=0.875)		#make room for the multiline title

		#save the image
		image_data = cStringIO.StringIO()					#setup the file handle
		TheFigure.savefig(image_data,format='pdf')				#make the image file

		plt.close('all')							#releases all the RAM that is never released automatically

		WriteBinaryData(image_data.getvalue(),directory+'CombinedCycleEngine.pdf')



		#save the engine design's to a file
		cPickle.dump(CascadeCycleParameters, open(OutputDirectory()+'CascadeCycleParameters.p', 'wb'))


		#print print out some summary information and latex syntax that can be dropped right into the table

		EngineWorkFractions=array(EnginePowerOutputList)/sum(EnginePowerOutputList)					#includes the fuel cell (even though it may be 0), so list is longer than the other variables used below. pay attention to that.
		MarginalCombinedCycleEfficiency=EngineWorkFractions*CombinedCycleEfficiency

		print 'Engine Work Fractions:            '+RoundAndPadArrayToString(EngineWorkFractions*100,2)
		print		#add a blank line

		#first table
		for EngineNumber in irange(1,len(CascadeCycleParameters)):

			FuelCellCycleExtraText=''

			if EnginePowerOutputList[0]!=0:		#consider the fuel cell
				if EngineNumber==1:
					CombinedToppingFuelCellCycleLHVEfficiency=CascadeCycleParameters[EngineNumber-1]['CycleRealEfficiency']*MethaneHHVoverLHV
					FuelCellMarginalLHVEfficiency=MarginalCombinedCycleEfficiency[0]*MethaneHHVoverLHV
					GasTurbineLHVEfficiency=(CombinedToppingFuelCellCycleLHVEfficiency-FuelCellMarginalLHVEfficiency)/(1-FuelCellMarginalLHVEfficiency)

					print(
						'Fuel Cell & \\multirow{2}{*}{1} & '+RoundAndPadToString(EngineWorkFractions[0]*100,DecimalPlaces=2)+
						' & \\multirow{2}{*}{'+
						RoundAndPadToString((EngineWorkFractions[0]+EngineWorkFractions[1])*100,DecimalPlaces=2)+
						'} & '+
						RoundAndPadToString(MarginalCombinedCycleEfficiency[0]*100,DecimalPlaces=2)+
						' & \\multirow{2}{*}{'+
						RoundAndPadToString(CombinedToppingFuelCellCycleLHVEfficiency*100/MethaneHHVoverLHV,DecimalPlaces=2)+
						'} & '+
						RoundAndPadToString(FuelCellMarginalLHVEfficiency*100,DecimalPlaces=2)+
						' & \\multirow{2}{*}{'+
						RoundAndPadToString(CombinedToppingFuelCellCycleLHVEfficiency*100,DecimalPlaces=2)+
						'} & '+
						RoundAndPadToString(FuelCellMarginalLHVEfficiency*100,DecimalPlaces=2)+
						' (LHV) & \\multirow{2}{*}{ '+
						RoundAndPadToString(CombinedToppingFuelCellCycleLHVEfficiency*100,DecimalPlaces=2)+
						' (LHV)} & \\multirow{2}{*}{-}\\tabularnewline'
						)

					print(
						'Gas Turbine &  & '+
						RoundAndPadToString(EngineWorkFractions[EngineNumber]*100,DecimalPlaces=2)+' &  & '+
						RoundAndPadToString(MarginalCombinedCycleEfficiency[EngineNumber]*100,DecimalPlaces=2)+' &  & '+
						RoundAndPadToString(MarginalCombinedCycleEfficiency[EngineNumber]*100*MethaneHHVoverLHV,DecimalPlaces=2)+' &  & '+
						RoundAndPadToString(GasTurbineLHVEfficiency*100,DecimalPlaces=2)+' (LHV) &  & \\tabularnewline'
						)
				else:
					print(
						str(EngineNumber)+' & \multicolumn{2}{c|}{'+
						RoundAndPadToString(EngineWorkFractions[EngineNumber]*100,DecimalPlaces=2)+'} & \multicolumn{2}{c|}{'+
						RoundAndPadToString(MarginalCombinedCycleEfficiency[EngineNumber]*100,DecimalPlaces=2)+'} & \multicolumn{2}{c|}{'+		#in the fuel cell cycle, this will be the HHV case because CombinedCycleEfficiency is based on HHV
						RoundAndPadToString(MarginalCombinedCycleEfficiency[EngineNumber]*100*MethaneHHVoverLHV,DecimalPlaces=2)+'} & \multicolumn{2}{c|}{'+
						RoundAndPadToString(CascadeCycleParameters[EngineNumber-1]['CycleRealEfficiency']*100,DecimalPlaces=2)+'} & '+
						RoundAndPadToString(CascadeCycleParameters[EngineNumber-1]['CycleExergyEfficiency']*100,DecimalPlaces=2)+' \\tabularnewline'
						)

			if EnginePowerOutputList[0]==0:
				print(
					str(EngineNumber)+' & '+
					RoundAndPadToString(EngineWorkFractions[EngineNumber]*100,DecimalPlaces=2)+' & '+
					RoundAndPadToString(MarginalCombinedCycleEfficiency[EngineNumber]*100,DecimalPlaces=2)+' & '+		#in the fuel cell cycle, this will be the HHV case because CombinedCycleEfficiency is based on HHV
					RoundAndPadToString(CascadeCycleParameters[EngineNumber-1]['CycleRealEfficiency']*100,DecimalPlaces=2)+' & '+
					RoundAndPadToString(CascadeCycleParameters[EngineNumber-1]['CycleExergyEfficiency']*100,DecimalPlaces=2)+' \\tabularnewline'
					)

		print		#add a blank line

		#second table
		for EngineNumber in irange(1,len(CascadeCycleParameters)):

			print(
				str(EngineNumber)+' & '+
				Kelvin2CelsiusAndKelvinString2(CascadeCycleParameters[EngineNumber-1]['HighInputTemperature'],DecimalPlaces=0)+' & '+			#probably want to manually delete this one after put into latex for the topping cycle because it is really the power turbine inlet temperature.
				Kelvin2CelsiusAndKelvinString2(CascadeCycleParameters[EngineNumber-1]['LowInputTemperature'],DecimalPlaces=0)+' & '+
				Kelvin2CelsiusAndKelvinString2(CascadeCycleParameters[EngineNumber-1]['PowerTurbine']['ExpandedProperties']['Temperature'],DecimalPlaces=0)+' & '+
				Kelvin2CelsiusAndKelvinString2(CascadeCycleParameters[EngineNumber-1]['MainCompressor']['CompressedProperties']['Temperature'],DecimalPlaces=0)+' \\tabularnewline'
				)


		print		#add a blank line



	print 'Combined Cycle Efficiency:        '+RoundAndPadToString(CombinedCycleEfficiency*100,2)+'%'+ExtraText
	print		#add a blank line



	return -CombinedCycleEfficiency











def OptimizeCombinedCycle(AllEnginesInitialGuessIndependentVariableValues,AllEnginesFixedIndependentVariableValues,ValueCount,LineColors,CombinedOptimization,AllEnginesIndependentVariableValueLimits,MinimalPrint=False):
	if CombinedOptimization:


#		OptimizedResult=minimize(CombinedCycle, AllEnginesInitialGuessIndependentVariableValues, args=(AllEnginesFixedIndependentVariableValues,ValueCount,LineColors,CombinedOptimization,MinimalPrint), bounds=AllEnginesIndependentVariableValueLimits, method='SLSQP')	#method has to be defined because minimize doesn't automatically choose a method that supports bounds (like it says it should). L-BFGS-B and TNC had problems.


		#break up into a list of tuples of parameters for each engine so can grab values for the NonCO2Cycle.
		#note, this partitioning is also done above in CombinedCycle, but can't pass the partitioned variable to the optimizer, so just have to do it twice in order
		#to be able to easily get things out of it. also note, the search loop below setup is slightly different than used for NumberOfEngines above
		PartitionedAllEnginesFixedIndependentVariableValues=PartitionList(AllEnginesFixedIndependentVariableValues,ValueCount[0],ValueCount[2]+ValueCount[3])

		#initialize the variables to some defaults in case they don't get defined
		popsize=200
		tol=2**-8
		polishtol=5e-5		#None is apparently the default for this option (but must have decided this value is more accurate?)
		polishmaxiter=200	#can't figure out what the default for this actually is (documentation is very bad), so set it to something, also note, the actual number of iterations is actually much higher, this must be some higher level function internal to the optimizer that it is talking about.

		#search for the population size and tolerance, and then assign it if found.
		#NonCO2CycleIndependentVariableMappings contains both variable and fixed independent variables, so need to skip the variable independent variables because never going to
		#be able to optimize an optimizer parameter.
		Offset=ValueCount[1]
		for ParameterNumber in range(0,len(PartitionedAllEnginesFixedIndependentVariableValues[0])):
			if NonCO2CycleIndependentVariableMappings[ParameterNumber+Offset] in ['popsize','tol','polishtol','polishmaxiter']:
				exec(NonCO2CycleIndependentVariableMappings[ParameterNumber+Offset]+'=PartitionedAllEnginesFixedIndependentVariableValues[0][ParameterNumber]')


		from _differentialevolution import differential_evolution
		OptimizedResult=differential_evolution(CombinedCycle, args=(AllEnginesFixedIndependentVariableValues,ValueCount,LineColors,CombinedOptimization,MinimalPrint), bounds=AllEnginesIndependentVariableValueLimits,maxiter=10**5,popsize=popsize,tol=tol,disp=True,polishtol=polishtol,polishoptions={'maxiter': polishmaxiter})


		#set the solution as the initial guess so that if change a parameter and re-run without restarting the interpreter, the optimization will have a better starting point.
		AllEnginesInitialGuessIndependentVariableValues=tuple(OptimizedResult.x)

		if not OptimizedResult.success:
			raise Exception("optimizer failed. error message is: "+OptimizedResult.message)


	#re-run and print out the optimal case, using the solution just found. note variable AllEnginesInitialGuessIndependentVariableValues is just set to the solution a few lines above
	#or, if this is not a Combined Optimization, then it will be the first time run
	CombinedCycleEfficiency=-CombinedCycle(AllEnginesInitialGuessIndependentVariableValues,AllEnginesFixedIndependentVariableValues,ValueCount,LineColors,CombinedOptimization,PrintSummary=True,MinimalPrint=MinimalPrint)

	return CombinedCycleEfficiency,AllEnginesInitialGuessIndependentVariableValues			#return AllEnginesInitialGuessIndependentVariableValues so it can be passed back later to get a better initial condition




def ReplicateCombinedCycleInputs(NonCO2Cycle,CO2Cycles,MaxNumberOfEngines):
	#build up the AllEngines variables based on what type of optimization procedure will be used.

	#need to use the upper limit on the number of engines because if sweeping number of engines, need to have the same number of parameters for all engine counts
	#so there will actually be some unused parameters when the actual number of engines is less than the maximum, but hopefully the optimizer will be smart enough
	#to not waste too much time on the extra parameters that are ignored.

	AllEngines=NonCO2Cycle+CO2Cycles*(MaxNumberOfEngines-1)

	return AllEngines


def PrepareInputs4(PermutationNumber,FixedIndependentVariableValues,ValueCount):
	#uses flattened grid from IndependentVariableValues items that are each an array of values to explore, building up SweptIndependentVariableValuesInstance, and then combines that with FixedIndependentVariableValues.
	#note, this does not eliminate the need for using PrepareInputs2.

	#this variable needs to be set by whatever imports this module (after importing but before running) or set as a global by another function in this module (RunPermutations), so that don't need to be passed around through parallel function calls, since they they are static for all permutations
	global IndependentVariableValuesGridFlat

	#initialize SweptIndependentVariableValuesInstance
	SweptIndependentVariableValuesInstance=[]

	#extract values for the current permutation number and add them to SweptIndependentVariableValuesInstance
	for counter in arange(0,len(IndependentVariableValuesGridFlat)):
		SweptIndependentVariableValuesInstance+=(IndependentVariableValuesGridFlat[counter][PermutationNumber],)

	#separate the list
	NonCO2CycleSweptIndependentVariableValuesInstance=SweptIndependentVariableValuesInstance[:ValueCount[3]]
	CO2CycleSweptIndependentVariableValuesInstance=SweptIndependentVariableValuesInstance[ValueCount[3]:]

	#package everything back together
	#doing it this way so that IndependentVariableMappings and NonCO2CycleIndependentVariableMappings match up, and so that the partitioning done by PartitionList works in CombinedCycle.
	NonCO2CycleFixedIndependentVariableValues=FixedIndependentVariableValues[0]+NonCO2CycleSweptIndependentVariableValuesInstance
	CO2CycleFixedIndependentVariableValues=FixedIndependentVariableValues[1]+CO2CycleSweptIndependentVariableValuesInstance

	AllEnginesSweptIndependentVariableValues=ReplicateCombinedCycleInputs(NonCO2CycleFixedIndependentVariableValues,CO2CycleFixedIndependentVariableValues,ValueCount[0])

	#return the combined value
	return AllEnginesSweptIndependentVariableValues





def ParameterSweepAndOptimizeCombinedCycleWrapper(PermutationNumber,ProcessPermutationNumber,ProcessTotalPermutations):
	#not using ProcessPermutationNumber and ProcessTotalPermutations for now but accept them anyway because they are passed by "Worker".

	global AllEnginesInitialGuessIndependentVariableValues, AllEnginesIndependentVariableValueLimits, FixedIndependentVariableValues,ValueCount

	#add the swept variables to AllEnginesFixedIndependentVariableValues
	AllEnginesFixedIndependentVariableValues=PrepareInputs4(PermutationNumber,FixedIndependentVariableValues,ValueCount)


	#set some values that need to be defined for this case
	LineColors=None				#not used, but needs to be defined because the function call expects it, and don't have it set to a default value right now. if want to set it as a default, need to move its position in the function call.
	MinimalPrint=True			#don't display a summary for every iteration
	CombinedOptimization=True		#only do CombinedOptimization for now. it may work but don't know that it is desired anyway.

	print "Starting Parameter Optimization for AllEnginesFixedIndependentVariableValues: "+str(AllEnginesFixedIndependentVariableValues)

	CombinedCycleEfficiency,AllEnginesOptimizedIndependentVariableValues=OptimizeCombinedCycle(AllEnginesInitialGuessIndependentVariableValues,AllEnginesFixedIndependentVariableValues,ValueCount,LineColors,CombinedOptimization,AllEnginesIndependentVariableValueLimits,MinimalPrint)

	return (CombinedCycleEfficiency,)+AllEnginesOptimizedIndependentVariableValues









