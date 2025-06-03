from qiskit.circuit import QuantumCircuit, QuantumRegister, AncillaRegister
from qiskit.quantum_info import Statevector
from .dict_arithmetic import *
import numpy as np

# Grover Iterations
#
# Description:
# 	Computes and returns the number of Grover iterations required to find a single state
#	amongst a search space of size 2^n.
#
# Inputs:
#	n - the number of qubits that parameterize the search space 
#
# Outputs:
#	iterations - the number of iterations required
#
# Requirements:
#	numpy as np

def grover_iterations(n):
	return int(np.rint(np.pi / (4 * np.arcsin(1 / np.sqrt(2**n))) - 1/2))
	
# ----------------------------------------------------------------------------------------
	
# Grover From Checker
#
# Description:
# 	Constructs and runs a full Grover circuit from a checker circuit that flips qubits
#	corresponding to constraints on the desired solution. Expects that the checker circuit
#	acts on n state qubits, a ancilla qubits, and c constraint qubits in that order, and
#   will leave the state and ancilla qubits unchanged and flip all c constraint qubits for
#	valid solutions. 
#
# Inputs:
#	checker_gate - the checker circuit as a Qiskit gate
#	n_qubits - a tuple containing the number of state qubits, number of ancillary qubits
#		that checker_gate requires, and the number of constraint qubit set by checker_gate
#	checker_gates_dict (optional) - a dict listing the number of gates of each type in the
#		checker circuit
#
# Outputs:
#	prob_dict - a dictionary mapping states to probabilities of measuring that bit string
#	iterations - number of Grover iteration required and run
#	gates_dict - a dict listing the number of each type of gates in the full Grover
#		circuit. Empty if no dict for the checker gate is given.
#
# Requirements:
#	QuantumCircuit, QuantumRegister, AncillaRegister from qiskit.circuit
#	Statevector from qiskit.quantum_info
#	dict_add, dict_scalar_multiply from .dict_arithmetic

def grover_from_checker(checker_gate, n_qubits, checker_gates_dict={}):

	(n,a,c) = n_qubits
	iterations = grover_iterations(n)
	x_reg = QuantumRegister(size=n, name='solution')
	a_reg = AncillaRegister(size=a, name='ancilla')
	c_reg = AncillaRegister(size=c, name='constraint')
	
	# build the marker block: checker, MCZ on c_reg, and then inverse of checker
	marker_qc = QuantumCircuit(x_reg, a_reg, c_reg, name='Marker')
	marker_qc.compose(checker_gate, qubits = x_reg[:] + a_reg[:] + c_reg[:], inplace=True)
	marker_qc.h(c_reg[-1])
	marker_qc.mcx(c_reg[:-1], c_reg[-1])
	marker_qc.h(c_reg[-1]) # H MCX H is equivalent to MCZ
	marker_qc.compose(
		checker_gate.inverse(), qubits = x_reg[:] + a_reg[:] + c_reg[:],
		inplace=True
	)
	
	# build the diffuser block: H X MCZ X H on x_reg
	diffuser_qc = QuantumCircuit(x_reg, name="Diffuser")
	diffuser_qc.h(x_reg)
	diffuser_qc.x(x_reg)
	diffuser_qc.h(x_reg[-1])
	diffuser_qc.mcx(x_reg[:-1], x_reg[-1])
	diffuser_qc.h(x_reg[-1]) # H MCX H is equivalent to MCZ
	diffuser_qc.x(x_reg)
	diffuser_qc.h(x_reg)
	
	# build full circuit
	grover_qc = QuantumCircuit(x_reg, a_reg, c_reg)
	grover_qc.h(x_reg)
	 
	for i in range(iterations):
		grover_qc.compose(marker_qc, inplace=True)
		grover_qc.compose(diffuser_qc, inplace=True)
    	
	# compute top measurement probabilities
	prob_dict = Statevector(grover_qc).probabilities_dict(decimals=6)
	# trim statevector to only show x qubits
	prob_dict = {str(state)[-n:]:p for state, p in prob_dict.items()}
	
	# build dictionary of numbers of each gate type
	if checker_gates_dict=={}:
		gates_dict = {}
	else:
		gates_dict = dict_add(
			dict_scalar_multiply(checker_gates_dict, 2*iterations),
			{'H': n*(2*iterations+1), 'X':2*n*iterations, 'MCZ':2*iterations}
		)
	
	return prob_dict, iterations, gates_dict
	 
# ----------------------------------------------------------------------------------------

# Print Probabilities
#
# Description:
# 	Prints probabilities outputted from grover_from_checker in a table-like format. 
#	Highlights the highest probability entry.
#
# Inputs:
#	prob_dict - a dictionary mapping bit strings to probabilities
#
# Outputs:
#	none
	
def print_probabilities(prob_dict):
	max_prob = max(prob_dict.values())
	print(f"{'':<20}{'probability':<20}")
	print(f"{'solution state':<20}{'of measurement':<20}")
	print(''.join(['-' for i in range(40)]))
	for state, p in prob_dict.items():
		if p == max_prob:
			print(f"{'|'+str(state)+'>':<20}{p:<10}{'<---'}")
		else:
			print(f"{'|'+str(state)+'>':<20}{p}")
