import xml.etree.ElementTree as ET

class Expression():

    def evaluate(self, environment):
        assert False, "not implemented"

    def arguments(self):
        assert False, "not implemented"

    def cost(self):
        return 1 + sum([0] + [argument.cost() for argument in self.arguments()])

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self): return hash(str(self))

    def __ne__(self, other): return str(self) != str(other)

    def __gt__(self, other): return str(self) > str(other)

    def __lt__(self, other): return str(self) < str(other)

    def minimum_cost_member_of_extension(self):
        assert False, "implement"

    def version_space_size(self):
        assert False, "implement"
        
class ConstantString(Expression):
    return_type = "str"
    argument_types = []
    
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return f'ConstantString("{self.content}")'

    def pretty_print(self):
        # output plain string content instead of wrapping it
        return self.content
    
    def arguments(self):
        return []
    
    def extension(self):
        return [self]
    
    def evaluate(self, environment):
        return self.content
    
    def version_space_size(self):
        return 1

    def minimum_cost_member_of_extension(self):
        return self
    
    def cost(self):
        base_cost = 50 # init high cost for constant strings
        length_penalty = len(self.content) ** 3  # cost increases exponentially w string length
        return base_cost + length_penalty

class XMLTag(Expression):
    return_type = "xml"
    argument_types = []

    def __init__(self, tag, attributes, text, children=None):
        self.tag = tag  # ConstantString or None
        self.attributes = attributes  # List of (ConstantString, ConstantString)
        self.text = text  # ConstantString or None
        self.children = children or []  # List of XMLTag

    def __str__(self):
        tag = str(self.tag) if self.tag else "none"
        attributes = f"[{', '.join(map(str, self.attributes))}]" if self.attributes else "none"
        text = str(self.text) if self.text else "none"
        children = f"[{', '.join(map(str, self.children))}]" if self.children else "none"
        return f"XMLTag({tag}, {attributes}, {text}, {children})"

    def evaluate(self, environment):
        tag = self.tag.evaluate(environment) if self.tag else None
        attributes = {
            k.evaluate(environment): v.evaluate(environment)
            for k, v in (self.attributes or [])
            if k.evaluate(environment) is not None
        }
        text = self.text.evaluate(environment) if self.text else None
        children = [child.evaluate(environment) for child in self.children]
        return {
            "tag": tag,
            "attributes": attributes,
            "text": text,
            "children": children  # List of evaluated children
        }

    def arguments(self):
        args = [self.tag] + (self.attributes or []) + ([self.text] if self.text else []) + self.children
        return args

class ExtractAttribute(Expression):
    return_type = "str"
    argument_types = ["xml", "str"]

    def __init__(self, xml_expr, attr_name=None):
        self.xml_expr = xml_expr
        self.attr_name = attr_name  # ConstantString or None

    def __str__(self):
        attr_name = str(self.attr_name) if self.attr_name else "none"
        return f"ExtractAttribute({self.xml_expr}, {attr_name})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        if self.attr_name:
            attr_name = self.attr_name.evaluate(environment)
            return xml["attributes"].get(attr_name, None)
        # dynamically collect all attribute names and values
        return xml["attributes"]

    def arguments(self):
        return [self.xml_expr] + ([self.attr_name] if self.attr_name else [])

class SetAttribute(Expression):
    return_type = "xml"
    argument_types = ["xml", "str", "str"]

    def __init__(self, xml_expr, attr_name, attr_value):
        self.xml_expr = xml_expr
        self.attr_name = attr_name
        self.attr_value = attr_value

    def __str__(self):
        return f"SetAttribute({self.xml_expr}, {self.attr_name}, {self.attr_value})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        attr_name = self.attr_name.evaluate(environment)
        attr_value = self.attr_value.evaluate(environment)
        if attr_name is not None:
            xml["attributes"][attr_name] = attr_value
        return xml

    def arguments(self):
        return [self.xml_expr, self.attr_name, self.attr_value]

class ExtractChild(Expression):
    return_type = "xml"
    argument_types = ["xml", "str", "int"]  # Add "int" for specifying index

    def __init__(self, xml_expr, child_tag=None, child_index=None):
        self.xml_expr = xml_expr
        self.child_tag = child_tag  # ConstantString or None
        self.child_index = child_index  # ConstantString or None

    def __str__(self):
        child_tag = str(self.child_tag) if self.child_tag else "none"
        child_index = str(self.child_index) if self.child_index else "none"
        return f"ExtractChild({self.xml_expr}, {child_tag}, {child_index})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        child_tag = self.child_tag.evaluate(environment) if self.child_tag else None
        child_index = self.child_index.evaluate(environment) if self.child_index else None

        children = xml.get("children", [])

        if child_tag:
            # Filter children by tag
            matching_children = [child for child in children if child["tag"] == child_tag]
            if child_index is not None and 0 <= child_index < len(matching_children):
                return matching_children[child_index]  # Return the child at the specified index
            return matching_children  # Return all matching children if no index is specified
        elif child_index is not None and 0 <= child_index < len(children):
            return children[child_index]  # Return the child at the specified index
        return children  # Return all children if no tag or index is specified

    def arguments(self):
        return [self.xml_expr] + ([self.child_tag] if self.child_tag else []) + ([self.child_index] if self.child_index else [])

class SetChild(Expression):
    return_type = "xml"
    argument_types = ["xml", "xml", "int"]  # Add "int" for specifying index

    def __init__(self, xml_expr, child_value, child_index=None):
        self.xml_expr = xml_expr
        self.child_value = child_value
        self.child_index = child_index  # ConstantString or None

    def __str__(self):
        child_index = str(self.child_index) if self.child_index else "none"
        return f"SetChild({self.xml_expr}, {self.child_value}, {child_index})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        child_value = self.child_value.evaluate(environment)
        child_index = self.child_index.evaluate(environment) if self.child_index else None

        children = xml.get("children", [])
        if child_index is not None and 0 <= child_index < len(children):
            # Replace the child at the specified index
            children[child_index] = child_value
        else:
            # Add a new child
            children.append(child_value)
        xml["children"] = children
        return xml

    def arguments(self):
        return [self.xml_expr, self.child_value] + ([self.child_index] if self.child_index else [])

class XMLVariable(Expression):
    return_type = "xml"
    argument_types = []

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"XMLVariable('{self.name}')"

    def pretty_print(self):
        return self.name

    def evaluate(self, environment):
        return environment[self.name].evaluate({})
    
    def extension(self):
        return [self]

    def arguments(self):
        return []
    
    def version_space_size(self):
        return 1

    def minimum_cost_member_of_extension(self):
        return self
    
class SetTag(Expression):
    return_type = "xml"
    argument_types = ["xml", "str"]

    def __init__(self, xml_expr, tag_value):
        self.xml_expr = xml_expr
        self.tag_value = tag_value

    def __str__(self):
        return f"SetTag({self.xml_expr}, {self.tag_value})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        tag_value = self.tag_value.evaluate(environment)
        xml["tag"] = tag_value
        return xml

    def arguments(self):
        return [self.xml_expr, self.tag_value]
    
class ExtractTag(Expression):
    return_type = "str"
    argument_types = ["xml"]

    def __init__(self, xml_expr):
        self.xml_expr = xml_expr

    def __str__(self):
        return f"ExtractTag({self.xml_expr})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        # Return the tag from the XML structure
        return xml.get("tag")

    def arguments(self):
        return [self.xml_expr]
    
class ExtractText(Expression):
    return_type = "str"
    argument_types = ["xml"]

    def __init__(self, xml_expr):
        self.xml_expr = xml_expr

    def __str__(self):
        return f"ExtractText({self.xml_expr})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        # Return the text from the XML structure
        return xml.get("text")

    def arguments(self):
        return [self.xml_expr]
    
class SetText(Expression):
    return_type = "xml"
    argument_types = ["xml", "str"]

    def __init__(self, xml_expr, text_value):
        self.xml_expr = xml_expr
        self.text_value = text_value  # Expected to be a ConstantString or equivalent

    def __str__(self):
        return f"SetText({self.xml_expr}, {self.text_value})"

    def evaluate(self, environment):
        # Evaluate the XML object and the new text value
        xml = self.xml_expr.evaluate(environment)
        text_value = self.text_value.evaluate(environment)
        
        # Update the text field of the XML
        xml["text"] = text_value
        
        # Return the updated XML object
        return xml

    def arguments(self):
        return [self.xml_expr, self.text_value]

def test_evaluation(verbose=False):
    expressions, ground_truth = [], []

    # Test creating a simple XML tag
    expressions.append(XMLTag(
        ConstantString("root"),
        [(ConstantString("key"), ConstantString("value"))],
        None,
        None
    ))
    ground_truth.append(lambda: {
        "tag": "root",
        "attributes": {"key": "value"},
        "text": None,
        "children": []
    })

    # Test extracting an attribute
    expressions.append(ExtractAttribute(
        XMLTag(
            ConstantString("root"),
            [(ConstantString("key"), ConstantString("value"))],
            None,
            None
        ),
        ConstantString("key")
    ))
    ground_truth.append(lambda: "value")

    # Test setting an attribute
    expressions.append(SetAttribute(
        XMLTag(
            ConstantString("root"),
            [],
            None,
            None
        ),
        ConstantString("key"),
        ConstantString("new_value")
    ))
    ground_truth.append(lambda: {
        "tag": "root",
        "attributes": {"key": "new_value"},
        "text": None,
        "children": []
    })

    # Test extracting a child
    expressions.append(ExtractChild(
        XMLTag(
            ConstantString("root"),
            [],
            None,
            [
                XMLTag(ConstantString("child"), None, None, None)
            ]
        ),
        ConstantString("child")
    ))
    ground_truth.append(lambda: {
        "tag": "child",
        "attributes": {},
        "text": None,
        "children": []
    })

    # Test setting a child
    expressions.append(SetChild(
        XMLTag(
            ConstantString("root"),
            [],
            None,
            []
        ),
        ConstantString("child"),
        XMLTag(ConstantString("child"), None, ConstantString("child text"), None)
    ))
    ground_truth.append(lambda: {
        "tag": "root",
        "attributes": {},
        "text": None,
        "children": [{
            "tag": "child",
            "attributes": {},
            "text": "child text",
            "children": []
        }]
    })

    all_correct, num_correct = True, 0
    for expression, correct_semantics in zip(expressions, ground_truth):
        result = expression.evaluate({})
        expected = correct_semantics()
        if result != expected:
            if verbose:
                print("Problem with evaluation for expression:")
                print(expression)
                print(f"Expected: {expected}")
                print(f"Got: {result}")
            all_correct = False
        else:
            num_correct += 1

    print(f" [+] XML DSL evaluation, +{num_correct}/{len(expressions)} points")
    return num_correct

def xml_to_dsl(xml_string):
    """
    Converts an XML string into a DSL representation using XMLTag and ConstantString.
    Wraps all attribute keys in quotes to prevent namespace prefixes from being identified by ElementTree.
    """

    def parse_element(element):
        """
        Recursively parses an ElementTree element into a DSL XMLTag.
        """
        # Extract the tag
        tag = ConstantString(element.tag)
        
        # Extract attributes
        attributes = [
            (ConstantString(k), ConstantString(v))
            for k, v in element.attrib.items()
        ]
        
        # Extract text content
        text = ConstantString(element.text.strip()) if element.text and element.text.strip() else None
        
        # Recursively parse child elements
        children = None
        child_elements = list(element)
        if len(child_elements) == 1:
            children = parse_element(child_elements[0])
        elif len(child_elements) > 1:
            raise ValueError("XMLTag in DSL only supports a single child.")
        
        # Construct and return the XMLTag
        return XMLTag(tag, attributes, text, children)
    
    # Parse the XML string
    root_element = ET.fromstring(xml_string)
    parsed_dsl = parse_element(root_element)
    
    # Capitalize 'none' in the DSL object
    return parsed_dsl

if __name__ == "__main__":
    test_evaluation(verbose=True)