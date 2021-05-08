#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import math

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

#
#==============================================================================
class RTSS:
	instanceID = ''
	initExFileName = ''
	initWNetFileName = ''
	nOfTaxi = 0
	newDemandSize = 0
	capacityOfEachTaxi = []
	noListOfPickDrop = [] # sorted (pair adjoining) future via points list of each taxi
	noListOfCarried = []
	noListOfAcceptedPoint = []
	currenTime = 10
	deadlineList = [] # assume that all pick-up points have no deadline request
	deadlineOfNewDemand = []
	viaPointLists = []
	preCaseVarList = []
	assumptionVar = 0
	cosTimeMatrices = [] # note that, the given symmetric cost time matrices have NOT been verified for any Euclidean axioms (such as triangle inequality)
	varID = 0
	maxWidthOfNet = 0
	conNet = []
	rchNet = []
	top = 1
	wcnf = None
	ip = ''
	yVarID = 0
	learntClause = [] # use for debug

	def __init__(self):
		self.instanceID = sys.argv[1]
		self.initExFileName = './' + self.instanceID + '-externality.txt'
		self.initWNetFileName = './' + self.instanceID + '-WNet.txt'
		initFile = open(self.initExFileName, 'r')
		stringBuffer = initFile.readlines()
		difFromCurrenTime = 0
		for line in stringBuffer:
			if line.rstrip().split(' ')[0] == 'nOfTaxi':
				self.nOfTaxi = map(int, line.rstrip().split(' ')[1:])[0]
				print(self.nOfTaxi)
			elif line.rstrip().split(' ')[0] == 'newDemandSize':
				self.newDemandSize = map(int, line.rstrip().split(' ')[1:])[0]
				print(self.newDemandSize)
			elif line.rstrip().split(' ')[0] == 'capacityOfEachTaxi':
				self.capacityOfEachTaxi = map(int, line.rstrip().split(' ')[1:])
				print(self.capacityOfEachTaxi)
			elif line.rstrip().split(' ')[0] == 'noListOfCarried':
				self.noListOfCarried = map(int, line.rstrip().split(' ')[1:])
				print(self.noListOfCarried)
			elif line.rstrip().split(' ')[0] == 'noListOfAcceptedPoint':
				self.noListOfAcceptedPoint = map(int, line.rstrip().split(' ')[1:])
				print(self.noListOfAcceptedPoint)
			elif line.rstrip().split(' ')[0] == 'noListOfPickDrop':
				tmpIntVec = map(int, line.rstrip().split(' ')[1:])
				nextStartIndex = 0
				for i in range(self.nOfTaxi):
					spliTmpIntVec = []
					for j in range(nextStartIndex, nextStartIndex+self.noListOfAcceptedPoint[i]):
						spliTmpIntVec.append(tmpIntVec[j])
					self.noListOfPickDrop.append(spliTmpIntVec[:])
					nextStartIndex += self.noListOfAcceptedPoint[i]
				print(self.noListOfPickDrop)
			elif line.rstrip().split(' ')[0] == 'currenTime':
				difFromCurrenTime = map(int, line.rstrip().split(' ')[1:])[0]
				self.currenTime = 0
				print(difFromCurrenTime)
			elif line.rstrip().split(' ')[0] == 'deadlineList':
				tmpIntVec = map(int, line.rstrip().split(' ')[1:])
				nextStartIndex = 0
				for i in range(self.nOfTaxi):
					spliTmpIntVec = []
					for j in range(nextStartIndex, nextStartIndex+self.noListOfAcceptedPoint[i]):
						spliTmpIntVec.append(tmpIntVec[j] - difFromCurrenTime)
					self.deadlineList.append(spliTmpIntVec[:])
					nextStartIndex += self.noListOfAcceptedPoint[i]
				print(self.deadlineList)
			elif line.rstrip().split(' ')[0] == 'deadlineOfNewDemand':
				self.deadlineOfNewDemand = [i - difFromCurrenTime for i in map(int, line.rstrip().split(' ')[1:])]
				print(self.deadlineOfNewDemand)
			elif line.rstrip().split(' ')[0] == 'viaPointLists':
				tmpIntVec = map(int, line.rstrip().split(' ')[1:])
				nextStartIndex = 0
				for i in range(self.nOfTaxi):
					spliTmpIntVec = []
					for j in range(nextStartIndex, nextStartIndex+self.noListOfAcceptedPoint[i]):
						spliTmpIntVec.append(tmpIntVec[j])
					self.viaPointLists.append(spliTmpIntVec[:])
					nextStartIndex += self.noListOfAcceptedPoint[i]
				print(self.viaPointLists)

		initFile = open(self.initWNetFileName, 'r')
		stringBuffer = initFile.readlines()
		self.cosTimeMatrices = [[] for i in range(self.nOfTaxi)]
		for line in stringBuffer:
			if '_0' in line:
				taxID = int(line.rstrip().replace('_0', '')) - 1
			else:
				self.cosTimeMatrices[taxID].append(map(int, line.rstrip().split(' ')))
		#print(self.cosTimeMatrices)

		print('\n')

		'''
		self.nOfTaxi = 3
		self.newDemandSize = 2
		self.capacityOfEachTaxi = [4, 4, 4]
		self.noListOfPickDrop = [[1, -1], [1, -1, -2], [-3]]
		self.noListOfCarried = []
		for i in range(len(self.noListOfPickDrop)):
			self.noListOfCarried.append(-1 * sum(self.noListOfPickDrop[i]))
		self.noListOfAcceptedPoint = []
		for i in range(len(self.noListOfPickDrop)):
			self.noListOfAcceptedPoint.append(len(self.noListOfPickDrop[i]))
		self.currenTime = 10
		self.deadlineList = [[self.currenTime, 60], [self.currenTime, 80, 100], [50]]
		self.deadlineOfNewDemand = [20, 90]
		self.viaPointLists = [[1, 2], [1, 2, 3], [1]]
		self.cosTimeMatrices = [[[0, 13, 54, 21, 46], 
				[13, 0, 29, 18, 64], 
				[54, 29, 0, 37, 25], 
				[21, 18, 37, 0, 34], 
				[46, 64, 25, 34, 0]], 

				[[0, 11, 38, 62, 19, 57], 
				[11, 0, 27, 45, 36, 49], 
				[38, 27, 0, 48, 65, 40], 
				[62, 45, 48, 0, 21, 31], 
				[19, 36, 65, 21, 0, 34], 
				[57, 49, 40, 31, 34, 0]], 

				[[0, 8, 28, 69], 
				[8, 0, 31, 52], 
				[28, 31, 0, 34], 
				[69, 52, 34, 0]]]
		'''
		self.maxWidthOfNet = 3 + max(self.noListOfAcceptedPoint)
		self.conNet = [[[0] * self.maxWidthOfNet for i in range(self.maxWidthOfNet)] for j in range(self.nOfTaxi)]
		self.rchNet = [[[0] * self.maxWidthOfNet for i in range(self.maxWidthOfNet)] for j in range(self.nOfTaxi)]
		self.top += sum(sum(sum(i) for i in j) for j in self.cosTimeMatrices)
		self.wcnf = WCNF()
		self.ip = 'Enter example\n\n'

	def newVarID(self):
		self.varID += 1
		return self.varID

	def isRequiredVar(self, k, row, column):
		exNoListOfPickDrop = [0] + self.noListOfPickDrop[k] + [self.newDemandSize, -1 * self.newDemandSize]
		exDeadlineList = [self.currenTime] + self.deadlineList[k] + self.deadlineOfNewDemand
		if row == 0 or row == column:
			return False
		elif row == 1+self.noListOfAcceptedPoint[k] and column == 1+row:
			return False
		elif row > 0 and row < self.noListOfAcceptedPoint[k] and self.noListOfPickDrop[k][row-1] > 0 and column == 1+row:
			return False
		elif exNoListOfPickDrop[column] > 0 and exNoListOfPickDrop[row] < 0 and exDeadlineList[column] > exDeadlineList[row]:
			return False
		else:
			return True

	def genVarForConNet(self):
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						self.conNet[k][i][j] = self.newVarID()

	def isTautologyVar(self, k, row, column):
		if row >= 1 and row <= self.noListOfAcceptedPoint[k] and column <= self.noListOfAcceptedPoint[k] and row != column and (not self.isRequiredVar(k, column, row)) and self.isRequiredVar(k, row, column):
			return True
		else:
			return False

	def genVarForRchNet(self):
		for k in range(self.nOfTaxi):
			for i in range(1+self.noListOfAcceptedPoint[k]):
				for j in range(1+i, 3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j) and (not self.isTautologyVar(k, i, j)):
						self.rchNet[k][i][j] = self.newVarID()
			for j in range(1, self.noListOfAcceptedPoint[k]):
				for i in range(1+j, 1+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j) and (not self.isTautologyVar(k, i, j)):
						self.rchNet[k][i][j] = -1 * self.rchNet[k][j][i]
			for i in range(1+self.noListOfAcceptedPoint[k], 3+self.noListOfAcceptedPoint[k]):
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						self.rchNet[k][i][j] = self.newVarID()

	def netPrinter(self, net): # function for debug
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				print(net[k][i][0:3+self.noListOfAcceptedPoint[k]])
			print('\n')

	def halfTseitinTransformation(self, auxiliaryVar, conjunctiVarList):
		for i in range(len(conjunctiVarList)):
			#print('Tseitin', [-1 * auxiliaryVar, conjunctiVarList[i]])
			self.wcnf.append([-1 * auxiliaryVar, conjunctiVarList[i]])

	def genSoftClause(self):
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						self.wcnf.append([(-1 * self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0]), (-1 * self.conNet[k][i][j])], weight = self.cosTimeMatrices[k][i][j])

	def genHardClauseForImplicationRule(self):
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j) and (i > self.noListOfAcceptedPoint[k] or j != 0) and (not self.isTautologyVar(k, i, j)):
						self.wcnf.append([(-1 * self.conNet[k][i][j]), self.rchNet[k][i][j]])

	def authenticLiteral(self, net, k, row, column, sign, isConNet):
		if isConNet:
			if self.isRequiredVar(k, row, column):
				return net[k][row][column] if sign else (-1 * net[k][row][column])
			else: # in this case, 'sign' must be true; otherwise process cannot come here
				return 0
		else:
			if self.isRequiredVar(k, row, column) and (not self.isTautologyVar(k, row, column)):
				return net[k][row][column] if sign else (-1 * net[k][row][column])
			else:
				return 0

	def genHardClauseForTransitionLaw(self):
		for k in range(self.nOfTaxi):
			for a in range(1+self.noListOfAcceptedPoint[k]):
				for b in range(1+a, 2+self.noListOfAcceptedPoint[k]):
					for c in range(1+b, 3+self.noListOfAcceptedPoint[k]):
						# correspond to ¬rchNet[k][b][a] ∨ ¬rchNet[k][c][b] ∨ rchNet[k][c][a]
						if self.isRequiredVar(k, b, a) and self.isRequiredVar(k, c, b) and (not self.isTautologyVar(k, c, a)):
							literaList = [self.authenticLiteral(self.rchNet, k, b, a, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.rchNet, k, c, a, True, False)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][b][c] ∨ ¬rchNet[k][a][b] ∨ rchNet[k][a][c]
						if self.isRequiredVar(k, b, c) and self.isRequiredVar(k, a, b) and (not self.isTautologyVar(k, a, c)):
							literaList = [self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.rchNet, k, a, b, False, False), 
									self.authenticLiteral(self.rchNet, k, a, c, True, False)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

						# correspond to ¬rchNet[k][c][a] ∨ ¬rchNet[k][b][c] ∨ rchNet[k][b][a]
						if self.isRequiredVar(k, c, a) and self.isRequiredVar(k, b, c) and (not self.isTautologyVar(k, b, a)):
							literaList = [self.authenticLiteral(self.rchNet, k, c, a, False, False), 
									self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.rchNet, k, b, a, True, False)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][c][b] ∨ ¬rchNet[k][a][c] ∨ rchNet[k][a][b]
						if self.isRequiredVar(k, c, b) and self.isRequiredVar(k, a, c) and (not self.isTautologyVar(k, a, b)):
							literaList = [self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.rchNet, k, a, c, False, False), 
									self.authenticLiteral(self.rchNet, k, a, b, True, False)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

						if not (a >= 1 and c <= self.noListOfAcceptedPoint[k]):
							# correspond to ¬rchNet[k][a][b] ∨ ¬rchNet[k][c][a] ∨ rchNet[k][c][b]
							if self.isRequiredVar(k, a, b) and self.isRequiredVar(k, c, a) and (not self.isTautologyVar(k, c, b)):
								literaList = [self.authenticLiteral(self.rchNet, k, a, b, False, False), 
										self.authenticLiteral(self.rchNet, k, c, a, False, False), 
										self.authenticLiteral(self.rchNet, k, c, b, True, False)]
								self.wcnf.append(filter(lambda elm: elm != 0, literaList))
								#print(filter(lambda elm: elm != 0, literaList))
							# correspond to ¬rchNet[k][a][c] ∨ ¬rchNet[k][b][a] ∨ rchNet[k][b][c]
							if self.isRequiredVar(k, a, c) and self.isRequiredVar(k, b, a) and (not self.isTautologyVar(k, b, c)):
								literaList = [self.authenticLiteral(self.rchNet, k, a, c, False, False), 
										self.authenticLiteral(self.rchNet, k, b, a, False, False), 
										self.authenticLiteral(self.rchNet, k, b, c, True, False)]
								self.wcnf.append(filter(lambda elm: elm != 0, literaList))
								#print(filter(lambda elm: elm != 0, literaList))

	def genHardClauseForChainLaw(self):
		for k in range(self.nOfTaxi):
			for a in range(1+self.noListOfAcceptedPoint[k]):
				for b in range(1+a, 2+self.noListOfAcceptedPoint[k]):
					for c in range(1+b, 3+self.noListOfAcceptedPoint[k]):
						# correspond to ¬rchNet[k][b][a] ∨ ¬rchNet[k][c][b] ∨ ¬conNet[k][c][a]
						if self.isRequiredVar(k, b, a) and self.isRequiredVar(k, c, b) and self.isRequiredVar(k, c, a):
							literaList = [self.authenticLiteral(self.rchNet, k, b, a, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.conNet, k, c, a, False, True)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][b][c] ∨ ¬rchNet[k][a][b] ∨ ¬conNet[k][a][c]
						if self.isRequiredVar(k, b, c) and self.isRequiredVar(k, a, b) and self.isRequiredVar(k, a, c):
							literaList = [self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.rchNet, k, a, b, False, False), 
									self.authenticLiteral(self.conNet, k, a, c, False, True)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

						# correspond to ¬rchNet[k][c][a] ∨ ¬rchNet[k][b][c] ∨ ¬conNet[k][b][a]
						if self.isRequiredVar(k, c, a) and self.isRequiredVar(k, b, c) and self.isRequiredVar(k, b, a):
							literaList = [self.authenticLiteral(self.rchNet, k, c, a, False, False), 
									self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.conNet, k, b, a, False, True)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][c][b] ∨ ¬rchNet[k][a][c] ∨ ¬conNet[k][a][b]
						if self.isRequiredVar(k, c, b) and self.isRequiredVar(k, a, c) and self.isRequiredVar(k, a, b):
							literaList = [self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.rchNet, k, a, c, False, False), 
									self.authenticLiteral(self.conNet, k, a, b, False, True)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

						# correspond to ¬rchNet[k][a][b] ∨ ¬rchNet[k][c][a] ∨ ¬conNet[k][c][b]
						if self.isRequiredVar(k, a, b) and self.isRequiredVar(k, c, a) and self.isRequiredVar(k, c, b):
							literaList = [self.authenticLiteral(self.rchNet, k, a, b, False, False), 
									self.authenticLiteral(self.rchNet, k, c, a, False, False), 
									self.authenticLiteral(self.conNet, k, c, b, False, True)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][a][c] ∨ ¬rchNet[k][b][a] ∨ ¬conNet[k][b][c]
						if self.isRequiredVar(k, a, c) and self.isRequiredVar(k, b, a) and self.isRequiredVar(k, b, c):
							literaList = [self.authenticLiteral(self.rchNet, k, a, c, False, False), 
									self.authenticLiteral(self.rchNet, k, b, a, False, False), 
									self.authenticLiteral(self.conNet, k, b, c, False, True)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

	def genHardClauseForConfluenceLaw(self):
		for k in range(self.nOfTaxi):
			for a in range(1+self.noListOfAcceptedPoint[k]):
				for b in range(1+a, 2+self.noListOfAcceptedPoint[k]):
					for c in range(1+b, 3+self.noListOfAcceptedPoint[k]):
						# correspond to ¬rchNet[k][a][b] ∨ ¬rchNet[k][a][c] ∨ rchNet[k][c][b] ∨ rchNet[k][b][c]
						if (not c <= self.noListOfAcceptedPoint[k]) and self.isRequiredVar(k, a, b) and self.isRequiredVar(k, a, c) and (not self.isTautologyVar(k, c, b)) and (not self.isTautologyVar(k, b, c)):
							literaList = [self.authenticLiteral(self.rchNet, k, a, b, False, False), 
									self.authenticLiteral(self.rchNet, k, a, c, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, True, False),
									self.authenticLiteral(self.rchNet, k, b, c, True, False)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][b][a] ∨ ¬rchNet[k][b][c] ∨ rchNet[k][c][a] ∨ rchNet[k][a][c]
						if (not (a >=1 and c <= self.noListOfAcceptedPoint[k])) and self.isRequiredVar(k, b, a) and self.isRequiredVar(k, b, c) and (not self.isTautologyVar(k, c, a)) and (not self.isTautologyVar(k, a, c)):
							literaList = [self.authenticLiteral(self.rchNet, k, b, a, False, False), 
									self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.rchNet, k, c, a, True, False),
									self.authenticLiteral(self.rchNet, k, a, c, True, False)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][c][a] ∨ ¬rchNet[k][c][b] ∨ rchNet[k][b][a] ∨ rchNet[k][a][b]
						if (not (a >=1 and b <= self.noListOfAcceptedPoint[k])) and self.isRequiredVar(k, c, a) and self.isRequiredVar(k, c, b) and (not self.isTautologyVar(k, b, a)) and (not self.isTautologyVar(k, a, b)):
							literaList = [self.authenticLiteral(self.rchNet, k, c, a, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.rchNet, k, b, a, True, False),
									self.authenticLiteral(self.rchNet, k, a, b, True, False)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

	def genHardClauseForRamificationLaw(self):
		for k in range(self.nOfTaxi):
			for a in range(1+self.noListOfAcceptedPoint[k]):
				for b in range(1+a, 2+self.noListOfAcceptedPoint[k]):
					for c in range(1+b, 3+self.noListOfAcceptedPoint[k]):
						# correspond to ¬rchNet[k][b][a] ∨ ¬rchNet[k][c][a] ∨ rchNet[k][c][b] ∨ rchNet[k][b][c]
						if (not c <= self.noListOfAcceptedPoint[k]) and self.isRequiredVar(k, b, a) and self.isRequiredVar(k, c, a) and (not self.isTautologyVar(k, c, b)) and (not self.isTautologyVar(k, b, c)):
							literaList = [self.authenticLiteral(self.rchNet, k, b, a, False, False), 
									self.authenticLiteral(self.rchNet, k, c, a, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, True, False),
									self.authenticLiteral(self.rchNet, k, b, c, True, False)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][a][b] ∨ ¬rchNet[k][c][b] ∨ rchNet[k][c][a] ∨ rchNet[k][a][c]
						if (not (a >=1 and c <= self.noListOfAcceptedPoint[k])) and self.isRequiredVar(k, a, b) and self.isRequiredVar(k, c, b) and (not self.isTautologyVar(k, c, a)) and (not self.isTautologyVar(k, a, c)):
							literaList = [self.authenticLiteral(self.rchNet, k, a, b, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.rchNet, k, c, a, True, False),
									self.authenticLiteral(self.rchNet, k, a, c, True, False)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][a][c] ∨ ¬rchNet[k][b][c] ∨ rchNet[k][b][a] ∨ rchNet[k][a][b]
						if (not (a >=1 and b <= self.noListOfAcceptedPoint[k])) and self.isRequiredVar(k, a, c) and self.isRequiredVar(k, b, c) and (not self.isTautologyVar(k, b, a)) and (not self.isTautologyVar(k, a, b)):
							literaList = [self.authenticLiteral(self.rchNet, k, a, c, False, False), 
									self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.rchNet, k, b, a, True, False),
									self.authenticLiteral(self.rchNet, k, a, b, True, False)]
							self.wcnf.append(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

	def genHardClauseForAcyclicLaw(self):
		for k in range(self.nOfTaxi):
			for a in range(2+self.noListOfAcceptedPoint[k]):
				for b in range(1+a, 3+self.noListOfAcceptedPoint[k]):
					# correspond to ¬rchNet[k][b][a] ∨ ¬rchNet[k][a][b]
					if (not (a >=1 and b <= self.noListOfAcceptedPoint[k])) and self.isRequiredVar(k, b, a) and self.isRequiredVar(k, a, b):
						self.wcnf.append([(-1 * self.rchNet[k][b][a]), (-1 * self.rchNet[k][a][b])])

	def atLeastOne(self, varList):
		self.wcnf.append(varList)

	def atMostOne(self, varList):
		for i in range(len(varList)):
			for j in range(1+i, len(varList)):
				self.wcnf.append([(-1 * varList[i]), (-1 * varList[j])])

	def exactlyOne(self, varList):
		self.atMostOne(varList)
		self.atLeastOne(varList)

	def genHardClauseForEq3(self):
		for k in range(self.nOfTaxi):
			for i in range(1, 1+self.noListOfAcceptedPoint[k]):
				varList = []
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						varList.append(self.conNet[k][i][j])
				self.atLeastOne(varList)

	def genHardClauseForEq4(self):
		for k in range(self.nOfTaxi):
			for i in range(1, 1+self.noListOfAcceptedPoint[k]):
				if self.noListOfPickDrop[k][i-1] > 0:
					varList = []
					for j in range(1, 3+self.noListOfAcceptedPoint[k]):
						if self.isRequiredVar(k, j, i):
							varList.append(self.conNet[k][j][i])
					self.atLeastOne(varList)

	def genHardClauseForBasicIdeaPatch(self):
		for k in range(self.nOfTaxi):
			for i in range(1, 3+self.noListOfAcceptedPoint[k]):
				varList = []
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						varList.append(self.conNet[k][i][j])
				self.atMostOne(varList)
			for i in range(3+self.noListOfAcceptedPoint[k]):
				varList = []
				for j in range(1, 3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, j, i):
						varList.append(self.conNet[k][j][i])
				self.atMostOne(varList)

	def genHardClauseForEq5(self):
		varList = []
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				if self.isRequiredVar(k, 1+self.noListOfAcceptedPoint[k], i):
					varList.append(self.conNet[k][1+self.noListOfAcceptedPoint[k]][i])
		self.exactlyOne(varList)

	def genHardClauseForEq6(self):
		varList = []
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				if self.isRequiredVar(k, 2+self.noListOfAcceptedPoint[k], i):
					varList.append(self.conNet[k][2+self.noListOfAcceptedPoint[k]][i])
		self.exactlyOne(varList)

	def genHardClauseForEq7(self):
		varList = []
		for k in range(self.nOfTaxi):
			for i in range(1, 3+self.noListOfAcceptedPoint[k]):
				if self.isRequiredVar(k, i, 1+self.noListOfAcceptedPoint[k]):
					varList.append(self.conNet[k][i][1+self.noListOfAcceptedPoint[k]])
		self.exactlyOne(varList)

	def genHardClauseForEq8(self):
		varList = []
		for k in range(self.nOfTaxi):
			for i in range(1, 3+self.noListOfAcceptedPoint[k]):
				if self.isRequiredVar(k, i, 2+self.noListOfAcceptedPoint[k]):
					varList.append(self.conNet[k][i][2+self.noListOfAcceptedPoint[k]])
		self.atMostOne(varList)

	def genHardClauseForEq9(self):
		for k in range(self.nOfTaxi):
			if self.noListOfAcceptedPoint[k] != 0:
				varList = []
				for i in range(1, 3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, 0):
						varList.append(self.conNet[k][i][0])
				self.atLeastOne(varList)

	def genHardClauseForHPConsWithBasicIdea(self):
		self.genHardClauseForImplicationRule()
		self.genHardClauseForTransitionLaw()
		self.genHardClauseForAcyclicLaw()
		self.genHardClauseForEq3()
		self.genHardClauseForEq4()
		self.genHardClauseForBasicIdeaPatch()
		self.genHardClauseForEq5()
		self.genHardClauseForEq6()
		self.genHardClauseForEq7()
		self.genHardClauseForEq8()
		self.genHardClauseForEq9()

	def genHardClauseForHPConsWithNewIdea(self):
		self.genHardClauseForImplicationRule()
		self.genHardClauseForTransitionLaw()
		self.genHardClauseForChainLaw()
		self.genHardClauseForConfluenceLaw()
		self.genHardClauseForRamificationLaw()
		self.genHardClauseForAcyclicLaw()
		self.genHardClauseForEq3()
		self.genHardClauseForEq4()
		self.genHardClauseForEq5()
		self.genHardClauseForEq6()
		self.genHardClauseForEq7()
		self.genHardClauseForEq8()
		self.genHardClauseForEq9()

	def genHardClauseForEq17(self):
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				if self.isRequiredVar(k, 1+self.noListOfAcceptedPoint[k], i):
					self.wcnf.append([(-1 * self.rchNet[k][1+self.noListOfAcceptedPoint[k]][i]), self.rchNet[k][2+self.noListOfAcceptedPoint[k]][1+self.noListOfAcceptedPoint[k]]])
				if self.isRequiredVar(k, i, 1+self.noListOfAcceptedPoint[k]):
					self.wcnf.append([(-1 * self.rchNet[k][i][1+self.noListOfAcceptedPoint[k]]), self.rchNet[k][2+self.noListOfAcceptedPoint[k]][1+self.noListOfAcceptedPoint[k]]])
				if self.isRequiredVar(k, 2+self.noListOfAcceptedPoint[k], i):
					self.wcnf.append([(-1 * self.rchNet[k][2+self.noListOfAcceptedPoint[k]][i]), self.rchNet[k][2+self.noListOfAcceptedPoint[k]][1+self.noListOfAcceptedPoint[k]]])
				if self.isRequiredVar(k, i, 2+self.noListOfAcceptedPoint[k]):
					self.wcnf.append([(-1 * self.rchNet[k][i][2+self.noListOfAcceptedPoint[k]]), self.rchNet[k][2+self.noListOfAcceptedPoint[k]][1+self.noListOfAcceptedPoint[k]]])

	def genHardClauseForEq18(self):
		varList = []
		for k in range(self.nOfTaxi):
			varList.append(self.rchNet[k][2+self.noListOfAcceptedPoint[k]][1+self.noListOfAcceptedPoint[k]])
		self.atMostOne(varList)

	def genHardClauseForViaPointLists(self):
		previousRoutes = []
		for k in range(self.nOfTaxi):
			eachPreRoute = []
			for i in range(len(self.viaPointLists[k])):
				eachPreRoute.append(self.conNet[k][self.viaPointLists[k][i]][0] if i == 0 else self.conNet[k][self.viaPointLists[k][i]][self.viaPointLists[k][i-1]])
			previousRoutes.append(eachPreRoute)
		self.preCaseVarList = [self.newVarID() for k in range(self.nOfTaxi)]
		#print(previousRoutes)
		#print(self.preCaseVarList)
		for k in range(self.nOfTaxi):
			for i in range(self.nOfTaxi):
				if i != k:
					for j in range(len(previousRoutes[i])):
						#print(-1 * self.preCaseVarList[k], previousRoutes[i][j])
						self.wcnf.append([-1 * self.preCaseVarList[k], previousRoutes[i][j]])
			#print(-1 * self.preCaseVarList[k], self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0])
			self.wcnf.append([-1 * self.preCaseVarList[k], self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0]])
		self.assumptionVar = self.newVarID()
		#print([-1 * self.assumptionVar] + self.preCaseVarList)
		self.wcnf.append([-1 * self.assumptionVar] + self.preCaseVarList)

	def getLastVarIDinConNet(self):
		k = self.nOfTaxi - 1
		row = 2 + self.noListOfAcceptedPoint[k]
		column = row - 1
		return self.conNet[k][row][column]

	def getLastVarIDinRchNet(self):
		k = self.nOfTaxi - 1
		row = 2 + self.noListOfAcceptedPoint[k]
		column = row - 1
		return self.rchNet[k][row][column]

	def fromTo(self, k, column):
		listOfCandidateMove = []
		for row in range(1, 3+self.noListOfAcceptedPoint[k]):
			listOfCandidateMove.append(self.conNet[k][row][column])
		return listOfCandidateMove

	def decodeAllModels(self, model):
		listOfRoute = []
		for k in range(self.nOfTaxi):
			listOFromTo = [0]
			listOfCandidateMove = self.fromTo(k, 0)
			while len(listOfCandidateMove) != 0:
				for i in range(len(listOfCandidateMove)):
					if listOfCandidateMove[i] in model:
						listOFromTo.append(1+i)
						listOfCandidateMove = self.fromTo(k, 1+i)
						break
					elif i == len(listOfCandidateMove) - 1:
						listOfCandidateMove = []
			listOfRoute.append(listOFromTo)
		print(listOfRoute)
		return listOfRoute

	def decodeModel(self, model):
		for k in range(self.nOfTaxi):
			listOfCandidateMove = filter(lambda elm: elm != 0, self.conNet[k][1+self.noListOfAcceptedPoint[k]])
			for i in range(len(listOfCandidateMove)):
				if listOfCandidateMove[i] in model:
					return (k, self.decodeAllModels(model)[k])

	def checkExCondition(self, taxID, route):
		isViolate = False
		sumDelay = 0
		sumCarried = self.noListOfCarried[taxID]
		reasoNegation = [-1 * self.rchNet[taxID][2+self.noListOfAcceptedPoint[taxID]][0]] #[] # 2020/08/24
		exNoListOfPickDrop = [0] + self.noListOfPickDrop[taxID] + [self.newDemandSize, -1 * self.newDemandSize]
		exDeadlineList = [self.currenTime] + self.deadlineList[taxID] + self.deadlineOfNewDemand
		for i in range(len(route)-1):
			reasoNegation.append(-1 * self.conNet[taxID][route[1+i]][route[i]])
			# checking for deadline contraints
			sumDelay += self.cosTimeMatrices[taxID][route[1+i]][route[i]]
			if exNoListOfPickDrop[route[1+i]] < 0:
				if sumDelay > (exDeadlineList[route[1+i]] - self.currenTime):
					print('drop-off DL violation')
					isViolate = True
					break
			elif exNoListOfPickDrop[route[1+i]] > 0:
				if sumDelay < (exDeadlineList[route[1+i]] - self.currenTime):
					print('pick-up DL violation')
					isViolate = True
					break
			# checking for capacity constraints
			sumCarried += exNoListOfPickDrop[route[1+i]]
			if sumCarried > self.capacityOfEachTaxi[taxID]:
				print('capacity violation')
				isViolate = True
				break
		return (isViolate, reasoNegation)

	def writExternalityFile(self, exFileName):
		externalityFile = open(exFileName + '.ext', 'w')
		externalityFile.write('nOfTaxi %d' % self.nOfTaxi)
		externalityFile.write('\nnewDemandSize %d' % self.newDemandSize)
		externalityFile.write('\ncapacityOfEachTaxi')
		for i in range(len(self.capacityOfEachTaxi)):
			externalityFile.write(' %d' % self.capacityOfEachTaxi[i])
		externalityFile.write('\nnoListOfCarried')
		for i in range(len(self.noListOfCarried)):
			externalityFile.write(' %d' % self.noListOfCarried[i])
		externalityFile.write('\nnoListOfAcceptedPoint')
		for i in range(len(self.noListOfAcceptedPoint)):
			externalityFile.write(' %d' % self.noListOfAcceptedPoint[i])
		externalityFile.write('\nnoListOfPickDrop')
		for i in range(len(self.noListOfPickDrop)):
			for j in range(len(self.noListOfPickDrop[i])):
				externalityFile.write(' %d' % self.noListOfPickDrop[i][j])
		externalityFile.write('\ncurrenTime %d' % self.currenTime)
		externalityFile.write('\ndeadlineList')
		for i in range(len(self.deadlineList)):
			for j in range(len(self.deadlineList[i])):
				externalityFile.write(' %d' % self.deadlineList[i][j])
		externalityFile.write('\ndeadlineOfNewDemand %d %d' % (self.deadlineOfNewDemand[0], self.deadlineOfNewDemand[1]))
		externalityFile.write('\nvarOfRchNewDemand')
		for i in range(self.nOfTaxi):
			externalityFile.write(' %d' % self.rchNet[i][2+self.noListOfAcceptedPoint[i]][0])
		externalityFile.write('\ncosTimeList')
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						externalityFile.write(' %d' % self.cosTimeMatrices[k][i][j])
		externalityFile.write('\nviaPointLists')
		for i in range(len(self.viaPointLists)):
			for j in range(len(self.viaPointLists[i])):
				externalityFile.write(' %d' % self.viaPointLists[i][j])
		externalityFile.write('\nassumptionVar %d' % self.assumptionVar)
		externalityFile.close()

	def solveRTSS(self, rc2):
		unviolatedModel = None
		model = rc2.compute()
		while model != None:
			model = filter(lambda elm: (elm > 0 and elm <= self.getLastVarIDinConNet()), model)
			#print(model)
			taxID, route = self.decodeModel(model)
			print(taxID, route, rc2.cost)
			isViolate, reasoNegation = self.checkExCondition(taxID, route)
			#print('reNeg', reasoNegation)
			#print('violate', isViolate)
			if isViolate:
				rc2.add_clause(reasoNegation)
				self.learntClause.append(reasoNegation)
				model = rc2.compute()
			else:
				unviolatedModel = model
				break
		return unviolatedModel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	def clauseToIP(self, literaList): # (literaList[0] ∨ ... ∨ literaList[n] = T) ≡ (literaList[0] + ... + literaList[n] ≥ 1)
		ip = ''
		if len(literaList) == 0:
			return ip
		else:
			rightSideInt = 1
			# negative polarity of Boolean variable which is illegal, because we cannot write IP as, e.g., x + ... + ¬y + ... ≥ 1 if ¬y < 0. Instead, we should use the equivalence replacement of ¬y associated with ¬¬y (i.e., y). Therefore, due to -y ≡ (¬y - 1) (i.e., ¬y ≡ (-y + 1)), we have x + ... + (-y + 1) + ... ≥ 1. 
			for i in range(len(literaList)):
				ip += ' + x' + str(literaList[i]) if literaList[i] > 0 else ' - x' + str(-1 * literaList[i])
				if literaList[i] < 0:
					rightSideInt -= 1
			#if rightSideInt > 0:
			#	ip += ' - ' + str(rightSideInt)
			#elif rightSideInt < 0:
			#	ip += ' + ' + str(-1 * rightSideInt)
			return ip.lstrip(' + ') + ' >= ' + str(rightSideInt) + '\n'

	def genIPObjectiveFunction(self):
		self.ip += 'Minimize z\n\nSubject to\n'
		strBF = ''
		listOfYVarCoefficient = []
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						self.yVarID += 1
						strBF += self.clauseToIP([self.yVarID, (-1 * self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0]), (-1 * self.conNet[k][i][j])]).replace('x', 'y', 1)
						listOfYVarCoefficient.append(self.cosTimeMatrices[k][i][j])
		for i in range(self.yVarID):
			if i == 0:
				self.ip += str(listOfYVarCoefficient[i]) + ' y' + str(1+i)
			elif listOfYVarCoefficient[i] > 0:
				self.ip += ' + ' + str(listOfYVarCoefficient[i]) + ' y' + str(1+i)
			elif listOfYVarCoefficient[i] < 0:
				self.ip += ' - ' + str(-1 * listOfYVarCoefficient[i]) + ' y' + str(1+i)
		self.ip += ' - z = 0\n' + strBF

	def genIPForImplicationRule(self):
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j) and (i > self.noListOfAcceptedPoint[k] or j != 0) and (not self.isTautologyVar(k, i, j)):
						self.ip += self.clauseToIP([(-1 * self.conNet[k][i][j]), self.rchNet[k][i][j]])

	def genIPForTransitionLaw(self):
		for k in range(self.nOfTaxi):
			for a in range(1+self.noListOfAcceptedPoint[k]):
				for b in range(1+a, 2+self.noListOfAcceptedPoint[k]):
					for c in range(1+b, 3+self.noListOfAcceptedPoint[k]):
						# correspond to ¬rchNet[k][b][a] ∨ ¬rchNet[k][c][b] ∨ rchNet[k][c][a]
						if self.isRequiredVar(k, b, a) and self.isRequiredVar(k, c, b) and (not self.isTautologyVar(k, c, a)):
							literaList = [self.authenticLiteral(self.rchNet, k, b, a, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.rchNet, k, c, a, True, False)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][b][c] ∨ ¬rchNet[k][a][b] ∨ rchNet[k][a][c]
						if self.isRequiredVar(k, b, c) and self.isRequiredVar(k, a, b) and (not self.isTautologyVar(k, a, c)):
							literaList = [self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.rchNet, k, a, b, False, False), 
									self.authenticLiteral(self.rchNet, k, a, c, True, False)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

						# correspond to ¬rchNet[k][c][a] ∨ ¬rchNet[k][b][c] ∨ rchNet[k][b][a]
						if self.isRequiredVar(k, c, a) and self.isRequiredVar(k, b, c) and (not self.isTautologyVar(k, b, a)):
							literaList = [self.authenticLiteral(self.rchNet, k, c, a, False, False), 
									self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.rchNet, k, b, a, True, False)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][c][b] ∨ ¬rchNet[k][a][c] ∨ rchNet[k][a][b]
						if self.isRequiredVar(k, c, b) and self.isRequiredVar(k, a, c) and (not self.isTautologyVar(k, a, b)):
							literaList = [self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.rchNet, k, a, c, False, False), 
									self.authenticLiteral(self.rchNet, k, a, b, True, False)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

						if not (a >= 1 and c <= self.noListOfAcceptedPoint[k]):
							# correspond to ¬rchNet[k][a][b] ∨ ¬rchNet[k][c][a] ∨ rchNet[k][c][b]
							if self.isRequiredVar(k, a, b) and self.isRequiredVar(k, c, a) and (not self.isTautologyVar(k, c, b)):
								literaList = [self.authenticLiteral(self.rchNet, k, a, b, False, False), 
										self.authenticLiteral(self.rchNet, k, c, a, False, False), 
										self.authenticLiteral(self.rchNet, k, c, b, True, False)]
								self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
								#print(filter(lambda elm: elm != 0, literaList))
							# correspond to ¬rchNet[k][a][c] ∨ ¬rchNet[k][b][a] ∨ rchNet[k][b][c]
							if self.isRequiredVar(k, a, c) and self.isRequiredVar(k, b, a) and (not self.isTautologyVar(k, b, c)):
								literaList = [self.authenticLiteral(self.rchNet, k, a, c, False, False), 
										self.authenticLiteral(self.rchNet, k, b, a, False, False), 
										self.authenticLiteral(self.rchNet, k, b, c, True, False)]
								self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
								#print(filter(lambda elm: elm != 0, literaList))

	def genIPForChainLaw(self):
		for k in range(self.nOfTaxi):
			for a in range(1+self.noListOfAcceptedPoint[k]):
				for b in range(1+a, 2+self.noListOfAcceptedPoint[k]):
					for c in range(1+b, 3+self.noListOfAcceptedPoint[k]):
						# correspond to ¬rchNet[k][b][a] ∨ ¬rchNet[k][c][b] ∨ ¬conNet[k][c][a]
						if self.isRequiredVar(k, b, a) and self.isRequiredVar(k, c, b) and self.isRequiredVar(k, c, a):
							literaList = [self.authenticLiteral(self.rchNet, k, b, a, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.conNet, k, c, a, False, True)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][b][c] ∨ ¬rchNet[k][a][b] ∨ ¬conNet[k][a][c]
						if self.isRequiredVar(k, b, c) and self.isRequiredVar(k, a, b) and self.isRequiredVar(k, a, c):
							literaList = [self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.rchNet, k, a, b, False, False), 
									self.authenticLiteral(self.conNet, k, a, c, False, True)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

						# correspond to ¬rchNet[k][c][a] ∨ ¬rchNet[k][b][c] ∨ ¬conNet[k][b][a]
						if self.isRequiredVar(k, c, a) and self.isRequiredVar(k, b, c) and self.isRequiredVar(k, b, a):
							literaList = [self.authenticLiteral(self.rchNet, k, c, a, False, False), 
									self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.conNet, k, b, a, False, True)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][c][b] ∨ ¬rchNet[k][a][c] ∨ ¬conNet[k][a][b]
						if self.isRequiredVar(k, c, b) and self.isRequiredVar(k, a, c) and self.isRequiredVar(k, a, b):
							literaList = [self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.rchNet, k, a, c, False, False), 
									self.authenticLiteral(self.conNet, k, a, b, False, True)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

						# correspond to ¬rchNet[k][a][b] ∨ ¬rchNet[k][c][a] ∨ ¬conNet[k][c][b]
						if self.isRequiredVar(k, a, b) and self.isRequiredVar(k, c, a) and self.isRequiredVar(k, c, b):
							literaList = [self.authenticLiteral(self.rchNet, k, a, b, False, False), 
									self.authenticLiteral(self.rchNet, k, c, a, False, False), 
									self.authenticLiteral(self.conNet, k, c, b, False, True)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][a][c] ∨ ¬rchNet[k][b][a] ∨ ¬conNet[k][b][c]
						if self.isRequiredVar(k, a, c) and self.isRequiredVar(k, b, a) and self.isRequiredVar(k, b, c):
							literaList = [self.authenticLiteral(self.rchNet, k, a, c, False, False), 
									self.authenticLiteral(self.rchNet, k, b, a, False, False), 
									self.authenticLiteral(self.conNet, k, b, c, False, True)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

	def genIPForConfluenceLaw(self):
		for k in range(self.nOfTaxi):
			for a in range(1+self.noListOfAcceptedPoint[k]):
				for b in range(1+a, 2+self.noListOfAcceptedPoint[k]):
					for c in range(1+b, 3+self.noListOfAcceptedPoint[k]):
						# correspond to ¬rchNet[k][a][b] ∨ ¬rchNet[k][a][c] ∨ rchNet[k][c][b] ∨ rchNet[k][b][c]
						if (not c <= self.noListOfAcceptedPoint[k]) and self.isRequiredVar(k, a, b) and self.isRequiredVar(k, a, c) and (not self.isTautologyVar(k, c, b)) and (not self.isTautologyVar(k, b, c)):
							literaList = [self.authenticLiteral(self.rchNet, k, a, b, False, False), 
									self.authenticLiteral(self.rchNet, k, a, c, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, True, False),
									self.authenticLiteral(self.rchNet, k, b, c, True, False)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][b][a] ∨ ¬rchNet[k][b][c] ∨ rchNet[k][c][a] ∨ rchNet[k][a][c]
						if (not (a >=1 and c <= self.noListOfAcceptedPoint[k])) and self.isRequiredVar(k, b, a) and self.isRequiredVar(k, b, c) and (not self.isTautologyVar(k, c, a)) and (not self.isTautologyVar(k, a, c)):
							literaList = [self.authenticLiteral(self.rchNet, k, b, a, False, False), 
									self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.rchNet, k, c, a, True, False),
									self.authenticLiteral(self.rchNet, k, a, c, True, False)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][c][a] ∨ ¬rchNet[k][c][b] ∨ rchNet[k][b][a] ∨ rchNet[k][a][b]
						if (not (a >=1 and b <= self.noListOfAcceptedPoint[k])) and self.isRequiredVar(k, c, a) and self.isRequiredVar(k, c, b) and (not self.isTautologyVar(k, b, a)) and (not self.isTautologyVar(k, a, b)):
							literaList = [self.authenticLiteral(self.rchNet, k, c, a, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.rchNet, k, b, a, True, False),
									self.authenticLiteral(self.rchNet, k, a, b, True, False)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

	def genIPForRamificationLaw(self):
		for k in range(self.nOfTaxi):
			for a in range(1+self.noListOfAcceptedPoint[k]):
				for b in range(1+a, 2+self.noListOfAcceptedPoint[k]):
					for c in range(1+b, 3+self.noListOfAcceptedPoint[k]):
						# correspond to ¬rchNet[k][b][a] ∨ ¬rchNet[k][c][a] ∨ rchNet[k][c][b] ∨ rchNet[k][b][c]
						if (not c <= self.noListOfAcceptedPoint[k]) and self.isRequiredVar(k, b, a) and self.isRequiredVar(k, c, a) and (not self.isTautologyVar(k, c, b)) and (not self.isTautologyVar(k, b, c)):
							literaList = [self.authenticLiteral(self.rchNet, k, b, a, False, False), 
									self.authenticLiteral(self.rchNet, k, c, a, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, True, False),
									self.authenticLiteral(self.rchNet, k, b, c, True, False)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][a][b] ∨ ¬rchNet[k][c][b] ∨ rchNet[k][c][a] ∨ rchNet[k][a][c]
						if (not (a >=1 and c <= self.noListOfAcceptedPoint[k])) and self.isRequiredVar(k, a, b) and self.isRequiredVar(k, c, b) and (not self.isTautologyVar(k, c, a)) and (not self.isTautologyVar(k, a, c)):
							literaList = [self.authenticLiteral(self.rchNet, k, a, b, False, False), 
									self.authenticLiteral(self.rchNet, k, c, b, False, False), 
									self.authenticLiteral(self.rchNet, k, c, a, True, False),
									self.authenticLiteral(self.rchNet, k, a, c, True, False)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))
						# correspond to ¬rchNet[k][a][c] ∨ ¬rchNet[k][b][c] ∨ rchNet[k][b][a] ∨ rchNet[k][a][b]
						if (not (a >=1 and b <= self.noListOfAcceptedPoint[k])) and self.isRequiredVar(k, a, c) and self.isRequiredVar(k, b, c) and (not self.isTautologyVar(k, b, a)) and (not self.isTautologyVar(k, a, b)):
							literaList = [self.authenticLiteral(self.rchNet, k, a, c, False, False), 
									self.authenticLiteral(self.rchNet, k, b, c, False, False), 
									self.authenticLiteral(self.rchNet, k, b, a, True, False),
									self.authenticLiteral(self.rchNet, k, a, b, True, False)]
							self.ip += self.clauseToIP(filter(lambda elm: elm != 0, literaList))
							#print(filter(lambda elm: elm != 0, literaList))

	def genIPForAcyclicLaw(self):
		for k in range(self.nOfTaxi):
			for a in range(2+self.noListOfAcceptedPoint[k]):
				for b in range(1+a, 3+self.noListOfAcceptedPoint[k]):
					# correspond to ¬rchNet[k][b][a] ∨ ¬rchNet[k][a][b]
					if (not (a >=1 and b <= self.noListOfAcceptedPoint[k])) and self.isRequiredVar(k, b, a) and self.isRequiredVar(k, a, b):
						self.ip += self.clauseToIP([(-1 * self.rchNet[k][b][a]), (-1 * self.rchNet[k][a][b])])

	def atLeastOneIP(self, varList):
		self.ip += self.clauseToIP(varList)

	def atMostOneIP(self, varList):
		if len(varList) > 1:
			self.ip += self.clauseToIP(varList).replace('>=', '<=')

	def exactlyOneIP(self, varList):
		self.ip += self.clauseToIP(varList).replace('>=', '=')

	def genIPForEq3(self):
		for k in range(self.nOfTaxi):
			for i in range(1, 1+self.noListOfAcceptedPoint[k]):
				varList = []
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						varList.append(self.conNet[k][i][j])
				self.atLeastOneIP(varList)

	def genIPForEq4(self):
		for k in range(self.nOfTaxi):
			for i in range(1, 1+self.noListOfAcceptedPoint[k]):
				if self.noListOfPickDrop[k][i-1] > 0:
					varList = []
					for j in range(1, 3+self.noListOfAcceptedPoint[k]):
						if self.isRequiredVar(k, j, i):
							varList.append(self.conNet[k][j][i])
					self.atLeastOneIP(varList)

	def genIPForBasicIdeaPatch(self):
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				varList = []
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						varList.append(self.conNet[k][i][j])
				self.atMostOneIP(varList)
			for i in range(3+self.noListOfAcceptedPoint[k]):
				varList = []
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, j, i):
						varList.append(self.conNet[k][j][i])
				self.atMostOneIP(varList)

	def genIPForEq5(self):
		varList = []
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				if self.isRequiredVar(k, 1+self.noListOfAcceptedPoint[k], i):
					varList.append(self.conNet[k][1+self.noListOfAcceptedPoint[k]][i])
		self.exactlyOneIP(varList)

	def genIPForEq6(self):
		varList = []
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				if self.isRequiredVar(k, 2+self.noListOfAcceptedPoint[k], i):
					varList.append(self.conNet[k][2+self.noListOfAcceptedPoint[k]][i])
		self.exactlyOneIP(varList)

	def genIPForEq7(self):
		varList = []
		for k in range(self.nOfTaxi):
			for i in range(1, 3+self.noListOfAcceptedPoint[k]):
				if self.isRequiredVar(k, i, 1+self.noListOfAcceptedPoint[k]):
					varList.append(self.conNet[k][i][1+self.noListOfAcceptedPoint[k]])
		self.exactlyOneIP(varList)

	def genIPForEq8(self):
		varList = []
		for k in range(self.nOfTaxi):
			for i in range(1, 3+self.noListOfAcceptedPoint[k]):
				if self.isRequiredVar(k, i, 2+self.noListOfAcceptedPoint[k]):
					varList.append(self.conNet[k][i][2+self.noListOfAcceptedPoint[k]])
		self.atMostOneIP(varList)

	def genIPForEq9(self):
		for k in range(self.nOfTaxi):
			if self.noListOfAcceptedPoint[k] != 0:
				varList = []
				for i in range(1, 3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, 0):
						varList.append(self.conNet[k][i][0])
				self.atLeastOneIP(varList)

	def genIPForHPConsWithBasicIdea(self):
		self.genIPForImplicationRule()
		self.genIPForTransitionLaw()
		self.genIPForAcyclicLaw()
		self.genIPForEq3()
		self.genIPForEq4()
		self.genIPForBasicIdeaPatch()
		self.genIPForEq5()
		self.genIPForEq6()
		self.genIPForEq7()
		self.genIPForEq8()
		self.genIPForEq9()

	def genIPForHPConsWithNewIdea(self):
		self.genIPForImplicationRule()
		self.genIPForTransitionLaw()
		self.genIPForChainLaw()
		self.genIPForConfluenceLaw()
		self.genIPForRamificationLaw()
		self.genIPForAcyclicLaw()
		self.genIPForEq3()
		self.genIPForEq4()
		self.genIPForEq5()
		self.genIPForEq6()
		self.genIPForEq7()
		self.genIPForEq8()
		self.genIPForEq9()

	def genIPForEq17(self):
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				if self.isRequiredVar(k, 1+self.noListOfAcceptedPoint[k], i):
					self.ip += self.clauseToIP([(-1 * self.rchNet[k][1+self.noListOfAcceptedPoint[k]][i]), self.rchNet[k][2+self.noListOfAcceptedPoint[k]][1+self.noListOfAcceptedPoint[k]]])
				if self.isRequiredVar(k, i, 1+self.noListOfAcceptedPoint[k]):
					self.ip += self.clauseToIP([(-1 * self.rchNet[k][i][1+self.noListOfAcceptedPoint[k]]), self.rchNet[k][2+self.noListOfAcceptedPoint[k]][1+self.noListOfAcceptedPoint[k]]])
				if self.isRequiredVar(k, 2+self.noListOfAcceptedPoint[k], i):
					self.ip += self.clauseToIP([(-1 * self.rchNet[k][2+self.noListOfAcceptedPoint[k]][i]), self.rchNet[k][2+self.noListOfAcceptedPoint[k]][1+self.noListOfAcceptedPoint[k]]])
				if self.isRequiredVar(k, i, 2+self.noListOfAcceptedPoint[k]):
					self.ip += self.clauseToIP([(-1 * self.rchNet[k][i][2+self.noListOfAcceptedPoint[k]]), self.rchNet[k][2+self.noListOfAcceptedPoint[k]][1+self.noListOfAcceptedPoint[k]]])

	def genIPForEq18(self):
		varList = []
		for k in range(self.nOfTaxi):
			varList.append(self.rchNet[k][2+self.noListOfAcceptedPoint[k]][1+self.noListOfAcceptedPoint[k]])
		self.atMostOneIP(varList)

	# big-M formulation is an alternative to indicator constraint
	def bigMFormulation(self, clausedIndict, IndictVar, linearExp, lowerBOfLinearExp, upperBOfLinearExp, comparator, rightSideInt, bigM):
		ip = ''
		lowerBOfLinearExp -= bigM
		upperBOfLinearExp += bigM
		if comparator == '=':
			if clausedIndict > 0:
				if lowerBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' + ' + str(lowerBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(clausedIndict) + ' >= ' + str(lowerBOfLinearExp) + '\n'
				else:
					ip += linearExp + ' - ' + str(abs(lowerBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(clausedIndict) + ' >= ' + str(lowerBOfLinearExp) + '\n'
				if upperBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' + ' + str(upperBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(clausedIndict) + ' <= ' + str(upperBOfLinearExp) + '\n'
				else:
					ip += linearExp + ' - ' + str(abs(upperBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(clausedIndict) + ' <= ' + str(upperBOfLinearExp) + '\n'

			else:
				if lowerBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' - ' + str(lowerBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(abs(clausedIndict)) + ' >= ' + str(rightSideInt) + '\n'
				else:
					ip += linearExp + ' + ' + str(abs(lowerBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(abs(clausedIndict)) + ' >= ' + str(rightSideInt) + '\n'
				if upperBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' - ' + str(upperBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(abs(clausedIndict)) + ' <= ' + str(rightSideInt) + '\n'
				else:
					ip += linearExp + ' + ' + str(abs(upperBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(abs(clausedIndict)) + ' <= ' + str(rightSideInt) + '\n'
		if comparator == '<':
			if clausedIndict > 0:
				if upperBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' + ' + str(upperBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(clausedIndict) + ' < ' + str(upperBOfLinearExp) + '\n'
				else:
					ip += linearExp + ' - ' + str(abs(upperBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(clausedIndict) + ' < ' + str(upperBOfLinearExp) + '\n'
			else:
				if upperBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' - ' + str(upperBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(abs(clausedIndict)) + ' < ' + str(rightSideInt) + '\n'
				else:
					ip += linearExp + ' + ' + str(abs(upperBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(abs(clausedIndict)) + ' < ' + str(rightSideInt) + '\n'
		if comparator == '<=':
			if clausedIndict > 0:
				if upperBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' + ' + str(upperBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(clausedIndict) + ' <= ' + str(upperBOfLinearExp) + '\n'
				else:
					ip += linearExp + ' - ' + str(abs(upperBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(clausedIndict) + ' <= ' + str(upperBOfLinearExp) + '\n'
			else:
				if upperBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' - ' + str(upperBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(abs(clausedIndict)) + ' <= ' + str(rightSideInt) + '\n'
				else:
					ip += linearExp + ' + ' + str(abs(upperBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(abs(clausedIndict)) + ' <= ' + str(rightSideInt) + '\n'
		if comparator == '>':
			if clausedIndict > 0:
				if lowerBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' + ' + str(lowerBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(clausedIndict) + ' > ' + str(lowerBOfLinearExp) + '\n'
				else:
					ip += linearExp + ' - ' + str(abs(lowerBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(clausedIndict) + ' > ' + str(lowerBOfLinearExp) + '\n'
			else:
				if lowerBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' - ' + str(lowerBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(abs(clausedIndict)) + ' > ' + str(rightSideInt) + '\n'
				else:
					ip += linearExp + ' + ' + str(abs(lowerBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(abs(clausedIndict)) + ' > ' + str(rightSideInt) + '\n'
		if comparator == '>=':
			if clausedIndict > 0:
				if lowerBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' + ' + str(lowerBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(clausedIndict) + ' >= ' + str(lowerBOfLinearExp) + '\n'
				else:
					ip += linearExp + ' - ' + str(abs(lowerBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(clausedIndict) + ' >= ' + str(lowerBOfLinearExp) + '\n'
			else:
				if lowerBOfLinearExp-rightSideInt > 0:
					ip += linearExp + ' - ' + str(lowerBOfLinearExp-rightSideInt) + ' ' + IndictVar + str(abs(clausedIndict)) + ' >= ' + str(rightSideInt) + '\n'
				else:
					ip += linearExp + ' + ' + str(abs(lowerBOfLinearExp-rightSideInt)) + ' ' + IndictVar + str(abs(clausedIndict)) + ' >= ' + str(rightSideInt) + '\n'
		return ip

	# for capacity constraints IP formulation ->
	def projectionFromConNetToCVarBigM(self):
		for k in range(self.nOfTaxi):
			exNoListOfPickDrop = [0] + self.noListOfPickDrop[k] + [self.newDemandSize, -1 * self.newDemandSize]
			for i in range(3+self.noListOfAcceptedPoint[k]): # column index 'i'
				if i == 0: # projection from conNet to cVar for 1st column
					j = 1 # row index 'j' starts from 2nd row because there is nothing in 1st row
					while j < 3+self.noListOfAcceptedPoint[k]:
						if self.isRequiredVar(k, j, i):
							if exNoListOfPickDrop[j] > 0:
								if self.noListOfCarried[k]+exNoListOfPickDrop[j] > self.capacityOfEachTaxi[k]:
									# over capacity
									self.ip += self.clauseToIP([-1 * self.conNet[k][j][i]]) # hard unit clause
								else:
									self.ip += self.bigMFormulation(self.conNet[k][j][i], 'x', 'c' + str(self.conNet[k][j][i]), 0, self.capacityOfEachTaxi[k], '=', self.noListOfCarried[k]+exNoListOfPickDrop[j], 0)
								j += 2 # because we already have Eqs. (15) and (16), skip the next row (i.e., drop-off of each pair)
							else: # although drop-off, nOfCarried will not become negative
								self.ip += self.bigMFormulation(self.conNet[k][j][i], 'x', 'c' + str(self.conNet[k][j][i]), 0, self.capacityOfEachTaxi[k], '=', self.noListOfCarried[k]+exNoListOfPickDrop[j], 0)
								j += 1
						else:
							j += 1

	def projectionFromCVarToConNetBigM(self):
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]): # row index 'i'
				for j in range(3+self.noListOfAcceptedPoint[k]): # column index 'j'
					if self.isRequiredVar(k, i, j):
						# '(cNet = 0) -> (cVar = 0)', i.e., the contraposition of '(cVar > 0) -> (cNet = 1)'
						self.ip += self.bigMFormulation(-1 * self.conNet[k][i][j], 'x', 'c' + str(self.conNet[k][i][j]), 0, self.capacityOfEachTaxi[k], '=', 0, 0)

	def cVarTransitionByIPBigM(self):
		for k in range(self.nOfTaxi):
			exNoListOfPickDrop = [0] + self.noListOfPickDrop[k] + [self.newDemandSize, -1 * self.newDemandSize]
			for i in range(3+self.noListOfAcceptedPoint[k]): # row index 'i'
				for j in range(1, 3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						strBF = 'c' + str(self.conNet[k][i][j])
						for m in range(3+self.noListOfAcceptedPoint[k]):
							if self.isRequiredVar(k, j, m):
								strBF += ' - c' + str(self.conNet[k][j][m])
						#indicators = [self.conNet[k][i][j]]
						indicators = [self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0], self.conNet[k][i][j]]
						assert len(indicators) > 0
						if len(indicators) > 1:
							self.yVarID += 1
							self.ip += self.clauseToIP([self.yVarID] + [-x for x in indicators]).replace('x', 'y', 1)
							self.ip += self.bigMFormulation(self.yVarID, 'y', strBF, (1-strBF.count('c'))*self.capacityOfEachTaxi[k], self.capacityOfEachTaxi[k], '=', exNoListOfPickDrop[i], 0)
						else:
							self.ip += self.bigMFormulation(indicators[0], 'x', strBF, (1-strBF.count('c'))*self.capacityOfEachTaxi[k], self.capacityOfEachTaxi[k], '=', exNoListOfPickDrop[i], 0)

	def cVarLessThanBigM(self):
		for k in range(self.nOfTaxi):
			for i in range(3+self.noListOfAcceptedPoint[k]):
				for j in range(3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						# add its indicator for relaxation
						#indicators = [self.conNet[k][i][j]]
						indicators = [self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0], self.conNet[k][i][j]]
						if len(indicators) > 1:
							self.yVarID += 1
							self.ip += self.clauseToIP([self.yVarID] + [-x for x in indicators]).replace('x', 'y', 1)
							self.ip += self.bigMFormulation(self.yVarID, 'y', 'c' + str(self.conNet[k][i][j]), 0, self.capacityOfEachTaxi[k], '<=', self.capacityOfEachTaxi[k], 0)
						else:
							self.ip += self.bigMFormulation(indicators[0], 'x', 'c' + str(self.conNet[k][i][j]), 0, self.capacityOfEachTaxi[k], '<=', self.capacityOfEachTaxi[k], 0)

	def genIPForCapConsBigM(self):
		self.projectionFromConNetToCVarBigM()
		self.projectionFromCVarToConNetBigM()
		self.cVarTransitionByIPBigM()
		self.cVarLessThanBigM()

	# for deadline constraints IP formulation ->
	def projectionFromConNetToDVarBigM(self):
		for k in range(self.nOfTaxi):
			exNoListOfPickDrop = [0] + self.noListOfPickDrop[k] + [self.newDemandSize, -1 * self.newDemandSize]
			exDeadlineList = [self.currenTime] + self.deadlineList[k] + self.deadlineOfNewDemand
			for i in range(3+self.noListOfAcceptedPoint[k]): # column index 'i'
				if i == 0: # projection from conNet to dVar for 1st column
					j = 1 # row index 'j' starts from 2nd row because there is nothing in 1st row
					while j < 3+self.noListOfAcceptedPoint[k]:
						if self.isRequiredVar(k, j, i):
							indicators = [self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0], self.conNet[k][j][i]]
							self.yVarID += 1
							self.ip += self.clauseToIP([self.yVarID] + [-x for x in indicators]).replace('x', 'y', 1)
							if exNoListOfPickDrop[j] > 0: # pick-up
								if self.currenTime+self.cosTimeMatrices[k][j][i] < exDeadlineList[j]:
									# exceed deadline
									self.ip += self.clauseToIP([-1 * self.conNet[k][j][i]]) # hard unit clause
								else:
									self.ip += self.bigMFormulation(self.yVarID, 'y', 'd' + str(self.conNet[k][j][i]), 0, self.top, '=', self.currenTime+self.cosTimeMatrices[k][j][i], 0)
								j += 2 # because we already have Eqs. (15) and (16), skip the next row (i.e., drop-off of each pair)
							else: # drop-off
								if self.currenTime+self.cosTimeMatrices[k][j][i] > exDeadlineList[j]:
									# exceed deadline
									self.ip += self.clauseToIP([-1 * self.conNet[k][j][i]]) # hard unit clause
								else:
									self.ip += self.bigMFormulation(self.yVarID, 'y', 'd' + str(self.conNet[k][j][i]), 0, exDeadlineList[j], '=', self.currenTime+self.cosTimeMatrices[k][j][i], 0)
								j += 1
						else:
							j += 1

	def projectionFromDVarToConNetBigM(self):
		for k in range(self.nOfTaxi):
			exNoListOfPickDrop = [0] + self.noListOfPickDrop[k] + [self.newDemandSize, -1 * self.newDemandSize]
			exDeadlineList = [self.currenTime] + self.deadlineList[k] + self.deadlineOfNewDemand
			for i in range(3+self.noListOfAcceptedPoint[k]): # row index 'i'
				for j in range(3+self.noListOfAcceptedPoint[k]): # column index 'j'
					if self.isRequiredVar(k, i, j):
						indicators = [self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0], -1 * self.conNet[k][i][j]]
						self.yVarID += 1
						self.ip += self.clauseToIP([self.yVarID] + [-x for x in indicators]).replace('x', 'y', 1)
						# '(cNet = 0) -> (dVar = 0)', i.e., the contraposition of '(dVar > currenTime) -> (cNet = 1)' # ???
						if exNoListOfPickDrop[i] > 0: # pick-up
							self.ip += self.bigMFormulation(self.yVarID, 'y', 'd' + str(self.conNet[k][i][j]), 0, self.top, '=', 0, 0)
						else: # drop-off
							self.ip += self.bigMFormulation(self.yVarID, 'y', 'd' + str(self.conNet[k][i][j]), 0, exDeadlineList[i], '=', 0, 0)

	def dVarTransitiveByIPBigM(self):
		for k in range(self.nOfTaxi):
			exNoListOfPickDrop = [0] + self.noListOfPickDrop[k] + [self.newDemandSize, -1 * self.newDemandSize]
			exDeadlineList = [self.currenTime] + self.deadlineList[k] + self.deadlineOfNewDemand
			for i in range(3+self.noListOfAcceptedPoint[k]): # row index 'i'
				for j in range(1, 3+self.noListOfAcceptedPoint[k]):
					if self.isRequiredVar(k, i, j):
						strBF = 'd' + str(self.conNet[k][i][j])
						for m in range(3+self.noListOfAcceptedPoint[k]):
							if self.isRequiredVar(k, j, m):
								strBF += ' - d' + str(self.conNet[k][j][m])
						#indicators = [self.conNet[k][i][j]]
						indicators = [self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0], self.conNet[k][i][j]]
						assert len(indicators) > 0
						if len(indicators) > 1:
							self.yVarID += 1
							self.ip += self.clauseToIP([self.yVarID] + [-x for x in indicators]).replace('x', 'y', 1)
							if exNoListOfPickDrop[i] > 0: # pick-up
								self.ip += self.bigMFormulation(self.yVarID, 'y', strBF, (1-strBF.count('d'))*exDeadlineList[j], exDeadlineList[i], '=', self.cosTimeMatrices[k][i][j], self.top)
							else: # drop-off
								self.ip += self.bigMFormulation(self.yVarID, 'y', strBF, (1-strBF.count('d'))*exDeadlineList[j], exDeadlineList[i], '=', self.cosTimeMatrices[k][i][j], self.top)
						else:
							if exNoListOfPickDrop[i] > 0: # pick-up
								self.ip += self.bigMFormulation(indicators[0], 'x', strBF, (1-strBF.count('d'))*exDeadlineList[j], exDeadlineList[i], '=', self.cosTimeMatrices[k][i][j], self.top)
							else: # drop-off
								self.ip += self.bigMFormulation(indicators[0], 'x', strBF, (1-strBF.count('d'))*exDeadlineList[j], exDeadlineList[i], '=', self.cosTimeMatrices[k][i][j], self.top)

	def dVarComparatorBigM(self):
		for k in range(self.nOfTaxi):
			exNoListOfPickDrop = [0] + self.noListOfPickDrop[k] + [self.newDemandSize, -1 * self.newDemandSize]
			exDeadlineList = [self.currenTime] + self.deadlineList[k] + self.deadlineOfNewDemand
			for i in range(3+self.noListOfAcceptedPoint[k]): # row index 'i'
				for j in range(1, 3+self.noListOfAcceptedPoint[k]): # column index 'j'
					if self.isRequiredVar(k, i, j):
						if exNoListOfPickDrop[i] < 0: # drop-off, thus, '<=N' (i.e., dLessThan)
							# add its indicator for relaxation
							#indicators = [self.conNet[k][i][j]]
							indicators = [self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0], self.conNet[k][i][j]]
							if len(indicators) > 1:
								self.yVarID += 1
								self.ip += self.clauseToIP([self.yVarID] + [-x for x in indicators]).replace('x', 'y', 1)
								self.ip += self.bigMFormulation(self.yVarID, 'y', 'd' + str(self.conNet[k][i][j]), 0, exDeadlineList[i], '<=', exDeadlineList[i], 0)
							else:
								self.ip += self.bigMFormulation(indicators[0], 'x', 'd' + str(self.conNet[k][i][j]), 0, exDeadlineList[i], '<=', exDeadlineList[i], 0)
						else: # pick-up, thus, '>=N' (i.e., dlMoreThan)
							# must add its indicator
							#indicators = [self.conNet[k][i][j]]
							indicators = [self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0], self.conNet[k][i][j]]
							assert len(indicators) > 0
							if len(indicators) > 1:
								self.yVarID += 1
								self.ip += self.clauseToIP([self.yVarID] + [-x for x in indicators]).replace('x', 'y', 1)
								self.ip += self.bigMFormulation(self.yVarID, 'y', 'd' + str(self.conNet[k][i][j]), 0, self.top, '>=', exDeadlineList[i], 0)
							else:
								self.ip += self.bigMFormulation(indicators[0], 'x', 'd' + str(self.conNet[k][i][j]), 0, self.top, '>=', exDeadlineList[i], 0)

	def genIPForDlConsBigM(self):
		self.projectionFromConNetToDVarBigM()
		self.projectionFromDVarToConNetBigM()
		self.dVarTransitiveByIPBigM()
		self.dVarComparatorBigM()

	def genIPForViaPointLists(self):
		previousRoutes = []
		for k in range(self.nOfTaxi):
			eachPreRoute = []
			for i in range(len(self.viaPointLists[k])):
				eachPreRoute.append(self.conNet[k][self.viaPointLists[k][i]][0] if i == 0 else self.conNet[k][self.viaPointLists[k][i]][self.viaPointLists[k][i-1]])
			previousRoutes.append(eachPreRoute)
		for k in range(self.nOfTaxi):
			for i in range(self.nOfTaxi):
				if i != k:
					for j in range(len(previousRoutes[i])):
						self.ip += self.clauseToIP([-1 * self.preCaseVarList[k], previousRoutes[i][j]])
			self.ip += self.clauseToIP([-1 * self.preCaseVarList[k], self.rchNet[k][2+self.noListOfAcceptedPoint[k]][0]])
		self.ip += self.clauseToIP([-1 * self.assumptionVar] + self.preCaseVarList)

	def declareBooleanVar(self):
		self.ip += '\nBinary\n'
		for i in range(self.getLastVarIDinRchNet()):
			self.ip += 'x' + str(1+i) + '\n'
		for i in range(self.yVarID):
			self.ip += 'y' + str(1+i) + '\n'

	def declareIntVar(self):
		self.ip += '\nGeneral\n'
		for i in range(self.getLastVarIDinConNet()):
			self.ip += 'c' + str(1+i) + '\n'
			self.ip += 'd' + str(1+i) + '\n'

	def genTailOfIPFile(self):
		self.ip += 'End\n\nOptimize\n\nDisplay solution variables -\n\nQuit'

	def writeIPFile(self, fileName):
		IPFile = open(fileName + '.lp', 'w')
		IPFile.write(self.ip)
		IPFile.close()

	def writeMSTFile(self, fileName):
		tmpStrBuf = ''
		MSTFile = open(fileName + '.mst', 'w')
		tmpStrBuf += '<?xml version = "1.0" encoding="UTF-8" standalone="yes"?>\n'
		tmpStrBuf += '<CPLEXSolutions version="1.2">\n'
		tmpStrBuf += ' <CPLEXSolution version="1.2">\n'
		tmpStrBuf += '  <header\n'
		tmpStrBuf += '    problemName="./' + fileName + '.lp"\n'
		tmpStrBuf += '    solutionName="m1"\n'
		tmpStrBuf += '    solutionIndex="0"\n'
		tmpStrBuf += '    MIPStartEffortLevel="0"\n'
		tmpStrBuf += '    writeLevel="2"/>\n'
		tmpStrBuf += '  <variables>\n'
		tmpStrBuf += '   <variable name="x' + str(self.assumptionVar) + '" index="1" value="1"/>\n'
		tmpStrBuf += '  </variables>\n'
		tmpStrBuf += ' </CPLEXSolution>\n'
		tmpStrBuf += '</CPLEXSolutions>\n'
		MSTFile.write(tmpStrBuf)
		MSTFile.close()

#==============================================================================
#

#===========================
if __name__ == '__main__':
	rtss = RTSS()
	rtss.genVarForConNet()
	rtss.genVarForRchNet()
	#rtss.netPrinter(rtss.conNet)
	#rtss.netPrinter(rtss.rchNet)

	rtss.genSoftClause()
	rtss.genHardClauseForHPConsWithBasicIdea()
	#rtss.genHardClauseForHPConsWithNewIdea()
	rtss.genHardClauseForEq17()
	rtss.genHardClauseForEq18()
	rtss.genHardClauseForViaPointLists()

	#rtss.wcnf.to_file('rtss.wcnf') # output wcnf file
	#rtss.writExternalityFile('rtss') # output externality file
	rtss.wcnf.to_file(rtss.instanceID + '.wcnf')
	rtss.writExternalityFile(rtss.instanceID)

	# IP formulation ->
	rtss.genIPObjectiveFunction()
	rtss.genIPForHPConsWithBasicIdea()
	#rtss.genIPForHPConsWithNewIdea()
	rtss.genIPForEq17()
	rtss.genIPForEq18()
	rtss.genIPForCapConsBigM()
	rtss.genIPForDlConsBigM()
	rtss.genIPForViaPointLists()
	rtss.declareBooleanVar()
	rtss.declareIntVar()
	rtss.genTailOfIPFile()

	#rtss.writeIPFile('rtss')
	#rtss.writeMSTFile('rtss')
	rtss.writeIPFile(rtss.instanceID)
	rtss.writeMSTFile(rtss.instanceID)

'''
with RC2(rtss.wcnf, incr=True, verbose=2) as rc2:
	model = rtss.solveRTSS(rc2)
	if model != None:
		print(rtss.decodeModel(model))
		print('cost: {}'.format(rc2.cost))
	else:
		print('UNSAT')
		print('c oracle time: {0:.4f}'.format(rc2.oracle_time()))
'''







