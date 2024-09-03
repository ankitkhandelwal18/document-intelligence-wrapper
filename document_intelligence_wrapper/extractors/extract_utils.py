# document_intelligence_wrapper/extractors/extract_utils.py

import re
import pandas as pd
import concurrent.futures
import threading

from document_intelligence_wrapper.extractors.helpers import calculate_cell_confidence_score,calculate_confidence_score

def table_markdown(table):
    """
    Converts a JSON representation of a table to a Markdown table format.

    Args:
        table (dict): The JSON representation of the table.

    Returns:
        str: The Markdown string of the table.
    """
    # Initialize an empty list to hold column headers and rows
    headers = []
    rows = []

    # Determine the number of rows and columns
    max_row = table['rowCount']
    max_col = table['columnCount']

    # Create a matrix to hold cell content
    cell_matrix = [[''] * max_col for _ in range(max_row)]

    # Populate the matrix with cell content based on row and column indices
    for cell in table['cells']:
        row_idx = cell['rowIndex']
        col_idx = cell['columnIndex']
        content = cell['content'].replace("\n", "")
        
        # Handle column span
        if 'columnSpan' in cell and cell['columnSpan'] > 1:
            for span in range(cell['columnSpan']):
                if 'kind' in cell and cell['kind'] == 'columnHeader':
                    cell_matrix[row_idx][col_idx + span] = content
                else:
                    cell_matrix[row_idx][col_idx + span] = content
                    break
        else:
            cell_matrix[row_idx][col_idx] = content

    # Use the provided logic to determine column headers and data rows
    for row_idx, row in enumerate(cell_matrix):
        if any('kind' in cell and cell['kind'] == 'columnHeader' for cell in table['cells'] if cell['rowIndex'] == row_idx):
            headers.append(row)
        else:
            rows.append(row)

    # Flatten the headers list and remove empty strings
    final_headers = []
    if headers:
        # Transpose headers to combine multi-level columns
        for col_idx in range(max_col):
            combined_header = '\n'.join([header_row[col_idx].strip() for header_row in headers if header_row[col_idx].strip()])
            final_headers.append(combined_header)
    else:
        # Generate default headers if none are found
        final_headers = ['Column ' + str(i + 1) for i in range(max_col)]

    # Merge adjacent columns with the same non-empty headers
    merged_headers = []
    merged_data = [[] for _ in range(len(rows))]

    col_idx = 0
    while col_idx < len(final_headers):
        header = final_headers[col_idx]
        # Check for adjacent identical headers
        merged_cols = [col_idx]
        for next_col_idx in range(col_idx + 1, len(final_headers)):
            if final_headers[next_col_idx] == header and header != '':
                merged_cols.append(next_col_idx)
            else:
                break
        
        merged_headers.append(header)

        # Merge the data from the merged columns
        for row_idx in range(len(rows)):
            merged_value = ''
            for col in merged_cols:
                if rows[row_idx][col].strip() != '':
                    merged_value += rows[row_idx][col].strip() + ' '
            merged_data[row_idx].append(merged_value.strip())

        col_idx = merged_cols[-1] + 1

    # Create a DataFrame with the headers and rows
    merged_df = pd.DataFrame(merged_data, columns=merged_headers)

    # Remove any rows that are still empty (can happen if there are row spans or empty rows)
    merged_df = merged_df.dropna(how='all').reset_index(drop=True)

    # Convert the DataFrame to markdown format
    markdown_text = merged_df.to_markdown(index=False)
    
    return markdown_text

def process_page(page_num, elements, data, figure_associations, table_text_dict, table_counter, calculate_confidence, calculate_cell_confidence):
    """
    Processes the elements of a given page and extracts their details.

    Parameters:
        page_num (int): The page number being processed.
        elements (list): A list of elements (paragraphs, tables, figures) on the current page.
        data (dict): The dictionary containing all document data.
        figure_associations (dict): A mapping of figures to associated paragraphs.
        table_text_dict (dict): A dictionary to store table content.
        table_counter (list): A list containing a single integer to give unique IDs to tables (used as a counter).
        calculate_confidence (bool): Flag to control calculation of confidence scores for elements.
        calculate_cell_confidence (bool): Flag to control calculation of confidence scores for table cells.

    Returns:
        tuple: Contains the page number, the concatenated text of the page, and a list of element details.
    """
    # Initialize a list to store text for the current page
    page_text = []
    page_elements = []  # List to store JSON objects for the current page

    # Initialize a counter for tables in the current page
    local_table_counter = 0

    # Iterate through each element in the current page
    for element in elements:
        # Initialize a dictionary to store element details
        element_details = {
            "element_name": "",
            "content": "",
            "bounding_box": [],
            "confidence_score": {
                "average": 0,
                "weighted": 0
            }
        }

        # Check if the element is a paragraph
        if 'paragraphs' in element:
            # Extract the paragraph number from the element string
            para_num = int(element.split(' ')[1])
            # Get the paragraph content
            para_content = data['paragraphs'][para_num]['content']
            # Get the bounding box of the paragraph
            para_bounding_box = data['paragraphs'][para_num]['boundingRegions'][0]['polygon']

            # Calculate confidence if the flag is set to True
            if calculate_confidence:
                average_confidence, weighted_confidence = calculate_confidence_score(data['paragraphs'][para_num], data)
                element_details["confidence_score"]["average"] = average_confidence
                element_details["confidence_score"]["weighted"] = weighted_confidence

            # Update element details
            element_details["element_name"] = "paragraph"
            element_details["content"] = para_content
            element_details["bounding_box"] = para_bounding_box

            # Append paragraph content to page text
            page_text.append(para_content)

        # Check if the element is a table
        elif 'tables' in element:
            # Extract the table number from the element string
            table_num = int(element.split(' ')[1])
            # Get the table content using a table_markdown function
            table_content = table_markdown(data['tables'][table_num])
            # Get the bounding box of the table
            table_bounding_box = data['tables'][table_num]['boundingRegions'][0]['polygon']

            # Calculate confidence if the flag is set to True
            if calculate_confidence:
                average_confidence, weighted_confidence = calculate_confidence_score(data['tables'][table_num], data)
                element_details["confidence_score"]["average"] = average_confidence
                element_details["confidence_score"]["weighted"] = weighted_confidence

                # Store table content in table_text_dict with a unique key
                with threading.Lock():
                    table_key = f"{page_num}_{local_table_counter}"
                    table_text_dict[table_key] = table_content
                    local_table_counter += 1

                # Add detailed cell information for the table if the cell confidence flag is set to True
                if calculate_cell_confidence:
                    element_details["cells"] = []
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        cell_futures = [
                            executor.submit(calculate_cell_confidence_score, cell, data) 
                            for cell in data['tables'][table_num]['cells']
                        ]
                        cell_results = []
                        for future in concurrent.futures.as_completed(cell_futures):
                            cell_avg_confidence, cell_weighted_confidence = future.result()
                            cell = data['tables'][table_num]['cells'][cell_futures.index(future)]
                            cell_details = {
                                "rowIndex": cell["rowIndex"],
                                "columnIndex": cell["columnIndex"],
                                "content": cell["content"],
                                "bounding_box": cell["boundingRegions"][0]["polygon"],
                                "confidence_score": {
                                    "average": cell_avg_confidence,
                                    "weighted": cell_weighted_confidence
                                }
                            }
                            cell_results.append(cell_details)
                        
                        # Sort cells based on rowIndex and columnIndex
                        sorted_cells = sorted(cell_results, key=lambda x: (x["rowIndex"], x["columnIndex"]))
                        element_details["cells"].extend(sorted_cells)
            
            # Append table content to page text
            page_text.append(table_content)
            element_details["element_name"] = "table"
            element_details["content"] = table_content
            element_details["bounding_box"] = table_bounding_box

        # Check if the element is a figure
        elif 'figures' in element:
            fig_content = ""
            # Get the associated paragraphs and polygons from figure_associations
            associated_data = figure_associations.get(element, {})
            associated_paragraphs = associated_data.get('associated_paragraphs', [])
            polygons = associated_data.get('polygons', [])

            # Check if there are any associated paragraphs
            if associated_paragraphs:
                # If associated paragraphs are present, use the content of the first one
                for para_index in associated_paragraphs:
                    fig_content += data['paragraphs'][para_index]['content'] + " "
            else:
                # If no associated paragraphs, use empty text
                fig_content = ""

            # Use the first polygon if present
            if polygons:
                fig_bounding_box = polygons[0]
            else:
                # If no polygons are available, set bounding box to None or an empty list
                fig_bounding_box = []

            # Update element details
            element_details["element_name"] = "figure"
            element_details["content"] = fig_content
            element_details["bounding_box"] = fig_bounding_box

            # Append figure content to page and full document text
            page_text.append(fig_content)

        # Add element details to the page elements list
        page_elements.append(element_details)

    # Join the list items with a newline character
    return page_num, '\n\n'.join(page_text), page_elements


def extract_page_text(ocr_json, page_section, figure_associations, calculate_confidence=True, calculate_cell_confidence=False):
    """
    Extracts text from each page of the document and processes elements using multi-threading.

    Parameters:
        ocr_json (dict): The dictionary containing all document data.
        page_section (dict): A dictionary mapping each page number to its list of elements.
        figure_associations (dict): A mapping of figures to associated paragraphs.
        calculate_confidence (bool): Flag to control calculation of confidence scores for elements.
        calculate_cell_confidence (bool): Flag to control calculation of confidence scores for table cells.

    Returns:
        tuple: Contains dictionaries of page text and table text, the combined full document text, and a list of all page elements.
    """
    # Initialize dictionaries and variables to store the text of each page, tables, and full document
    page_text_dict = {}
    table_text_dict = {}
    all_page_elements = []  # List to store JSON objects for all pages

    # Table counter to give unique IDs to tables
    table_counter = [1]  # Using a list to mutate the counter across threads

    # Use ThreadPoolExecutor to process each page in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Pass arguments to the process_page function using a list of futures
        future_to_page = {
            executor.submit(process_page, page_num, elements, ocr_json, figure_associations, table_text_dict, table_counter, calculate_confidence, calculate_cell_confidence): page_num 
            for page_num, elements in page_section.items()
        }

        # Process the results as they complete
        for future in concurrent.futures.as_completed(future_to_page):
            page_num, page_text, page_elements = future.result()
            page_text_dict[page_num] = page_text
            all_page_elements.append({"page_number": page_num, "elements": page_elements})

    # Sort page_text_dict by page number
    sorted_page_text_dict = dict(sorted(page_text_dict.items()))

    # Renaming tables with a simple sequence
    sorted_table_text_dict = {}
    global_table_counter = 1  # Initialize a global table counter
    for key in sorted(table_text_dict.keys(), key=lambda x: (int(x.split('_')[0]), int(x.split('_')[1]))):
        sorted_table_text_dict[str(global_table_counter)] = table_text_dict[key]
        global_table_counter += 1

    # Create full_doc_text_combined from the sorted page_text_dict
    full_doc_text_combined = '\n\n'.join(f"Page Number {page_number}\n{text}" for page_number, text in sorted(sorted_page_text_dict.items()))

    # Sort all_page_elements by page_number
    all_page_elements_sorted = sorted(all_page_elements, key=lambda x: x["page_number"])

    return sorted_page_text_dict, sorted_table_text_dict, full_doc_text_combined, all_page_elements_sorted
