import matplotlib.pyplot as plt
import numpy as np

# Star Battle Class
#
# Description:
# 	Takes in a star battle puzzle (and possibly the location of some known stars) and
#	produces the constraints on the remaining unknown cells. 
#
# Inputs:
#	n - size of puzzle
#	region_array - an n x n array, where each element is an element between 0 and n-1, 
#		indicating what region that cell is part of
#	k (optional) - number of stars required to be in each row, column and region.
#		Currently this class is only implemented for k=1.
#
# Methods:
#	set_known_stars - add known stars to the puzzle grid, reducing the number of unknown
#		cells and constraints
#	reset_known_stars - clear the known stars
#	get_constraints - returns the list of constraints on unknown cells accounting for the
#		known stars
#	print_constraints - prints the list of constraints in a table-like format
#	set_solution_stars - adds solution stars, as indicated by unknown cell index, to the
#		solution gird
#	show_puzzle_grid - displays the puzzle grid
#
# Requirements:
#	matplotlib.pyplot as plt
#	numpy as np

class Star_Battle:
	
	def __init__(self, n, region_array, k=1):
		self.n = n
		self.k = 1 # currently this class is only implemented for the case k=1
		self.region_array = region_array
		self.known_stars = []
		self.solution_stars = []
		self.__update_unknown_cells()
		self.__update_constraints()
		
	def set_known_stars(self, coords_list):
		self.known_stars = coords_list
		self.__update_unknown_cells()
		self.__update_constraints()
		
	def reset_known_stars(self):
		self.set_known_stars([])
		
	def __update_unknown_cells(self):
	
		delta_ij_neighbors = [(di,dj) for di in range(-1,2) for dj in range(-1,2)]
		
		# warning: can only rule out rows, columns, and regions like this if k=1!
		self.forbidden_cells = (
		 	# all cells in the rows of known stars
			[(i,j) for j in range(0,self.n) for i,_ in self.known_stars]
			
			# all cells in the columns of known stars
			+ [(i,j) for i in range(0,self.n) for _,j in self.known_stars]
			
			# all cells in the regions of known stars
			+ [
				(i,j) for i in range(0,self.n) for j in range(0,self.n)
				for coords_known in self.known_stars
				if self.region_array[i,j] == self.region_array[coords_known]
			]
			
			 # all cells adjacent to known stars
			+ [
				(i+di,j+dj) for di,dj in delta_ij_neighbors for i,j in self.known_stars
				if 0<=i+di<self.n and 0<=j+dj<self.n
			]
		)		
		
		# generate lists of unknown cells (i.e. those not disallowed)
		self.unknown_cells = [
			(i,j) for i in range(0,self.n) for j in range(0,self.n)
			if (i,j) not in self.forbidden_cells
		]
		
		# ... and mappings between the coordinates and a linear index
		self.coords_to_index = {}
		self.index_to_coords = {}
		for (ind,coords) in enumerate(self.unknown_cells):
			self.coords_to_index[coords] = ind
			self.index_to_coords[ind] = coords
	
	def __update_constraints(self):
		# generate lists of constraints of the form:
		# 	(<list of cell indicies>, <the required star tally amongst those cells>),
		#	where the required tally is either an integer or the string '<=1'
		
		# ... for columns, rows and regions, the only valid star tally is k
		row_constraints = [
			(
				[self.coords_to_index[(i,j)] for i,j in self.unknown_cells if i==row],
				self.k
			)
			for row in range(0,self.n)
		]
		column_constraints = [
			(
				[self.coords_to_index[(i,j)] for i,j in self.unknown_cells if j==col],
				self.k
			)
			for col in range(0,self.n)
		]
		region_constraints = [
			(
				[
					self.coords_to_index[(i,j)] for i,j in self.unknown_cells
					if self.region_array[i,j]==reg
				],
				self.k
			)
			for reg in range(0,self.n)
		]

		# ... for 2x2 areas, the valid star tallies are 0 or 1
		two_by_two_constraints = [
			([
				self.coords_to_index[(i,j)] for i,j in self.unknown_cells
				if (i==col and j==row) or (i==col+1 and j==row) or (i==col and j==row+1)
				or (i==col+1 and j==row+1)
			],'<=1')
			for row in range(0,self.n-1)
			for col in range(0,self.n-1) # index 2x2 area by coordinates of top-left cell
		]

		# combine all constraints
		# ... for row, column, and region constraints, drop any entries with no unknown
		#      cells - these correspond to the row, column, or region of known stars
		# ... for 2x2 constraints, drop any entries with no or one unknown cells
		#      - these will automatically be satisfied
		all_constraints = (
    		[entry for entry in row_constraints if len(entry[0])>0]
			+ [entry for entry in column_constraints if len(entry[0])>0]
			+ [entry for entry in region_constraints if len(entry[0])>0]
			+ [entry for entry in two_by_two_constraints if len(entry[0])>1]
		)
		# delete duplicate constraints and store in class variable
		self.constraints = [
			(list(inds),tally)
			for inds,tally in set((tuple(inds),tally)
			for inds,tally in all_constraints)
		]
		
	# return number of unknown cells and constraints - this is key information required to
	# build the quantum solver
	def get_constraints(self):
		return len(self.unknown_cells), self.constraints
		
	# print constraints in a table-like format
	def print_constraints(self):
		print("constraints:")
		print(f"{'cells':^10}{str(self.constraints[0][0])[1:-1]:^15}{'must collectively contain':^25}{self.constraints[0][1]:^10}{'star(s)'}")
		for con in self.constraints[1:]:
			print(f"{'...':^10}{str(con[0])[1:-1]:^15}{'...':^25}{con[1]:^10}{'  ...  '}")
		
	def set_solution_stars(self, index_list):
		self.solution_stars = [self.index_to_coords[ind] for ind in index_list]
	
	# display the current state of the puzzle grid, including known stars, ruled-out
	# cells, and possibly indexed markers for unknown cells to be solved for 
	def show_puzzle_grid(self, display_unknowns=False):
		
		plt.imshow(self.region_array) 
		if len(self.forbidden_cells)>0:
			plt.plot(
				np.array(self.forbidden_cells)[:,1], np.array(self.forbidden_cells)[:,0],
				'rx', ms=8
			)
		if len(self.known_stars)>0:
			plt.plot(
				np.array(self.known_stars)[:,1], np.array(self.known_stars)[:,0],
				'y*', ms=30
			)
		if len(self. solution_stars)>0:
			plt.plot(
				np.array(self.solution_stars)[:,1], np.array(self.solution_stars)[:,0],
				'y*', ms=40
			)
		if display_unknowns:
			plt.plot(
				np.array(self.unknown_cells)[:,1], np.array(self.unknown_cells)[:,0],
				'b.', ms=40
			)
			for coords in self.unknown_cells:
				plt.text(
					coords[1] ,coords[0], str(self.coords_to_index[coords]),
					c='w',ha='center',va='center'
				)
		
		#axes = plt.gca()
		#axes.set_xticks(np.arange(-.5,self.n-.5), minor=True)
		#axes.set_yticks(np.arange(-.5,self.n-.5), minor=True)
		#plt.grid(which='minor')
		
		plt.show()