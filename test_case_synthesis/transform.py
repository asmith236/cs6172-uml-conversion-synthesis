import os
import traceback
import re
from xml.dom import minidom
from lxml import etree as ET # used over xml.etree.ElementTree due to iterancestor support
import uuid

# this script converts the analysis class contents stored at architecture_model/analysis_classes/* to Eclipse UML2.0 XMI format for manipulation in MagicDraw
# the output .uml file is stored at automation/output/analysis_classes/analysis_classes.uml
# to run this script, navigate to the root of this git repo, and type 'python automation/analysis_classes.py'

RED = "\033[91m" # ansi text escape codes for logging
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def generate_custom_uuid():
    # generate uuid
    raw_uuid = uuid.uuid4()
    # convert the UUID to a string and remove hyphens
    uuid_str = str(raw_uuid).replace('-', '')
    # take the first 22 characters and add a prefix '_'
    custom_uuid = '_' + uuid_str[:22]
    return custom_uuid

class EclipseUMLAnalysisClassGenerator:
    def __init__(self, filename, namespaces):
        self.root = ET.Element("{xmi}XMI", attrib={
            "{xmi}version": "2.1"
        }, nsmap=namespaces)

        # model init
        self.model = ET.SubElement(self.root, "{uml}Model", attrib={
            "{xmi}id": "eee_1045467100313_135436_1",
            "name": "Model"
        })

        # model imports
        self.prim_import = ET.SubElement(self.model, "packageImport", attrib={
            "{xmi}id": "_0primitiveTypesMsodel"
        })
        ET.SubElement(self.prim_import, "importedPackage", attrib={
            "{xmi}type": "uml:Model",
            "href": "pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#_0"
        })

        self.java_import = ET.SubElement(self.model, "packageImport", attrib={
            "{xmi}id": "_0javaPrimitiveTypesModel",
        })
        ET.SubElement(self.java_import, "importedPackage", attrib={
            "{xmi}type": "uml:Model",
            "href" : "pathmap://UML_LIBRARIES/JavaPrimitiveTypes.library.uml#_0"
        })

        # uml standard profile auxiliary resource
        ET.SubElement(self.root, "{MagicDrawProfile}auxiliaryResource", attrib={
            "{xmi}id": "_1CH6wRoqEe-oY8ZQluKI2Q",
            "base_element": "magicdraw_uml_standard_profile_v_0001"
        })

        # init dir for analysis classes
        self.analysis_classes = ET.SubElement(self.model, "packagedElement", attrib={
                "{xmi}type": "uml:Package",
                "{xmi}id" : "_383AC7D3023A3A716F100C4",
                "name" : "Analysis Classes",
                "visibility" : "public"
        })

        # create element to store OA and OD classes for type references
        self.imported_elem = ET.SubElement(self.model, "packagedElement", attrib={
                "{xmi}type": "uml:Package",
                "{xmi}id" : "_383AC7D3023A3A79E6F100C4",
                "name" : "Imported Elements",
                "visibility" : "public"
        })
        self.oa_elem = ET.SubElement(self.imported_elem, "packagedElement", attrib={
                "{xmi}type": "uml:Class",
                "{xmi}id" : "_383AC7D3023A3A79E6F100C5",
                "name" : "OA",
                "visibility" : "public"
        })
        self.od_elem = ET.SubElement(self.imported_elem, "packagedElement", attrib={
                "{xmi}type": "uml:Class",
                "{xmi}id" : "_383AC7D3023A3A79E6F100C6",
                "name" : "OD",
                "visibility" : "public"
        })
        self.unknown_elem = ET.SubElement(self.imported_elem, "packagedElement", attrib={
                "{xmi}type": "uml:Class",
                "{xmi}id" : "_383AC7D3023A3A79E6F100C7",
                "name" : "Unknown Element",
                "visibility" : "public"
        })

        self.current_out_pkg = None
        self.current_efx_namespaces = None
        self.current_efx_pkg = None

        self.add_analysis_class(f'{filename}') 
        
    def add_class(self, efx_elem, out_ancestor_elem):
        try:
            attribs = {
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : efx_elem.attrib["name"],
                "visibility" : "public"
            }
            # add isAbstract, visibility, clientDependency attribs to packagedElement only if they exist
            if "isAbstract" in efx_elem.attrib:
                    attribs["isAbstract"] = efx_elem.attrib["isAbstract"]
            if "visibility" in efx_elem.attrib:
                attribs["visibility"] = efx_elem.attrib["visibility"]
            if "clientDependency" in efx_elem.attrib:
                attribs["clientDependency"] = efx_elem.attrib["clientDependency"]
            
            out_elem = ET.SubElement(out_ancestor_elem, "packagedElement", attrib=attribs)

            # handle ownedComment subelements
            self.handle_ownedComment_subelements(efx_elem, out_elem)

            # handle ownedAttribute subelements 
            for efx_ownedAttrib in efx_elem.findall('ownedAttribute', self.current_efx_namespaces):
                attribs = {
                    "{xmi}id" : efx_ownedAttrib.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "visibility" : "public"
                }
                # add name, visibility, isUnique attribs only if they exist
                if "name" in efx_ownedAttrib.attrib:
                    attribs["name"] = efx_ownedAttrib.attrib["name"]
                if "visibility" in efx_ownedAttrib.attrib:
                    attribs["visibility"] = efx_ownedAttrib.attrib["visibility"]
                if "isUnique" in efx_ownedAttrib.attrib:
                    attribs["isUnique"] = efx_ownedAttrib.attrib["isUnique"]
                if "aggregation" in efx_ownedAttrib.attrib:
                    attribs["aggregation"] = efx_ownedAttrib.attrib["aggregation"]
                    
                # handle type attrib or tag of ownedAttribute
                primitive_type_attribs = None
                type_elem = efx_ownedAttrib.find("type", self.current_efx_namespaces)
                if type_elem is not None: # type id is from another file
                    if type_elem.attrib["href"].startswith("..") is True: # stored in another file
                        if efx_ownedAttrib.attrib["name"].lower().endswith(" tod") or efx_ownedAttrib.attrib["name"].lower().endswith(" od") or efx_ownedAttrib.attrib["name"].lower().endswith(" hod"): # is type od
                            attribs["type"] = self.od_elem.attrib["{xmi}id"] # assign to temp od class
                        elif efx_ownedAttrib.attrib["name"].lower().endswith(" oa"): # is type oa
                            attribs["type"] = self.oa_elem.attrib["{xmi}id"] # assign to temp oa class
                    elif type_elem.attrib["href"].startswith("pathmap") is True: # parse and add primitive type value
                        if type_elem.attrib["href"].startswith("pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#") is True:
                            # type is UMLPrimitiveType
                            prim_type = re.search(r'#([^/?]+)', type_elem.attrib["href"]).group(1)
                        else:
                            # primitive type is a rational rose data type and needs to be extracted
                            prim_type = re.search(r'/([^/^#]+)\?', type_elem.attrib["href"]).group(1)
                        if prim_type == "int":
                            prim_type = "Integer"
                        elif prim_type == "bool":
                            prim_type = "Boolean"
                        href = f'pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#{prim_type}'
                        if prim_type == "float":
                            href = f'pathmap://UML_LIBRARIES/JavaPrimitiveTypes.library.uml#{prim_type}'
                        primitive_type_attribs = { 
                            "{xmi}type" : "uml:PrimitiveType",
                            "href" : href
                        }
                    else: # parse id from href
                        attribs["type"] = re.search(r'#([a-zA-Z0-9_-]+)\?', type_elem.attrib["href"]).group(1)
                elif "type" in efx_ownedAttrib.attrib: # type id is in file
                    attribs["type"] = efx_ownedAttrib.attrib["type"]

                # handle association attrib/tag of ownedAttribute
                association_elem = efx_ownedAttrib.find("association", self.current_efx_namespaces)
                if association_elem is not None: # association id is from another file
                    if association_elem.attrib["href"].startswith("..") is False:
                        attribs["association"] = re.search(r'#([a-zA-Z0-9_-]+)\?', association_elem.attrib["href"]).group(1)
                elif "association" in efx_ownedAttrib.attrib: # association id is in file
                    attribs["association"] = efx_ownedAttrib.attrib["association"]
                
                # assign unknown type if ownedAttribute has an association but no type attrib (or else association will not import)
                if "association" in attribs and "type" not in attribs: 
                    attribs["type"] = self.unknown_elem.attrib["{xmi}id"]

                out_ownedAttrib = ET.SubElement(out_elem, "ownedAttribute", attrib=attribs)

                # handle any ownedComment subelements of ownedAttribute
                self.handle_ownedComment_subelements(efx_ownedAttrib, out_ownedAttrib)

                if primitive_type_attribs is not None:
                    ET.SubElement(out_ownedAttrib, "type", attrib=primitive_type_attribs)

                # handle upperValue and lowerValue subelements of ownedAttrib
                self.handle_upperValue_lowerValue_subelements(efx_ownedAttrib, out_ownedAttrib)

                # handle defaultValue subelement tag if exists
                self.handle_defaultValue_subelement(efx_ownedAttrib, out_ownedAttrib)

            # handle ownedOperation subelements 
            for efx_ownedOp in efx_elem.findall("ownedOperation", self.current_efx_namespaces):
                attribs = {
                    "{xmi}id": efx_ownedOp.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "name": efx_ownedOp.attrib["name"],
                    "visibility" : "public"
                }
                # add visibility attrib only if it exists
                if "visibility" in efx_ownedOp.attrib:
                    attribs["visibility"] = efx_ownedOp.attrib["visibility"]
                out_ownedOp = ET.SubElement(out_elem, "ownedOperation", attrib=attribs)
                # handle any ownedComment subelements of ownedOperation
                efx_ownedOp_ownedCom = efx_ownedOp.find("ownedComment", self.current_efx_namespaces)
                if efx_ownedOp_ownedCom is not None:
                    efx_ownedOp_ownedCom_body = efx_ownedOp_ownedCom.find("body", self.current_efx_namespaces)
                    attribs = {
                        "{xmi}id" : efx_ownedOp_ownedCom.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                        "body" : efx_ownedOp_ownedCom_body.text,
                    }
                    # add annotatedElement attribute if it exists
                    if "annotatedElement" in efx_ownedOp_ownedCom.attrib: 
                        attribs["annotatedElement"] = efx_ownedOp_ownedCom.attrib["annotatedElement"]
                    else: # see if the ownedCom has a subElement tag named annotatedElement and parse
                        efx_ownedOp_ownedCom_annotatedElem = efx_ownedOp_ownedCom.find("ownedComment", self.current_efx_namespaces) 
                        if efx_ownedOp_ownedCom_annotatedElem is not None:
                            efx_ownedOp_ownedCom_annotatedElem_body = efx_ownedOp_ownedCom_annotatedElem.find("body", self.current_efx_namespaces)
                            attribs["annotatedElement"] = efx_ownedOp_ownedCom_annotatedElem_body.text
                    ET.SubElement(out_ownedOp, "ownedComment", attrib=attribs)
                # handle any ownedParameter subelements of ownedOperation
                for efx_ownedOp_ownedParam in efx_ownedOp.findall('ownedParameter', self.current_efx_namespaces):
                    attribs = {
                        "{xmi}id": efx_ownedOp_ownedParam.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                        "visibility": "public",
                        "effect": "create"
                    }
                    # add direction, isUnique, type attribs only if they exist
                    if "direction" in efx_ownedOp_ownedParam.attrib:
                        attribs["direction"] = efx_ownedOp_ownedParam.attrib["direction"]
                    if "isUnique" in efx_ownedOp_ownedParam.attrib:
                        attribs["isUnique"] = efx_ownedOp_ownedParam.attrib["isUnique"]

                    # handle type attrib or tag of ownedAttribute
                    type_elem = efx_ownedOp_ownedParam.find("type", self.current_efx_namespaces)
                    if type_elem is not None: # type id is from another file
                        if type_elem.attrib["href"].startswith("..") is False and type_elem.attrib["href"].startswith("pathmap") is False:
                            attribs["type"] = re.search(r'#([a-zA-Z0-9_-]+)\?', type_elem.attrib["href"]).group(1)
                    elif "type" in efx_ownedOp_ownedParam.attrib: # type id is in file
                        attribs["type"] = efx_ownedOp_ownedParam.attrib["type"]
                    
                    # default ownedParam name to "" if does not exist
                    attribs["name"] = efx_ownedOp_ownedParam.attrib.get("name", "")
                    out_ownedOp_ownedParam = ET.SubElement(out_ownedOp, "ownedParameter", attrib=attribs)
                    # handle any ownedComment subelements of ownedParameter
                    self.handle_ownedComment_subelements(efx_ownedOp_ownedParam, out_ownedOp_ownedParam)
                    # handle defaultvalue subelement tags
                    self.handle_defaultValue_subelement(efx_ownedOp_ownedParam, out_ownedOp_ownedParam)
            # handle interfaceRealization subelements 
            for efx_interReal in efx_elem.findall("interfaceRealization", self.current_efx_namespaces):
                attribs = {
                    "{xmi}id": efx_interReal.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "name": "",
                    "client" : efx_interReal.attrib["client"]
                }
                # handle supplier and contract tags
                realization_is_deprecated = False
                supplier_elem = efx_interReal.find("supplier", self.current_efx_namespaces)
                if "supplier" in efx_interReal.attrib: # supplier id is in file
                    attribs["supplier"] = efx_interReal.attrib["supplier"]
                elif supplier_elem is not None: # supplier id is in another file
                    if supplier_elem.attrib["href"].startswith("..") is False:
                        attribs["supplier"] = re.search(r'#([a-zA-Z0-9_-]+)\?', supplier_elem.attrib["href"]).group(1)
                    else:
                        realization_is_deprecated = True
                else: # no supplier
                    realization_is_deprecated = True

                if "contract" in efx_interReal.attrib: # supplier id is in file
                    attribs["contract"] = efx_interReal.attrib["contract"]
                else: # supplier id is in another file
                    contract_elem = efx_interReal.find("contract", self.current_efx_namespaces)
                    if contract_elem.attrib["href"].startswith("..") is False:
                        attribs["contract"] = re.search(r'#([a-zA-Z0-9_-]+)\?', contract_elem.attrib["href"]).group(1)
                if realization_is_deprecated is False:
                    ET.SubElement(out_elem, "interfaceRealization", attrib=attribs)
            # handle generalization subelements 
            for efx_general in efx_elem.findall("generalization", self.current_efx_namespaces):
                attribs = {
                    "{xmi}id": efx_general.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "isSubstitutable": "true",
                }
                # handle general attrib/tag
                if "general" in efx_general.attrib: # general id is in file
                    attribs["general"] = efx_general.attrib["general"]
                else: # general id is in another file
                    general_elem = efx_general.find("general", self.current_efx_namespaces)
                    if general_elem.attrib["href"].startswith("..") is False: # is never True
                        attribs["general"] = re.search(r'#([a-zA-Z0-9_-]+)\?', general_elem.attrib["href"]).group(1)
                ET.SubElement(out_elem, "generalization", attrib=attribs)
            # TODO handle templateBinding, ownedTemplateSignature dependency tags?
            # ignores subelements ownedTemplateSignature, nestedClassifier...
        except Exception as e:
            print(f'{RED}error in add_class for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())
    
    def handle_ownedComment_subelements(self, efx_elem, out_elem):
        # handle ownedComment subelements
        for efx_ownedCom in efx_elem.findall("ownedComment", self.current_efx_namespaces):
            efx_ownedCom_body = efx_ownedCom.find("body", self.current_efx_namespaces)
            ET.SubElement(out_elem, "ownedComment", attrib={
                "{xmi}id" : efx_ownedCom.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "body" : efx_ownedCom_body.text,
                "annotatedElement" : efx_ownedCom.attrib["annotatedElement"]
            })

    def handle_defaultValue_subelement(self, efx_elem, out_elem):
        # handle defaultValue subelement tag if exists
        efx_defaultValue = efx_elem.find("defaultValue", self.current_efx_namespaces)
        if efx_defaultValue is not None: 
            efx_defaultVal_type = efx_defaultValue.find("type", self.current_efx_namespaces)
            efx_defaultValue_body = efx_defaultValue.find("body", self.current_efx_namespaces)
            attribs = {
                "{xmi}id" : efx_defaultValue.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
            }
            if efx_defaultValue_body.text == "null": # declare element as uml:LiteralNull type
                attribs["{xmi}type"] = "uml:LiteralNull"
                attribs["{xmi}name"] = ""
                ET.SubElement(out_elem, "defaultValue", attrib=attribs)
            else:
                attribs["{xmi}type"] = efx_defaultValue.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id']
                out_defaultValue = ET.SubElement(out_elem, "defaultValue", attrib=attribs)
                if efx_defaultVal_type is not None: 
                    # add the default value type tag
                    ET.SubElement(out_defaultValue, "type", attrib={
                        "{xmi}type" : efx_defaultVal_type.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                        "href" : efx_defaultVal_type.attrib["href"]
                    })
                    # append the value itself
                    efx_defaultValue_body = efx_defaultValue.find("body", self.current_efx_namespaces)
                    if efx_defaultValue_body is not None:
                        out_body = ET.Element("body")
                        out_body.text = efx_defaultValue_body.text
                        out_defaultValue.append(out_body)
                    else: # do not add default value with no body
                        parent = out_defaultValue.getparent()
                        parent.remove(out_defaultValue)
                        print(f'{YELLOW}removed defaultValue with id {efx_defaultValue.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id']} due to no body tag{RESET}')
                else: # do not add defaultValue since it is NA
                    parent = out_defaultValue.getparent()
                    parent.remove(out_defaultValue)
                    print(f'{YELLOW}removed defaultValue with id {efx_defaultValue.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id']} due to no type tag{RESET}')
            

    def handle_upperValue_lowerValue_subelements(self, efx_elem, out_elem):
        # handle upperValue and lowerValue subelements of ownedAttrib
        efx_upperVal = efx_elem.find("upperValue", self.current_efx_namespaces)
        efx_lowerVal = efx_elem.find("lowerValue", self.current_efx_namespaces)
        if efx_upperVal is not None and efx_lowerVal is not None: 
            upper_attribs = {
                "{xmi}id" : efx_upperVal.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "{xmi}type" : efx_upperVal.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type']
            }
            lower_attribs = {
                "{xmi}id" : efx_lowerVal.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "{xmi}type" : efx_lowerVal.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type']
            }
            if "value" in efx_upperVal.attrib:
                upper_attribs["value"] = efx_upperVal.attrib["value"]
            if "value" in efx_lowerVal.attrib:
                lower_attribs["value"] = efx_lowerVal.attrib["value"]
            ET.SubElement(out_elem, "upperValue", attrib=upper_attribs)
            ET.SubElement(out_elem, "lowerValue", attrib=lower_attribs)
    
    def add_interface(self, efx_elem, out_ancestor_elem):
        try:
            attribs = {
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : efx_elem.attrib["name"]
            }
            out_elem = ET.SubElement(out_ancestor_elem, "packagedElement", attrib=attribs)

            # handle ownedComment subelements
            self.handle_ownedComment_subelements(efx_elem, out_elem)

            # handle ownedAttribute subelements 
            for efx_ownedAttrib in efx_elem.findall('ownedAttribute', self.current_efx_namespaces):
                attribs = {
                    "{xmi}id" : efx_ownedAttrib.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                }
                # add name and visibility attribs only if they exist
                if "name" in efx_ownedAttrib.attrib:
                    attribs["name"] = efx_ownedAttrib.attrib["name"]
                if "visibility" in efx_ownedAttrib.attrib:
                    attribs["visibility"] = efx_ownedAttrib.attrib["visibility"]
                ET.SubElement(out_elem, "ownedAttribute", attrib=attribs)

            # handle ownedOperation subelements 
            for efx_ownedOp in efx_elem.findall("ownedOperation", self.current_efx_namespaces):
                attribs = {
                    "{xmi}id": efx_ownedOp.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "name": efx_ownedOp.attrib["name"]
                }
                # add visibility attrib only if it exists
                if "visibility" in efx_ownedOp.attrib:
                    attribs["visibility"] = efx_ownedOp.attrib["visibility"]
                out_ownedOp = ET.SubElement(out_elem, "ownedOperation", attrib=attribs)
                # handle any ownedComment subelements of ownedOperation
                efx_ownedOp_ownedCom = efx_ownedOp.find("ownedComment", self.current_efx_namespaces)
                if efx_ownedOp_ownedCom is not None:
                    efx_ownedOp_ownedCom_body = efx_ownedOp_ownedCom.find("body", self.current_efx_namespaces)
                    attribs = {
                        "{xmi}id" : efx_ownedOp_ownedCom.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                        "body" : efx_ownedOp_ownedCom_body.text,
                    }
                    # add annotatedElement attribute if it exists
                    if "annotatedElement" in efx_ownedOp_ownedCom.attrib: 
                        attribs["annotatedElement"] = efx_ownedOp_ownedCom.attrib["annotatedElement"]
                    else: # see if the ownedCom has a subElement tag named annotatedElement and parse
                        efx_ownedOp_ownedCom_annotatedElem = efx_ownedOp_ownedCom.find("ownedComment", self.current_efx_namespaces)
                        if efx_ownedOp_ownedCom_annotatedElem is not None:
                            efx_ownedOp_ownedCom_annotatedElem_body = efx_ownedOp_ownedCom_annotatedElem.find("body", self.current_efx_namespaces)
                            attribs["annotatedElement"] = efx_ownedOp_ownedCom_annotatedElem_body.text
                    ET.SubElement(out_ownedOp, "ownedComment", attrib=attribs)
                # handle any ownedParameter subelements of ownedOperation
                for efx_ownedOp_ownedParam in efx_ownedOp.findall('ownedParameter', self.current_efx_namespaces):
                    attribs = {
                        "{xmi}id": efx_ownedOp_ownedParam.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                        "visibility": "public",
                        "effect": "create"
                    }
                    # add direction and attribs only if they exist
                    if "direction" in efx_ownedOp_ownedParam.attrib:
                        attribs["direction"] = efx_ownedOp_ownedParam.attrib["direction"]
                    if "isUnique" in efx_ownedOp_ownedParam.attrib:
                        attribs["isUnique"] = efx_ownedOp_ownedParam.attrib["isUnique"]

                    # handle type attrib or tag of ownedParameter
                    primitive_type_attribs = None
                    type_elem = efx_ownedOp_ownedParam.find("type", self.current_efx_namespaces)
                    if type_elem is not None: # type id is from another file
                        if type_elem.attrib["href"].startswith("pathmap") is True: # parse and add primitive type value
                            if type_elem.attrib["href"].startswith("pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#") is True:
                                # type is UMLPrimitiveType
                                prim_type = re.search(r'#([^/?]+)', type_elem.attrib["href"]).group(1)
                            else:
                                # primitive type is a rr data type and needs to be extracted
                                prim_type = re.search(r'/([^/^#]+)\?', type_elem.attrib["href"]).group(1)
                            if prim_type == "int":
                                prim_type = "Integer"
                            elif prim_type == "bool":
                                prim_type = "Boolean"
                            href = f'pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#{prim_type}'
                            if prim_type == "float":
                                href = f'pathmap://UML_LIBRARIES/JavaPrimitiveTypes.library.uml#{prim_type}'
                            primitive_type_attribs = { 
                                "{xmi}type" : "uml:PrimitiveType",
                                "href" : href
                            }
                        else: # parse id from href
                            attribs["type"] = re.search(r'#([a-zA-Z0-9_-]+)\?', type_elem.attrib["href"]).group(1)
                    elif "type" in efx_ownedOp_ownedParam.attrib: # type id is in file
                        attribs["type"] = efx_ownedOp_ownedParam.attrib["type"]

                    # default ownedParam name to "" if does not exist
                    attribs["name"] = efx_ownedOp_ownedParam.attrib.get("name", "")
                    out_ownedOp_ownedParam = ET.SubElement(out_ownedOp, "ownedParameter", attrib=attribs)
                    self.handle_ownedComment_subelements(efx_ownedOp_ownedParam, out_ownedOp_ownedParam)
                    if primitive_type_attribs is not None:
                        ET.SubElement(out_ownedOp_ownedParam, "type", attrib=primitive_type_attribs)
                    # handle upperValue, lowerValue, defaultValue subelement tags of ownedParam attrib
                    self.handle_upperValue_lowerValue_subelements(efx_ownedOp_ownedParam, out_ownedOp_ownedParam)
                    self.handle_defaultValue_subelement(efx_ownedOp_ownedParam, out_ownedOp_ownedParam)   

            # handle generalization subelements
            for efx_general in efx_elem.findall("generalization", self.current_efx_namespaces):
                attribs = {
                    "{xmi}id": efx_general.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "isSubstitutable": "true",
                }
                # handle general attrib/tags
                if "general" in efx_general.attrib: # general id is in file
                    attribs["general"] = efx_general.attrib["general"]
                else: # general id is in another file
                    general_elem = efx_general.find("general", self.current_efx_namespaces)
                    if general_elem.attrib["href"].startswith("..") is False: # is never True
                        attribs["general"] = re.search(r'#([a-zA-Z0-9_-]+)\?', general_elem.attrib["href"]).group(1)
                ET.SubElement(out_elem, "generalization", attrib=attribs)
        except Exception as e:
            print(f'{RED}error in add_interface for pkg:elem {efx_elem.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())

    def add_association(self, efx_elem, out_ancestor_elem):
        try:
            attribs = {
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id']
            }
            # add name attrib to packagedElement only if they exist
            if "name" in efx_elem.attrib:
                attribs["name"] = efx_elem.attrib["name"]

            # handle memberEnd tags/attribs
            efx_memberEnds = efx_elem.findall("./memberEnd", self.current_efx_namespaces)
            if "memberEnd" in efx_elem.attrib: # memberEnd id is in file 
                attribs["memberEnd"] = efx_elem.attrib["memberEnd"]
            if len(efx_memberEnds) != 0: # memberEnd id is in another file
                memberEnd_list = []
                for memberEnd in efx_memberEnds:
                    # ignore associations that do not come from an analysis class 
                    if memberEnd.attrib["href"].startswith("..") is False:
                        memberEnd_list.append(re.search(r'#([a-zA-Z0-9_-]+)\?', memberEnd.attrib["href"]).group(1))
                    else: # do not add association which references a non-analysis class element (an elem in different dir)
                        return # rely on resolve_dependnecies to remove any references to skipped association value
                attribs["memberEnd"] = " ".join(memberEnd_list)
            if len(attribs["memberEnd"].split()) < 2: # association is deprecated 
                return
        
            out_elem = ET.SubElement(out_ancestor_elem, "packagedElement", attrib=attribs)
                                
            # handle ownedEnd subelement
            efx_ownedEnds = efx_elem.findall("./ownedEnd", self.current_efx_namespaces)
            if efx_ownedEnds is not None:
                if len(efx_ownedEnds) > 1: # association is deprecated if there is more than one owendEnd
                    parent = out_elem.getparent()
                    parent.remove(out_elem)
                    print(f'{YELLOW}removed association with id {out_elem.attrib["{xmi}id"]} due to multiple ownedEnds{RESET}')
                    return
                for efx_ownedEnd in efx_ownedEnds:
                    attribs = {
                        "{xmi}id" : efx_ownedEnd.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                        "visibility" : "public"
                    }

                    # add name, isUnique, visibility and association attribs only if they exist
                    if "name" in efx_ownedEnd.attrib:
                        attribs["name"] = efx_ownedEnd.attrib["name"]
                    if "isUnique" in efx_ownedEnd.attrib:
                        attribs["isUnique"] = efx_ownedEnd.attrib["isUnique"]
                    if "visibility" in efx_ownedEnd.attrib:
                        attribs["visibility"] = efx_ownedEnd.attrib["visibility"]
                    if "association" in efx_ownedEnd.attrib:
                        attribs["association"] = efx_ownedEnd.attrib["association"]

                    # handle any type tags/attribs in ownedEnd
                    type_elem = efx_ownedEnd.find("type", self.current_efx_namespaces)
                    if type_elem is not None: # type id is from another file
                        if type_elem.attrib["href"].startswith("..") is False and type_elem.attrib["href"].startswith("pathmap") is False: 
                            attribs["type"] = re.search(r'#([a-zA-Z0-9_-]+)\?', type_elem.attrib["href"]).group(1)
                        else:
                            parent = out_elem.getparent()
                            parent.remove(out_elem)
                            print(f'{YELLOW}removed association with id {out_elem.attrib["{xmi}id"]} due to deprecated ownedEnd {attribs["{xmi}id"]}{RESET}')
                            return
                    elif "type" in efx_ownedEnd.attrib: # type id is in file
                        attribs["type"] = efx_ownedEnd.attrib["type"]
                    
                    out_ownedEnd = ET.SubElement(out_elem, "ownedEnd", attrib=attribs)

                    # handle upperValue and lowerValue subelements of ownedEnd
                    self.handle_upperValue_lowerValue_subelements(efx_ownedEnd, out_ownedEnd)
            else: # association is deprecated if it has no ownedEnd
                # remove association
                parent = out_elem.getparent()
                parent.remove(out_elem)
                print(f'{YELLOW}removed associaiton with id {attribs["{xmi}id"]} due to no ownedEnd{RESET}')
                return

            # handle ownedComment subelements
            self.handle_ownedComment_subelements(efx_elem, out_elem)
        except Exception as e:
            print(f'{RED}error in add_association for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())

    def add_package(self, efx_elem):
        try:
            if "href" in efx_elem.attrib: # referenced package is from another file
                # ignore package imports that do not come from an analysis class
                if efx_elem.attrib["href"].startswith("..") is False:
                    # convert any package with an href into a package import 
                    attribs = {
                        "importedPackage" : re.search(r'#([a-zA-Z0-9_-]+)\?', efx_elem.attrib["href"]).group(1)
                    }
                    ET.SubElement(self.current_out_pkg, "packageImport", attrib=attribs) 
            else:
                # add attributes to uml:Package element
                attribs = {
                        "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                        "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                        "name" : efx_elem.attrib["name"],
                        "visibility" : "public"
                    }
                out_elem = ET.SubElement(self.current_out_pkg, "packagedElement", attrib=attribs) 

                # handle ownedComment subelements
                self.handle_ownedComment_subelements(efx_elem, out_elem)

                # handle any packagedElement subelements
                efx_packagedElems = efx_elem.findall("./packagedElement", self.current_efx_namespaces)
                for efx_packagedElem in efx_packagedElems:
                    xmi_type = efx_packagedElem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type']                    
                    match xmi_type:
                        # handle any uml:Dependency subelements
                        case "uml:Dependency":
                            self.add_dependency(efx_packagedElem, out_elem)
                        # handle any packagedElement uml:Class subelements
                        case "uml:Class":
                            self.add_class(efx_packagedElem, out_elem)
                        # handle any packagedElement uml:Association subelements
                        case "uml:Association":
                            self.add_association(efx_packagedElem, out_elem)
                        # handle any uml:Interface subelements
                        case "uml:Interface":
                            self.add_interface(efx_packagedElem, out_elem)
                        case _:
                            print(f'{RED}unexpected packagedElement of type {xmi_type}{RESET}')
        except Exception as e:
            print(f'{RED}error in add_package for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())

    def add_association_class(self, efx_elem):
        try:
            attribs = {
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : ""
            }
            # add name attrib to packagedElement only if they exist
            if "name" in efx_elem.attrib:
                    attribs["name"] = efx_elem.attrib["name"]

            # handle memberEnd tag/attribs
            efx_memberEnds = efx_elem.findall("./memberEnd", self.current_efx_namespaces)
            if "memberEnd" in efx_elem.attrib: # memberEnd id is in file 
                attribs["memberEnd"] = efx_elem.attrib["memberEnd"]
            elif len(efx_memberEnds) != 0: # memberEnd id is in another file
                # handle memberEnd subelements
                memberEnd_list = []
                for memberEnd in efx_memberEnds:
                    memberEnd_list.append(re.search(r'#([a-zA-Z0-9_-]+)\?', memberEnd.attrib["href"]).group(1))
                attribs["memberEnd"] = " ".join(memberEnd_list)
            else: # association class is deprecated and should not be created
                return
                
            out_elem = ET.SubElement(self.current_out_pkg, "packagedElement", attrib=attribs)
                                
            # handle ownedEnd subelement
            efx_ownedEnd = efx_elem.find("ownedEnd", self.current_efx_namespaces)
            if efx_ownedEnd is not None:
                attribs = {
                    "{xmi}id" : efx_ownedEnd.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id']
                }
                # add name, isUnique, visibility and association attribs only if they exist
                if "name" in efx_ownedEnd.attrib:
                    attribs["name"] = efx_ownedEnd.attrib["name"]
                if "isUnique" in efx_ownedEnd.attrib:
                    attribs["isUnique"] = efx_ownedEnd.attrib["isUnique"]
                if "visibility" in efx_ownedEnd.attrib:
                    attribs["visibility"] = efx_ownedEnd.attrib["visibility"]
                if "association" in efx_ownedEnd.attrib:
                    attribs["association"] = efx_ownedEnd.attrib["association"]
                # handle any type subelements of ownedEnd
                
                efx_type_elem = efx_ownedEnd.find('type', self.current_efx_namespaces)
                if "type" in efx_ownedEnd.attrib:
                    attribs["type"] = efx_ownedEnd.attrib["type"]
                elif efx_type_elem is not None:
                    # extract id from href
                    attribs["type"] = re.search(r'#([a-zA-Z0-9_-]+)\?', efx_type_elem.attrib["href"]).group(1)
                ET.SubElement(out_elem, "ownedEnd", attrib=attribs)
            else:
                parent = out_elem.getparent()
                parent.remove(out_elem)
                print(f'{YELLOW}removed association class with id {attribs["{xmi}id"]} due to no ownedEnd{RESET}')
        except Exception as e:
            print(f'{RED}error in add_association_class for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())

    def add_enumeration(self, efx_elem):
        try:
            out_elem = ET.SubElement(self.current_out_pkg, "packagedElement", attrib={
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : efx_elem.attrib["name"]
            })

            # handle ownedComment subelement
            self.handle_ownedComment_subelements(efx_elem, out_elem)
                    
            # handle ownedLiteral subelements
            efx_ownedLiterals = efx_elem.findall("./ownedLiteral", self.current_efx_namespaces)
            for efx_ownedLiteral in efx_ownedLiterals:
                attribs = {
                    "{xmi}id" : efx_ownedLiteral.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "name" : efx_ownedLiteral.attrib["name"]
                }
                if "classifier" in efx_ownedLiteral.attrib:
                    attribs["classifier"] = efx_ownedLiteral.attrib["classifier"]
                out_ownedLiteral = ET.SubElement(out_elem, "ownedLiteral", attrib=attribs)
                # handle ownedComment ownedLiteral subelements
                self.handle_ownedComment_subelements(efx_ownedLiteral, out_ownedLiteral)
            
                # handle specification tag of ownedLiteral if exists
                efx_spec = efx_ownedLiteral.find("specification", self.current_efx_namespaces)
                if efx_spec is not None:
                    ET.SubElement(out_ownedLiteral, "specification", attrib={
                        "{xmi}id" : efx_spec.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                        "{xmi}type" : efx_spec.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                        "value" : efx_spec.attrib["value"]
                    })
                    
            # handle ownedAttribute subelement
            efx_ownedAttribs = efx_elem.findall("./ownedAttribute", self.current_efx_namespaces)
            for efx_ownedAttrib in efx_ownedAttribs:
                attribs = {
                    "{xmi}id" : efx_ownedAttrib.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "name" : efx_ownedAttrib.attrib["name"]
                }
                if "visibility" in efx_ownedAttrib.attrib:
                    attribs["visibility"] = efx_ownedAttrib.attrib["visibility"]
                ET.SubElement(out_elem, "ownedAttribute", attrib=attribs)
                    
            # handle ownedOperation subelement
            efx_ownedOperations = efx_elem.findall("./ownedAttribute", self.current_efx_namespaces)
            for efx_ownedOperation in efx_ownedOperations:
                attribs = {
                    "{xmi}id" : efx_ownedOperation.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "name" : efx_ownedOperation.attrib["name"]
                }
                if "visibility" in efx_ownedOperation.attrib:
                    attribs["visibility"] = efx_ownedOperation.attrib["visibility"]
                ET.SubElement(out_elem, "ownedAttribute", attrib=attribs)
        except Exception as e:
            print(f'{RED}error in add_enumeration for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())

    def add_instance_specification(self, efx_elem):
        try:
            ET.SubElement(self.current_out_pkg, "packagedElement", attrib={
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : efx_elem.attrib["name"],
                "classifier" : efx_elem.attrib["classifier"],
                "visibility" : "public"
            })
        except Exception as e:
            print(f'{RED}error in add_instance_specification for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())

    def add_signal(self, efx_elem):
        try:
            attribs = {
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : efx_elem.attrib["name"],
                "visibility" : "public"
            }
            ET.SubElement(self.current_out_pkg, "packagedElement", attrib=attribs)
        except Exception as e:
            print(f'{RED}error in add_signal for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())
    
    def add_collaboration(self, efx_elem):
        try:
            attribs = {
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : efx_elem.attrib["name"]
            }
            ET.SubElement(self.current_out_pkg, "packagedElement", attrib=attribs)
            # TODO handle templateBinding subelement (add singleton value to name)
        except Exception as e:
            print(f'{RED}error in add_collaboration for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())
    
    def add_dependency(self, efx_elem, out_ancestor_elem):
        try:
            # ignore all uml:dependency attributes with an href attrib bc they reference elems that do not exist
            if "href" in efx_elem.attrib:
                return
                    
            attribs = {
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "name" : ""
            }
            
            # handle client attrib or tag
            client_elem = efx_elem.find("client", self.current_efx_namespaces)
            if client_elem is not None: # client id is from another file
                if client_elem.attrib["href"].startswith("..") is False:
                    attribs["client"] = re.search(r'#([a-zA-Z0-9_-]+)\?', client_elem.attrib["href"]).group(1)
                else: # do not add dependency if it does not reference an analysis class
                    return 
            elif "client" in efx_elem.attrib: # client id is in file
                attribs["client"] = efx_elem.attrib["client"]
            else: # dependency error (no client)
                return

            # handle supplier attrib or tag
            supplier_elem = efx_elem.find("supplier", self.current_efx_namespaces)
            if supplier_elem is not None: # client id is from another file
                if supplier_elem.attrib["href"].startswith("..") is False:
                    attribs["supplier"] = re.search(r'#([a-zA-Z0-9_-]+)\?', supplier_elem.attrib["href"]).group(1)
                else:  # do not add dependency if it does not reference an analysis class
                    return
            elif "supplier" in efx_elem.attrib: # client id is in file
                attribs["supplier"] = efx_elem.attrib["supplier"]
            else: # dependency error
                return

            # add xmi:id attrib 
            attribs["{xmi}id"] = efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id']      

            out_elem = ET.SubElement(out_ancestor_elem, "packagedElement", attrib=attribs)

            # handle ownedComment subelements
            self.handle_ownedComment_subelements(efx_elem, out_elem)  
        except Exception as e:
            print(f'{RED}error in add_dependency for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id']}\n{e}{RESET}')
            print(traceback.format_exc())
    
    def add_realization(self, efx_elem):
        try:
            attribs = {
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : ""
            }
            # handle supplier and client tags/attribs
            supplier_elem = efx_elem.find("supplier", self.current_efx_namespaces)
            if "supplier" in efx_elem.attrib: # supplier id is in file
                attribs["supplier"] = efx_elem.attrib["supplier"]
            elif supplier_elem is not None:# supplier id is in another file
                if supplier_elem.attrib["href"].startswith("..") is False:
                    attribs["supplier"] = re.search(r'#([a-zA-Z0-9_-]+)\?', supplier_elem.attrib["href"]).group(1)
                else:  # don't add realization
                    return
            else: # realization error (no supplier)
                return
            client_elem = efx_elem.find("client", self.current_efx_namespaces)
            if "client" in efx_elem.attrib: # client id is in file
                attribs["client"] = efx_elem.attrib["client"]
            elif client_elem is not None: # client id is in another file
                if client_elem.attrib["href"].startswith("..") is False:
                    attribs["client"] = re.search(r'#([a-zA-Z0-9_-]+)\?', client_elem.attrib["href"]).group(1)
                else: # don't add realization
                    return
            else: # realization error (no client)
                return
            ET.SubElement(self.current_out_pkg, "packagedElement", attrib=attribs)
        except Exception as e:
            print(f'{RED}error in add_realization for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())

    def add_usage(self, efx_elem):
        try:
            attribs = {
                "{xmi}type": efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type'],
                "{xmi}id" : efx_elem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : ""
            }
            # handle supplier and client tags/attribs
            supplier_elem = efx_elem.find("supplier", self.current_efx_namespaces)
            if "supplier" in efx_elem.attrib: # supplier id is in file
                attribs["supplier"] = efx_elem.attrib["supplier"]
            elif supplier_elem is not None: # supplier id is in another file
                if supplier_elem.attrib["href"].startswith("..") is False:
                    attribs["supplier"] = re.search(r'#([a-zA-Z0-9_-]+)\?', supplier_elem.attrib["href"]).group(1)
                else: # do not add usage if it references an element that is not an analysis class
                    return
            else: # usage error
                return
            client_elem = efx_elem.find("client", self.current_efx_namespaces)
            if "client" in efx_elem.attrib: # client id is in file
                attribs["client"] = efx_elem.attrib["client"]
            elif client_elem is not None: # client id is in another file
                if client_elem.attrib["href"].startswith("..") is False:
                    attribs["client"] = re.search(r'#([a-zA-Z0-9_-]+)\?', client_elem.attrib["href"]).group(1)
                else: # do not add usage if it references an element that is not an analysis class
                    return
            else: # usage error
                return
            ET.SubElement(self.current_out_pkg, "packagedElement", attrib=attribs)
        except Exception as e:
            print(f'{RED}error in add_usage for pkg:elem {self.current_out_pkg.attrib["name"]}:{efx_elem.attrib["name"]}\n{e}{RESET}')
            print(traceback.format_exc())

    def add_analysis_class(self, efx_filepath):
        try:
            efx_tree = ET.parse(efx_filepath)
            efx_root = efx_tree.getroot()
            
            self.current_efx_namespaces = dict(
                [node for _, node in ET.iterparse(efx_filepath, events=['start-ns'])])

            self.current_efx_pkg = efx_root.find('./uml:Package', self.current_efx_namespaces) # assumes there is only one package per file
            if self.current_efx_pkg is None:
                self.current_efx_pkg = efx_root

            # initialize package
            self.current_out_pkg = ET.SubElement(self.analysis_classes, "packagedElement", attrib={
                "{xmi}type" : "uml:Package",
                "{xmi}id": self.current_efx_pkg.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : self.current_efx_pkg.attrib["name"],
                "visibility" : "public"
            })

            # handle package ownedComment
            efx_pkg_ownedCom = self.current_efx_pkg.find("ownedComment", self.current_efx_namespaces)
            if efx_pkg_ownedCom is not None:
                efx_pkg_ownedCom_body = efx_pkg_ownedCom.find("body", self.current_efx_namespaces)
                ET.SubElement(self.current_out_pkg, "ownedComment", attrib={
                    "{xmi}id" : efx_pkg_ownedCom.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "body" : efx_pkg_ownedCom_body.text,
                    "annotatedElement" : self.current_out_pkg.attrib["{xmi}id"]
                })

            efx_packagedElems = self.current_efx_pkg.findall(
                './packagedElement', self.current_efx_namespaces) 
            
            # handle packagedElements in analysis class
            for efx_packagedElem in efx_packagedElems:
                efx_elem_type = efx_packagedElem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type']
                match efx_elem_type:
                    case "uml:Class": 
                        self.add_class(efx_packagedElem, self.current_out_pkg)
                    case "uml:Interface": 
                        self.add_interface(efx_packagedElem, self.current_out_pkg)
                    case "uml:InstanceSpecification":
                        self.add_instance_specification(efx_packagedElem)
                    case "uml:Package":
                        self.add_package(efx_packagedElem)
                    case "uml:Signal":
                        self.add_signal(efx_packagedElem)
                    case "uml:AssociationClass":
                        self.add_association_class(efx_packagedElem)
                    case "uml:Association":
                        self.add_association(efx_packagedElem, self.current_out_pkg)
                    case "uml:Enumeration":
                        self.add_enumeration(efx_packagedElem)
                    case "uml:Collaboration":
                        self.add_collaboration(efx_packagedElem)
                    case "uml:Dependency":
                        self.add_dependency(efx_packagedElem, self.current_out_pkg)
                    case "uml:Realization":
                        self.add_realization(efx_packagedElem)
                    case "uml:Usage":
                        self.add_usage(efx_packagedElem)
                    case _:
                        print(f'{RED}unidentified xmi:type {efx_elem_type}{RESET}')
 
        except Exception as e:
            print(f'{RED}unexpected error in add_analysis_class for {efx_filepath}\n{e}{RESET}')
            print(traceback.format_exc())
    
    # converts the output XML file into Eclipse UML2 XMI format and beautifies
    def format(self):
        try:
            # convert xml content to strings
            contents = ET.tostring(self.root, encoding="unicode")
            # write nsmap attribute to dict
            nsmaps = re.findall(r'xmlns:(ns\d+)="([^"]+)"', contents)
            # replace ns values with Eclipse UML2 XMI equivalent
            for key, value in nsmaps:
                contents = contents.replace(
                    f'xmlns:{key}="{value}"', "").replace(f'{key}', f'{value}')
            # beautify spacing
            beautified_contents = minidom.parseString(contents).toprettyxml(indent="  ")
            return beautified_contents
        except Exception as e:
            print(f'{RED}unexpected error formatting output file\n{e}{RESET}')
            print(traceback.format_exc())
            return ""
        
    def to_file(self, file_name):
        # Create the output file path in the current directory
        out_file = os.path.join(os.getcwd(), file_name)
        
        # Write formatted contents to file
        with open(out_file, "w", encoding="utf-8-sig") as file:  # BOM handling is required to prevent MagicDraw byte exception upon load
            file.write(self.format())

    def clean(self):
        # remove duplicates of xmi:ids and ensure all uml:AssociationClass elements have two ownedEnds
        id_map = {}
        duplicates = []
        # iterate through all elements and track their xmi:id
        for elem in self.root.iter():
            elem_xmi_id = elem.attrib.get("{xmi}id")
            if elem_xmi_id:
                # make sure each memberEnd elem has a corresponding ownedEnd elem for every uml:AssociationClass
                if elem.attrib.get("{xmi}type"):
                    if elem.attrib["{xmi}type"] == "uml:AssociationClass":
                        memberEnd_ids = elem.attrib.get('memberEnd').split()
                        ownedEnd = elem.find("ownedEnd")
                        new_ownedEnd_id = None
                        new_memberEnd_ids = []
                        for memberEnd_id in memberEnd_ids:
                            if memberEnd_id != ownedEnd.attrib["{xmi}id"]:
                                located_elem = self.root.find(f".//*[@{{xmi}}id='{memberEnd_id}']")
                                if located_elem is not None:
                                    # add ownedEnd tag to AssociationClass 
                                    new_ownedEnd_id = generate_custom_uuid() # generate a unique uuid
                                    ET.SubElement(elem, "ownedEnd", attrib={
                                        "{xmi}id": new_ownedEnd_id, 
                                        "name": "",
                                        "visibility" : "private",
                                        "type" : located_elem.attrib["type"],
                                        "association" : elem_xmi_id
                                    })  
                                    memberEnd_id = new_ownedEnd_id
                                    # add shared aggregation to ownedElem
                                    located_elem.attrib["aggregation"] = "shared"
                            new_memberEnd_ids.append(memberEnd_id)
                        # replace memberId value with new ownedEnd id value
                        elem.attrib["memberEnd"] =  ' '.join(new_memberEnd_ids)
                    # make sure all uml:Usage and uml:Dependency clients have a corresponding clientDependency attrib
                    elif elem.attrib["{xmi}type"] == "uml:Usage" or elem.attrib["{xmi}type"] == "uml:Dependency":
                        client_elem = self.root.find(f".//*[@{{xmi}}id='{elem.attrib.get('client')}']")
                        if client_elem is not None:
                            # add usage/dependency id to client clientDependency attrib if does not exist already
                            client_clientDep = client_elem.attrib.get("clientDependency")
                            if client_clientDep is None:
                                # init clientDependnecy attrib with usage client id
                                client_elem.attrib["clientDependency"] = elem_xmi_id
                            elif elem_xmi_id not in client_clientDep.split():
                                # append usage client id to existing clientDependency
                                clientDep_list = client_clientDep.split()
                                clientDep_list.append(elem_xmi_id)
                                client_elem.attrib["clientDependency"] = ' '.join(clientDep_list)
                # gather duplicated elems
                if elem_xmi_id in id_map:
                    duplicates.append(elem)
                else:
                    id_map[elem_xmi_id] = elem
        # remove duplicate elements
        for dup in duplicates:
            parent = dup.getparent()
            if parent is not None:
                print(f'{YELLOW}removed duplicate elem with id {dup.attrib["{xmi}id"]}{RESET}')
                parent.remove(dup)
        
        self.resolve_dependencies()
            
    def resolve_dependencies(self):
        while True:
            # collect all xmi:ids
            all_ids = set()
            for elem in self.root.iter():
                if "{xmi}id" in elem.attrib:
                    all_ids.add(elem.attrib["{xmi}id"])

            # check all references
            unresolved_references = []
            for elem in self.root.iter():
                for attr in ["type", "classifier", "client", "supplier", "clientDependency", "ownedEnd", "memberEnd", "general", "association", "importedPackage", "contract"]:
                    if attr in elem.attrib:
                        # extract the reference ids
                        ref_ids = elem.attrib[attr].split(' ')
                        for ref_id in ref_ids:
                            if ref_id not in all_ids:
                                unresolved_references.append((elem, attr, ref_id))

            if not unresolved_references:
                break

            for elem, attr, ref_id in unresolved_references:
                try:
                    elem_type = elem.attrib["{xmi}type"]
                except KeyError:
                    elem_type = elem.tag
                # remove the unresolved reference from the attribute
                ref_ids = elem.attrib[attr].split(' ')
                ref_ids = [id for id in ref_ids if id != ref_id]
                if ref_ids:  # there are still valid ids in the attribute
                    if attr == "memberEnd" and len(ref_ids) == 1: # delete entire relationship element because memberEnd only includes ownedEnd id
                        print(f'{YELLOW}removed {elem_type} with id {elem.attrib.get("{xmi}id")} due to deprecated memberEnd {ref_id}{RESET}')
                        parent = elem.getparent()
                        if parent is not None:  # elem has already been removed
                            parent.remove(elem)
                    else: 
                        elem.attrib[attr] = ' '.join(ref_ids)
                        print(f'{YELLOW}removed {attr} with id {ref_id} from {elem_type} with id {elem.attrib.get("{xmi}id")}{RESET}')
                else:  # attribute is empty
                    if attr == "clientDependency":  # delete the clientDependency attribute of uml:class
                        print(f'{YELLOW}removed {elem.attrib[attr]} from clientDependency of {elem_type} with id {elem.attrib.get("{xmi}id")}{RESET}')
                        del elem.attrib[attr]
                    else:  # delete the relationship element
                        print(f'{YELLOW}removed {elem_type} with id {elem.attrib.get("{xmi}id")} due to unresolved {attr} {ref_id}{RESET}')
                        parent = elem.getparent()
                        if parent is not None:  # elem has already been removed
                            parent.remove(elem)

    def add_analysis_class_to_class_diagram(self, efx_filepath):
        try:
            efx_tree = ET.parse(efx_filepath)
            efx_root = efx_tree.getroot()
            
            self.current_efx_namespaces = dict(
                [node for _, node in ET.iterparse(efx_filepath, events=['start-ns'])])

            self.current_efx_pkg = efx_root.find('./uml:Package', self.current_efx_namespaces) # assumes there is only one package per file
            if self.current_efx_pkg is None:
                self.current_efx_pkg = efx_root

            # initialize package
            self.current_out_pkg = ET.SubElement(self.class_diagrams, "packagedElement", attrib={
                "{xmi}type" : "uml:Package",
                "{xmi}id": self.current_efx_pkg.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                "name" : self.current_efx_pkg.attrib["name"],
                "visibility" : "public"
            })

            # handle package ownedComment
            efx_pkg_ownedCom = self.current_efx_pkg.find("ownedComment", self.current_efx_namespaces)
            if efx_pkg_ownedCom is not None:
                efx_pkg_ownedCom_body = efx_pkg_ownedCom.find("body", self.current_efx_namespaces)
                ET.SubElement(self.current_out_pkg, "ownedComment", attrib={
                    "{xmi}id" : efx_pkg_ownedCom.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}id'],
                    "body" : efx_pkg_ownedCom_body.text,
                    "annotatedElement" : self.current_out_pkg.attrib["{xmi}id"]
                })

            efx_packagedElems = self.current_efx_pkg.findall(
                './packagedElement', self.current_efx_namespaces) 
            
            # handle packagedElements in analysis class
            for efx_packagedElem in efx_packagedElems:
                efx_elem_type = efx_packagedElem.attrib[f'{{{self.current_efx_namespaces.get("xmi")}}}type']
                match efx_elem_type:
                    case "uml:Class": 
                        self.add_class(efx_packagedElem, self.current_out_pkg)
                    case "uml:Interface": 
                        self.add_interface(efx_packagedElem, self.current_out_pkg)
                    case "uml:Enumeration":
                        self.add_enumeration(efx_packagedElem)
                    case _:
                        pass
 
        except Exception as e:
            print(f'{RED}unexpected error in add_analysis_class for {efx_filepath}\n{e}{RESET}')
            print(traceback.format_exc())

magicdraw_namespaces = {
    "xmi": "http://schema.omg.org/spec/XMI/2.1",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "MagicDrawProfile": "http://UML_Standard_Profile/MagicDraw_Profile/_be00301_1073394351331_445580_2",
    "ecore": "http://www.eclipse.org/emf/2002/Ecore",
    "uml": "http://www.eclipse.org/uml2/2.0.0/UML"
}

efx_file = "anonymized_input.efx"
magicdraw_file = "output.uml"

eclipse_analysis_classes = EclipseUMLAnalysisClassGenerator(efx_file, magicdraw_namespaces)
eclipse_analysis_classes.clean()

eclipse_analysis_classes.to_file(f'{magicdraw_file}')
print(f'{GREEN}analysis classes successfully written to {magicdraw_file}/analysis_classes.uml{RESET}')