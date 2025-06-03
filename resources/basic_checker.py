from qiskit.circuit import QuantumCircuit, QuantumRegister, AncillaRegister
import numpy as np
from .tally import *
from .dict_arithmetic import *

# Basic Checker
#
# Description:
# 	Constructs a 'checker' circuit that check solution qubits against the given
#	constraints. To be used in the marker blocks of a Grover circuit. 
#
# Inputs:
#	n - the number of solution qubits
#	constraints - a list of constraints on the primary qubits of the form produced by the
#		Star_Battle class (see ./star_battle.py).
#
# Outputs:
#	gate - the checker circuit as a qiskit gate
#	(n, a, c) - the number of 'input' (solution) qubits, the number of ancilla required of
#		the circuit, and the number of 'output' (constraint) qubits to be set by the
#		circuit
#	circuit - the circuit with barriers for display
#	gates_dict - a dictionary mapping gate types to the number of that type of gate used
#		in the circuit
#
# Requirements:
#	QuantumCircuit, QuantumRegister, AncillaRegister from qiskit.circuit
#	RemoveBarriers from qiskit.transpiler.passes
#	get_tally_controlled_X_gate from .tally
#	dict_add from .dict_arithmetic

def basic_checker(n, constraints):
	
	c = len(constraints)
	a = max([len(inds) for inds,tally in constraints]) + 1
	
	x_reg = QuantumRegister(size=n)
	a_reg = AncillaRegister(size=a)
	c_reg = QuantumRegister(size=c)
	
	circuit = QuantumCircuit(x_reg, a_reg, c_reg, name='Check Constraints')
	gates_dict = {}
	
	for k, (inds, tally) in enumerate(constraints): # loop over contraints
		if k != 0:
			circuit.barrier()
		# ... and add a Tally-Controlled X circuit for each one
		_, _, tallyCX_circuit, tally_dict = get_tally_controlled_X_gate(len(inds), tally)
		circuit.compose(
			RemoveBarriers()(tallyCX_circuit),
			qubits = x_reg[inds] + a_reg[0:len(inds)+1] + [c_reg[k]], inplace=True
		)
		gates_dict = dict_add(gates_dict, tally_dict)
		
	gate = RemoveBarriers()(circuit).to_gate()
	
	
	return gate, (n, a, c), circuit, gates_dict	
	
# ----------------------------------------------------------------------------------------	

# Print Circuit Width
#
# Description:
# 	Prints the width of a checker circuit with table-like formatting.
#
# Inputs:
#	num_qubits - tuple containing number of qubits of each type
#
# Outputs:
#	none
	
def print_circuit_width(num_qubits):
	(n,a,c) = num_qubits
	print(f"{'number of solution qubits required: ':>40}{n:>5}")
	print(f"{'number of ancilla qubits required: ':>40}{a:>5}")
	print(f"{'number of constraint qubits required: ':>40}{c:>5}")
	print(''.join(['-' for i in range(45)]))
	print(f"{'total number of qubits required: ':>40}{n+c+a:>5}")
	
# ----------------------------------------------------------------------------------------	

# Print Number of Gates
#
# Description:
# 	Prints the number and type of gates in a circuit with table-like formatting.
#
# Inputs:
#	gates_dict - a dictionary mapping gate types to the number of that type of gate used
#		in the circuit
#
# Outputs:
#	none

def print_number_of_gates(gates_dict):
	for gate, n in gates_dict.items():
		print(f"{'number of '+gate+' gates required: ':>40}{n:>5}")
	print(''.join(['-' for i in range(45)]))
	print(f"{'total number of gates required: ':>40}{sum(gates_dict.values()):>5}")