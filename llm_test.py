import xml.etree.ElementTree as ET

def transform_element(xml_string):
    root = ET.fromstring(xml_string)
    transform_node(root)
    return ET.tostring(root, encoding='unicode')

def transform_node(node):
    # Transformation 1: Add visibility="public" if the element is "packagedElement" and it doesn't have visibility
    if node.tag == 'packagedElement' and 'visibility' not in node.attrib:
        node.set('visibility', 'public')

    # Transformation 2 & 3: Convert ownedComment body to attribute and remove the sub-element
    if node.tag == 'ownedComment':
        body_element = node.find('body')
        if body_element is not None:
            node.set('body', body_element.text)
            node.remove(body_element)

    # Transformation 4: Remove <eAnnotations> and its children if source="http://www.eclipse.org/uml2/2.0.0/UML"
    eannotations = node.find('eAnnotations')
    if eannotations is not None and eannotations.attrib.get('source') == "http://www.eclipse.org/uml2/2.0.0/UML":
        node.remove(eannotations)

    # Recursively transform child nodes
    for child in list(node):
        transform_node(child)

# Example usage
test_inputs = [
    '<packagedElement name="expects_cachoeira"></packagedElement>',
    '<ownedComment annotatedElement="_383AC7D3023A40C0CE87009D">\n  <body>This is body gemonies d4143d60.</body>\n</ownedComment>',
    '<packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira">\n  <ownedComment id="_0-3eYuRbEduVs91jndUPVw" annotatedElement="_383AC7D3023A40C0CE87009D">\n    <body>This is body d4143d60.</body>\n  </ownedComment>\n</packagedElement>',
    '<packagedElement type="uml:Class" id="_383AC7D3023A40C0CE87009D" name="expects_cachoeira">\n  <eAnnotations id="_0-3eZeRbEduVs91jndUPVw" source="http://www.eclipse.org/uml2/2.0.0/UML">\n    <details id="_0-3eZuRbEduVs91jndUPVw" key="entity" />\n  </eAnnotations>\n</packagedElement>'
    '<packagedElement type="uml:Class" id="_TYwJQFb6Ed-xTsassymaRA" name="safely_nimmed">\n  <eAnnotations id="_0gKwMORbEduVs91jndUPVw" source="http://www.eclipse.org/uml2/2.0.0/UML">\n    <details id="_0gxNKuRbEduVs91jndUPVw" key="entity" />\n  </eAnnotations>\n  <ownedComment id="_383AC7D3023A3F097A88029B" annotatedElement="_TYwJQFb6Ed-xTsassymaRA">\n    <body>This is body d4128197.</body>\n  </ownedComment>\n  <ownedAttribute id="_383AC7D3023A40C0CEBF005E" name="unsteep_commaes" visibility="private" />\n  <ownedAttribute id="_383AC7D3023A40C0CE9C0271" name="polarography_palirrhea"\n    visibility="public" type="_383AC7D3023A40C0CAFC0106" isUnique="false" aggregation="shared"\n    association="_383AC7D3023A40C0CE9B034C" />\n</packagedElement>'
]

for i, input_xml in enumerate(test_inputs, start=1):
    print(f"Transformation {i} Output:")
    print(transform_element(input_xml))
    print("\n")
