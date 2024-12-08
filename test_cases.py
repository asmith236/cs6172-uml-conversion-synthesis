from dsl import *

input1 = '<packagedElement visibility="public"></packagedElement>'

output1 = '<packagedElement></packagedElement>'

test_case_1 = [({"input1": xml_to_dsl(input1)}, xml_to_dsl(output1))]

# test_case_1 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("visibility"), ConstantString("public"))], None, None)}, 
#     XMLTag(ConstantString("packagedElement"), [], None, None)
#     )
# ]

input2 = '<packagedElement></packagedElement>'

output2 = '<packagedElement visibility="public"></packagedElement>'

test_case_2 = [({"input1": xml_to_dsl(input2)}, xml_to_dsl(output2))]

# test_case_2 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [], None, None)}, 
#     XMLTag(ConstantString("packagedElement"), [(ConstantString("visibility"), ConstantString("public"))], None, None)
#     )
# ]

input3 = '''
        <ownedComment>
            <body>This is body d4143d60.</body>
        </ownedComment>
        '''

output3 = '<ownedComment body="This is body d4143d60." />'

test_case_3 = [({"input1": xml_to_dsl(input3)}, xml_to_dsl(output3))]

# test_case_3 = [
#     ({"input1": XMLTag(ConstantString("ownedComment"), [], None,
#                         XMLTag(ConstantString("body"), None, ConstantString("This is body d4143d60."), None))}, 
#     XMLTag(ConstantString("ownedComment"), [(ConstantString("body"), ConstantString("This is body d4143d60."))], None, None)
#     )
# ]

input4 = '<ownedComment body="This is body d4143d60." />'

output4 = '''
        <ownedComment>
            <body>This is body d4143d60.</body>
        </ownedComment>
        '''

test_case_4 = [({"input1": xml_to_dsl(input4)}, xml_to_dsl(output4))]

# test_case_4 = [
#     ({"input1": XMLTag(ConstantString("ownedComment"), [(ConstantString("body"), ConstantString("This is body d4143d60."))], None, None)}, 
#     XMLTag(ConstantString("ownedComment"), [], None,
#                         XMLTag(ConstantString("body"), None, ConstantString("This is body d4143d60."), None))
#                         )
# ]

input5 = '''
        <packagedElement id="_0-3eYuRbEduVs91jndUPVw">
            <ownedComment>
                <body>This is body d4143d60.</body>
            </ownedComment>
        </packagedElement>
        '''

output5 = '''
        <packagedElement id="_0-3eYuRbEduVs91jndUPVw" >
            <ownedComment body="This is body d4143d60." />
        </packagedElement>
'''

test_case_5 = [({"input1": xml_to_dsl(input5)}, xml_to_dsl(output5))]

# test_case_5 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw"))], None,
#                       XMLTag(ConstantString("ownedComment"), None, None,
#                               XMLTag(ConstantString("body"), None, ConstantString("This is body d4143d60."), None)))},
#      XMLTag(ConstantString("packagedElement"), [(ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw"))], None,
#             XMLTag(ConstantString("ownedComment"), [(ConstantString("body"), ConstantString("This is body d4143d60."))], None, None)))
# ]

# more difficult test cases...

input6 = '<packagedElement name="TempClass1" visibility="public"></packagedElement>'

output6 = '<packagedElement name="TempClass1"></packagedElement>'

test_case_6 = [({"input1": xml_to_dsl(input6)}, xml_to_dsl(output6))]

# test_case_6 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("name"), ConstantString("TempClass1")), (ConstantString("visibility"), ConstantString("public"))], None, None)}, 
#     XMLTag(ConstantString("packagedElement"), [(ConstantString("name"), ConstantString("TempClass1"))], None, None)
#     )
# ]

input7 = '<packagedElement name="TempClass1"></packagedElement>'

output7 = '<packagedElement name="TempClass1" visibility="public"></packagedElement>'

test_case_7 = [({"input1": xml_to_dsl(input7)}, xml_to_dsl(output7))]

# test_case_7 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("name"), ConstantString("TempClass1"))], None, None)}, 
#     XMLTag(ConstantString("packagedElement"), [(ConstantString("name"), ConstantString("TempClass1")), (ConstantString("visibility"), ConstantString("public"))], None, None)
#     )
# ]

input8 = '<packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="TempClass1"></packagedElement>'

output8 = '<packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="TempClass1" visibility="public"></packagedElement>'

test_case_8 = [({"input1": xml_to_dsl(input8)}, xml_to_dsl(output8))]

# test_case_8 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("name"), ConstantString("TempClass1"))], None, None)}, 
#     XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("name"), ConstantString("TempClass1")), (ConstantString("visibility"), ConstantString("public"))], None, None)
#     )
# ]

input9 = '''
        <ownedComment annotatedElement="_383AC7D3023A40C0CE87009D">
            <body>This is body d4143d60.</body>
        </ownedComment>
        '''

output9 = '<ownedComment annotatedElement="_383AC7D3023A40C0CE87009D" body="This is body d4143d60." />'

test_case_9 = [({"input1": xml_to_dsl(input9)}, xml_to_dsl(output9))]

# test_case_9 = [
#     ({"input1": XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("_383AC7D3023A40C0CE87009D"))], None,
#                         XMLTag(ConstantString("body"), None, ConstantString("This is body d4143d60."), None))}, 
#     XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("body"), ConstantString("This is body d4143d60."))], None, None)
#     )
# ]

input10 = '''
        <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D">
            <ownedComment annotatedElement="_383AC7D3023A40C0CE87009D">
                <body>This is body d4143d60.</body>
            </ownedComment>
        </packagedElement>
        '''

output10 = '''
        <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" >
            <ownedComment annotatedElement="_383AC7D3023A40C0CE87009D" body="This is body d4143d60." />
        </packagedElement>
        '''

test_case_10 = [({"input1": xml_to_dsl(input10)}, xml_to_dsl(output10))]

# test_case_11 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D"))], None,
#                       XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("annotatedElement"))], None,
#                               XMLTag(ConstantString("body"), None, ConstantString("This is body d4143d60."), None)))},
#      XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D"))], None,
#             XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("annotatedElement")), (ConstantString("body"), ConstantString("This is body d4143d60."))], None, None)))
# ]

input11 = '<ownedComment id="_0-3eYuRbEduVs91jndUPVw" body="This is body d4143d60." annotatedElement="_383AC7D3023A40C0CE87009D" />'

output11 = '''
        <ownedComment id="_0-3eYuRbEduVs91jndUPVw" annotatedElement="_383AC7D3023A40C0CE87009D">
            <body>This is body d4143d60.</body>
        </ownedComment>
        '''

test_case_11 = [({"input1": xml_to_dsl(input11)}, xml_to_dsl(output11))]

# test_case_10 = [
#     ({"input1": XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw")), (ConstantString("body"), ConstantString("This is body d4143d60."))], None, None)}, 
#     XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw"))], None,
#                         XMLTag(ConstantString("body"), None, ConstantString("This is body d4143d60."), None))
#     )
# ]

input12 = '''
        <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="TempClass1">
            <ownedComment id="_0-3eYuRbEduVs91jndUPVw" annotatedElement="_383AC7D3023A40C0CE87009D">
                <body>This is body d4143d60.</body>
            </ownedComment>
        </packagedElement>
        '''

output12 = '''
        <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="TempClass1" visibility="public">
            <ownedComment id="_0-3eYuRbEduVs91jndUPVw" body="This is body d4143d60." annotatedElement="_383AC7D3023A40C0CE87009D" />
        </packagedElement>
        '''

test_case_12 = [({"input1": xml_to_dsl(input12)}, xml_to_dsl(output12))]

# test_case_12 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("name"), ConstantString("TempClass1"))], None,
#                       XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("annotatedElement")), (ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw"))], None,
#                               XMLTag(ConstantString("body"), None, ConstantString("This is body d4143d60."), None)))},
#      XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("name"), ConstantString("TempClass1"))], None,
#             XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("annotatedElement")), (ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw")), (ConstantString("body"), ConstantString("This is body d4143d60."))], None, None)))
# ]

# input13 = '''
#         <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="TempClass1">
#             <eAnnotations id="_0-3eZeRbEduVs91jndUPVw" source="http://www.eclipse.org/uml2/2.0.0/UML">
#                 <details id="_0-3eZuRbEduVs91jndUPVw" key="entity" />
#             </eAnnotations>
#             <ownedComment id="_0-3eYuRbEduVs91jndUPVw" annotatedElement="_383AC7D3023A40C0CE87009D">
#                 <body>This is body d4143d60.</body>
#             </ownedComment>
#             <ownedAttribute id="_383AC7D3023A40C0CEBF005E" name="TempAttrib1" visibility="private" />
#             <ownedAttribute id="_383AC7D3023A40C0CE9C0271" name="TempAttrib2"
#                 visibility="public" type="_383AC7D3023A40C0CAFC0106" isUnique="false" aggregation="shared"
#                 association="_383AC7D3023A40C0CE9B034C" />
#         </packagedElement>
#         '''

# output13 = '''
#         <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="TempClass1" visibility="public">
#             <ownedComment id="_0-3eYuRbEduVs91jndUPVw" body="This is body d4143d60." annotatedElement="_383AC7D3023A40C0CE87009D" />
#             <ownedAttribute id="_383AC7D3023A40C0CEBF005E" visibility="private" name="TempAttrib1" />
#             <ownedAttribute id="_383AC7D3023A40C0CE9C0271" visibility="public"
#                 name="TempAttrib2" isUnique="false" aggregation="shared"
#                 type="_383AC7D3023A40C0CAFC0106" association="_383AC7D3023A40C0CE9B034C" />
#         </packagedElement>
#         '''

# test_case_13 = [({"input1": xml_to_dsl(input13)}, xml_to_dsl(output13))]

# test_case_13 = [
#     ({"input1": XMLTag(
#         ConstantString("packagedElement"), 
#         [
#             (ConstantString("type"), ConstantString("uml:Class")), 
#             (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D")), 
#             (ConstantString("name"), ConstantString("TempClass1"))
#         ], 
#         None,
#         [
#             XMLTag(
#                 ConstantString("eAnnotations"), 
#                 [
#                     (ConstantString("id"), ConstantString("_0-3eZeRbEduVs91jndUPVw")), 
#                     (ConstantString("source"), ConstantString("http://www.eclipse.org/uml2/2.0.0/UML"))
#                 ], 
#                 None,
#                 XMLTag(
#                     ConstantString("details"), 
#                     [
#                         (ConstantString("id"), ConstantString("_0-3eZuRbEduVs91jndUPVw")), 
#                         (ConstantString("key"), ConstantString("entity"))
#                     ], 
#                     None, 
#                     None
#                 )
#             ),
#             XMLTag(
#                 ConstantString("ownedComment"), 
#                 [
#                     (ConstantString("annotatedElement"), ConstantString("_383AC7D3023A40C0CE87009D")), 
#                     (ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw"))
#                 ], 
#                 None,
#                 XMLTag(
#                     ConstantString("body"), 
#                     None, 
#                     ConstantString("This is body d4143d60."), 
#                     None
#                 )
#             ),
#             XMLTag(
#                 ConstantString("ownedAttribute"), 
#                 [
#                     (ConstantString("id"), ConstantString("_383AC7D3023A40C0CEBF005E")), 
#                     (ConstantString("name"), ConstantString("TempAttrib1")), 
#                     (ConstantString("visibility"), ConstantString("private"))
#                 ], 
#                 None, 
#                 None
#             ),
#             XMLTag(
#                 ConstantString("ownedAttribute"), 
#                 [
#                     (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE9C0271")), 
#                     (ConstantString("name"), ConstantString("TempAttrib2")), 
#                     (ConstantString("visibility"), ConstantString("public")), 
#                     (ConstantString("type"), ConstantString("_383AC7D3023A40C0CAFC0106")), 
#                     (ConstantString("isUnique"), ConstantString("false")), 
#                     (ConstantString("aggregation"), ConstantString("shared")), 
#                     (ConstantString("association"), ConstantString("_383AC7D3023A40C0CE9B034C"))
#                 ], 
#                 None, 
#                 None
#             )
#         ]
#     )}, 
#     XMLTag(
#         ConstantString("packagedElement"), 
#         [
#             (ConstantString("type"), ConstantString("uml:Class")), 
#             (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D")), 
#             (ConstantString("name"), ConstantString("TempClass1")), 
#             (ConstantString("visibility"), ConstantString("public"))
#         ], 
#         None,
#         [
#             XMLTag(
#                 ConstantString("ownedComment"), 
#                 [
#                     (ConstantString("annotatedElement"), ConstantString("_383AC7D3023A40C0CE87009D")), 
#                     (ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw")), 
#                     (ConstantString("body"), ConstantString("This is body d4143d60."))
#                 ], 
#                 None, 
#                 None
#             ),
#             XMLTag(
#                 ConstantString("ownedAttribute"), 
#                 [
#                     (ConstantString("id"), ConstantString("_383AC7D3023A40C0CEBF005E")), 
#                     (ConstantString("visibility"), ConstantString("private")), 
#                     (ConstantString("name"), ConstantString("TempAttrib1"))
#                 ], 
#                 None, 
#                 None
#             ),
#             XMLTag(
#                 ConstantString("ownedAttribute"), 
#                 [
#                     (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE9C0271")), 
#                     (ConstantString("visibility"), ConstantString("public")), 
#                     (ConstantString("name"), ConstantString("TempAttrib2")), 
#                     (ConstantString("isUnique"), ConstantString("false")), 
#                     (ConstantString("aggregation"), ConstantString("shared")), 
#                     (ConstantString("type"), ConstantString("_383AC7D3023A40C0CAFC0106")), 
#                     (ConstantString("association"), ConstantString("_383AC7D3023A40C0CE9B034C"))
#                 ], 
#                 None, 
#                 None
#             )
#         ]
#     ))
# ]
