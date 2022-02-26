"""XML utilities"""
import xml.etree.ElementTree as ET
from typing import Optional


def create_parser():
    """Creates an XML parser that is aware of comments"""
    return ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))


def parse(filename: str):
    """Parses the given XML file"""
    return ET.parse(filename, parser=create_parser())


def find_at_tree(tree: ET.ElementTree, *args):
    if tree is None:
        return None
    return find(tree.getroot(), *args)


def find(node: Optional[ET.Element], *args) -> Optional[ET.Element]:
    current_node = node
    for arg in args:
        if current_node is None:
            return None
        current_node = current_node.find(arg)
    return current_node
