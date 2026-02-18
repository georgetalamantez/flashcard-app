from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def parse_html_content(html_content: str):
    """Parses HTML content and extracts headings and paragraphs."""
    soup = BeautifulSoup(html_content, 'html.parser')
    sections = []
    
    # Common heading tags
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    
    # Find all elements and extract content
    current_section = {"heading": "Introduction", "content": ""}
    
    for element in soup.find_all(['p'] + heading_tags):
        tag_name = element.name
        
        if tag_name in heading_tags:
            # If we already have content in the current section, save it
            if current_section["content"].strip():
                sections.append(current_section)
            
            # Start a new section
            current_section = {
                "heading": element.get_text().strip(),
                "content": ""
            }
        else:
            # Add paragraph text to current section
            text = element.get_text().strip()
            if text:
                current_section["content"] += text + " "
    
    # Add the last section
    if current_section["content"].strip():
        sections.append(current_section)
        
    return sections

def parse_xml_content(xml_content: str):
    """Parses XML content and extracts structured text."""
    # Simplified XML parsing using similar logic to HTML
    soup = BeautifulSoup(xml_content, 'xml')
    sections = []
    
    # Try to find standard technical document structures
    # This is a heuristic and can be refined
    
    # Common title/heading tags in technical XML
    heading_tags = ['title', 'heading', 'h1', 'h2', 'h3', 'h4', 'section_title']
    paragraph_tags = ['paragraph', 'p', 'para', 'text', 'content']
    
    current_section = {"heading": "Main", "content": ""}
    
    for element in soup.find_all(heading_tags + paragraph_tags):
        tag_name = element.name.lower()
        
        if tag_name in heading_tags:
            if current_section["content"].strip():
                sections.append(current_section)
            
            current_section = {
                "heading": element.get_text().strip(),
                "content": ""
            }
        else:
            text = element.get_text().strip()
            if text:
                current_section["content"] += text + " "
                
    if current_section["content"].strip():
        sections.append(current_section)
        
    # If standard tags weren't found, try a generic approach
    if not sections:
        logger.info("Standard XML tags not found, falling back to generic extraction")
        # Just extract all text content from the root
        text = soup.get_text().strip()
        if text:
            sections.append({"heading": "Content", "content": text})
            
    return sections
