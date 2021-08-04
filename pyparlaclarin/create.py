"""
Generate new Parla Clarin documents
"""
import copy as _copy
from lxml import etree as _etree

# Generate parla clarin header
def pc_header(metadata):
    """
    Generate a teiHeader for Parla-Clarin documents.

    Args:
        metadata: python dictionary with the appropriate metadata. Missing keys
            are allowed and filled with 'N/A' values.
    """
    teiHeader = _etree.Element("teiHeader")
    
    # fileDesc
    fileDesc = _etree.SubElement(teiHeader, "fileDesc")
    
    titleStmt = _etree.SubElement(fileDesc, "titleStmt")
    title = _etree.SubElement(titleStmt, "title")
    title.text = metadata.get("document_title", "N/A")
    
    if "edition" in metadata:
        editionStmt = _etree.SubElement(fileDesc, "editionStmt")
        edition = _etree.SubElement(editionStmt, "edition")
        edition.text = metadata.get("edition", "N/A")

    extent = _etree.SubElement(fileDesc, "extent")
    publicationStmt = _etree.SubElement(fileDesc, "publicationStmt")
    authority = _etree.SubElement(publicationStmt, "authority")
    authority.text = metadata.get("authority", "N/A")
    
    sourceDesc = _etree.SubElement(fileDesc, "sourceDesc")
    sourceBibl = _etree.SubElement(sourceDesc, "bibl")
    sourceTitle = _etree.SubElement(sourceBibl, "title")
    sourceTitle.text = metadata.get("document_title", "N/A")
    
    # encodingDesc
    encodingDesc = _etree.SubElement(teiHeader, "encodingDesc")
    editorialDecl = _etree.SubElement(encodingDesc, "editorialDecl")
    correction = _etree.SubElement(editorialDecl, "correction")
    correction_p = _etree.SubElement(correction, "p")
    correction_p.text = metadata.get("correction", "No correction of source texts was performed.")
    
    return teiHeader
    
def create_parlaclarin(teis, metadata):
    if type(teis) != list:
        tei = teis
        return create_parlaclarin([tei], metadata)
    
    teiCorpus = _etree.Element("teiCorpus", xmlns="http://www.tei-c.org/ns/1.0")
    teiHeader = pc_header(metadata)
    teiCorpus.append(teiHeader)
    
    for tei in teis:
        teiCorpus.append(tei)
    
    teiCorpusTree = _etree.ElementTree(teiCorpus)
    
    for xml_element in teiCorpusTree.iter():
        content = xml_element.xpath('normalize-space()')

        if not content and len(xml_element.attrib) == 0:
            xml_element.getparent().remove(xml_element)
            
    s = _etree.tostring(teiCorpusTree, pretty_print=True, encoding="utf-8", xml_declaration=True).decode("utf-8")
    return s
    
def create_tei(root, metadata):
    """
    Create a Parla-Clarin TEI element from a list of segments.

    Args:
        txts: a list of lists of strings, corresponds to content blocks and paragraphs, respectively.
        metadata: Metadata of the parliamentary session
    """
    metadata = _copy.deepcopy(metadata)
    
    tei = _etree.Element("TEI")
    documentHeader = pc_header(metadata)
    tei.append(documentHeader)
    
    text = _etree.SubElement(tei, "text")
    front = _etree.SubElement(text, "front")
    preface = _etree.SubElement(front, "div", type="preface")
    _etree.SubElement(preface, "head").text = protocol_id.split(".")[0]
    if "date" not in metadata:
        year = metadata.get("year", 2020)
        metadata["date"] = str(year) + "-01-01"
        
    _etree.SubElement(preface, "docDate", when=metadata["date"]).text = metadata.get("date", "2020-01-01")

    body = _etree.SubElement(text, "body")
    body_div = _etree.SubElement(body, "div")
    
    pb = _etree.SubElement(body_div, "pb")
    pb.attrib["n"] = "0"
    
    return tei

