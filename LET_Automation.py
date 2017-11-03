#This program: 
#	1. generates reference and target sequences; 
#	2. stores the Labeled-eulerian-tour in a nested list;
#	3. applies smooth, trim, fork, de-knot, and combine to the list;
#	4. prints the result in "output.txt".

import time

#class Random Number Generator(RNG) 
class RNG:
	def __init__(self, seed):											 
		self.n = seed													
		
	def next(self):
		self.n = (16807 * self.n)%(2147483648 - 1)						
		return self.n
	
	def choose(self, objects):
		index = self.next()												
		return objects[index % len(objects)]							

#class NDA the main class
class GENE:
	#N: reference/target length
	#L: window length
	#M: mistake characters tolerated in a window
	#P: possibility to mutate of each character
	#S: initial seed to feed the RNG
	#O: operating mode: 0: prints results only;
	#					1: prints results and methods used;
	#					2: prints results, methods used, and input/output 
	#					of each method. This is time consuming.  
	def __init__(self, N, L, M, P, S, O):
		self.L = L
		self.M = M
		self.P = P
		self.S = S
		self.N = N
		self.O = O
		self.rng = RNG(S)
		
		self.LM = False
		self.run = False
		self.done = False
		
		self.let = []
		self.label = {}
		self.edge = ()
		
		self.reference = ''
		self.target = ''
		self.start = ''
		self.end = ''
		self.result = ''
		
	def Reference(self):
		for i in range(self.N):
			self.reference += self.rng.choose(['A','C','G','T'])
			
		if self.O == 2:
			print("Reference is: ----------------------------------------")	
			print(self.reference)
			print
		
	def Randomize(self):
		self.target = ''
		self.target += self.reference[0:self.L]
		
		for i in self.reference[self.L:(self.N-self.L)]:
			if ((self.rng.next() % 100) + 1) > (100 * self.P):
				self.target += i
			else:
				if i=='A':
					self.target += self.rng.choose(['C','G','T'])
				if i=='C':
					self.target += self.rng.choose(['A','G','T'])
				if i=='G':
					self.target += self.rng.choose(['C','A','T'])
				if i=='T':
					self.target += self.rng.choose(['C','G','A'])
		
		self.target += self.reference[(self.N-self.L):]
		
#		if self.O == 2:
#			print("Random target is: ")
#			print(self.target)
#			print
		
	def Generate(self):
		self.rng.next()
		self.LM = False
		while self.LM == False:
			self.Randomize()
			for index in range(self.L, (self.N - 2*self.L + 1)):
				mistake = 0
				for k_dex in range(0, self.L):
					if self.target[index + k_dex] != self.reference[index + k_dex]:
						mistake += 1
				
				if mistake > self.M:
					self.LM = False
					break
				else:
					self.LM = True
					
		for index in range(len(self.target) - self.L - 1):
			self.Edge(self.target[(index+1):(index+self.L+1)])
		self.Start(self.target[0:self.L])
		self.End(self.target[(len(self.target) - self.L):])
		
		if self.O == 2:
			print("Final target is: ----------------------------------------")	
			print(self.target)
			print
		
	def Label(self):	
		num_edge = len(self.reference) - self.L + 1
		 
		for i in self.edge:
			labels = []
			for j in range(num_edge):
				num_same = 0
				for k in range(self.L):
					if i[k] == self.reference[j+k]:
						num_same += 1
				if num_same >= (self.L - self.M):
					labels += (j+1,)
			if len(labels) != 0:	
				self.label.update({i:labels})
		
		if self.O == 2:
			print("Labels are: ") 
			print(self.label)
			print
	
	def Let(self):
		noend_label = self.label.copy()
		del noend_label[self.end]
		
		for i in noend_label:
			node = i[1:]
			pointed = []
			pointing = []
#			middle_label = noend_label.copy()
#			del middle_label[self.start]
			
			for j in self.label:
				if node == j[1:] and j != self.end:
					pointed += [[j[0], self.label[j]]]
				if node == j[0:-1] and j != self.start:
					pointing += [[j[-1], self.label[j]]]
					
			if not self.isIn(node, self.let):
				self.let += [[node, pointed, pointing]]
		
		if self.O != 0:		
			print(self.let)
			print
	
	def Split(self):	
		isRun = self.let[0:]
		for node in self.let:
			for incoming in node[1]:
				if len(incoming[1]) > 1:
					self.run = True
					new_incoming = []
					for i in range(len(incoming[1])):
						node[1].append([incoming[0], [incoming[1][i]]])					
					node[1].remove(incoming)

			for outgoing in node[2]:
				if len(outgoing[1]) > 1:
					self.run = True
					new_outgoing = []
					for i in range(len(outgoing[1])):
						node[2].append([outgoing[0], [outgoing[1][i]]])
					node[2].remove(outgoing)
		
		if self.O == 2:
			print(self.let)
			print
		if isRun == self.let:
			self.run = False
							
	def isIn(self, node, nodes):
		for i in nodes:
			if node == i[0]:
				return True
		return False 
		
	def Start(self, edge):
		self.edge += (edge,)
		self.start = edge
		
	def End(self, edge):
		self.edge += (edge,)
		self.end = edge
		
	def Edge(self, edge):
		self.edge += (edge,)
		
	def Target_given(self, target):
		f = open(target, "r")
		self.target = f.read()
		f.close()
		
		for index in range(len(self.target) - self.L - 1):
			self.Edge(self.target[(index+1):(index+self.L+1)])
		self.Start(self.target[0:self.L])
		self.End(self.target[(len(self.target) - self.L):])
		
	def Reference_given(self, reference):
		f = open(reference, "r")
		self.reference = f.read()
		f.close()
		
	def Smooth(self):
		isRun = self.let[0:]
		for node in self.let:
			for pointed in node[1]:
				for incoming in pointed[1]:
					keep = False
					for pointing in node[2]:
						for outgoing in pointing[1]:
							if outgoing == incoming + len(node[0]) - self.L + 2:
								keep = True
					if keep == False:
						if self.O == 2:
							print("smoothed"+str(incoming)+"forward"+node[0]+"from"+str(pointed[1]))
						if len(pointed[1]) != 1:
							pointed[1].remove(incoming)
							self.run = True
						elif len(node[1]) != 1:
							node[1].remove(pointed)
							self.run = True
					
			for pointing in node[2]:
				for outgoing in pointing[1]:
					keep = False
					for pointed in node[1]:
						for incoming in pointed[1]:
							if outgoing == incoming + len(node[0]) - self.L + 2:
								keep = True
					if keep == False:
						if self.O == 2:
							print("smoothed"+str(outgoing)+"back"+node[0]+"from"+str(pointing[1]))
						if len(pointing[1]) != 1:
							pointing[1].remove(outgoing)
							self.run = True
						elif len(node[2]) != 1:
							node[2].remove(pointing)
							self.run = True
		
#		self.Format()
		if isRun == self.let:
			self.run = False
#		else:
#			print "smoothed successfully--------------------------------------------------------------------------------------"
		if self.O == 2:
			print(self.let)
			print
		
	def Trim(self):
		isRun = self.let[0:]
		removePoint = []
		for node in self.let:
			for inOut in node[1:]:
				for point in inOut:
					if len(point[1]) == 1:
#						print("singleton found: "+str(point[1][0])+" "+node[0])
						singleton = point[1][0]
						for node_find in self.let:
							if node_find[0] != node[0]:
								for inOut_find in node_find[1:]:
									for point_find in inOut_find:
										if len(point_find[1]) != 1:
											for find in point_find[1]:
												if ((point[0]+node[0][0:self.L-1]!=node_find[0][-(self.L-1):]+point_find[0]) and (point_find[0]+node_find[0][0:self.L-1]!=node[0][-(self.L-1):]+point[0])):
													if find == singleton:
														if self.O == 2:
															print("trimmed "+str(find)+" point:"+str(node)+" "+str(point[1])+" node_find:"+node_find[0]+" from"+str(node_find))
														point_find[1].remove(find)
														self.run = True
														
#												elif (point[0]+node[0][0:self.L-1]==node_find[0][-(self.L-1):]+point_find[0]):
#													print "found pointed pair: "+node[0]+" "+str(node_find)
#												elif (point_find[0]+node_find[0][0:self.L-1]==node[0][-(self.L-1):]+point[0]):
#													print "found pointed pair: "+node[0]+" "+str(node_find)
		
#		self.Format()						
		if isRun == self.let:
			self.run = False
		if self.O == 2:
			print (self.let)
			print
		
	def Fork(self):
		isRun = self.let[0:]
		addNode = []
		for node in self.let:
			len_pointed = len(node[1])
			len_pointing = len(node[2])
			if len_pointed >= 2 or len(node[1][0][1]) >= 2:
				matches = 0
				max_match = 0
				for i in node[1]:
					max_match += len(i[1])
				for pointed in node[1]:
					for pointed_index in pointed[1]:	
						for pointing in node[2]:
							for pointing_index in pointing[1]:
								if pointing_index == pointed_index + len(node[0]) - self.L + 2:
									matches += 1
									if self.O == 2:
										print("match is: "+pointed[0]+" "+pointing[0])
								
				if matches == max_match:
					if self.O == 2:
						print("match found: "+node[0])
					for pointed in node[1]:
						for pointed_index in pointed[1]:	
							for pointing in node[2]:
								for pointing_index in pointing[1]:
									if pointing_index == pointed_index + len(node[0]) - self.L + 2:
										addNode += [[node[0], [[pointed[0],[pointed_index]]], [[pointing[0],[pointing_index]]]]]
										if self.O == 2:
											print("added node: ")
											print(addNode)
										self.run = True
										
		for newNode in addNode:
			for node in self.let:
				if newNode[0] == node[0]:
					if self.O == 2:
						print("current let is:")
						print(self.let)				
					self.let.remove(node)
					if self.O == 2:	
						print("node removed:")
						print(node)
					break
				
		self.let += addNode
		
#		self.Format()
		if isRun == self.let:
			self.run = False
		if self.O == 2:
			print(self.let)
			print

	def Deknot_old(self):
		try:
			removeTotal = []
			for node in self.let:
				if len(node[1]) > 1:
					removeNode = []
#					newNode = [node[0]] + [node[1]] + [node[2]]
					newNode = node
					for pointing in node[2]:
						nextNode = node[0][1:] + pointing[0]
						while nextNode != node:
							for searchNode in self.let:
								if searchNode[0] == nextNode:
									newNode[0] += searchNode[0][2]
									newNode[2] = searchNode[2]
									nextNode = newNode[0][-2:] + newNode[2][0][0]
									removeNode += [searchNode[0]]
									for newPointed in newNode[1]:
										for newPointing in newNode[2]:
											if newPointed[0] == newPointing[0]:
												newNode[1].remove(newPointed)
									removeTotal += removeNode 
									print(newNode)
									print(removeNode)
		finally:
			print (self.let)
			for node in self.let:
				for newRemove in removeTotal:
					if newRemove == node[0]:				
						self.let.remove(node)
						break
			print (self.let)
			
	def Deknot(self):
			isRun = self.let[0:]
			removeTotal = []
			for node in self.let:
				pointed_size = 0
				pointing_size = 0
				for pointed in node[1]:
					pointed_size += len(pointed[1])
				for pointing in node[2]:
					pointing_size += len(pointing[1])
				if pointed_size == 2 and pointing_size == 2:
					if self.O == 2:
						print "Found 2 in 2 out: " + node[0]
					for pointing in node[2]:
						nextLabel = node[0][-(self.L-2):] + pointing[0]
						for searchNode in self.let:
							if searchNode[0][0:(self.L-1)] == nextLabel and len(searchNode[1]) == 1 and len(searchNode[1][0][1]) == 1 and len(searchNode[2]) == 1 and len(searchNode[2][0][1]) == 1 and searchNode[0][-(self.L-2):]+searchNode[2][0][0] == node[0]:
								if self.O == 2:
									print "Found deknot pair: " + node[0] + searchNode[0]
								node[0] += (searchNode[0][self.L-2:]+searchNode[2][0][0])
								if len(node[1]) > 1:
									node[1].remove(searchNode[2][0])
								else:
									node[1][0][1].remove(searchNode[2][0][1][0])
								if len(node[2]) > 1:
									node[2].remove(searchNode[1][0])
								else:
									node[2][0][1].remove(searchNode[1][0][1][0])
								removeTotal.append(searchNode[0])
								break
							break
			for node in self.let:
				if node[0] in removeTotal:
					if self.O == 2:
						print "Deknot removed y: " + node[0]
					self.let.remove(node)
			
#			self.Format()
			if isRun == self.let:
				self.run = False
			if self.O == 2:
				print (self.let)
				print
	
	def Combine(self):
		isRun = self.let[0:]
		self.let.sort(key = lambda row: row[1][0][1][0])
		for node in self.let:
			if len(node[2]) == 1 and len(node[2][0][1]) == 1:
				nextLabel = node[0][-(self.L-2):] + node[2][0][0]
				while True:
					foundNext = False
					for searchNode in self.let:
						if searchNode[0][0:(self.L-1)] == nextLabel and len(searchNode[1]) == 1 and len(searchNode[1][0][1]) == 1 and searchNode[1][0][1] == node[2][0][1]:
							if self.O == 2:
								print(searchNode)
								print
							node[0] += searchNode[0][(self.L-2):]
							node[2] = searchNode[2]
							if len(searchNode[0]) != len(self.reference) - 2:
								self.let.remove(searchNode)
#								print "Combine removed: " + str(searchNode)
							nextLabel = node[0][-(self.L-2):] + node[2][0][0]
							foundNext = True
							self.run = True
							break
					if foundNext == False:
						break
		for node in self.let:
			if len(node[0]) == len(self.reference) - 2:
				self.let = [node[0:]]
				break
		if len(self.let) == 1:
			self.result = self.start[0] + self.let[0][0] + self.end[-1]
			print ("The result is: ")
			print (self.result)
			self.done = True
			
		else:
			if self.O == 2:
				print (self.let)
				print
		
#		self.Format()	
		if isRun == self.let:
			self.run = False
	
	def cutDup(self):
		for node in self.let:
			count = 0
			for searchNode in self.let:
				if searchNode == node:
					count += 1
					if count > 1:
						print "Found dup node" + str(searchNode)
						self.let.remove(searchNode)
	
	def Shrink(self):
		nodeShrink = []
		for node in self.let:
			if len(node[0]) > self.L-1 and len(node[1]) == 1 and len(node[1][0][1]) == 1 and len(node[2]) == 1 and len(node[2][0][1]) == 1:
				nodeShrink.append(node)
		
		for searchNode in self.let:
			if len(searchNode[1]) == 1 and len(searchNode[1][0][1]) == 1 and len(searchNode[2]) == 1 and len(searchNode[2][0][1]) == 1:
				for bigNode in nodeShrink:
					if searchNode[0] != bigNode[0] and searchNode[0] in bigNode[0] and bigNode[1][0][1] < searchNode[1][0][1] and bigNode[2][0][1] > searchNode[2][0][1]:
						print "Shrinked range: " + str(searchNode) + "from " + str(bigNode) 
						try:
							self.let.remove(searchNode)
						except ValueError:
							pass
						
	def Reverse(self):
		for node in self.let:
			if len(node[1]) == 1 and len(node[1][0][1]) == 1 and len(node[2]) == 1 and len(node[2][0][1]) == 1 and node[1][0][1] > node[2][0][1]:
				print "Deleted reversed node: " + str(node)
				self.let.remove(node)
				
	def Format(self):
		self.Shrink()
		self.cutDup()
		 
	def toFile(self, infile):
		f = open("output.txt", "a")
		infile = str(infile)
		f.write(infile)
		f.write("\n")
		f.close()
		
	def Snip(self):
		snip = ''
		print "Snip list is: "
		self.toFile("Snip list is: ")
		for i in range(self.N):
			if self.target[i] != self.reference[i]:
				snip += str(i)
				snip += self.reference[i]
				snip += self.target[i]
				snip += "\n"
		print snip
		self.toFile(snip)	
		
	def Run(self):
		self.Label()
		self.Let()
		self.Snip()
		print("Target is: ")
		print(self.target)
		
		while True:
			self.Smooth()
			if self.O != 0:
				print("<-Smoothed()--------------------------------------------------------------------------------------")
			if self.run == False:
				self.Trim()
				if self.O != 0:
					print("<-Trimmed()--------------------------------------------------------------------------------------")
				if self.run == False:
					self.Combine()
					if self.O != 0:
						print("<-Combined()--------------------------------------------------------------------------------------")
					if self.done == True:
						break
					if self.run == False:
						self.Fork()
						if self.O != 0:
							print("<-Forked()--------------------------------------------------------------------------------------")
						if self.run == False:
							self.Deknot()
							if self.O != 0:
								print("<-Deknotted()--------------------------------------------------------------------------------------")
							if self.run == False:
								print("Unable to proceed, the final LET is: ")
								self.toFile("Unable to proceed: \n")
								self.toFile(self.let)
								self.toFile("\n")
								print(self.let)
								break
		
		self.toFile("Target is: \n")
		self.toFile(self.target)
		self.toFile("Reference is: \n")
		self.toFile(self.reference)
		
		if self.result == self.target:
			print("The result is the same as the target.")
			self.toFile("Successful result: \n")
			self.toFile(self.result)
			self.toFile("\n")
		elif self.result != self.target and self.result != '':
			print("The result is different: ")
			print("Result is: ")
			print(self.result)
			self.toFile("Different result: \n")
			self.toFile(self.result)
			self.toFile("\n")
			print("Target is: ")
			print(self.target)

def testSeed(seed):		
	A = GENE(50, 6, 1, 0.05, seed, 2)
	A.Reference()
	A.Generate()

	#A.Reference_given("reference.txt")
	#A.Target_given(   "target.txt")

	start_time = time.time()

	A.Run()

	print("--- %s seconds ---" % (time.time() - start_time))

testSeed(7)
