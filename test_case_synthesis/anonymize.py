import re
from random_word import RandomWords
import uuid

# Initialize the RandomWords object
r = RandomWords()

def generate_unique_name():
    """Generate a unique name using random English words."""
    return r.get_random_word() + "_" + r.get_random_word()

def generate_unique_body():
    """Generate a unique body text using random English words."""
    return f"This is body {r.get_random_word()} {uuid.uuid4().hex[:8]}."

def anonymize_xml(input_file, output_file):
    # Read the entire XML file as a string
    with open(input_file, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    # Use regex to replace names in attributes
    xml_content = re.sub(r'(?<=name=")([^"]+)(?=")', lambda x: generate_unique_name(), xml_content)

    # Use regex to replace body content
    xml_content = re.sub(r'(<body>)(.*?)(</body>)', lambda x: f"{x.group(1)}{generate_unique_body()}{x.group(3)}", xml_content, flags=re.DOTALL)

    # Write the modified XML to the output file
    with open(output_file, 'w', encoding='utf-8-sig') as file:  # BOM handling is required to prevent MagicDraw byte exception upon load
        file.write(xml_content)

# Example usage
input_file = 'input.efx'  # Replace with your input file path
output_file = 'anonymized_input.efx'  # Replace with your desired output file path
anonymize_xml(input_file, output_file)

print(f"Anonymization complete. Output saved to {output_file}.")