# CS 6172 UML Conversion Synthesis

Execute the bottom_up enumerator by executing python3 bottom_up/bottom_up.py.

Below is the bottom_up output when executed on test cases 1-10:

==================================================

Executing test case 1 with size bound 20...

Input:
<packagedElement visibility="public"/>

Desired Output:
<packagedElement/>

Test case passed!
Number of programs generated: 9

Synthesized program:
RemoveAttribute(
    XMLVariable('input1'),
    ConstantString('visibility')
)

Execution time: 0.0004 seconds

==================================================

Executing test case 2 with size bound 20...

Input:
<packagedElement/>

Desired Output:
<packagedElement visibility="public"/>

Test case passed!
Number of programs generated: 14

Synthesized program:
SetAttribute(
    XMLVariable('input1'),
    ConstantString('visibility'),
    ConstantString('public')
)

Execution time: 0.0007 seconds

==================================================

Executing test case 3 with size bound 20...

Input:
<ownedComment>
    <body>This is body.</body>
</ownedComment>

Desired Output:
<ownedComment body="This is body."/>

Test case passed!
Number of programs generated: 119

Synthesized program:
SetAttribute(
    RemoveChild(
        XMLVariable('input1')
    ),
    ConstantString('body'),
    ExtractText(
        ExtractChild(
            XMLVariable('input1')
        )
    )
)

Execution time: 0.0112 seconds

==================================================

Executing test case 4 with size bound 20...

Input:
<ownedComment body="This is body."/>

Desired Output:
<ownedComment>
    <body>This is body.</body>
</ownedComment>

Test case passed!
Number of programs generated: 11574

Synthesized program:
SetChild(
    RemoveAttribute(
        XMLVariable('input1'),
        ConstantString('body')
    ),
    ConstantString('body'),
    SetTag(
        SetText(
            RemoveAttribute(
                XMLVariable('input1'),
                ConstantString('body')
            ),
            ExtractAttribute(
                XMLVariable('input1'),
                ConstantString('body')
            )
        ),
        ConstantString('body')
    )
)

Execution time: 1.0701 seconds

==================================================

Executing test case 5 with size bound 20...

Input:
<packagedElement id="_YuRb">
    <ownedComment>
        <body>This is body.</body>
    </ownedComment>
</packagedElement>

Desired Output:
<packagedElement id="_YuRb">
    <ownedComment body="This is body."/>
</packagedElement>

Test case passed!
Number of programs generated: 85475

Synthesized program:
SetChild(
    XMLVariable('input1'),
    ConstantString('id'),
    SetAttribute(
        RemoveChild(
            ExtractChild(
                XMLVariable('input1')
            )
        ),
        ConstantString('body'),
        ExtractText(
            ExtractChild(
                ExtractChild(
                    XMLVariable('input1')
                )
            )
        )
    )
)

Execution time: 8.8303 seconds

==================================================

Executing test case 6 with size bound 20...

Input:
<packagedElement name="TempClass1" visibility="public"/>

Desired Output:
<packagedElement name="TempClass1"/>

Test case passed!
Number of programs generated: 12

Synthesized program:
RemoveAttribute(
    XMLVariable('input1'),
    ConstantString('visibility')
)

Execution time: 0.0004 seconds

==================================================

Executing test case 7 with size bound 20...

Input:
<packagedElement name="TempClass1"/>

Desired Output:
<packagedElement name="TempClass1" visibility="public"/>

Test case passed!
Number of programs generated: 20

Synthesized program:
SetAttribute(
    XMLVariable('input1'),
    ConstantString('visibility'),
    ConstantString('public')
)

Execution time: 0.0008 seconds

==================================================

Executing test case 8 with size bound 20...

Input:
<packagedElement type="uml:Class" id="_383A" name="TempClass1"/>

Desired Output:
<packagedElement type="uml:Class" id="_383A" name="TempClass1" visibility="public"/>

Test case passed!
Number of programs generated: 47

Synthesized program:
SetAttribute(
    XMLVariable('input1'),
    ConstantString('visibility'),
    ConstantString('public')
)

Execution time: 0.0015 seconds

==================================================

Executing test case 9 with size bound 20...

Input:
<ownedComment annotatedElement="_383A">
    <body>This is body.</body>
</ownedComment>

Desired Output:
<ownedComment annotatedElement="_383A" body="This is body."/>

Test case passed!
Number of programs generated: 326

Synthesized program:
SetAttribute(
    RemoveChild(
        XMLVariable('input1')
    ),
    ConstantString('body'),
    ExtractText(
        ExtractChild(
            XMLVariable('input1')
        )
    )
)

Execution time: 0.0254 seconds

==================================================

Executing test case 10 with size bound 20...

Input:
<packagedElement type="uml:Class" id="_383A">
    <ownedComment annotatedElement="_383A">
        <body>This is body.</body>
    </ownedComment>
</packagedElement>

Desired Output:
<packagedElement type="uml:Class" id="_383A">
    <ownedComment annotatedElement="_383A" body="This is body."/>
</packagedElement>

Test case passed!
Number of programs generated: 661855

Synthesized program:
SetChild(
    XMLVariable('input1'),
    ConstantString('id'),
    SetAttribute(
        RemoveChild(
            ExtractChild(
                XMLVariable('input1')
            )
        ),
        ConstantString('body'),
        ExtractText(
            ExtractChild(
                ExtractChild(
                    XMLVariable('input1')
                )
            )
        )
    )
)

Execution time: 64.7667 seconds

==================================================  
[+] XML Bottom-Up Synthesis: +10/10 points