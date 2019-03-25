###############################################################################
###############################################################################
#Copyright (c) 2016, Andy Schroder
#See the file README.md for licensing information.
###############################################################################
###############################################################################


import os,inspect
from numpy import asarray,arange,ceil,floor,around,array





#make a special dictionary that automatically makes sub dictionaries instead of having to make them explicitly defined
#SmartDictionary needs to be setup in a separate module because of this bug: https://bugs.launchpad.net/ipython/+bug/363115
class SmartDictionary(dict):
	def __missing__(self, key):
		self[key]=SmartDictionary()
		return self[key]



#simple function to test whether one value is within a certain percentage of another
#just made to clean up a lot of conditional statements where the test below would be needed to account for roundoff errors that won't make things exactly equal
def CheckPercentage(Value,RelativeTo,PercentError):
	if RelativeTo*(1-PercentError/100)<=Value<=RelativeTo*(1+PercentError/100):
		return True
	else:
		return False



#round a number to so many decimal places and zero pad if necessary and convert to a string
#note, need to go through the code and put this all places and remove some duplicate code where it was hardcoded in a couple of times before this function was made.
#can use isinstance(np.array([]),np.ndarray) to check to see if it is an array or not
#from decimal import Decimal
def RoundAndPadToString(Value,DecimalPlaces=3,LeftPad=None,PadCharacter=' '):
#	PLACES=Decimal('10')**-DecimalPlaces	#setup the number of decimal places for use. no idea why the input is a string here and below.
	LeftPadding=''
	if LeftPad is not None:
		#pad digits left of decimal place (LeftPad=2 for example converts "0.1" to " 0.1") up to this digit
		for digit in irange(2,LeftPad):		#skip the first digit, even if specified because it will always be there (will be a 0 if the value is less than 1) with the current formatting method used below
			if Value<10.0**(digit-1):
				LeftPadding+=str(PadCharacter)
				if digit in iarange(4,LeftPad,3):	#every 3rd digit, starting with the fourth
					#be smart enough to also add padding for thousands separators
					LeftPadding+=str(PadCharacter)
	return LeftPadding+'{1:,.{0}f}'.format(DecimalPlaces,Value)		#still don't understand this formatting syntax, but it works
#str(Decimal(str(Value)).quantize(PLACES))

#unpack each values in an array and add a comma and space between the values and return that as a string
def RoundAndPadArrayToString(Values,DecimalPlaces=3,LeftPad=None,PadCharacter=' '):
	String=''
	for ValueNumber in range(len(Values)):
		String+=RoundAndPadToString(Values[ValueNumber],DecimalPlaces,LeftPad,PadCharacter)

		#don't need a separator on the last item
		if ValueNumber<len(Values)-1:
			String+=',   '

	return String



def nearestMultiple(number,multiplier,direction=None):
	#round to any number, not just a multiple of 10 like most other rounding functions do
	#accepts an array or integer or float
	#returns a float or an array with type float

	if direction=='up':
		rounder=ceil
	elif direction=='down':
		rounder=floor
	elif direction is None:
		rounder=around
	else:
		raise Exception('direction not understood')

	return rounder(array(number).astype(float)/float(multiplier))*float(multiplier)



#simple functions for converting to/from celsius/kelvin, so code doesn't have to have addition in fields and so don't have to remember the .15.
def Kelvin(Celsius):
	return Celsius+273.15
def Celsius(Kelvin):
	return Kelvin-273.15


#simple function to create a string for printing that includes both celsius and kelvin temperatures, from a kelvin temperature.
def Kelvin2CelsiusAndKelvinString(Kelvin,DecimalPlaces=3,LeftPad=None):
	return RoundAndPadToString(Celsius(Kelvin),DecimalPlaces,LeftPad)+'C,  '+RoundAndPadToString(Kelvin,DecimalPlaces,LeftPad)+'K'

def Kelvin2CelsiusAndKelvinString2(Kelvin,DecimalPlaces=3,LeftPad=None):
	return RoundAndPadToString(Kelvin,DecimalPlaces,LeftPad)+' ['+RoundAndPadToString(Celsius(Kelvin),DecimalPlaces,LeftPad)+']'






#split a list l into n equal length chunks (except 1 chunk may be off in length due to remainder if not equally divisible)
#it would be nice to also make this split a numpy array into a list of numpy arrays, rather than just being able to split a list into a list of lists
#also, note that this will convert a tuple into a list of tuples
def partition(lst, n):
	if (len(lst)==0 and n==0):
		#list is empty, so don't try to parition it
		return list()		#return a new empty list, because just returning lst is not going to always work since it could actually be an array and calls to this function really expect a list.
	else:
		division = len(lst) / float(n)
		return [ lst[int(round(division * i)): int(round(division * (i + 1)))] for i in xrange(n) ]




#need an n dimensional meshgrid for setting up the permutation set for the design space explorer, which numpy doesn't have already
def meshgrid2_off(*arrs):
	#taken from http://stackoverflow.com/questions/1827489/numpy-meshgrid-in-3d, but then modified and also made to not reverse the indices like regular meshgrid does
	#note, new version of numpy accomplishes this same thing, if the indexing='ij' option is used.

	#also, the new numpy meshgrid version also has a sparse=True option which allows for creating an array that has size of 1 for each dimension that has values repeated (saves memory, etc)
	#don't know if sparse is really the most technically correct word they could have used for that option.
	#using "sparse" arrays works because of http://docs.scipy.org/doc/numpy/user/basics.broadcasting.html
	#however, don't think it is okay to use though when flattening the grid for setting up indexable permutation numbered inputs.

	#another thing that is better with the new numpy meshgrid version is it actually will accept a scalar instead of a 1-D array of length 1 for one of the arrays represeting
	#the coordinates of an axis of the grid, which is more convenient.
	#the new numpy version of meshgrid doesn't rely on a length of the array that defines the coordinates of the axis, but rather http://docs.scipy.org/doc/numpy/user/basics.broadcasting.html
	#because of this option to use a scalar, just switching over to the new numpy meshgrid function instead of making this one also do the option of giving a scalar as an input.

	#wanted to see if there was a way that scalars could just be skipped and pretty much pass through transparently in this meshgrid2 function
	#in order to reduce the amount of unnecessary data when there are many scalar parameters. however, this has a similiar problem
	#as trying to use the new sparse=True option described above with flattening the grid and setting up an indexable permutation of numbered inputs.
	#it could be done, contrary to using the sparse=True, but it would loose generalization in many parts of the code that want to create and
	#use those flattened grids for all parameters, rather than just some. so, it's probably not worth trying since the scalar parameters don't
	#add more data to all the non-scalar parameters, just another dimension of size of 1 which is nothing when flattened. (adding more scalar
	#parameters doesn't exponentially increase the amount of data for the permutation count, it linearly increases it, which is not as huge of a deal.
	#also, usually when a lot of scalar parameters will be used, there will be a very small number of non-scalar parameters, so the total number of
	#data points won't be that big for each parameter.
	#however, in (non-brute force) optimizer parameter sweep mode, really have to loose some generalization with the inputs, and manually control what is a scalar parameter
	#so, the problem is even less of a deal


	arrs = tuple(arrs)		#this is not the same as regular meshgrid (and the example linked above), because don't like the way meshgrid does it in reverse. don't know that this line is even needed at alls ince the reverse statement was removed???
	lens = map(len, arrs)
	dim = len(arrs)

	sz = 1					#initialize variable
	for s in lens:
		sz*=s

	ans = []
	for i, arr in enumerate(arrs):
		slc = [1]*dim			#initialize variable? can this just be done with "ones"?
		slc[i] = lens[i]
		arr2 = asarray(arr).reshape(slc)
		for j, sz in enumerate(lens):
			if j!=i:
				arr2 = arr2.repeat(sz, axis=j) 
		ans.append(arr2)

	return tuple(ans)




#short function that writes binary data to a file so plotting can be made to work with both webserver and files easily.
def WriteBinaryData(Data,File):
	TheFile=open(File,'wb')
	TheFile.write(Data)
	TheFile.close()



#print out values of a dictionary heirarchically
def PrintKeysAndValues(Title,Variable,Indention=''):
	if Indention is '':	#add a separator if the top level
		print "==========================================="
		print Title
		print "==========================================="
	else:
		print Indention+Title
	
	for key in sorted(Variable.keys()):
		if isinstance(Variable[key], dict):		#if the value is also a dictionary, print each value of this dictionary separately as well, and indent
			PrintKeysAndValues(key+":",Variable[key],'            '+Indention)
		else:
			print Indention+'            '+key+": "+str(Variable[key])

	if Indention is '':	#add an extra space if the top leval
		print ""
	return None	



#make an easy way to control if warning messages are printed out
PrintWarningMessages=False
def PrintWarning(Message):
	if PrintWarningMessages:
		print Message











#define a more intelligent range and arange function because the default one is stupid for many uses and doesn't include the endpoint
def irange(start=None,stop=None,step=1):
	if (start is not None) and (stop is None) and (step is 1):
		#then user actually wants to just specify the stop
		stop=start
		start=1					#default to 1 instead of 0
	elif (start is None) and (stop is not None):
		start=1					#default to 1 instead of 0
 	elif (start is None) and (stop is None):
		raise Exception('must specify a stop value')

	return range(start,stop+1,step)			#note, range's stop (actually stop-1) value is the maximum it can get to, but will be less if stop-1-step is not a multiple of step

def iarange(start=None,stop=None,step=1):			#numpy array version
	if (start is not None) and (stop is None) and (step is 1):
		#then user actually wants to just specify the stop
		stop=start
		start=1					#default to 1 instead of 0
	elif (start is None) and (stop is not None):
		start=1					#default to 1 instead of 0
 	elif (start is None) and (stop is None):
		raise Exception('must specify a stop value')


	return arange(start,stop+1,step)		#note, arange's stop (actually stop-1) value is the maximum it can get to, but will be less if stop-1-step is not a multiple of step










#search for the indices of an element containing a substring in a numpy array
def FindSubString(NumpyArray,Substring):
	return array([Substring in s for s in NumpyArray.flat]).reshape(NumpyArray.shape).nonzero()













def GetCaseName():
	#assume the current script's file name is what the naming of the output files should be based on.
	#obviously, this function will not work right if it is called directly/manually from the interpreter and not from a calling script file of any kind.

	#have to do some special stuff to also work with execfil, which is what run files are started with

	RelativeFileName=inspect.getframeinfo(inspect.stack()[1][0]).filename		#find the file name of the calling frame relative to the current working directory.

	AbsolutePath=os.path.abspath(RelativeFileName)					#find the absolute path to the current frame
	FileName=os.path.split(AbsolutePath)[1]						#find just the file name
	FilePrefix = os.path.splitext(FileName)[0]					#find the prefix only

	return FilePrefix













