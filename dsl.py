import xml.etree.ElementTree as ET
import html

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
        assert False, "implement as part of homework"

    def version_space_size(self):
        assert False, "implement as part of homework"


class FALSE(Expression):
    return_type = "bool"
    argument_types = []
    
    def __init__(self): pass

    def __str__(self):
        return "False"

    def pretty_print(self):
        return "False"
    
    def evaluate(self, environment):
        return False
    
class Number(Expression):
    return_type = "int"
    argument_types = []
    
    def __init__(self, n):
        self.n = n

    def __str__(self):
        return f"Number({self.n})"

    def pretty_print(self):
        return str(self.n)

    def evaluate(self, environment):
        return self.n
    
    # for part4
    def extension(self):
        return [self]

    def version_space_size(self):
        return 1

    def minimum_cost_member_of_extension(self):
        return self
    
    def arguments(self):
        return []
    
    def cost(self):
        if self.n < 0:
            return 0.1 # extremely low cost for negative indices
        else:
            return 1 + self.n # pos nums have a cost proportional to their distance from 0

class NumberVariable(Expression):
    return_type = "int"
    argument_types = []
    
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"NumberVariable('{self.name}')"

    def pretty_print(self):
        return self.name

    def evaluate(self, environment):
        return environment[self.name]

class Plus(Expression):
    return_type = "int"
    argument_types = ["int","int"]
    
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return f"Plus({self.x}, {self.y})"

    def pretty_print(self):
        return f"(+ {self.x.pretty_print()} {self.y.pretty_print()})"

    def evaluate(self, environment):
        x = self.x.evaluate(environment)
        y = self.y.evaluate(environment)
        assert isinstance(x, int) and isinstance(y, int)
        return x + y

class Times(Expression):
    return_type = "int"
    argument_types = ["int","int"]
    
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return f"Times({self.x}, {self.y})"

    def pretty_print(self):
        return f"(* {self.x.pretty_print()} {self.y.pretty_print()})"
    
    def evaluate(self, environment):
        x = self.x.evaluate(environment)
        y = self.y.evaluate(environment)
        assert isinstance(x, int) and isinstance(y, int)
        return x * y

class LessThan(Expression):
    return_type = "bool"
    argument_types = ["int","int"]
    
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return f"LessThan({self.x}, {self.y})"

    def pretty_print(self):
        return f"(< {self.x.pretty_print()} {self.y.pretty_print()})"
    
    def evaluate(self, environment):
        x = self.x.evaluate(environment)
        y = self.y.evaluate(environment)
        assert isinstance(x, int) and isinstance(y, int)
        return x < y

class And(Expression):
    return_type = "bool"
    argument_types = ["bool","bool"]
    
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return f"And({self.x}, {self.y})"

    def pretty_print(self):
        return f"(and {self.x.pretty_print()} {self.y.pretty_print()})"
    
    def evaluate(self, environment):
        x = self.x.evaluate(environment)
        y = self.y.evaluate(environment)
        assert isinstance(x, bool) and isinstance(y, bool)
        return x and y

class Not(Expression):
    return_type = "bool"
    argument_types = ["bool"]
    
    def __init__(self, x):
        self.x = x

    def __str__(self):
        return f"Not({self.x})"

    def pretty_print(self):
        return f"(not {self.x.pretty_print()})"
    
    def evaluate(self, environment):
        x = self.x.evaluate(environment)
        assert isinstance(x, bool)
        return not x

class If(Expression):
    return_type = "int"
    argument_types = ["bool","int","int"]
    
    def __init__(self, test, yes, no):
        self.test, self.yes, self.no = test, yes, no

    def __str__(self):
        return f"If({self.test}, {self.yes}, {self.no})"

    def pretty_print(self):
        return f"(if {self.test.pretty_print()} {self.yes.pretty_print()} {self.no.pretty_print()})"

    def evaluate(self, environment):
        test_result = self.test.evaluate(environment)
        assert isinstance(test_result, bool)
        if test_result:
            return self.yes.evaluate(environment)
        else:
            return self.no.evaluate(environment)
        
class Concatenate(Expression):
    return_type = "str"
    argument_types = ["str", "str"]
    
    def __init__(self, left, right):
        self.left, self.right = left, right

    def __str__(self):
        return f"Concatenate({self.left}, {self.right})"

    def pretty_print(self):
        return f'{self.left.pretty_print()} + {self.right.pretty_print()}'
    
    def extension(self):
        return [Concatenate(left, right)
                for left in self.left.extension()
                for right in self.right.extension() ]

    def arguments(self):
        return [self.left, self.right]
    
    def evaluate(self, environment):
        left_string = self.left.evaluate(environment)
        right_string = self.right.evaluate(environment)
        assert isinstance(left_string, str) and isinstance(right_string, str)
        return left_string + right_string
    
    def version_space_size(self):
        return self.left.version_space_size() * self.right.version_space_size()

    def minimum_cost_member_of_extension(self):
        return Concatenate(
            self.left.minimum_cost_member_of_extension(),
            self.right.minimum_cost_member_of_extension()
        )

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

class Substring(Expression):
    return_type = "str"
    argument_types = ["str", "int", "int"]
    
    def __init__(self, the_string, left, right):
        self.the_string, self.left, self.right = the_string, left, right

    def __str__(self):
        return f'Substring({self.the_string}, {self.left}, {self.right})'

    def pretty_print(self):
        return f'Substring({self.the_string.pretty_print()}, {self.left.pretty_print()}, {self.right.pretty_print()})'

    def evaluate(self, environment):
        """
        Slightly different semantics from ordinary python list slicing:
        We think of the indices as referring to characters in the string, rather than referring to places in between characters
        The extracted substring is the span between the start and end indices, **inclusive** (so it includes the ending index)
        This causes the start and end indices to be treated symmetrically - specifically both `the_string[left]` and `the_string[right]` will be in the output
        If an index is negative, we make it positive by calculating `len(the_string) + the_index`
        As a consequence, `Substring(string, 0, -1)` gives the entire string.
        """
        the_string = self.the_string.evaluate(environment)
        left = self.left.evaluate(environment)
        right = self.right.evaluate(environment)

        # if the index = -1, that refers to the last character
        if left < 0: left = len(the_string) + left
        if right < 0: right = len(the_string) + right
        
        return the_string[left : right + 1]

    def extension(self):
        return [Substring(s,l,r)
                for s in self.the_string.extension()
                for l in self.left.extension()
                for r in self.right.extension() ]

    def arguments(self):
        return [self.the_string, self.left, self.right]
    
    def version_space_size(self):
        return self.the_string.version_space_size() * self.left.version_space_size() * self.right.version_space_size()

    def minimum_cost_member_of_extension(self):
        # min cost member is a substring where the string, left index, and right index are the min cost members of their respective extensions
        return Substring(
            self.the_string.minimum_cost_member_of_extension(),
            self.left.minimum_cost_member_of_extension(),
            self.right.minimum_cost_member_of_extension()
        )

class StringVariable(Expression):
    return_type = "str"
    argument_types = []
    
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"StringVariable('{self.name}')"

    def pretty_print(self):
        return self.name
    
    def extension(self):
        return [self]

    def version_space_size(self): 
        return 1

    def arguments(self):
        return []
    
    def evaluate(self, environment):
        return environment[self.name]
    
    def version_space_size(self):
        return 1

    def minimum_cost_member_of_extension(self):
        return self

class Union(Expression):
    def __init__(self, members):
        self.members = members

    def __str__(self):
        return 'Union(' + ', '.join([str(m) for m in self.members ]) + ')'

    def pretty_print(self):
        return 'Union(' + ', '.join([m.pretty_print() for m in self.members ]) + ')'

    def extension(self):
        return [ expression
                 for member in self.members
                 for expression in member.extension() ]

    def evaluate(self, environment):
        assert False, "cannot evaluate union"

    @staticmethod
    def make(members):
        """
        Helper function for building unions
        Flattens nested unions, and prevents the creation of singleton unions
        """
        members = [ expression
                    for member in members
                    for expression in (member.members if isinstance(member, Union) else [member]) ]
        if len(members) == 1: return members[0]
        return Union(members)

    def minimum_cost_member_of_extension(self):
        return min([ member.minimum_cost_member_of_extension() for member in self.members ],
                   key=lambda expression: expression.cost())

    def version_space_size(self):
        return sum( member.version_space_size() for member in self.members )
    
class XMLTag(Expression):
    return_type = "ET"
    argument_types = []

    def __init__(self, name, attributes=None, children=None):
        self.name = name
        self.attributes = attributes or {}
        self.children = children or []

    def __str__(self):
        return f'XMLTag("{self.name}", {self.attributes}, {self.children})'

    def pretty_print(self):
        attributes_str = " ".join(f'{key}="{value.pretty_print()}"' for key, value in self.attributes.items())
        children_str = "".join(child.pretty_print() for child in self.children)
        return f'<{self.name} {attributes_str}>{children_str}</{self.name}>'

    def evaluate(self, environment):
        """
        Convert to an ET.Element.
        """
        element = ET.Element(
            self.name,
            {key: value.evaluate(environment) for key, value in self.attributes.items()}
        )
        for child in self.children:
            child_result = child.evaluate(environment)
            if child_result.tag == "content":  # Special handling for text content
                element.text = child_result.text
            else:
                element.append(child_result)
        return element


class XMLAttribute(Expression):
    return_type = "str"
    argument_types = []

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return f'XMLAttribute("{self.key}", {self.value})'

    def pretty_print(self):
        return f'{self.key}="{self.value.pretty_print()}"'

    def evaluate(self, environment):
        """
        Return the attribute value as a string.
        """
        return self.value.evaluate(environment)


class XMLContent(Expression):
    return_type = "ET"
    argument_types = []

    def __init__(self, content):
        self.content = content

    def __str__(self):
        return f'XMLContent("{self.content}")'

    def pretty_print(self):
        return self.content

    def evaluate(self, environment):
        """
        Wrap the content in an ET.Element with text.
        """
        # Create a placeholder element to hold the text content
        element = ET.Element("content")  # Tag "content" is arbitrary; it's a wrapper
        element.text = self.content
        return element

    def version_space_size(self):
        return 1
    
    def extension(self):
        return [self]
    
    def minimum_cost_member_of_extension(self):
        return self
    
    def arguments(self):
        return []

def parse_xml_to_dsl(xml_string):
    """
    Parses an XML string into a DSL representation using XMLTag, XMLAttribute, and XMLContent.
    Handles namespaces by stripping them.
    """
    def strip_namespace(element):
        """Remove namespaces from the tags."""
        if '}' in element.tag:
            element.tag = element.tag.split('}', 1)[1]  # strip namespace
        for key in list(element.attrib.keys()):
            if '}' in key:
                new_key = key.split('}', 1)[1]  # strip namespace from attribute keys
                element.attrib[new_key] = element.attrib.pop(key)
        for child in element:
            strip_namespace(child)

    def parse_element(element):
        """Recursively parse the XML element into DSL components."""
        tag_name = element.tag
        attributes = {key: ConstantString(value) for key, value in element.attrib.items()}
        children = []

        # parse child elements and text content
        for child in element:
            children.append(parse_element(child))
        if element.text and element.text.strip():
            children.append(XMLContent(element.text.strip()))

        return XMLTag(tag_name, attributes=attributes, children=children)
    try:
        # parse the XML string
        root = ET.fromstring(xml_string)
        # clean namespaces
        strip_namespace(root)
        # convert to DSL
        return parse_element(root)
    except ET.ParseError as e:
        print("Debug: Invalid XML input")
        raise ValueError(f"Error parsing XML: {e}")

def test_xml_evaluation(verbose=False):
    expressions, ground_truth = [], []

    # Test case 1: Basic XMLTag with attributes and no children
    input = '<example id="1" type="test"/>'
    expressions.append(parse_xml_to_dsl(input))
    def ground_truth1():
        root = ET.Element("example", {"id": "1", "type": "test"})
        return root
    ground_truth.append(ground_truth1)

    # Test case 2: Nested XMLTag with attributes and children
    input = '<parent id="1"><child key="value">Content of child</child></parent>'
    expressions.append(parse_xml_to_dsl(input))
    def ground_truth2():
        parent = ET.Element("parent", {"id": "1"})
        child = ET.SubElement(parent, "child", {"key": "value"})
        child.text = "Content of child"
        return parent
    ground_truth.append(ground_truth2)

    # Test case 3: XMLContent wrapped in ET.Element
    input = 'Some text'
    expressions.append(XMLContent(input))  
    def ground_truth3():
        # Wrap the text in an ET.Element with a placeholder tag
        content = ET.Element("content")
        content.text = "Some text"
        return content
    ground_truth.append(ground_truth3)

    # Test case 4: More complex nested structure
    input = '''
        <root root_attr="root_value">
            <level1>
                <level2 level2_attr="level2_value"></level2>
            </level1>
        </root>
    '''
    expressions.append(parse_xml_to_dsl(input))
    def ground_truth4():
        root = ET.Element("root", {"root_attr": "root_value"})
        level1 = ET.SubElement(root, "level1")
        ET.SubElement(level1, "level2", {"level2_attr": "level2_value"})
        return root
    ground_truth.append(ground_truth4)

    # Evaluate
    all_correct = True
    for i, (expression, ground_truth_fn) in enumerate(zip(expressions, ground_truth)):
        expected = ground_truth_fn()
        result = expression.evaluate({})
        if isinstance(result, ET.Element):
            # Compare ET.Elements using string serialization
            result_str = ET.tostring(result, encoding='unicode')
            expected_str = ET.tostring(expected, encoding='unicode')
            this_correct = result_str == expected_str
        else:
            # For XMLContent and other simple cases
            this_correct = result == expected

        if not this_correct:
            all_correct = False
            if verbose:
                print(f"Test case {i+1} failed:")
                print(f"Expected: {ET.tostring(expected, encoding='unicode') if isinstance(expected, ET.Element) else expected}")
                print(f"Got: {ET.tostring(result, encoding='unicode') if isinstance(result, ET.Element) else result}")

    if all_correct:
        print("[+] All XML evaluation test cases passed!")
    else:
        print("[-] Some test cases failed.")

if __name__ == "__main__":
    test_xml_evaluation(verbose=True)


