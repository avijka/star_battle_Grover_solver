# A Quantum Solver for Star Battle Puzzles Based on Grover's Algorithm
This repository implements in Qiskit a quantum computer solver for [star battle puzzles](https://www.puzzle-star-battle.com/) using Grover's algorithm. For an introduction to star battle puzzles, complete details of the approach to building the solver, complexity analysis, and a discussion of possible future innovations, see the [iPython notebook](https://github.com/avijka/star_battle_Grover_solver/blob/main/01_star_battle_Grover_solver.ipynb) in this repository. For a usage example, see below.

### Usage Example
As an example, suppose you have partially solved a star battle puzzle, having found a couple of the stars:

![puzzle2_partial_solve](https://github.com/user-attachments/assets/d94fe92a-25eb-4355-8f23-758bafbe77f6)

But suppose you are now stuck, and want your quantum computer to solve the rest. In that case, first, load up the packages from this repository.
```python
from resources.star_battle import *
from resources.basic_checker import *
from resources.grover import *
```
Then initialize the Star Battle class with details from the puzzle. Pass in information about the regions with a numpy array. The array should identify membership of each cell to a region using a unique number for each region (between $0$ and $n-1$ for $n\times n$ puzzles). Also set the coordinates of the stars you know about, here $(4,2)$ and $(2,3)$.
```python
region_array = np.array([[0,0,0,0,1],[0,0,0,1,1],[2,2,0,3,3],[2,2,2,3,4],[2,2,4,4,4]])
sb = Star_Battle(region_array.shape[0], region_array)
sb.set_known_stars([(4,2),(2,3)])
sb2.show_puzzle_grid(display_unknowns=True)
```
The last line above prints the state of the puzzle, showing which cells are known to be forbidden from classical preprocessing. It also labels unknown cells with an index. Each of those cells are to be associated with a qubit.

![puzzle2_partial_solve_code_output](https://github.com/user-attachments/assets/416bbe3c-67e2-4c9b-93b2-9005d3cbde97)


Now extract the neccessary information from the classical pre-processing stage using `Star_Battle.get_constraints()` and pass the resulting constraints on the unknown puzzle cells to `basic_check`. This generates a quantum circuit that checks if those constraints are satisfied.

```python
# generate the checker circuit from constraints
num_solution_qubits, constraints = sb.get_constraints()
check_constraints_gate, num_qubits, _, checker_gates_dict = basic_checker(num_solution_qubits, constraints)
```
Finally, pass the checker circuit into `grover_from_checker`, which automatically builds the full Grover circuit with the right number of iterations, runs that circuit, and outputs measurement probabilities.  

```python
# generate and run the full Grover circuit
probs, iterations, gates_dict = grover_from_checker(check_constraints_gate, num_qubits, checker_gates_dict)
print_probabilities(probs)
```
The last line above prints out measurement probabilites for the qubits associated with unknown cells. In this example, it identifies that $\left|x_5 x_4 x_3 x_2 x_1 x_0 \right> = \left|110100\right>$ (which corresponds to stars in cells $2$, $4$, and $5$) will be measured with $99.7$ percent probability. Now, one can visualize the solution in the grid:

```python
# set stars identified from Grover's algorithm
sb.set_solution_stars([2,4,5])
sb.show_puzzle_grid(display_unknowns=True)
```

![puzzle2_full_solve_code_output](https://github.com/user-attachments/assets/5ac2ceda-a5ce-48e1-b807-29edc9efa5fe)

