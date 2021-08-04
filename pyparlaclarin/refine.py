"""
Modify and curate Parla-Clarin documents
"""
from lxml import etree as _etree
import random as _random

def _iter(root, ns="{http://www.tei-c.org/ns/1.0}"):
    for body in root.findall(".//" + ns +"body"):
        for div in body.findall(ns + "div"):
            for ix, elem in enumerate(div):
                if elem.tag == ns + "u":
                    yield "u", elem
                elif elem.tag == ns + "note":
                    yield "note", elem
                elif elem.tag == ns + "pb":
                    yield "pb", elem
                elif elem.tag == ns + "seg":
                    yield "seg", elem
                elif elem.tag == "u":
                    elem.tag = ns + "u"
                    yield "u", elem
                else:
                    print(elem.tag)
                    yield None

def random_classifier(paragraph):
    alternatives = ["note", "u"]
    return _random.choice(alternatives)


def reclassify(root, classifier, tei="{http://www.tei-c.org/ns/1.0}"):
    """
    Reclassify nodes in a Parla-Clarin tree.

    Args:
        root: root of the lxml tree to be reclassified
        classifier: lambda function that classifies paragraphs. str->str,
            takes paragraph content as input, outputs predicted xml tag, such
            as note or u.
        tei: namespace for the output xml
    """
    prev_elem = None
    for ix, elem_tuple in enumerate(list(_iter(root))):
        tag, elem = elem_tuple

        prev_elem = elem
        if tag == "u":
            for seg in elem:
                paragraph = seg.text
                c = classifier(paragraph)
                if c != "u":
                    print("Change u to note")
                    prev_elem.addnext(seg)
                    prev_elem = seg
                    seg.tag = tei + c
                elif prev_elem != elem:
                    if prev_elem.tag == tei + "u":
                        prev_elem.append(seg)
                    else:
                        new_elem = _etree.Element(tei + "u")
                        prev_elem.addnext(new_elem)
                        prev_elem = new_elem
                        prev_elem.append(seg)
                else:
                    pass

        elif tag == "note":
            paragraph = elem.text
            c = classifier(paragraph)
            if c != tag:                
                if c == "u":
                    elem.tag = tei + "seg"
                    if prev_elem.tag == tei + "u":
                        print("Change note to u")
                    else:
                        # Create new u node
                        new_elem = _etree.Element(tei + c)
                        prev_elem.addnext(new_elem)
                        prev_elem = new_elem

                    prev_elem.append(elem)

                else:
                    prev_elem = elem
                    elem.tag = tei + c
            else:
                prev_elem = elem
        else:
            prev_elem = elem
    return root


def format_paragraph(paragraph, spaces=12):
    """
    Formats paragraphs to be equal in width.

    Args:
        paragraph: paragraph content, str.
        spaces: size of indentation as number of spaces.
    """
    words = paragraph.replace("\n", "").strip().split()
    s = "\n" + " " * spaces
    row = ""

    for word in words:
        if len(row) > 60:
            s += row.strip() + "\n" + " " * spaces
            row = word
        else:
            row += " " + word

    if len(row.strip()) > 0:
        s += row.strip() + "\n" + " " * (spaces - 2)

    if s.strip() == "":
        return None
    return s

def format_texts(root):
    """
    Formats all text elements in a Parla-Clarin document.

    Args:
        root: Parla-Clarin document as an lxml tree root.
    """
    for tag, elem in _iter(root):

        if type(elem.text) == str:
            elem.text = format_paragraph(elem.text)
        elif tag == "u":
            if len(list(elem)) > 0:
                for seg in elem:
                    if type(seg.text) == str:
                        seg.text = format_paragraph(seg.text, spaces=14)
                    else:
                        seg.text = None
                elem.text = None
            else:
                elem.getparent().remove(elem)
        elif tag == "pb":
            if "{http://www.w3.org/XML/1998/namespace}url" in elem.attrib:
                url = elem.attrib["{http://www.w3.org/XML/1998/namespace}url"]
                del elem.attrib["{http://www.w3.org/XML/1998/namespace}url"]
                elem.attrib["facs"] = url

    return root
