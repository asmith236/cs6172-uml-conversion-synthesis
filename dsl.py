import itertools
from math import prod
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

    def version_space_size(self):
        # Composite classes calculate the size based on arguments
        return 1 if not self.arguments() else prod(arg.version_space_size() for arg in self.arguments())
        
    def minimum_cost_member_of_extension(self):
        """
        Default implementation selects the minimal-cost member from arguments.
        Override this method for non-composite classes.
        """
        return self.__class__(*[arg.minimum_cost_member_of_extension() for arg in self.arguments()])

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

class XMLTag(Expression):
    return_type = "xml"
    argument_types = []

    def __init__(self, tag, attributes, text, child):
        self.tag = tag  # ConstantString or None
        self.attributes = attributes  # list of (ConstantString, ConstantString)
        self.text = text  # ConstantString or None
        self.child = child  # XMLTag or None

    def __str__(self):
        tag = str(self.tag) if self.tag else "none"
        attributes = f"[{', '.join(map(str, self.attributes))}]" if self.attributes else "none"
        text = str(self.text) if self.text else "none"
        child = str(self.child) if self.child else "none"
        return f"XMLTag({tag}, {attributes}, {text}, {child})"

    def evaluate(self, environment):
        tag = self.tag.evaluate(environment) if self.tag else None
        attributes = {
            k.evaluate(environment): v.evaluate(environment)
            for k, v in (self.attributes or [])
            if k.evaluate(environment) is not None
        }
        text = self.text.evaluate(environment) if self.text else None
        child = self.child.evaluate(environment) if self.child else None
        return {
            "tag": tag,
            "attributes": attributes,
            "text": text,
            "children": child  # single child or None
        }   

    def arguments(self):
        args = [self.tag] + (self.attributes or []) + ([self.text] if self.text else []) + ([self.child] if self.child else [])
        args = [arg for arg in args if arg is not None]
        return args
    
    @staticmethod
    def witness(specification):
        environment, target_output = specification

        if isinstance(target_output, dict) and "tag" in target_output:
            # Extract the tag, attributes, text, and children from the target XML
            tag = target_output["tag"]
            attributes = target_output.get("attributes", {})
            text = target_output.get("text", None)
            children = target_output.get("children", None)

            # Create the tag expression
            tag_expr = ConstantString(tag) if tag else None

            # Create attribute expressions by iterating over the environment
            attribute_exprs = []
            for var, xml in environment.items():
                for attr, val in attributes.items():
                    attribute_exprs.append(
                        SetAttribute(XMLVariable(var), ConstantString(attr), ConstantString(val))
                    )

            # Create the text expression
            text_expr = None
            if text:
                for var in environment.keys():  # Ensure `var` is defined
                    text_expr = SetText(XMLVariable(var), ConstantString(text))
                    break  # Only one `SetText` is needed per target text

            # Create the child expression recursively
            child_expr = None
            if children:
                for var in environment.keys():  # Ensure `var` is defined
                    child_witness = XMLTag.witness((environment, children))
                    child_expr = SetChild(
                        XMLVariable(var),
                        ConstantString(children["tag"]),
                        Union.make(child_witness) if isinstance(child_witness, list) else child_witness
                    )
                    break  # Only one `SetChild` is needed per target child

            # Return the constructed XMLTag expression
            return [XMLTag(tag_expr, attribute_exprs, text_expr, child_expr)]

        # If the specification is not valid for an XMLTag, return an empty list
        return []
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Generate extensions for the tag, text, and child components
        tag_ext = self.tag.extension() if self.tag else [None]
        text_ext = self.text.extension() if self.text else [None]
        child_ext = self.child.extension() if self.child else [None]

        # Handle attributes as transformation expressions
        if self.attributes:  # Ensure attributes are iterable expressions
            attributes_ext = [
                attr.extension() for attr in self.attributes if isinstance(attr, Expression)
            ]
        else:
            attributes_ext = [[]]  # No attributes

        # Flatten and construct combinations
        return [
            XMLTag(tag, list(attributes), text, child)
            for tag in tag_ext
            for attributes in itertools.product(*attributes_ext) if attributes_ext
            for text in text_ext
            for child in child_ext
        ]
    
    def minimum_cost_member_of_extension(self):
        """
        Returns the minimal-cost member of the extension by recursively choosing
        the minimal-cost member of each component (tag, attributes, text, child).
        """
        # Get the minimal-cost member for the tag
        min_tag = self.tag.minimum_cost_member_of_extension() if self.tag else None

        # Get the minimal-cost members for the attributes
        min_attributes = []
        if self.attributes:
            for attribute in self.attributes:
                if isinstance(attribute, tuple):
                    # If it's a tuple, unpack and process
                    attr_key, attr_value = attribute
                    min_key = attr_key.minimum_cost_member_of_extension()
                    min_value = attr_value.minimum_cost_member_of_extension()
                    min_attributes.append((min_key, min_value))
                elif isinstance(attribute, Expression):
                    # If it's an Expression (e.g., SetAttribute), process it directly
                    min_attributes.append(attribute.minimum_cost_member_of_extension())
                else:
                    raise TypeError(f"Unexpected attribute type: {type(attribute)}")

        # Get the minimal-cost member for the text
        min_text = self.text.minimum_cost_member_of_extension() if self.text else None

        # Get the minimal-cost member for the child
        min_child = self.child.minimum_cost_member_of_extension() if self.child else None

        # Construct a minimal-cost XMLTag
        return XMLTag(min_tag, min_attributes, min_text, min_child)

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
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Generate all combinations of extensions for arguments
        xml_extensions = self.xml_expr.extension()
        if self.attr_name:
            attr_name_extensions = self.attr_name.extension()
            return [
                ExtractAttribute(xml, attr_name)
                for xml in xml_extensions
                for attr_name in attr_name_extensions
            ]
        else:
            return [ExtractAttribute(xml, None) for xml in xml_extensions]
        
    def minimum_cost_member_of_extension(self):
        min_xml_expr = self.xml_expr.minimum_cost_member_of_extension()
        min_attr_name = self.attr_name.minimum_cost_member_of_extension() if self.attr_name else None
        return ExtractAttribute(min_xml_expr, min_attr_name)

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
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Combine extensions of arguments
        return [
            SetAttribute(xml, attr_name, attr_value)
            for xml in self.xml_expr.extension()
            for attr_name in self.attr_name.extension()
            for attr_value in self.attr_value.extension()
        ]
    
    def minimum_cost_member_of_extension(self):
        return SetAttribute(
            self.xml_expr.minimum_cost_member_of_extension(),
            self.attr_name.minimum_cost_member_of_extension(),
            self.attr_value.minimum_cost_member_of_extension(),
        )

class ExtractChild(Expression):
    return_type = "xml"
    argument_types = ["xml"]

    def __init__(self, xml_expr):
        self.xml_expr = xml_expr

    def __str__(self):
        return f"ExtractChild({self.xml_expr})"

    def evaluate(self, environment):
        # extract XML obj from the given expression
        xml = self.xml_expr.evaluate(environment)
        
        # get single child elem if it exists
        child = xml.get("children", None)
        if child is not None:
            return child
        return None  # return None if no child exists

    def arguments(self):
        return [self.xml_expr]
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Generate all possible extensions for the XML expression
        return [ExtractChild(xml) for xml in self.xml_expr.extension()]
    
    def minimum_cost_member_of_extension(self):
        min_xml_expr = self.xml_expr.minimum_cost_member_of_extension()
        return ExtractChild(min_xml_expr)

class SetChild(Expression):
    return_type = "xml"
    argument_types = ["xml", "str", "xml"]

    def __init__(self, xml_expr, child_tag, child_value):
        self.xml_expr = xml_expr
        self.child_tag = child_tag
        self.child_value = child_value

    def __str__(self):
        return f"SetChild({self.xml_expr}, {self.child_tag}, {self.child_value})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        child_tag = self.child_tag.evaluate(environment)
        child_value = self.child_value.evaluate(environment)

        # replace child only if the tags match
        if xml.get("children") and xml["children"]["tag"] == child_tag:
            xml["children"] = child_value
        else:
            # if there is no child or tag does not match, just set the child
            xml["children"] = child_value

        return xml

    def arguments(self):
        return [self.xml_expr, self.child_tag, self.child_value]
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Generate all combinations of argument extensions
        xml_extensions = self.xml_expr.extension()
        child_tag_extensions = self.child_tag.extension()
        child_value_extensions = self.child_value.extension()

        return [
            SetChild(xml, child_tag, child_value)
            for xml in xml_extensions
            for child_tag in child_tag_extensions
            for child_value in child_value_extensions
        ]
    
    def minimum_cost_member_of_extension(self):
        min_xml_expr = self.xml_expr.minimum_cost_member_of_extension()
        min_child_tag = self.child_tag.minimum_cost_member_of_extension()
        min_child_value = self.child_value.minimum_cost_member_of_extension()
        return SetChild(min_xml_expr, min_child_tag, min_child_value)
    
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
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Combine extensions of arguments
        return [
            SetTag(xml, value)
            for xml in self.xml_expr.extension()
            for value in self.tag_value.extension()
        ]
    
    def minimum_cost_member_of_extension(self):
        min_xml_expr = self.xml_expr.minimum_cost_member_of_extension()
        min_tag_value = self.tag_value.minimum_cost_member_of_extension()
        return SetTag(min_xml_expr, min_tag_value)
    
class ExtractTag(Expression):
    return_type = "str"
    argument_types = ["xml"]

    def __init__(self, xml_expr):
        self.xml_expr = xml_expr

    def __str__(self):
        return f"ExtractTag({self.xml_expr})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        # return the tag from the XML structure
        return xml.get("tag")

    def arguments(self):
        return [self.xml_expr]
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Generate all possible extensions for the XML expression
        return [ExtractTag(xml) for xml in self.xml_expr.extension()]
    
    def minimum_cost_member_of_extension(self):
        min_xml_expr = self.xml_expr.minimum_cost_member_of_extension()
        return ExtractTag(min_xml_expr)
    
class ExtractText(Expression):
    return_type = "str"
    argument_types = ["xml"]

    def __init__(self, xml_expr):
        self.xml_expr = xml_expr

    def __str__(self):
        return f"ExtractText({self.xml_expr})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        # return the text from the XML structure
        return xml.get("text")

    def arguments(self):
        return [self.xml_expr]
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Generate all possible extensions for the XML expression
        return [ExtractText(xml) for xml in self.xml_expr.extension()]
    
    def minimum_cost_member_of_extension(self):
        min_xml_expr = self.xml_expr.minimum_cost_member_of_extension()
        return ExtractText(min_xml_expr)
    
class SetText(Expression):
    return_type = "xml"
    argument_types = ["xml", "str"]

    def __init__(self, xml_expr, text_value):
        self.xml_expr = xml_expr
        self.text_value = text_value  # expected to be a ConstantString or equivalent

    def __str__(self):
        return f"SetText({self.xml_expr}, {self.text_value})"

    def evaluate(self, environment):
        # eval XML object and new text value
        xml = self.xml_expr.evaluate(environment)
        text_value = self.text_value.evaluate(environment)
        # update text field of the XML
        xml["text"] = text_value
        return xml

    def arguments(self):
        return [self.xml_expr, self.text_value]
    
    def extension(self):
        # Generate all combinations of argument extensions
        xml_extensions = self.xml_expr.extension()
        text_extensions = self.text_value.extension()

        return [
            SetText(xml, text_value)
            for xml in xml_extensions
            for text_value in text_extensions
        ]
    
    def minimum_cost_member_of_extension(self):
        return SetText(
            self.xml_expr.minimum_cost_member_of_extension(),
            self.text_value.minimum_cost_member_of_extension(),
        )

class RemoveAttribute(Expression):
    return_type = "xml"
    argument_types = ["xml", "str"]

    def __init__(self, xml_expr, attr_name):
        self.xml_expr = xml_expr
        self.attr_name = attr_name  # expected to be a ConstantString or equivalent

    def __str__(self):
        return f"RemoveAttribute({self.xml_expr}, {self.attr_name})"

    def evaluate(self, environment):
        # eval the XML object and attribute name
        xml = self.xml_expr.evaluate(environment)
        attr_name = self.attr_name.evaluate(environment)
        # rm specified attribute
        if attr_name in xml["attributes"]:
            del xml["attributes"][attr_name]
        return xml

    def arguments(self):
        return [self.xml_expr, self.attr_name]
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Combine extensions of arguments
        return [
            RemoveAttribute(xml, attr_name)
            for xml in self.xml_expr.extension()
            for attr_name in self.attr_name.extension()
        ]
    
    def minimum_cost_member_of_extension(self):
        return RemoveAttribute(
            self.xml_expr.minimum_cost_member_of_extension(),
            self.attr_name.minimum_cost_member_of_extension(),
        )

class RemoveTag(Expression):
    return_type = "xml"
    argument_types = ["xml"]

    def __init__(self, xml_expr):
        self.xml_expr = xml_expr

    def __str__(self):
        return f"RemoveTag({self.xml_expr})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        # rm tag by setting it to None
        xml["tag"] = None
        return xml

    def arguments(self):
        return [self.xml_expr]
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Generate all possible extensions for the XML expression
        return [RemoveTag(xml) for xml in self.xml_expr.extension()]
    
    def minimum_cost_member_of_extension(self):
        return RemoveTag(
            self.xml_expr.minimum_cost_member_of_extension()
        )

class RemoveChild(Expression):
    return_type = "xml"
    argument_types = ["xml"]

    def __init__(self, xml_expr):
        self.xml_expr = xml_expr

    def __str__(self):
        return f"RemoveChild({self.xml_expr})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        # rm child by setting it to None
        xml["children"] = None
        return xml

    def arguments(self):
        return [self.xml_expr]
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Generate all possible extensions for the XML expression
        return [RemoveChild(xml) for xml in self.xml_expr.extension()]
    
    def minimum_cost_member_of_extension(self):
        min_xml_expr = self.xml_expr.minimum_cost_member_of_extension()
        return RemoveChild(min_xml_expr)

class RemoveText(Expression):
    return_type = "xml"
    argument_types = ["xml"]

    def __init__(self, xml_expr):
        self.xml_expr = xml_expr

    def __str__(self):
        return f"RemoveText({self.xml_expr})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        # rm text by setting it to None
        xml["text"] = None
        return xml

    def arguments(self):
        return [self.xml_expr]
    
    def version_space_size(self):
        return prod(arg.version_space_size() for arg in self.arguments())
    
    def extension(self):
        # Generate all possible extensions for the XML expression
        return [RemoveText(xml) for xml in self.xml_expr.extension()]
    
    def minimum_cost_member_of_extension(self):
        min_xml_expr = self.xml_expr.minimum_cost_member_of_extension()
        return RemoveText(min_xml_expr)
    
class Union(Expression):
    def __init__(self, members):
        self.members = members

    def __str__(self):
        return 'Union(' + ', '.join([str(m) for m in self.members]) + ')'

    def pretty_print(self):
        return 'Union(' + ', '.join([m.pretty_print() for m in self.members]) + ')'

    def extension(self):
        return [
            expression
            for member in self.members
            for expression in member.extension()
        ]

    def evaluate(self, environment):
        assert False, "cannot evaluate union"

    @staticmethod
    def make(members):
        """
        Helper function for building unions.
        Flattens nested unions, ensures members are valid `Expression` instances,
        and prevents singleton unions.
        """
        flat_members = [
            member
            for m in members
            for member in (m.members if isinstance(m, Union) else [m])
            if isinstance(member, Expression)  # Include only valid Expressions
        ]
        if len(flat_members) == 1:
            return flat_members[0]
        return Union(flat_members)

    def minimum_cost_member_of_extension(self):
        # Prioritize transformations based on cost and structural changes
        return min(
            [member.minimum_cost_member_of_extension() for member in self.members],
            key=lambda expression: (expression.cost(), self._structural_change_priority(expression))
        )

    def _structural_change_priority(self, expression):
        # Assign higher priority to structural changes like SetChild over RemoveAttribute
        if isinstance(expression, SetChild):
            return 0
        if isinstance(expression, SetAttribute) or isinstance(expression, RemoveAttribute):
            return 1
        return 2


    def version_space_size(self):
        return sum(member.version_space_size() for member in self.members)

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

def dsl_to_pretty_string(xml, indent=0):
    """
    Converts an XMLTag to a prettified XML-like string for readable output with proper indentation.
    """
    spacing = " " * indent
    if xml is None:
        return f"{spacing}<none/>"

    attributes = " ".join([f'{key.content}="{value.content}"' for key, value in (xml.attributes or [])])
    tag = xml.tag.content if xml.tag else "none"
    text = xml.text.content if xml.text else ""
    child = dsl_to_pretty_string(xml.child, indent + 4) if xml.child else ""
    
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