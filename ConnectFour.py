import sys
class MyConnectFour:
	
	def __init__(self):
		#self.grid = int[7][6]
		self.grid = []
		for x in range(7):
			self.grid.append([])
			for y in range(6):
				self.grid[x].append(0)
	
	def move(self, grid, col, player):
		changed = False
		if player == 1:
			piece = 1
		elif player == 2:
			piece = 2
		else:
			print("invalid player")
			return False
		
		for y in range(6):
			if grid[col][y] == 0:
				grid[col][y] = piece
				changed = True
				break
		return changed
	
	def actualMove(self, col, player):
		return self.move(self.grid, col, player)
		
	def pretendMove(self, grid, col, player):
		return self.move(grid, col, player)
	
	def printGrid(self, grid):
		if not grid:
			print("None")
			return
		print(" 1 2 3 4 5 6 7")
		print(" - - - - - - -")
		for y in range(len(grid[0])-1,-1,-1):
			line = ""
			for x in range(len(grid)):
				line = line+" "+str(grid[x][y])
			print(line)
	
	def convertToDoubleGrid(self, grid, player):	
		return DoubleGrid(grid,player)
	
	def evaluate(self, grid):
		for x in range(7):
			for y in range(6):
				try:
					vertical = grid[x][y]*grid[x][y+1]*grid[x][y+2]*grid[x][y+3]
					vertical2 = grid[x][y]+grid[x][y+1]+grid[x][y+2]+grid[x][y+3]
					if vertical == 1 and vertical2 == 4:
						return 1
					elif vertical == 16 and vertical2 == 8:
						return 2
					horizontal = grid[x][y]*grid[x+1][y]*grid[x+2][y]*grid[x+3][y]
					horizontal2 = grid[x][y]+grid[x+1][y]+grid[x+2][y]+grid[x+3][y]
					if horizontal == 1 and horizontal2 == 4:
						return 1
					if horizontal == 16 and horizontal2 == 8:
						return 2
					diagonalFirst = grid[x][y]*grid[x+1][y+1]*grid[x+2][y+2]*grid[x+3][y+3]
					diagonalFirst2 = grid[x][y]+grid[x+1][y+1]+grid[x+2][y+2]+grid[x+3][y+3]
					if diagonalFirst == 1 and diagonalFirst2 == 4:
						return 1
					if diagonalFirst == 16 and diagonalFirst2 == 8:
						return 2
					diagonalSecond = grid[x][y]*grid[x-1][y+1]*grid[x-2][y+2]*grid[x-3][y+3]
					diagonalSecond2 = grid[x][y]+grid[x-1][y+1]+grid[x-2][y+2]+grid[x-3][y+3]
					if diagonalSecond == 1 and diagonalSecond2 == 4:
						return 1
					if diagonalSecond == 16 and diagonalSecond2 == 8:
						return 2
				except IndexError:
					pass
		return 0
	
	def getGameOutcome(self, grid):
		winner = self.evaluate(grid)
		if winner != 0:
			return winner
		for x in range(7):
			if grid[x][5] == 0:
				return 0
		return 3
	
	def copyGrid(self, grid):
		gridCopy = []
		for x in range(7):
			gridCopy.append([])
			for y in range(6):
				n = grid[x][y]
				gridCopy[x].append(n)
		return gridCopy
	
	def getPotentialDoubleGrids(self, player, grid, depth):
		if depth == 0:
			return self.convertToDoubleGrid(grid, player)
		else:
			output = []
			#for each move player can make
			for myMove in range(7):
				gridCopy = self.copyGrid(grid)
				#attempt that move on the copy of the grid given
				moveSuccess = self.pretendMove(gridCopy, myMove, player)
				evaluation = self.evaluate(gridCopy)
				#if the move failed, put None in the output instead of a list of recursive outputs
				if moveSuccess == 0:
					output.append(None)
				#if the move resulted in a victory, put that single victory in the output, instead of a list
				elif evaluation == player:
					output.append([self.convertToDoubleGrid(gridCopy, player)])
				#if the move was valid and the game continues
				else:
					#add a list to the output
					output.append([])
					#for each move the other player could make
					for theirMove in range(7):
						#attempt that move on a copy of the grid
						gridCopy2 = self.copyGrid(gridCopy)
						moveSuccess2 = self.pretendMove(gridCopy2, theirMove, 3-player)
						evaluation2 = self.evaluate(gridCopy2)
						if moveSuccess2 == 0:
							output[myMove].append(None)
						elif evaluation2 == 3-player:
							output[myMove].append(self.convertToDoubleGrid(gridCopy2, player))
						else:
							output[myMove].append(self.getPotentialDoubleGrids(player, gridCopy2, depth-2))
							
			return output
							
	def getPotentialDoubleGridsFlat(self, player, grid, depth):
		depth=depth*2
		originalList = self.getPotentialDoubleGrids(player, grid, depth)
		newList = []
		for i in range(len(originalList)):
			newList.append(self.flatten(originalList[i]))
		return newList
	
	def isDoubleGrid(self, source):
		return isinstance(source, DoubleGrid)

	def flatten(self, source):
		#base case
		if source == None:
			return source
		#base case - if this is a doubleGrid
		elif self.isDoubleGrid(source):
			return source
		
		output = []
		#flatten everything inside source
		for i in range(len(source)):
			inner = self.flatten(source[i])
			#if inner isn't a double grid, add each thing in it to output
			if isinstance(inner, list):
				for j in range(len(inner)):
					output.append(inner[j])
			else:
				output.append(inner)
		return output
	
	def printPotentials(self,potentials):
		for i in range(len(potentials)):
			if isinstance(potentials[i],list):
				num=0
				for j in range(len(potentials[i])):
					if potentials[i][j] != None:
						num += 1
				print("COL",i+1,":",num,"Possibilities")
			elif self.isDoubleGrid(potentials[i]):
				print("COL",i+1,":",1,"Possibilities")
			else:
				print("COL",i+1,":",0,"Possibilities")
				
	def play(self,depth):
		while True:
			self.printGrid(self.grid)
			potentials = self.getPotentialDoubleGridsFlat(1,self.grid,depth)
			self.printPotentials(potentials)
			moveSuccess = 0
			while moveSuccess == 0:
				col = input("Player 1 move: ")
				col = int("0"+col)
				if col>=1 and col<=7:
					moveSuccess = self.actualMove(col-1, 1)
					evaluation = self.evaluate(self.grid)
			if evaluation == 1:
				print ("\nPLAYER 1 WINS")
				break
			elif evaluation == 3:
				print ("\nTIE GAME")
			self.printGrid(self.grid)
			potentials2 = self.getPotentialDoubleGridsFlat(2,self.grid,depth)
			self.printPotentials(potentials2)
			moveSuccess = 0
			while moveSuccess == 0:
				col = input("Player 2 move: ")
				col = int("0"+col)
				if col>=1 and col<=7:
					moveSuccess = self.actualMove(col-1, 2)
					evaluation = self.evaluate(self.grid)
			if evaluation == 2:
				print ("\nPLAYER 1 WINS")
				break
			elif evaluation == 3:
				print ("\nTIE GAME")
		self.printGrid(self.grid)

class DoubleGrid():
	
	def __init__(self,grid,player):
		self.doubleGrid = []
		for x in range(14):
			self.doubleGrid.append([])
			for y in range(6):
				self.doubleGrid[x].append(0)
				
		for x in range(7):
			for y in range(6):
				if grid[x][y]==1:
					if player == 1:
						self.doubleGrid[x][y]=1
					else:
						self.doubleGrid[x+7][y]=1
				elif grid[x][y]==2:
					if player == 1:
						self.doubleGrid[x+7][y]=1
					else:
						self.doubleGrid[x][y]=1
					
	def getDoubleGrid(self):
		return self.doubleGrid
	
	def getReverseDoubleGrid(self):
		reverseGrid = []
		for x in range(14):
			reverseGrid.append([])
			for y in range(6):
				reverseGrid[x].append(0)
				
		for x in range(7):
			for y in range(6):
				if grid[x][y]==1:
					if player == 1:
						reverseGrid[13-x][y]=1
					else:
						reverseGrid[13-(x+7)][y]=1
				elif grid[x][y]==2:
					if player == 1:
						reverseGrid[13-(x+7)][y]=1
					else:
						reverseGrid[13-x][y]=1
				
	
def main():			
	c4 = MyConnectFour()
	depth = int(input("How many pairs of moves ahead would you like to compute?\nEnter an integer 1-3: "))
	c4.play(depth)
	
if __name__=="__main__":
	main()
					
		