
import inspect
import itertools
import json
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dsl import *
from test_cases import *

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

def bottom_up_generator(global_bound, operators, input_outputs):
    """
    Generates programs in a bottom-up manner using extraction operators.
    """
    # Extract variables from input
    variables = list({make_variable(var_name, var_value)
                      for inputs, _ in input_outputs
                      for var_name, var_value in inputs.items()})
    
    # Extract unique attribute keys and tags from input
    attribute_keys = set()
    tags = set()
    for inputs, _ in input_outputs:
        for value in inputs.values():
            if isinstance(value, XMLTag):
                # Extract attribute keys
                attribute_keys.update(attr_key.content for attr_key, _ in value.attributes)
                # Extract tags
                if value.tag:
                    tags.add(value.tag.content)
    
    # Extract unique attribute keys, values, and tags from output
    for _, output in input_outputs:
        if isinstance(output, XMLTag):
            # Extract attribute keys and values
            attribute_keys.update(attr_key.content for attr_key, _ in output.attributes)
            attribute_keys.update(attr_value.content for _, attr_value in output.attributes)
            # Extract tags
            if output.tag:
                tags.add(output.tag.content)
    
    # Create terminals for extracted keys, values, and tags
    attribute_terminals = [ConstantString(key_or_value) for key_or_value in attribute_keys]
    tag_terminals = [ConstantString(tag) for tag in tags]

    # Initialize expressions by size and type
    expr_by_size_and_type = {}

    # Add empty XMLTag structures
    empty_xml = XMLTag(None, [], None, None)
    if ("xml", 1) not in expr_by_size_and_type:
        expr_by_size_and_type[("xml", 1)] = set()
    expr_by_size_and_type[("xml", 1)].add(empty_xml)

    # Initialize with variables and terminals
    terminals = variables + attribute_terminals + tag_terminals
    for expr in terminals:
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
                        outputs = tuple(json.dumps(expr.evaluate(input), default=lambda x: x.content if isinstance(x, ConstantString) else x, sort_keys=True) for input, _ in input_outputs)
                        # Add only unique outputs
                        if outputs not in observational_equivalence:
                            observational_equivalence[outputs] = expr
                            t = expr.return_type
                            if (t, size) not in expr_by_size_and_type:
                                expr_by_size_and_type[(t, size)] = set()
                            expr_by_size_and_type[(t, size)].add(expr)
                            yield expr

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

def bottom_up_xml(global_bound, operators, input_outputs):
    """
    global_bound: int. Upper bound on expression size.
    operators: List of operator classes for XML.
    constants: List of constant XML expressions.
    input_outputs: List of input-output XML pairs.
    """
    target_outputs = tuple(json.dumps(output.evaluate({}), sort_keys=True) for _, output in input_outputs)
    # print(target_outputs)

    expression_count = 0  

    # with open("outputs.txt", "w") as o_file: # for debugging
        # with open("programs.txt", "w") as p_file:
    for expr in bottom_up_generator(global_bound, operators, input_outputs):
        # p_file.write(f"{expr}\n")
        expression_count += 1 
        outputs = tuple(json.dumps(expr.evaluate(input), sort_keys=True) for input, _ in input_outputs)
        # o_file.write(f"{outputs}\n")
        if outputs == target_outputs:
            return expr, expression_count
    return None, expression_count

def test_bottom_up_xml(verbose=False):
    operators = [
        ExtractTag, ExtractAttribute, ExtractText, ExtractChild, SetTag, SetAttribute, SetText, SetChild
    ]
    
    test_cases = []

    test_cases.append((test_case_1, 1))
    test_cases.append((test_case_2, 2))
    test_cases.append((test_case_3, 3))
    test_cases.append((test_case_4, 4))
    test_cases.append((test_case_5, 5))
    test_cases.append((test_case_6, 6))
    test_cases.append((test_case_7, 7))
    test_cases.append((test_case_8, 8))
    test_cases.append((test_case_9, 9))
    test_cases.append((test_case_10, 10))
    test_cases.append((test_case_11, 11))
    test_cases.append((test_case_12, 12))
    # test_cases.append((test_case_13, 13))
    
    # Points for each test case
    how_many_points = [1] * len(test_cases)

    # Optimal sizes for each test case
    # optimal_sizes = [20, 20, 20, 20, 20, 20, 20, 30]
    optimal_sizes = [20] * len(test_cases)

    total_points = 0
    
    def prettify_expression(expression, indent=0):
        """
        Prettifies a nested DSL expression for readable output.
        """
        spacing = " " * indent
        if isinstance(expression, Expression):
            args = expression.arguments()
            if args:
                pretty_args = ",\n".join(prettify_expression(arg, indent + 4) for arg in args)
                return f"{spacing}{expression.__class__.__name__}(\n{pretty_args}\n{spacing})"
            elif hasattr(expression, 'content'):  # Handles ConstantString and similar classes
                return f"{spacing}{expression.__class__.__name__}({repr(expression.content)})"
            elif hasattr(expression, 'name'):  # Handles XMLVariable and similar classes
                return f"{spacing}{expression.__class__.__name__}({repr(expression.name)})"
            else:
                return f"{spacing}{expression.__class__.__name__}()"
        elif isinstance(expression, str):
            return f"{spacing}\"{expression}\""
        else:
            return f"{spacing}{str(expression)}"

    def xml_to_pretty_string(xml, indent=0):
        """
        Converts an XMLTag to a prettified XML-like string for readable output with proper indentation.
        """
        spacing = " " * indent
        if xml is None:
            return f"{spacing}<none/>"

        attributes = " ".join([f'{key.content}="{value.content}"' for key, value in (xml.attributes or [])])
        tag = xml.tag.content if xml.tag else "none"
        text = xml.text.content if xml.text else ""
        child = xml_to_pretty_string(xml.child, indent + 4) if xml.child else ""
        
        # Format the attributes part
        opening_tag = f"<{tag} {attributes}".strip()
        
        # If there's no child or text, close the tag on the same line
        if not text and not child:
            return f"{spacing}{opening_tag}/>"
        
        # If there's only text, keep everything on the same line
        if text and not child:
            return f"{spacing}{opening_tag}>{text}</{tag}>"
        
        # If there's a child, properly indent it
        return (
            f"{spacing}{opening_tag}>\n"
            f"{child}\n"
            f"{spacing}</{tag}>"
        )

    for (test_case, case_number), optimal_size, pt in zip(test_cases, optimal_sizes, how_many_points):
        print("\n" + "=" * 50 + "\n")
        print(f"Executing test case {case_number} with size bound {optimal_size}...\n")
        inputs, desired_output = test_case[0]

        # Convert input and desired output to prettified XML strings
        input_xml = xml_to_pretty_string(inputs["input1"])
        desired_output_xml = xml_to_pretty_string(desired_output)
        
        print(f"Input:\n{input_xml}\n")
        print(f"Desired Output:\n{desired_output_xml}\n")

        # Run the bottom-up generator
        start_time = time.time()
        program, expression_count = bottom_up_xml(optimal_size, operators, test_case)
        if program is None:
            print(f"Failed to synthesize a program.")
            continue

        # Evaluate the program and validate it
        fails_test_case = False
        for inputs, expected_output in test_case:
            output = program.evaluate(inputs)
            if output != expected_output.evaluate({}):
                print(f"Program failed for input {inputs}.\nExpected:\n{xml_to_pretty_string(expected_output)}\nGot:\n{xml_to_pretty_string(output)}")
                fails_test_case = True
            else:
                print(f"Test case passed!")

        if fails_test_case:
            continue

        # Prettify and display the synthesized program
        print(f"Number of programs generated: {expression_count}\n")
        print(f"Synthesized program:\n{prettify_expression(program)}\n")
        print(f"Execution time: {time.time() - start_time:.4f} seconds")

        total_points += pt

    print("=" * 50)
    print(f"[+] XML Bottom-Up Synthesis: +{total_points}/{sum(how_many_points)} points")
    return total_points

if __name__ == "__main__":
    test_bottom_up_xml(verbose=True)