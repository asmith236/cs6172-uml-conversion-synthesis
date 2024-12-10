from dsl import *

# Test Case 1

input1 = '<packagedElement visibility="public"></packagedElement>'

output1 = '<packagedElement></packagedElement>'

test_case_1 = [({"input": xml_to_dsl(input1)}, xml_to_dsl(output1))]

# Test Case 2

input2 = '<packagedElement></packagedElement>'

output2 = '<packagedElement visibility="public"></packagedElement>'

test_case_2 = [({"input": xml_to_dsl(input2)}, xml_to_dsl(output2))]

# Test Case 3

input3 = '''
        <ownedComment>
            <body>This is body d4143d60.</body>
        </ownedComment>
        '''

output3 = '<ownedComment body="This is body d4143d60." />'

test_case_3 = [({"input": xml_to_dsl(input3)}, xml_to_dsl(output3))]

# Test Case 4

input4 = '<ownedComment body="This is body d4143d60." />'

output4 = '''
        <ownedComment>
            <body>This is body d4143d60.</body>
        </ownedComment>
        '''

test_case_4 = [({"input": xml_to_dsl(input4)}, xml_to_dsl(output4))]

# Test Case 5

input5 = '''
        <packagedElement id="_YuRb">
            <ownedComment>
                <body>This is body d4143d60.</body>
            </ownedComment>
        </packagedElement>
        '''

output5 = '''
        <packagedElement id="_YuRb" >
            <ownedComment body="This is body d4143d60." />
        </packagedElement>
'''

test_case_5 = [({"input": xml_to_dsl(input5)}, xml_to_dsl(output5))]

# Test Case 6

input6 = '<packagedElement name="TempClass1" visibility="public"></packagedElement>'

output6 = '<packagedElement name="TempClass1"></packagedElement>'

test_case_6 = [({"input": xml_to_dsl(input6)}, xml_to_dsl(output6))]

# Test Case 7

input7 = '<packagedElement name="TempClass1"></packagedElement>'

output7 = '<packagedElement name="TempClass1" visibility="public"></packagedElement>'

test_case_7 = [({"input": xml_to_dsl(input7)}, xml_to_dsl(output7))]

# Test Case 8

input8 = '<packagedElement type="uml:Class" id="_383A" name="TempClass1"></packagedElement>'

output8 = '<packagedElement type="uml:Class" id="_383A" name="TempClass1" visibility="public"></packagedElement>'

test_case_8 = [({"input": xml_to_dsl(input8)}, xml_to_dsl(output8))]

# Test Case 9

input9 = '''
        <ownedComment annotatedElement="_383A">
            <body>This is body d4143d60.</body>
        </ownedComment>
        '''

output9 = '<ownedComment annotatedElement="_383A" body="This is body d4143d60." />'

test_case_9 = [({"input": xml_to_dsl(input9)}, xml_to_dsl(output9))]

# Test Case 10

input10 = '''
        <packagedElement type="uml:Class" id="_383A">
            <ownedComment annotatedElement="_383A">
                <body>This is body d4143d60.</body>
            </ownedComment>
        </packagedElement>
        '''

output10 = '''
        <packagedElement type="uml:Class" id="_383A" >
            <ownedComment annotatedElement="_383A" body="This is body d4143d60." />
        </packagedElement>
        '''

test_case_10 = [({"input": xml_to_dsl(input10)}, xml_to_dsl(output10))]

# Test Case 11

input11 = '<ownedComment id="_YuRb" body="This is body d4143d60." annotatedElement="_383A" />'

output11 = '''
        <ownedComment id="_YuRb" annotatedElement="_383A">
            <body>This is body d4143d60.</body>
        </ownedComment>
        '''

test_case_11 = [({"input": xml_to_dsl(input11)}, xml_to_dsl(output11))]

# Test Case 12

input12 = '''
        <packagedElement type="uml:Class" id="_383A" name="TempClass1">
            <ownedComment id="_YuRb" annotatedElement="_383A">
                <body>This is body d4143d60.</body>
            </ownedComment>
        </packagedElement>
        '''

output12 = '''
        <packagedElement type="uml:Class" id="_383A" name="TempClass1" visibility="public">
            <ownedComment id="_YuRb" body="This is body d4143d60." annotatedElement="_383A" />
        </packagedElement>
        '''

test_case_12 = [({"input": xml_to_dsl(input12)}, xml_to_dsl(output12))]

# input13 = '''
#         <packagedElement type="uml:Class" id="_383A" name="TempClass1">
#             <eAnnotations id="_0-3eZeRbEduVs91jndUPVw" source="http://www.eclipse.org/uml2/2.0.0/UML">
#                 <details id="_0-3eZuRbEduVs91jndUPVw" key="entity" />
#             </eAnnotations>
#             <ownedComment id="_YuRb" annotatedElement="_383A">
#                 <body>This is body d4143d60.</body>
#             </ownedComment>
#             <ownedAttribute id="_383AC7D3023A40C0CEBF005E" name="TempAttrib1" visibility="private" />
#             <ownedAttribute id="_383AC7D3023A40C0CE9C0271" name="TempAttrib2"
#                 visibility="public" type="_383AC7D3023A40C0CAFC0106" isUnique="false" aggregation="shared"
#                 association="_383AC7D3023A40C0CE9B034C" />
#         </packagedElement>
#         '''

# output13 = '''
#         <packagedElement type="uml:Class" id="_383A" name="TempClass1" visibility="public">
#             <ownedComment id="_YuRb" body="This is body d4143d60." annotatedElement="_383A" />
#             <ownedAttribute id="_383AC7D3023A40C0CEBF005E" visibility="private" name="TempAttrib1" />
#             <ownedAttribute id="_383AC7D3023A40C0CE9C0271" visibility="public"
#                 name="TempAttrib2" isUnique="false" aggregation="shared"
#                 type="_383AC7D3023A40C0CAFC0106" association="_383AC7D3023A40C0CE9B034C" />
#         </packagedElement>
#         '''

# test_case_13 = [({"input": xml_to_dsl(input13)}, xml_to_dsl(output13))]
