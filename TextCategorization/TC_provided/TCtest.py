#Hillel Weintraub
#ECE 467: Natural Language Processing
#
#TCtest - a program that tests a text categorization system/performs text categorization

import cPickle
import nltk
from TCtrain import getWords

# buildDocDict(wordList,categoryDict)
# builds a dictionary mapping words in a document to their TFIDF values
def buildDocDict(wordList,categoryDict):
	docDict = {}
	# get the TF values
	for word in wordList:
		if word in categoryDict:
			docDict[word] = docDict.get(word,0) + 1
    # multiply TF values by IDF values to get TFIDF
	for word in docDict:
		docDict[word]*=categoryDict[word].IDF
	return docDict

# categorizeDocument(categoryDict,docDict,output,document)
# predicts the category of a single document and writes the prediction to an output file
def categorizeDocument(categoryDict,docDict,output,document):
	candidateDict = {} # a dictionary mapping from categories to their similarity with the given document
	for word, tfidf in docDict.iteritems():
		if word in categoryDict:
			for category, tfidfstruct in categoryDict[word].TF_dict.iteritems():
				candidateDict[category] = candidateDict.get(category,0) + tfidf*tfidfstruct.TFIDF
	predictedCategory = max(candidateDict,key=candidateDict.get)
	outstring = '{0} {1}\n'.format(document,predictedCategory)
	output.write(outstring)

# categorizeDocuments(categoryDict)
# categorizes test documents and writes results to an output file
def categorizeDocuments(categoryDict):
	testListFileName = raw_input('Please enter the name of the file containing a list of test documents: ')
	outputFileName = raw_input('PLease enter the name of an output file in which to store the predicted labels: ')
	with open(testListFileName,'r') as testList:
		with open(outputFileName,'wb') as output:
			for document in testList:
				document = document.strip()
				wordList = getWords(document)
				docDict = buildDocDict(wordList,categoryDict)
				categorizeDocument(categoryDict,docDict,output,document)

# loadCategoryDict()
# load in a categoryDict containing previously learned corpus statistics
def loadCategoryDict():
	cdFile = raw_input('Please enter the name of the file containing the saved corpus statistics: ')
	with open(cdFile,'rb') as input:
		categoryDict = cPickle.load(input)
	return categoryDict

#Driver program: Loads in previously saved corpus statistics and performs text categorization on a new test corpora
if __name__ == "__main__":
	categoryDict = loadCategoryDict()
	categorizeDocuments(categoryDict)