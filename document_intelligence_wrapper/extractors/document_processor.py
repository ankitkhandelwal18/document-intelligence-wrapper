# document_intelligence_wrapper/extractors/document_processor.py

def process_document(data):
    """
    Processes the document data to organize paragraphs and tables by page number 
    and track elements referenced in sections in order.

    Args:
        data (dict): The structured document data containing paragraphs, tables, figures and sections.

    Returns:
        dict: A dictionary where keys are page numbers and values are lists of element identifiers in order.
    """
    # Create a dictionary to keep track of elements by page number
    pages = {}
    
    # Create a dictionary to keep track of figure associations with paragraphs
    figure_associations = {}

    # Process paragraphs and store them by page
    for i, para in enumerate(data.get("paragraphs", [])):
        for region in para.get("boundingRegions", []):
            page = region.get("pageNumber")
            if page not in pages:
                pages[page] = []
            pages[page].append(f"paragraphs {i}")  # Track paragraphs by index

    # Process tables and store them by page
    for j, table in enumerate(data.get("tables", [])):
        for region in table.get("boundingRegions", []):
            page = region.get("pageNumber")
            if page not in pages:
                pages[page] = []
            pages[page].append(f"tables {j}")  # Track tables by index
        
    # Process figures and store them by page, also capture associated paragraphs
    for k, figure in enumerate(data.get("figures", [])):
        polygons = []  # List to store all polygons for the current figure
        for region in figure.get("boundingRegions", []):
            page = region.get("pageNumber", 1)  # Default to page 1 if not present
            if page not in pages:
                pages[page] = []
            polygons.append(region.get("polygon", []))  # Capture the polygon
            
            # Find associated paragraph numbers from the elements list
            associated_paragraphs = []
            for element in figure.get("elements", []):
                if element.startswith("/paragraphs/"):
                    para_index = element.split("/")[2]
                    associated_paragraphs.append(int(para_index))
            
            # Store figure and associated paragraphs along with polygons in the figure_associations dictionary
            figure_associations[f"figures {k}"] = {
                "associated_paragraphs": associated_paragraphs,
                "polygons": polygons
            }
            
            pages[page].append(f"figures {k}")
    
    print("pages",pages)

    # Track elements that are referenced in sections in order
    section_elements_by_page = {}

    for section in data.get("sections", []):
        for element in section.get("elements", []):
            # Check if element is a list or a string
            if isinstance(element, list):
                _, element_type, element_index = element
            elif isinstance(element, str):
                _, element_type, element_index = element.split('/')
            else:
                continue
            
            element_index = int(element_index)
            element_id = f"{element_type} {element_index}"
            
            # Add element to the appropriate page if it exists there
            for page, elements in pages.items():
                if element_id in elements:
                    if page not in section_elements_by_page:
                        section_elements_by_page[page] = []
                    if element_id not in section_elements_by_page[page]:
                        section_elements_by_page[page].append(element_id)

    # Replace the pages dict with ordered elements from sections
    pages_ordered = {}
    for page, elements in section_elements_by_page.items():
        pages_ordered[page] = elements

    return pages_ordered, figure_associations
