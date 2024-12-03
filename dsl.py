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

    def __init__(self, tag, attributes, text, children):
        self.tag = tag  # ConstantString
        self.attributes = attributes  # List of (ConstantString, ConstantString)
        self.text = text  # ConstantString or None
        self.children = children  # List of XMLTag or None

    def __str__(self):
        attributes = f"[{', '.join(map(str, self.attributes))}]" if self.attributes else "none"
        text = str(self.text) if self.text else "none"
        children = f"[{', '.join(map(str, self.children))}]" if self.children else "none"
        return f"XMLTag({self.tag}, {attributes}, {text}, {children})"
    
    def evaluate(self, environment):
        tag = self.tag.evaluate(environment)
        attributes = {
                    k.evaluate(environment): v.evaluate(environment)
                    for k, v in (self.attributes or [])
                    if k.evaluate(environment) is not None
                }
        text = self.text.evaluate(environment) if self.text else None
        children = [child.evaluate(environment) for child in self.children or []]
        return {
            "tag": tag,
            "attributes": attributes,
            "text": text,
            "children": children
        }

    def arguments(self):
        args = [self.tag] + (self.attributes or []) + ([self.text] if self.text else []) + (self.children or [])
        return args

class ExtractAttribute(Expression):
    return_type = "str"
    argument_types = ["xml", "str"]

    def __init__(self, xml_expr, attr_name):
        self.xml_expr = xml_expr
        self.attr_name = attr_name

    def __str__(self):
        return f"ExtractAttribute({self.xml_expr}, {self.attr_name})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        attr_name = self.attr_name.evaluate(environment)
        return xml["attributes"].get(attr_name, None)

    def arguments(self):
        return [self.xml_expr, self.attr_name]

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
    argument_types = ["xml", "str"]

    def __init__(self, xml_expr, child_tag):
        self.xml_expr = xml_expr
        self.child_tag = child_tag

    def __str__(self):
        return f"ExtractChild({self.xml_expr}, {self.child_tag})"

    def evaluate(self, environment):
        xml = self.xml_expr.evaluate(environment)
        child_tag = self.child_tag.evaluate(environment)
        for child in xml["children"]:
            if child["tag"] == child_tag:
                return child
        return None

    def arguments(self):
        return [self.xml_expr, self.child_tag]

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
        xml["children"] = [child for child in xml["children"] if child["tag"] != child_tag] + [child_value]
        return xml

    def arguments(self):
        return [self.xml_expr, self.child_tag, self.child_value]
    
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

if __name__ == "__main__":
    test_evaluation(verbose=True)