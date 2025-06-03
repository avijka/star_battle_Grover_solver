from qiskit.circuit import QuantumCircuit, QuantumRegister, AncillaRegister
from qiskit.transpiler.passes import RemoveBarriers

# Tally Gate
#
# Description:
# 	Generates a qiskit circuit that operates on n 'input' qubits and n+1 'output' qubits
#	with the following classical interpretation: assuming the ancillary bits are each
#	initially 0,the kth output bit is set to 1 (and all others set to 0) if exactly k of
#	the input qubits are 1. Uses one X gate and n*(n+1) CCX gates.
#
# Inputs:
#	n - the number of qubits to be tallied
#
# Outputs:
#	gate - the circuit as a qiskit gate
#	(n, n+1) - the number of gate inputs (and outputs) of each type
#	circuit - the circuit with barriers for display
#	gates_dict - a dictionary mapping gate types to the number of that type of gate used
#		in the circuit
#
# Requirements:
#	QuantumCircuit, QuantumRegister, AncillaRegister from qiskit.circuit
#	RemoveBarriers from qiskit.transpiler.passes

def get_tally_gate(n):
	input_reg = QuantumRegister(size=n, name='x')
	output_reg = QuantumRegister(size=n+1, name='y')
	circuit = QuantumCircuit(input_reg, output_reg, name='Tally('+str(n)+')')
	
	# set y0=1: the flag starts at the 0th bit of y, which indicates that the starting
	# tally is 0
	circuit.x(output_reg[0])
	
	# tally by looping over input bits
	for iX in range(0,n):
		circuit.barrier()
		# propogate the flag if the input bit is 1 - start from the highest possible
		# position of the flag (iX+1) and work back
		for iY in range(iX+1,0,-1):
			# if the iXth bit of x is 1 and the flag is at the (iY-1)th bit of Y, move it
			# to the iYth bit
			circuit.ccx(input_reg[iX], output_reg[iY-1], output_reg[iY])
			circuit.ccx(input_reg[iX], output_reg[iY], output_reg[iY-1])
	
	gate = RemoveBarriers()(circuit).to_gate()
	
	return gate, (n, n+1), circuit, {'X':1, 'CCX': n*(n+1)}
	
# ----------------------------------------------------------------------------------------
	
# Tally-Controlled X Gate
#
# Description:
# 	Generates a qiskit circuit that operates on n input qubits, n+1 ancillary qubits, and
#	one controlled qubit, which applies X to the controlled qubit if the number of 1's
#	amongst the input qubits matches the given tally. Uses one tally gate, one inverse
#	tally gate, and either one CX gate if the given tally is an integer or five X gates 
#	and one CCX gate if the valid tally is '<=1'. In total: two X gates, one CX gate and
#	2*n*(n+1) CCX gates or seven X gates and 2*n*(n+1)+1 CCX gates, respectively.
#
# Inputs:
#	n - the number of qubits to be tallied
#	valid_tally - the valid tally; a single integer or the string '<=1'
#
# Outputs:
#	gate - the circuit as a qiskit gate
#	(n, n+1, 1) - the number of gate inputs (and outputs) of each type
#	circuit - the circuit with barriers for display
#	gates_dict - a dictionary mapping gate types to the number of that type of gate used
#		in the circuit
#
# Requirements:
#	QuantumCircuit, QuantumRegister, AncillaRegister from qiskit.circuit
#	RemoveBarriers from qiskit.transpiler.passes
#	get_tally_gate

def get_tally_controlled_X_gate(n, valid_tally):
	quantum_reg = QuantumRegister(size=n, name='x')
	ancilla_reg = AncillaRegister(size=n+1, name='a')
	controlled_qubit = QuantumRegister(size=1, name='y')
	circuit = QuantumCircuit(
		quantum_reg, ancilla_reg, controlled_qubit,
		name='TallyCX('+str(n)+', '+str(valid_tally)+')'
	)
	
	tally_gate,_,_,_ = get_tally_gate(n)
	
	# compute the tally
	circuit.compose(tally_gate, qubits = quantum_reg[:] + ancilla_reg[:], inplace=True)
	circuit.barrier()
	
	if valid_tally == '<=1':
		# if given '<=1', tallies of either 0 or 1 are valid, so
		# ... produce an OR gate by 1) flipping the ancilla corresponding to those tallies
		circuit.x(ancilla_reg[0]) 
		circuit.x(ancilla_reg[1])
		# ... and the qubit to be controlled,
		circuit.x(controlled_qubit)
		# ... 2) applying CCX
		circuit.ccx(ancilla_reg[0], ancilla_reg[1], controlled_qubit)
		# ... and 3) un-flipping the ancilla
		circuit.x(ancilla_reg[0])
		circuit.x(ancilla_reg[1])
		
		gates_dict = {'X':7, 'CCX': 2*n*(n+1)+1}
	else:
		# else apply X controlled by the ancilla corresponding to the desired tally
		circuit.cx(ancilla_reg[valid_tally], controlled_qubit)
		
		gates_dict = {'X':2, 'CX': 1, 'CCX': 2*n*(n+1)}
		
	circuit.barrier()
    
	# un-compute the tally
	circuit.compose(
		tally_gate.inverse(), qubits = quantum_reg[:] + ancilla_reg[:], 
		inplace=True
	)
	
	gate = RemoveBarriers()(circuit).to_gate()
	
	return gate, (n, n+1, 1), circuit, gates_dict