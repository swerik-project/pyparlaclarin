#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Read and extract information from Parla-Clarin documents.
"""

from lxml import etree as _etree
import hashlib as _hashlib

def element_hash(elem, protocol_id="", chars=16):
    """
    Calculate a deterministic hash for an XML element
    """
    # The hash seed consists of 
    # 1. Element text without line breaks
    elem_text = elem.text
    if elem_text is None:
        elem_text = ""
    elem_text = elem_text.strip().replace("\n", " ")
    elem_text = ' '.join(elem_text.split())
    # 2. The element tag
    elem_tag = elem.tag
    # 3. The element attributes in alphabetical order,
    # excluding the XML ID and XML n
    xml_id = "{http://www.w3.org/XML/1998/namespace}id"
    xml_n = "{http://www.w3.org/XML/1998/namespace}n"
    n = "n"
    excluded = [xml_id, xml_n, n, "prev", "next"]
    elem_attrib = {key: value for key, value in elem.attrib.items() if key not in excluded}
    elem_attrib = str(sorted(elem_attrib.items()))
    seed = protocol_id + "\n" + elem_text + "\n" + elem_tag + "\n" + elem_attrib
    encoded_seed = seed.encode("utf-8")
    # Finally, the hash is calculated via MD5
    digest = _hashlib.md5(encoded_seed).hexdigest()
    return digest[:chars]
    
def validate_xml_schema(xml_path, schema_path):
    # TODO: refactor into 'validate_parlaclarin'
    xml_file = _etree.parse(xml_path)

    schema = _etree.XMLSchema(file=schema_path)
    is_valid = schema.validate(xml_file)

    return is_valid


def parlaclarin_to_md(root):
    """
    Convert Parla-Clarin XML to markdown. Returns a string.

    Args:
        root: Parla-Clarin document root, as an lxml tree root.
    """
    return None

def parlaclarin_to_txt(root):
    """
    Convert Parla-Clarin XML to plain text. Returns a string.

    Args:
        root: Parla-Clarin document root, as an lxml tree root. 
    """
    paragraphs = paragraph_iterator(root)
    return "\n\n".join(paragraphs)

def speeches_with_name(root, name=None):
    """
    Convert Parla-Clarin XML to plain text. Returns a concatenated string.
    
    Args:
        root: Parla-Clarin document root, as an lxml tree root. 
        name: Name of the person whose speeches are returned. If name is None, returns all speeches.
    """
    us = root.findall('.//{http://www.tei-c.org/ns/1.0}u')
    for u in us:
        if name is None:
            yield "\n".join(u.itertext())
        elif name.lower() in u.attrib['who'].lower():
            yield "\n".join(u.itertext())

def paragraph_iterator(root, output="str"):
    """
    Convert Parla-Clarin XML to an iterator of paragraphs. 

    Args:
        root: Parla-Clarin document root, as an lxml tree root.
        output: Output format of paragraphs. Accepts "str" (default), or "lxml".
    """
    for body in root.findall(".//{http://www.tei-c.org/ns/1.0}body"):
        for div in body.findall("{http://www.tei-c.org/ns/1.0}div"):
            for elem in div:
                if output == "str":
                    p = "\n".join(elem.itertext())
                    yield p
                elif output == "lxml":
                    yield elem
