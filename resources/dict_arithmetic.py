# Arithmetic on Dictionaries
#
# Description:
# 	This module contains functions that perform basic arithmetic operations on the values
#	of dictionaries. Assumes the values are numbers and that the value of missing entries
#	is 0.

def dict_add(dict1, dict2):
	common = {k:dict1[k]+dict2[k] for k in (set(dict1.keys()) & set(dict2.keys()))}
	return dict1 | dict2 | common # note: values in common replaces those in dict1 / dict2 

def dict_scalar_multiply(dictionary, scalar):
	return {k: scalar*v for k, v in dictionary.items()}