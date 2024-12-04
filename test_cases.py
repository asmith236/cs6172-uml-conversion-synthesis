# from dsl import *

# # <!-- Test Case 1 -->

# input1 = '<packagedElement name="expects_cachoeira" visibility="public"></packagedElement>'

# output1 = '<packagedElement name="expects_cachoeira"></packagedElement>'

# test_case_1 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("name"), ConstantString("expects_cachoeira")), (ConstantString("visibility"), ConstantString("public"))], None, None)}, 
#     XMLTag(ConstantString("packagedElement"), [(ConstantString("name"), ConstantString("expects_cachoeira"))], None, None)
#     )
# ]

# # <!-- Test Case 2 -->

# input2 = '<packagedElement name="expects_cachoeira"></packagedElement>'

# output2 = '<packagedElement name="expects_cachoeira" visibility="public"></packagedElement>'

# test_case_2 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("name"), ConstantString("expects_cachoeira"))], None, None)}, 
#     XMLTag(ConstantString("packagedElement"), [(ConstantString("name"), ConstantString("expects_cachoeira")), (ConstantString("visibility"), ConstantString("public"))], None, None)
#     )
# ]

# # <!-- Test Case 3 -->

# input3 = '<packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira"></packagedElement>'

# output3 = '<packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira" visibility="public"></packagedElement>'

# test_case_3 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("name"), ConstantString("expects_cachoeira"))], None, None)}, 
#     XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("name"), ConstantString("expects_cachoeira")), (ConstantString("visibility"), ConstantString("public"))], None, None)
#     )
# ]

# # <!-- Test Case 4 -->

# input4 = '''
#         <ownedComment annotatedElement="_383AC7D3023A40C0CE87009D">
#             <body>This is body gemonies d4143d60.</body>
#         </ownedComment>
#         '''

# output4 = '<ownedComment annotatedElement="_383AC7D3023A40C0CE87009D" body="This is body gemonies d4143d60." />'

# test_case_4 = [
#     ({"input1": XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("_383AC7D3023A40C0CE87009D"))], None,
#                         XMLTag(ConstantString("body"), None, ConstantString("This is body gemonies d4143d60."), None))}, 
#     XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("body"), ConstantString("This is body gemonies d4143d60."))], None, None)
#     )
# ]

# # <!-- Test Case 5 -->

# input5 = '<ownedComment id="_0-3eYuRbEduVs91jndUPVw" body="This is body gemonies d4143d60." annotatedElement="_383AC7D3023A40C0CE87009D" />'

# output5 = '''
#         <ownedComment id="_0-3eYuRbEduVs91jndUPVw" annotatedElement="_383AC7D3023A40C0CE87009D">
#             <body>This is body gemonies d4143d60.</body>
#         </ownedComment>
#         '''

# test_case_5 = [
#     ({"input1": XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw")), (ConstantString("body"), ConstantString("This is body gemonies d4143d60."))], None, None)}, 
#     XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw"))], None,
#                         XMLTag(ConstantString("body"), None, ConstantString("This is body gemonies d4143d60."), None))
#     )
# ]

# # <!-- Test Case 6 -->

# input6 = '''
#         <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D">
#             <ownedComment annotatedElement="_383AC7D3023A40C0CE87009D">
#                 <body>This is body gemonies d4143d60.</body>
#             </ownedComment>
#         </packagedElement>
#         '''

# output6 = '''
#         <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" >
#             <ownedComment annotatedElement="_383AC7D3023A40C0CE87009D" body="This is body gemonies d4143d60." />
#         </packagedElement>
# '''

# test_case_6 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D"))], None,
#                       XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("annotatedElement"))], None,
#                               XMLTag(ConstantString("body"), None, ConstantString("This is body gemonies d4143d60."), None)))},
#      XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D"))], None,
#             XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("annotatedElement")), (ConstantString("body"), ConstantString("This is body gemonies d4143d60."))], None, None)))
# ]

# # <!-- Test Case 7 -->

# input7 = '''
#         <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira">
#             <ownedComment id="_0-3eYuRbEduVs91jndUPVw" annotatedElement="_383AC7D3023A40C0CE87009D">
#                 <body>This is body gemonies d4143d60.</body>
#             </ownedComment>
#         </packagedElement>
#         '''

# output7 = '''
#         <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira" visibility="public">
#             <ownedComment id="_0-3eYuRbEduVs91jndUPVw" body="This is body gemonies d4143d60." annotatedElement="_383AC7D3023A40C0CE87009D" />
#         </packagedElement>
#         '''

# test_case_7 = [
#     ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("name"), ConstantString("expects_cachoeira"))], None,
#                       XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("annotatedElement")), (ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw"))], None,
#                               XMLTag(ConstantString("body"), None, ConstantString("This is body gemonies d4143d60."), None)))},
#      XMLTag(ConstantString("packagedElement"), [(ConstantString("type"), ConstantString("uml:Class")), (ConstantString("id"), ConstantString("_383AC7D3023A40C0CE87009D")), (ConstantString("name"), ConstantString("expects_cachoeira"))], None,
#             XMLTag(ConstantString("ownedComment"), [(ConstantString("annotatedElement"), ConstantString("annotatedElement")), (ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw")), (ConstantString("body"), ConstantString("This is body gemonies d4143d60."))], None, None)))
# ]

# # <!-- Test Case 8 -->

# input8 = '''
#         <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira">
#             <eAnnotations id="_0-3eZeRbEduVs91jndUPVw" source="http://www.eclipse.org/uml2/2.0.0/UML">
#                 <details id="_0-3eZuRbEduVs91jndUPVw" key="entity" />
#             </eAnnotations>
#             <ownedComment id="_0-3eYuRbEduVs91jndUPVw" annotatedElement="_383AC7D3023A40C0CE87009D">
#                 <body>This is body gemonies d4143d60.</body>
#             </ownedComment>
#             <ownedAttribute id="_383AC7D3023A40C0CEBF005E" name="unsteep_commaes" visibility="private" />
#             <ownedAttribute id="_383AC7D3023A40C0CE9C0271" name="polarography_palirrhea"
#                 visibility="public" type="_383AC7D3023A40C0CAFC0106" isUnique="false" aggregation="shared"
#                 association="_383AC7D3023A40C0CE9B034C" />
#         </packagedElement>
#         '''

# output8 = '''
#         <packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira" visibility="public">
#             <ownedComment id="_0-3eYuRbEduVs91jndUPVw" body="This is body gemonies d4143d60." annotatedElement="_383AC7D3023A40C0CE87009D" />
#             <ownedAttribute id="_383AC7D3023A40C0CEBF005E" visibility="private" name="unsteep_commaes" />
#             <ownedAttribute id="_383AC7D3023A40C0CE9C0271" visibility="public"
#                 name="polarography_palirrhea" isUnique="false" aggregation="shared"
#                 type="_383AC7D3023A40C0CAFC0106" association="_383AC7D3023A40C0CE9B034C" />
#         </packagedElement>
#         '''

from dsl import *

# <!-- Test Case 1 -->

input1 = '<packagedElement visibility="public"></packagedElement>'

output1 = '<packagedElement></packagedElement>'

test_case_1 = [
    ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("visibility"), ConstantString("public"))], None, None)}, 
    XMLTag(ConstantString("packagedElement"), [], None, None)
    )
]

# <!-- Test Case 2 -->

input2 = '<packagedElement></packagedElement>'

output2 = '<packagedElement visibility="public"></packagedElement>'

test_case_2 = [
    ({"input1": XMLTag(ConstantString("packagedElement"), [], None, None)}, 
    XMLTag(ConstantString("packagedElement"), [(ConstantString("visibility"), ConstantString("public"))], None, None)
    )
]

# <!-- Test Case 3 -->

input3 = '''
        <ownedComment>
            <body>This is body d4143d60.</body>
        </ownedComment>
        '''

output3 = '<ownedComment body="This is body d4143d60." />'

test_case_3 = [
    ({"input1": XMLTag(ConstantString("ownedComment"), [], None,
                        XMLTag(ConstantString("body"), None, ConstantString("This is body d4143d60."), None))}, 
    XMLTag(ConstantString("ownedComment"), [(ConstantString("body"), ConstantString("This is body d4143d60."))], None, None)
    )
]

# <!-- Test Case 4 -->

input4 = '<ownedComment body="This is body gemonies d4143d60." />'

output4 = '''
        <ownedComment>
            <body>This is body gemonies d4143d60.</body>
        </ownedComment>
        '''

test_case_4 = [
    ({"input1": XMLTag(ConstantString("ownedComment"), [(ConstantString("body"), ConstantString("This is body d4143d60."))], None, None)}, 
    XMLTag(ConstantString("ownedComment"), [], None,
                        XMLTag(ConstantString("body"), None, ConstantString("This is body d4143d60."), None))
                        )
]

# <!-- Test Case 5 -->

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

test_case_5 = [
    ({"input1": XMLTag(ConstantString("packagedElement"), [(ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw"))], None,
                      XMLTag(ConstantString("ownedComment"), None, None,
                              XMLTag(ConstantString("body"), None, ConstantString("This is body d4143d60."), None)))},
     XMLTag(ConstantString("packagedElement"), [(ConstantString("id"), ConstantString("_0-3eYuRbEduVs91jndUPVw"))], None,
            XMLTag(ConstantString("ownedComment"), [(ConstantString("body"), ConstantString("This is body d4143d60."))], None, None)))
]
