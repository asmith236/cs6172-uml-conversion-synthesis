# Test Case 1

input1 = '<packagedElement xmi:type="uml:Class" xmi:id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira"></packagedElement>'
output1 = '<packagedElement xmi:type="uml:Class" xmi:id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira" visibility="public"></packagedElement>'

# Test Case 2

input2 = '<ownedComment xmi:id="_0-3eYuRbEduVs91jndUPVw" annotatedElement="_383AC7D3023A40C0CE87009D"><body>This is body gemonies d4143d60.</body></ownedComment>'
output2 = '<ownedComment xmi:id="_0-3eYuRbEduVs91jndUPVw" body="This is body gemonies d4143d60." annotatedElement="_383AC7D3023A40C0CE87009D" />'

# Test Case 3

input3 = '<packagedElement xmi:type="uml:Class" xmi:id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira"><ownedComment xmi:id="_0-3eYuRbEduVs91jndUPVw" annotatedElement="_383AC7D3023A40C0CE87009D"><body>This is body gemonies d4143d60.</body></ownedComment></packagedElement>'
output3 = '<packagedElement xmi:type="uml:Class" xmi:id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira" visibility="public"><ownedComment xmi:id="_0-3eYuRbEduVs91jndUPVw" body="This is body gemonies d4143d60." annotatedElement="_383AC7D3023A40C0CE87009D" /></packagedElement>'
