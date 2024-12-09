import json
import os
import sys
import re
import time
import frozendict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dsl import *
from test_cases import *

def flashfill_one_example_xml(environment, target_output, dynamic_programming_table=None):
    """
    Flashfill implementation for synthesizing XML transformations from a single example.
    """
    if dynamic_programming_table is None:
        dynamic_programming_table = {}

    # Use a frozendict for memoization
    frozen_environment = frozendict.frozendict(environment)
    key = (frozen_environment, json.dumps(target_output, sort_keys=True))

    # Check memoization table
    if key in dynamic_programming_table:
        return dynamic_programming_table[key]

    # Initialize version space as an empty union
    version_space = Union([])

    # Step 1: Handle constants
    constant_witnesses = XMLTag.witness((environment, target_output))
    if constant_witnesses:
        version_space = Union.make([version_space] + constant_witnesses)

    # Step 2: Generate unified transformations
    for var_name, var_value in environment.items():
        if isinstance(var_value, XMLTag):
            unified_transformations = generate_xml_transformations(var_value, target_output)
            if unified_transformations:
                version_space = Union.make([version_space] + unified_transformations)

    # Memoize the result
    dynamic_programming_table[key] = version_space
    return version_space

def generate_xml_transformations(input_xml, target_xml):
    """
    Generate a unified XML transformation to convert input_xml to target_xml.
    """
    transformations = []

    # Step 1: Handle tag changes
    tag_expr = None
    input_tag = input_xml.tag.evaluate({}) if input_xml.tag else None
    target_tag = target_xml.get("tag", None)
    if input_tag != target_tag:
        tag_expr = ConstantString(target_tag) if target_tag else None

    # Step 2: Handle attributes
    attribute_exprs = []
    input_attributes = {k.evaluate({}): v.evaluate({}) for k, v in (input_xml.attributes or [])}
    target_attributes = target_xml.get("attributes", {})
    for attr, val in target_attributes.items():
        if attr not in input_attributes or input_attributes[attr] != val:
            attribute_exprs.append(
                SetAttribute(XMLVariable('input1'), ConstantString(attr), ConstantString(val))
            )
    for attr in input_attributes:
        if attr not in target_attributes:
            attribute_exprs.append(RemoveAttribute(XMLVariable('input1'), ConstantString(attr)))

    # Step 3: Handle text changes
    text_expr = None
    input_text = input_xml.text.evaluate({}) if input_xml.text else None
    target_text = target_xml.get("text", None)
    if input_text != target_text:
        text_expr = (
            SetText(XMLVariable('input1'), ConstantString(target_text))
            if target_text
            else RemoveText(XMLVariable('input1'))
        )

    # Step 4: Handle children
    child_expr = None
    input_child = input_xml.child
    target_child = target_xml.get("children", None)
    if target_child:
        child_witness = XMLTag.witness(({"input1": input_child}, target_child))
        if child_witness:
            child_expr = SetChild(
                XMLVariable('input1'),
                ConstantString(target_child["tag"]),
                Union.make(child_witness) if isinstance(child_witness, list) else child_witness,
            )
    elif input_child:
        child_expr = RemoveChild(XMLVariable('input1'))

    # Step 5: Combine into an XMLTag
    unified_transform = XMLTag(tag_expr, attribute_exprs, text_expr, child_expr)
    transformations.append(unified_transform)
    return transformations

def test_flashfill_one_example(verbose=False):
    # collection of input-output specifications
    test_cases = []

    # environment = {"input1": xml_to_dsl(input11)}
    # target_output = xml_to_dsl(output11)
    # test_cases.append(((environment, target_output), 1))

    # test_cases.append((test_case_1[0], 1))
    # test_cases.append((test_case_2[0], 2))
    # test_cases.append((test_case_3[0], 3))
    # test_cases.append((test_case_4[0], 4))
    # test_cases.append((test_case_5[0], 5))
    # test_cases.append((test_case_6[0], 6))
    # test_cases.append((test_case_7[0], 7))
    # test_cases.append((test_case_8[0], 8))
    # test_cases.append((test_case_9[0], 9))

    # test_cases.append((test_case_10[0], 10))
    test_cases.append((test_case_11[0], 11))
    # test_cases.append((test_case_12[0], 12))

    how_many_points = [1] * len(test_cases)
    total_points = 0

    failure = False

    for (input_outputs, case_number), pt in zip(test_cases, how_many_points):
        print("\n" + "=" * 50 + "\n")
        print(f"Executing test case {case_number}...\n")

        inputs, desired_output = input_outputs

        start_time = time.time()
        version_space = flashfill_one_example_xml(inputs, desired_output.evaluate({}))
        
        # Convert input and desired output to prettified XML strings
        input_xml = dsl_to_pretty_string(inputs["input1"])
        desired_output_xml = dsl_to_pretty_string(desired_output)
        
        print(f"Input:\n{input_xml}\n")
        print(f"Desired Output:\n{desired_output_xml}\n")

        if verbose: print(f"Ran Synthesizer in Time: {time.time() - start_time:.4f} seconds")

        version_space_size = version_space.version_space_size()
        print(f"Version Space Size: {version_space_size}\n")
        
        if version_space_size == 0:
            if verbose: 
                print(" !! You constructed an empty version space.\n")
            failure = True
            continue

        tractable = version_space_size < 10000
        
        if tractable:
            if verbose: print("Verifying everything in version space satisfies input-outputs...")
            expressions = version_space.extension()
        else:
            if verbose: print("Verifying minimum cost member of version space satisfies input-outputs...")
            expressions = [version_space.minimum_cost_member_of_extension()]
        
        for expression in expressions:
            environment, target_output = input_outputs
            predicted_output = expression.evaluate(environment)
            if predicted_output != target_output:
                if verbose: 
                    print("You constructed a version space containing the following program:")
                    print(f"\n{prettify_expression(expression)}\n")
                    print(f' !! This predicts the incorrect output: "{predicted_output}"\n')
                failure = True

        if not failure:
            if verbose: 
                print(f"Test case passed!\n")
                prettified_program = prettify_expression(version_space.minimum_cost_member_of_extension())
                print(f"Synthesized program:\n{prettified_program}\n")
        
            total_points += pt

    print("=" * 50)
    print(f"[+] XML Bottom-Up Synthesis: +{total_points}/{sum(how_many_points)} points")

    return total_points

if __name__ == "__main__":
    test_flashfill_one_example(verbose=True)

# def flashfill(input_outputs):
#     """
#     input_outputs: a list of input-output examples (each example is a tuple of environment and the target output)
#     returns: the version space of all solutions to we synthesis problem
    
#     You should call your implementation of `intersect` and also `flashfill_one_example`.
#     """
#     # run synthesizer on the first input-output example
#     version_space = flashfill_one_example(input_outputs[0][0], input_outputs[0][1])

#     # intersect with version spaces for all other input-output examples
#     for environment, target_output in input_outputs[1:]:
#         example_version_space = flashfill_one_example(environment, target_output)
#         version_space = intersect(version_space, example_version_space)

#     return version_space

# def intersect(vs1, vs2, dynamic_programming_table=None):
#     if dynamic_programming_table is None:
#         dynamic_programming_table = {}

#     dynamic_programming_key = (id(vs1), id(vs2))
#     if dynamic_programming_key in dynamic_programming_table:
#         return dynamic_programming_table[dynamic_programming_key]

#     # intersection is empty if either of the version spaces is empty
#     if not vs1 or not vs2:
#         return Union([])

#     result = Union([])

#     # handle union structures
#     if isinstance(vs1, Union) and isinstance(vs2, Union):
#         for member1 in vs1.members:
#             for member2 in vs2.members:
#                 intersected_member = intersect(member1, member2, dynamic_programming_table)
#                 if intersected_member:  
#                     result = Union.make([result, intersected_member])

#     # handle substring structures
#     elif isinstance(vs1, Substring) and isinstance(vs2, Substring):
#         # check substrings refer to same variable and have intersecting start and end indices
#         if vs1.the_string == vs2.the_string:
#             start_expr = intersect(vs1.left, vs2.left, dynamic_programming_table)
#             end_expr = intersect(vs1.right, vs2.right, dynamic_programming_table)

#             if isinstance(start_expr, Union) and not start_expr.members:
#                 result = Union([])
#             elif isinstance(end_expr, Union) and not end_expr.members:
#                 result = Union([])
#             elif start_expr and end_expr:  # if both start and end expressions intersect
#                 result = Substring(vs1.the_string, start_expr, end_expr)

#     # handle concat structures
#     elif isinstance(vs1, Concatenate) and isinstance(vs2, Concatenate):
#         # intersect the left (prefix) and right (suffix) expressions separately
#         left_intersection = intersect(vs1.left, vs2.left, dynamic_programming_table)
#         right_intersection = intersect(vs1.right, vs2.right, dynamic_programming_table)

#         if isinstance(left_intersection, Union) and not left_intersection.members:
#             result = Union([])
#         elif isinstance(right_intersection, Union) and not right_intersection.members:
#             result = Union([])
#         elif left_intersection and right_intersection:  # if both parts intersect
#             result = Concatenate(left_intersection, right_intersection)

#     # handle constantstring structures
#     elif isinstance(vs1, ConstantString) and isinstance(vs2, ConstantString):
#         if vs1.content == vs2.content:  
#             result = vs1 

#     # handle for number structures (for indices in substring)
#     elif isinstance(vs1, Number) and isinstance(vs2, Number):
#         if vs1.n == vs2.n:  
#             result = vs1  

#     # handle stringvariable structures
#     elif isinstance(vs1, StringVariable) and isinstance(vs2, StringVariable):
#         if vs1.name == vs2.name:  
#             result = vs1  

#     # memoize result
#     dynamic_programming_table[dynamic_programming_key] = result
#     return result

# def test_flashfill(verbose=False):
#     # collection of input-output specifications
#     test_cases = []
#     test_cases.append([ ({"input1": "test"}, "t") ])
#     test_cases.append([ ({"input1": "121"}, "1") ])
#     test_cases.append([ ({"input1": "test"}, "t"),
#                         ({"input1": "121"}, "1") ])
#     test_cases.append([ ({"input1": "xyz"}, "xyz") ])
#     test_cases.append([ ({"input1": "xyz"}, "Dr xyz") ])
#     test_cases.append([ ({"input1": "abcdefgh"}, "Dr abcdefgh") ])
#     test_cases.append([ ({"input1": "xyz"}, "Dr xyz"),
#                         ({"input1": "abcdefgh"}, "Dr abcdefgh")])
#     test_cases.append([ ({"input1": "y"}, "abc")])
#     test_cases.append([ ({"input1": "z"}, "abcdefgh")])
#     test_cases.append([ ({"input1": "y"}, "abcdefgh"),
#                         ({"input1": "z"}, "abcdefgh") ])
#     test_cases.append([ ({"input1": "June",    "input2": "14", "input3": "1997"}, "1997, June 14")])
#     test_cases.append([ ({"input1": "June",    "input2": "14", "input3": "1997"}, "1997, June 14"),
#                         ({"input1": "October", "input2": "2",  "input3": "2012"}, "2012, October 2")])
#     test_cases.append([ ({"input1": "555-360-9792"}, "(555) 360-9792"),
#                         ({"input1": "425-923-7777"}, "(425) 923-7777") ])

#     failure = False

#     for input_outputs in test_cases:

#         if verbose: print()

#         start_time = time.time()
#         version_space = flashfill(input_outputs)
        
#         if verbose: print("\tran synthesizer in time", time.time() - start_time, "seconds")

#         version_space_size = version_space.version_space_size()
#         if verbose: print("\tversion space contains",version_space_size,"programs")
        
#         if version_space_size == 0:
#             if verbose: 
#                 print("Based on the input-outputs:")
#                 for training_input, training_output in input_outputs:
#                     print("\t",training_input,f" --> '{training_output}'")
#                 print(" [-] You constructed an empty version space.")
#                 print()
#             failure = True
#             continue

#         tractable = version_space_size < 10000
        
#         if tractable:
#             if verbose: print("\tverifying everything in version space satisfies input-outputs.")
#             expressions = version_space.extension()
#         else:
#             if verbose: print("\tverifying minimum cost member of version space satisfies input-outputs.")
#             expressions = [version_space.minimum_cost_member_of_extension()]
            
#         for expression in expressions:
#             for environment, target_output in input_outputs:
#                 predicted_output = expression.evaluate(environment)
#                 if predicted_output != target_output:
#                     if verbose: 
#                         print("Based on the input-outputs:")
#                         for training_input, training_output in input_outputs:
#                             print("\t",training_input,f" --> '{training_output}'")
#                         print("You constructed a version space containing the following program:")
#                         print("\t",expression)
#                         print("Which, when pretty printed, looks like:")
#                         print("\t",expression.pretty_print())
#                         print(f' [-] This predicts the incorrect output: "{predicted_output}"')
#                         print()
#                     failure = True

#         if not failure and verbose:
#             print("\t[+] passed synthesis test case:")
#             for training_input, training_output in input_outputs:
#                 print("\t\t",training_input,f" --> '{training_output}'")
#             print("\t\twith the program:")
#             to_print = version_space.minimum_cost_member_of_extension().pretty_print()
#             print("\t\t", to_print)
#             print("\t\tequivalently:\n\t\t",
#                 re.sub("Substring\\(input(.), 0, -1\\)", "input\\1", to_print))
    
#     if failure:
#         total_points = 0
#     else:
#         total_points = 10
#     print(f" [+] 4.4, flashfill, +{total_points}/10 points")
#     return total_points
    
# if __name__ == "__main__":
#     test_flashfill(verbose=True)
    
# def test_4_6(verbose=False):
#     # collection of input-output specifications
#     test_cases = []
#     test_cases.append([ ({"input1": "June",    "input2": "14", "input3": "1997"}, "1997, June 14")])
#     test_cases.append([ ({"input1": "June",    "input2": "14", "input3": "1997"}, "1997, June 14"),
#                         ({"input1": "October", "input2": "2",  "input3": "2012"}, "2012, October 2")])

#     target_programs = ['Substring(input3, 0, -1) + ", " + Substring(input1, 0, -1) + " " + Substring(input2, 0, -1)',
#                        'Substring(input3, 0, -1) + ", " + Substring(input1, 0, -1) + " " + Substring(input2, 0, -1)']

#     failure = False

#     for input_outputs, target_program in zip(test_cases, target_programs):

#         if verbose: print()

#         start_time = time.time()
#         version_space = flashfill(input_outputs)
        
#         if verbose: print("\tran synthesizer in time", time.time() - start_time, "seconds")

#         version_space_size = version_space.version_space_size()
#         if verbose: print("\tversion space contains",version_space_size,"programs")
        
#         if version_space_size == 0:
#             if verbose:
#                 print("Based on the input-outputs:")
#                 for training_input, training_output in input_outputs:
#                     print("\t",training_input,f" --> '{training_output}'")
#                 print(" [-] You constructed an empty version space.")
#             print()
#             failure = True
#             continue

#         expression = version_space.minimum_cost_member_of_extension()
#         if expression.pretty_print() != target_program:
#             if verbose:
#                 print("Based on the input-outputs:")
#                 for training_input, training_output in input_outputs:
#                     print("\t",training_input,f" --> '{training_output}'")
#                 print("You constructed a version space containing the following program:")
#                 print("\t",expression)
#                 print("Which, when pretty printed, looks like:")
#                 print("\t",expression.pretty_print())
#                 print(f' [-] This is not the correct program: "{target_program}"')
#                 print()
#             failure = True
    
#     if failure:
#         total_points = 0
#     else:
#         total_points = 5
    
#     print(f" [+] 4.6, cost definitions, +{total_points}/5 points")
#     return total_points

# if __name__ == "__main__":
#     test_4_6(verbose=True)