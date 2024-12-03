import itertools
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dsl import *

# suggested first thing: variables and constants should be treated the same, because they are both leaves in syntax trees
# after computing `variables_and_constants`, you should no longer refer to `constants`. express everything in terms of `variables_and_constants`
# `make_variable` is just a helper function for making variables that smartly wraps the variable name in the correct class depending on the type of the variable
def make_variable(variable_name, variable_value):
    """
    Creates a variable representation for the given variable name and value.
    Supports integers, strings, and XMLTag structures.
    """
    if isinstance(variable_value, XMLTag):  # Handle XMLTag structures
        return XMLVariable(variable_name)
    assert False, f"Unsupported input type: {type(variable_value)}"

def bottom_up_generator(global_bound, operators, constants, input_outputs):
    """
    Generates programs in a bottom-up manner to synthesize expressions that satisfy input-output pairs.
    Starts with empty XMLTag structures and incrementally populates them.
    """
    variables = list({make_variable(variable_name, variable_value)
                      for inputs, _ in input_outputs
                      for variable_name, variable_value in inputs.items()})

    variables_and_constants = constants + variables

    expr_by_size_and_type = {}

    # Initialize with empty XMLTag structures
    empty_xml = XMLTag(ConstantString(""), [], None, [])
    if ("xml", 1) not in expr_by_size_and_type:
        expr_by_size_and_type[("xml", 1)] = set()
    expr_by_size_and_type[("xml", 1)].add(empty_xml)

    # Add constants and variables as size 1 expressions
    for expr in variables_and_constants:
        t = expr.return_type
        if (t, 1) not in expr_by_size_and_type:
            expr_by_size_and_type[(t, 1)] = set()
        expr_by_size_and_type[(t, 1)].add(expr)

    observational_equivalence = {}

    for size in range(2, global_bound + 1):
        for operator in operators:
            arity = len(operator.argument_types)
            partitions = integer_partitions(size - 1, arity)

            for partition in partitions:
                argument_combinations = []

                # Collect arguments matching the operator's types and size partitions
                for arg_size, arg_type in zip(partition, operator.argument_types):
                    if (arg_type, arg_size) in expr_by_size_and_type:
                        argument_combinations.append(list(expr_by_size_and_type[(arg_type, arg_size)]))
                    else:
                        break
                else:
                    # Generate combinations of arguments for the operator
                    for args in itertools.product(*argument_combinations):
                        expr = operator(*args)

                        # Evaluate the expression on inputs
                        outputs = tuple(json.dumps(expr.evaluate(input), sort_keys=True) for input, _ in input_outputs)

                        # Add only unique outputs
                        if outputs not in observational_equivalence:
                            observational_equivalence[outputs] = expr
                            t = expr.return_type
                            if (t, size) not in expr_by_size_and_type:
                                expr_by_size_and_type[(t, size)] = set()
                            expr_by_size_and_type[(t, size)].add(expr)
                            yield expr

# def bottom_up_generator(global_bound, operators, constants, input_outputs):
#     """
#     Generates programs in a bottom-up manner to synthesize expressions that satisfy input-output pairs.
#     """
#     variables = list({make_variable(variable_name, variable_value)
#                       for inputs, _ in input_outputs
#                       for variable_name, variable_value in inputs.items()})
    
#     variables_and_constants = constants + variables

#     expr_by_size_and_type = {}

#     # Initialize expressions of size 1 (constants and variables)
#     for expr in variables_and_constants:
#         t = expr.return_type
#         if (t, 1) not in expr_by_size_and_type:
#             expr_by_size_and_type[(t, 1)] = set()
#         expr_by_size_and_type[(t, 1)].add(expr)

#     observational_equivalence = {}

#     for size in range(2, global_bound + 1):
#         for operator in operators:
#             arity = len(operator.argument_types)
#             partitions = integer_partitions(size - 1, arity)

#             for partition in partitions:
#                 argument_combinations = []

#                 # Collect arguments matching the operator's types and size partitions
#                 for arg_size, arg_type in zip(partition, operator.argument_types):
#                     if (arg_type, arg_size) in expr_by_size_and_type:
#                         argument_combinations.append(list(expr_by_size_and_type[(arg_type, arg_size)]))
#                     else:
#                         break
#                 else:
#                     # Generate combinations of arguments for the operator
#                     for args in itertools.product(*argument_combinations):
#                         expr = operator(*args)

#                         # Evaluate the expression on inputs
#                         outputs = tuple(json.dumps(expr.evaluate(input), sort_keys=True) for input, _ in input_outputs)
#                         # outputs = tuple(expr.evaluate(input) for input, _ in input_outputs)
#                         # print(outputs)

#                         if outputs not in observational_equivalence:
#                             observational_equivalence[outputs] = expr
#                             t = expr.return_type
#                             if (t, size) not in expr_by_size_and_type:
#                                 expr_by_size_and_type[(t, size)] = set()
#                             expr_by_size_and_type[(t, size)].add(expr)
#                             # print(expr)
#                             yield expr

def integer_partitions(target_value, number_of_arguments):
    """
    Returns all ways of summing up to `target_value` by adding `number_of_arguments` nonnegative integers
    You may find this useful when implementing `bottom_up_generator`:

    Imagine that you are trying to enumerate all expressions of size 10, and you are considering using an operator with 3 arguments.
    So the total size has to be 10, which includes +1 from this operator, as well as 3 other terms from the 3 arguments, which together have to sum to 10.
    Therefore: 10 = 1 + size_of_first_argument + size_of_second_argument + size_of_third_argument
    Also, every argument has to be of size at least one, because you can't have a syntax tree of size 0
    Therefore: 10 = 1 + (1 + size_of_first_argument_minus_one) + (1 + size_of_second_argument_minus_one) + (1 + size_of_third_argument_minus_one)
    So, by algebra:
         10 - 1 - 3 = size_of_first_argument_minus_one + size_of_second_argument_minus_one + size_of_third_argument_minus_one
    where: size_of_first_argument_minus_one >= 0
           size_of_second_argument_minus_one >= 0
           size_of_third_argument_minus_one >= 0
    Therefore: the set of allowed assignments to {size_of_first_argument_minus_one,size_of_second_argument_minus_one,size_of_third_argument_minus_one} is just the integer partitions of (10 - 1 - 3).
    """

    if target_value < 0:
        return []

    if number_of_arguments == 1:
        return [[target_value]]

    return [ [x1] + x2s
             for x1 in range(target_value + 1)
             for x2s in integer_partitions(target_value - x1, number_of_arguments - 1) ]

def bottom_up_xml(global_bound, operators, constants, input_outputs):
    """
    global_bound: int. Upper bound on expression size.
    operators: List of operator classes for XML.
    constants: List of constant XML expressions.
    input_outputs: List of input-output XML pairs.
    """
    target_outputs = tuple(json.dumps(output.evaluate({}), sort_keys=True) for _, output in input_outputs)
    print(target_outputs)

    # with open("outputs.txt", "w") as file:
    for expr in bottom_up_generator(global_bound, operators, constants, input_outputs):
        outputs = tuple(json.dumps(expr.evaluate(input), sort_keys=True) for input, _ in input_outputs)
        # print(outputs)
        # file.write(f"{outputs}\n")
        if outputs == target_outputs:
            # print(outputs)
            return expr
    return None

input_output_pairs = [
    ({"input1": XMLTag(ConstantString("root"), [(ConstantString("root_attr"), ConstantString("root_value"))], None,
                      [XMLTag(ConstantString("level1"), None, None,
                              [XMLTag(ConstantString("body"), None, ConstantString("body text"), None)])])},
     XMLTag(ConstantString("root"), [(ConstantString("root_attr"), ConstantString("root_value"))], None,
            [XMLTag(ConstantString("level1"), [(ConstantString("body"), ConstantString("body text"))], None, None)]))
]

# input_output_pairs = [
#     ({"input1": XMLTag(ConstantString("root"), [], None,
#                         [XMLTag(ConstantString("body"), None, ConstantString("body text"), None)])}, 
#     XMLTag(ConstantString("root"), [(ConstantString("body"), ConstantString("body text"))], None, [])
#     )
# ]

operators = [ExtractAttribute, SetAttribute, ExtractChild, SetChild, SetTag]
# constants = [ConstantString("root"), ConstantString("body"), ConstantString("body text")] 
constants = [ConstantString("root"), ConstantString("body"), ConstantString("body text"), ConstantString("level1"), ConstantString("root_attr"), ConstantString("root_value")] 

program = bottom_up_xml(15, operators, constants, input_output_pairs)
print("Generated Program:", program)

