import sys
import json
from bs4 import BeautifulSoup, NavigableString

# Ensure correct module path
sys.path.insert(0, r"C:\Users\RELINQ\Downloads\browser_use\browser_use")

# Import necessary classes
from browser_use.dom.views import DOMElementNode
from browser_use.dom.history_tree_processor.service import HistoryTreeProcessor  

def convert_to_dom_node(soup_element, xpath="", parent=None):
    """Convert a BeautifulSoup element into a DOMElementNode."""
    if soup_element is None or isinstance(soup_element, NavigableString):
        return None  # Skip text nodes

    dom_node = DOMElementNode(
        tag_name=soup_element.name,
        xpath=xpath,
        attributes=soup_element.attrs if hasattr(soup_element, "attrs") else {},
        children=[],
        is_visible=True,
        parent=parent
    )

    # Recursively process child elements
    dom_node.children = [
        child_node for child in soup_element.contents
        if (child_node := convert_to_dom_node(child, f"{xpath}/{child.name}" if hasattr(child, "name") else xpath, parent=dom_node))
    ]

    return dom_node

def parse_html_to_dom(html):
    """Parses HTML and converts it into a DOMElementNode structure."""
    soup = BeautifulSoup(html, "html.parser")
    root_element = soup.body if soup.body else list(soup.children)[0]  
    return convert_to_dom_node(root_element, "/html/body")

# Sample HTML inputs
html_samples = {
    "html1": "<div><p>Hello</p></div>",
    "html2": "<div><p>Hello</p></div>"
}

# Process each HTML sample
dom_trees = {key: parse_html_to_dom(html) for key, html in html_samples.items()}
hash_trees = {key: HistoryTreeProcessor._hash_dom_element(dom) for key, dom in dom_trees.items()}

# Compare hash values
are_same = all(
    hash_trees["html1"].__dict__[key] == hash_trees["html2"].__dict__[key]
    for key in ["branch_path_hash", "attributes_hash", "xpath_hash"]
)

# Identify differences
differences = {
    key: {
        "html1": hash_trees["html1"].__dict__[key],
        "html2": hash_trees["html2"].__dict__[key]
    }
    for key in ["branch_path_hash", "attributes_hash", "xpath_hash"]
    if hash_trees["html1"].__dict__[key] != hash_trees["html2"].__dict__[key]
}

# Output JSON
output = {
    "hash_tree_1": hash_trees["html1"].__dict__,
    "hash_tree_2": hash_trees["html2"].__dict__,
    "are_same": are_same,
    "differences": differences if not are_same else None
}

# Save JSON to a file
download_path = "C:\\Users\\RELINQ\\Downloads\\dom_hash_output.json"
with open(download_path, "w") as json_file:
    json.dump(output, json_file, indent=2)

print(f"JSON file saved at: {download_path}")
