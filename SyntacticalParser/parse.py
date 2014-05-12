# Hillel Weintraub
# 4/14/14
# parse.py - My implementation of the Earley algorithm for syntactic parsing of a sentence.
# 			 I also return the valid parse trees that exist


from nltk import Tree

# class Production
# a class that represents a grammar rule in a CFG
class Production:
	def __init__(self,lhs,rhs):
		self.LHS = lhs  # a string
		self.RHS = rhs  # a tuple
	def getRHS(self):
		return self.RHS
	def getLHS(self):
		return self.LHS

# class State
# a class to store the states used in the dynamic programming algorithm
class State:
	def __init__(self,arg1,startPos=None,currPos=None,currSymIdx=None):
		if isinstance(arg1,Production):
			production = arg1
			self.production = production
			self.startPos = startPos
			self.currPos = currPos 
			self.currSymIdx = currSymIdx
			self.children = [None for i in xrange(len(self.production.RHS))]
		else:
			state = arg1
			self.production = state.getProduction()
			self.startPos = state.getStartPos()
			self.currPos = state.getCurrPos()
			self.currSymIdx = state.getCurrSymIdx()
			self.children = [child for child in state.getChildren()]

	def __eq__(self,other):
		if not isinstance(other,State): return False
		return (self.production == other.production 
			   and self.startPos == other.startPos
			   and self.currPos == other.currPos
			   and self.currSymIdx == other.currSymIdx)
	def getSetTuple(self):
		return (self.getStartSym(),self.startPos)
	def getChildren(self):
		return self.children
	def setChild(self,childNum,state):
		self.children[childNum] = state
	def getProduction(self):
		return self.production
	def getStartPos(self):
		return self.startPos
	def getStartSym(self):
		return self.production.getLHS()
	def setStartPos(self,startPos):
		self.startPos = startPos
	def getCurrPos(self):
		return self.currPos
	def setCurrPos(self,currPos):
		self.currPos = currPos
	def getCurrSymIdx(self):
		return self.currSymIdx
	def setCurrSymIdx(self,currSymIdx):
		self.currSymIdx = currSymIdx
	def getLHS(self):
		return self.production.getLHS()
	def getRHS(self):
		return self.production.getRHS()
	def getCurrSym(self):
		if self.isComplete(): return None
		return self.production.getRHS()[self.currSymIdx]
	def isComplete(self):
		return self.currSymIdx == len( self.production.getRHS() )
	def isParse(self,grammar):
		return self.isComplete() and self.getStartPos() == 0 and self.getStartSym() == grammar.getStartSym()

# class Grammar
# a class to store all the productions in a CFG
class Grammar:
	def __init__(self):
		self.prodDict = {}
		self.startSymbol = ""
		filename = raw_input("Enter the name of a file from which to load in a grammar: ")
		with open(filename,'r') as f:
			for line in f:
				if line == '\n': continue
				if line[0] == '#': continue
				if line[0:6] == '%start': 
					line = line.split()
					self.startSymbol = line[1]
					continue
				line = line.split('->')
				lhs = line[0].strip()
				if self.startSymbol == "": 
					self.startSymbol = lhs
				rhslist = line[1].split(' | ')
				for rhs in rhslist:
					rhs = tuple(rhs.split())
					production = Production(lhs,rhs)
					if production.getLHS() not in self.prodDict:
						self.prodDict[production.getLHS()] = [production]
					else: self.prodDict[production.getLHS()].append(production)
	
	def getProdsByLHS(self,lhs):
		if lhs in self.prodDict:
			return self.prodDict[lhs]
		else: return []
	
	def isPOS(self,lhs):
		if lhs not in self.prodDict: return False
		else: 
			sym = self.getProdsByLHS(lhs)[0].getRHS()[0]
			if sym in self.prodDict: return False
			else: return True

	def getStartSym(self):
		return self.startSymbol

# predictor()
# adds new states to the current cell for each production
# that exists in the grammar for the current symbol in the current state
def predictor(state,grammar,cell,setcell):
	#print 'predictor called in cell', state.getCurrPos()
	setTuple = (state.getCurrSym(),state.getCurrPos())
	if setTuple in setcell: return
	for production in grammar.getProdsByLHS( state.getCurrSym() ):
		newstate = State(production,state.getCurrPos(),state.getCurrPos(),0)
		cell.append(newstate)
		setcell.add(newstate.getSetTuple())

# scanner()
# adds a new state to the next cell if the word in the sentence matches 
# the POS curent symbol in the current state
def scanner(sentence, state, grammar, nextcell,nextsetcell):
	#print 'scanner called in cell', state.getCurrPos()
	setTuple = (state.getCurrSym(),state.getCurrPos())
	if setTuple in nextsetcell: return
	for production in grammar.getProdsByLHS( state.getCurrSym() ):
		if sentence[ state.getCurrPos() ] == production.getRHS()[0][1:-1]: #[1:-1] to strip the "" for comparison
			newstate = State(production,state.getCurrPos(),state.getCurrPos()+1,1)
			nextcell.append( newstate )
			nextsetcell.add(newstate.getSetTuple())
			break

# completer()
# adds a new state to the current cell by joining a current completed production with 
# productions in previous cells that were searching for the given production
def completer(state,chart):
	#print 'completer called in cell', state.getCurrPos()
	for s in chart[ state.getStartPos() ]:
		if state.getLHS() == s.getCurrSym():
			newstate = State(s)
			newstate.setCurrPos( state.getCurrPos() )
			newstate.setCurrSymIdx(newstate.getCurrSymIdx()+1)
			newstate.setChild(s.getCurrSymIdx(),state)
			chart[state.currPos].append( newstate )

# parseSentence()
# THe main implementation of the Earley algorithm to parse a sentence and fill in
# the parse chart
def parseSentence(sentence,grammar):
	chart = [ [] for i in xrange(len(sentence)+1)]
	setchart = [ set() for i in xrange(len(sentence)+1)]
	production = Production( 'dummyinitstate',tuple([grammar.getStartSym()]) )
	startstate=State(production,0,0,0)
	chart[0].append(startstate); setchart[0].add(startstate.getSetTuple())
	for c in xrange(len(chart)):
		cell = chart[c]; setcell = setchart[c] 
		i = 0
		while i<len(cell): #for each state in the cell
			#print i, 'th state in', c, 'th cell'
			state = cell[i]
			if not state.isComplete() and not grammar.isPOS( state.getCurrSym() ):
				predictor(state,grammar,cell,setcell)
			else:
				if not state.isComplete() and grammar.isPOS( state.getCurrSym() ):
					if c == len(chart)-1: 
						i+=1
						continue
					scanner(sentence, state, grammar, chart[c+1],setchart[c+1])
				else:
					completer(state,chart)
			i+=1
	return chart

# getNumParses()
# A function that determines and returns the number of possible valid parses of the sentence
# using the given CFG
def getNumParses(chart,grammar):
	numParses = 0
	for state in chart[len(chart)-1]:
		if state.isParse(grammar): numParses +=1
	return numParses

# printChart()
# A function that prints the parse chart in a readable format
def printChart(chart):
	i=0
	for cell in chart:
		print "Cell #{}:".format(i)
		printCell(cell)
		i+=1

# printCell()
# A function that prints the given cell in a parse chart in a readable format
def printCell(cell):
	for state in cell:
		printState(state)

# printState()
# A function that prints the given state in a readable format
def printState(state):
	s = state.getProduction().getLHS()
	s+= ' -> '
	for i in xrange(state.getCurrSymIdx()):   
		s+= state.getProduction().getRHS()[i] + ' '
	s+='* '                                       #len(####THis is SIGMA####)
	for i in xrange(state.getCurrSymIdx(),len(state.getProduction().getRHS())):
		s+= state.getProduction().getRHS()[i] + ' '
	s+='   [{},{}]'.format(state.getStartPos(),state.getCurrPos())
	print s 

# buildTreeString()
# A function that builds and returns a string representation of the parse tree 
# rooted at the given state
def buildTreeString(state,treeString):
	if state == None: return treeString
	treeString+='(' + state.getStartSym()+' '
	if state.getChildren()[0] == None:
		treeString+=state.getRHS()[0]+') '
		return treeString
	for child in state.getChildren():
		treeString = buildTreeString(child,treeString)
	treeString+=') '
	return treeString

# writeParsestoFile()
# A function that writes all the valid parses to an output file
def writeParsestoFile(chart):
	filename = raw_input('Enter an output file name to store the parses in: ')
	with open(filename,'w') as f:
		for state in chart[-1]:
			if state.isParse(grammar):
				treeString = buildTreeString(state,'')
				f.write(treeString+'\n')

# drawTree()
# A function that uses nltk to draw the valid parse trees discovered
def drawTrees(chart):
	for state in chart[-1]:
		if state.isParse(grammar):
			treeString = buildTreeString(state,'')
			tree = Tree(treeString)
			print 'Showing parse tree. Close window to continue.'
			tree.draw()
			ans = raw_input('Do you want to see another parse tree?(y/n): ')
			if ans == 'n': return
	print 'No more valid parses'

# A driver program that loads in a grammar, gets an input sentence, finds 
# the valid parses of hte sentence, writes them to an output file, and displays them to the user
if __name__ == "__main__":
	grammar = Grammar()
	sentence = raw_input("Enter a sentence to be parsed: " ).split()
	chart = parseSentence(sentence,grammar)
	writeParsestoFile(chart)
	print 'Number of valid parses:', getNumParses(chart,grammar)
	drawTrees(chart)