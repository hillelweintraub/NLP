#Hillel Weintraub
#ECE 467: Natural Language Processing
#
#TCtrain - a program that trains a text categorization system

from math import log,sqrt
import nltk
import cpickle

class Token:
	"""A class to store the IDF value and list of TF/TFIDF values for a given token (a.k.a. word)"""
	
	class TFIDFStruct: # a nested class/struct to store TF and TFIDF values
		pass
	
	def __init__(self):
		self.TF_dict={}  #key is category name, value is a TFIDF struct for that document
	
	def updateTF(self,category):
		if category in self.TF_dict:
			self.TF_dict[category].TF+=1
		else:
			tfidf = TFIDFStruct()
			tfidf.TF = 1
			self.TF_dict[category] = tfidf
	
	def setIDF(self,N):
		self.IDF =  log(float(N)/self.numdocs)

	def setTFIDF():
		for tfidf in self.TF_dict.values():
			tfidf.TFIDF = self.IDF*tfidf.TF

# getWords()
# tokenizes file and return list of tokens
def getWords(trainingFile): 
	with open(trainingFile,'r') as document:
		wordList = nltk.word_tokenize(document.read())
		wordList = [word.lower() for word in wordList]
		return wordList

# updateCategoryDict()
# update the TF values and the count of the number of docs that contain each word
def updateCategoryDict(categoryDict,wordList,category):
	# update the numdocs count for each word
	wordset = set(wordList)
	for word in wordset:
		if word in categoryDict:
			categoryDict[word].numdocs+=1
		else:
			token = Token()
			token.numdocs=1
			categoryDict[word] = token
	# update the TF values
	for word in wordList:
		categoryDict[word].updateTF(category)

# setTFIDFVals(categoryDict,Numdocs)
# set the IDF and TF-IDF values for all the categories
def setTFIDFVals(categoryDict,Numdocs):
	for token in categoryDict.values():
		token.setIDF(Numdocs)
		token.setTFIDF()

# normalizeCategories(categoryDict)
# normalize each each category so that the sum of the squared TFIDF values equals one
def normalizeCategories(categoryDict):
	scalefactors = {} # a dictionary mapping categories to their scale factors
	# calculate scalefactors
	for token in categoryDict.values():
		for category, tfidf in token.TF_dict.iteritems():
			if category in scalefactors:
				scalefactors[category]+=tfidf.TFIDF**2
			else:
				scascalefactors[category] = tfidf.TFIDF**2
	# update TFIDF values
	for token in categoryDict.values():
		for category, tfidf in token.TF_dict.iteritems():
			tfidf.TFIDF/=sqrt(scalefactors[category])

# buildCategoryDict()
# Builds and  returns inverted index to store the category vectors. 
# It is a dictionary mapping words to Token objects
def buildCategoryDict(): 
	categoryDict = {}
	trainListFileName = raw_input('Please enter the name of the file containing a list of labeled training documents: ')
	with open(trainListFileName,'r') as trainList:
		Numdocs=0
		for line in trainList:
			numdocs+=1
			trainingFile, category = line.split()
			wordList = getWords(trainingFile)     # tokenize file and return list of tokens
			updateCategoryDict(categoryDict,wordList,category) # update the TF values and the number of docs that contain each word
	setTFIDFVals(categoryDict,Numdocs)
	normalizeCategories(categoryDict)
	return categoryDict

# saveCategoryDict(categoryDict)
# saves the built categoryDict to an output file using the cpickle module 
def saveCategoryDict(categoryDict):
	outFile = raw_input('Enter the name of an output file in which to store the learned statistics: ')
	with open(outFile,'wb') as output:
		cpickle.dump(categoryDict,output)

#Driver program: Builds a categoryDict and saves it to a file to be used in TCTest.py
categoryDict = buildCategoryDict()
saveCategoryDict(categoryDict)