#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Read and extract information from Parla-Clarin documents.
"""

from lxml import etree as _etree
import hashlib as _hashlib
import datetime as _datetime

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

def speeches_with_name(root, name=None, return_ids=False):
    """
    Convert Parla-Clarin XML to plain text. Returns a concatenated string.
    
    Args:
        root: Parla-Clarin document root, as an lxml tree root. 
        name: Name of the person whose speeches are returned. If name is None, returns all speeches.
        return_ids: Return a generator of tuples (text, id) instead of only text. Default False.
    """
    us = root.findall('.//{http://www.tei-c.org/ns/1.0}u')
    for u in us:
        if name is None or name.lower() in u.attrib['who'].lower():
            content = "\n".join(u.itertext())
            if return_ids:
                yield (content, u.attrib['{http://www.w3.org/XML/1998/namespace}id'])
            else:
                yield content

def speech_iterator(root):
    """
    Convert Parla-Clarin XML to an iterator of of concatenated speeches and speaker ids.
    Speech segments are concatenated unless a new speaker appears (ignoring any notes).

    Args:
        root: Parla-Clarin document root, as an lxml tree root.
    """
    us = root.findall('.//{http://www.tei-c.org/ns/1.0}u')
    if len(us) == 0: return None
    idx_old = us[0].attrib.get("who", "")
    speech = []

    for u in us:
        for text in u.itertext():
            idx = u.attrib.get("who", "")
            if idx != idx_old:
                yield([' '.join(speech), idx])
                speech = []
            speech.extend(text.split())
            idx_old = idx

def paragraph_iterator(root, page=None, output="str"):
    """
    Convert Parla-Clarin XML to an iterator of paragraphs. 

    Args:
        root: Parla-Clarin document root, as an lxml tree root.
        output: Output format of paragraphs. Accepts "str" (default), or "lxml".
    """
    tei_ns = "{http://www.tei-c.org/ns/1.0}"
    if page is not None:
        page = str(page)
        correct_page = False
    for body in root.findall(".//{http://www.tei-c.org/ns/1.0}body"):
        for div in body.findall("{http://www.tei-c.org/ns/1.0}div"):
            for elem in div:
                # Check if we enter the page the user requested
                if page is not None:
                    if elem.tag == tei_ns + "pb":
                        correct_page = elem.attrib.get("n") == page
                if output == "str":
                    p = "\n".join(elem.itertext())
                    if page is None or correct_page:
                        yield p
                elif output == "lxml":
                    if page is None or correct_page:
                        yield elem

def get_dates(root):
    """
    Get dates of a Parla-Clarin file. 

    Args:
        root: Parla-Clarin document root, as an lxml tree root.
    
    returns:
        as a datetime
    """
    dates = []
    for docDate in root.findall(".//{http://www.tei-c.org/ns/1.0}docDate"):
        date_string = docDate.text
        datetime = _datetime.datetime.strptime(date_string, "%Y-%m-%d")
        dates.append(datetime.date())

    return dates
            
