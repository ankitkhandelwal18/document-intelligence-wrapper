# Document Intelligence Wrapper

## Overview

The `document_intelligence_wrapper` is a Python package that provides a wrapper around the Azure Document Intelligence API. It offers easy-to-use functions to extract structured data, including text and tables, from documents. This wrapper is designed to handle complex document structures, such as tables with merged cells, and convert the extracted data into Markdown format, which is particularly useful for Generative AI processes and other automated text-processing workflows.

## Features

- Document Intelligence Client Wrapper: Simplifies the initialization and interaction with the Azure Document Intelligence API.
- Text Extraction: Extracts paragraphs and text from documents, organizing them page-by-page.
- Table Extraction with Merged Cells Handling: Converts tables, including those with merged cells, from JSON format to Markdown format.
- Confidence Score Calculation:
    * Paragraph Confidence Scores: Calculates and returns confidence scores for each paragraph, helping users understand the accuracy and reliability of extracted text.
    * Table Confidence Scores: Provides confidence scores for entire tables, giving an overview of the extraction quality for complex tabular data.
    * Table Cell Confidence Scores: Offers optional detailed confidence scores for individual cells within tables, useful for applications that require high precision in cell-level data extraction.

- Markdown Output: Generates Markdown-formatted tables and text for easy visualization and integration with other text-processing tools.
- Organizes Data by Page: Outputs text and tables organized by page number and element order.

## Installation

To use this package, simply install it, and all necessary dependencies will be automatically downloaded. Run the following command in your terminal to install the package:
```python
pip install document-intelligence-wrapper==1.0.0b1
```

# Supported Formats

The `document_intelligence_wrapper` supports a variety of document formats for text and table extraction. These include:

- **PDF**: Portable Document Format files.
- **JPEG, JPG**: Common image formats for photographs and scanned documents.
- **PNG**: Portable Network Graphics files, often used for screenshots and images with transparency.
- **TIF**: Tagged Image File Format, used for high-quality graphics.
- **HEIC**: High-Efficiency Image Coding, used by modern smartphones for image compression.

## Special Case: DOCX Files

When DOCX files are passed into the `document_intelligence_wrapper`, the behavior differs slightly:

- Only `ocr_result` will contain data, showing the raw OCR information.
- Other outputs (`page_text`, `table_text`, `doc_text`, `all_page_elements`) will be empty.

## Usage

- The primary function to utilize from this package is analyze_document_text. This function efficiently extracts text and tables from the source file and organizes them into a structured format. The `DocumentIntelligenceClientWrapper` class is employed to streamline the initialization of the client, making it simpler to work with the Azure Document Intelligence API. 
- Additionally, the package provides a custom JSON output that includes easy-to-navigate content along with confidence scores, enabling users to quickly assess the reliability of the extracted information.


### Step-by-Step Guide

### 1.Initialize the Document Intelligence Client: Use the DocumentIntelligenceClientWrapper to create a client with your Azure endpoint and key.

### 2. Call the Function: Use analyze_document_text with the initialized client and the path to your file.

```python
from document_intelligence_wrapper.document_intelligence_client import DocumentIntelligenceClientWrapper
from document_intelligence_wrapper.extractors.text_extractor import analyze_document_text

# Define your Azure endpoint and key
endpoint = "your-azure-endpoint"
key = "your-azure-key"

# Initialize the Document Intelligence Client using the wrapper
client_wrapper = DocumentIntelligenceClientWrapper(endpoint, key)
client = client_wrapper.get_document_intelligence_client()

# Define the path to your file
file_path = "path/to/your/document.pdf"

# Extract text and table data from the file
page_text, table_text, doc_text, all_page_elements, ocr_result = analyze_document_text(
    client,
    file_path,
    calculate_confidence=True,  # Calculate confidence for paragraphs and tables
    calculate_cell_confidence=True  # Calculate confidence for individual table cells
)
```

### Returned Values:

1. **`page_text`**: A dictionary containing text extracted from each page of the document. The keys in this dictionary represent the page numbers, and the values are the corresponding text content extracted from those pages. This structure helps to maintain the original pagination and sequence of content within the document.

    **Example:**
    ```python
    {
        1: "Text content from page 1",
        2: "Text content from page 2",
        ...
    }
    ```

2. **`table_text`**: A dictionary containing the extracted table content. Each table in the document is stored as a separate entry in this dictionary. The keys are unique identifiers for the tables (e.g., "Table 1", "Table 2"), and the values are the Markdown-formatted representation of each table's content. This allows easy access and identification of table data within the document.

    **Example:**
    ```python
    {
        1: "| Header 1 | Header 2 |\n|----------|----------|\n| Data 1   | Data 2   |",
        2: "| Header A | Header B |\n|----------|----------|\n| Data A   | Data B   |",
        ...
    }
    ```

3. **`doc_text`**: A single string that combines the text content from all pages of the document. This aggregated text includes all paragraphs, tables, and other text elements, presented in the order they appear within the document. This is useful for tasks that require a continuous flow of text without regard to page breaks, such as full-text analysis or document summarization.

    **Example:**
    ```python
    "Full text from page 1.\n\nFull text from page 2.\n\n..."
    ```

4. **`all_page_elements`**: A list of JSON-like objects, each representing the detailed content and metadata of elements found on a specific page. Each object contains:
    - **`page_number`**: The page number where the elements are located.
    - **`elements`**: A list of elements found on that page. Each element object includes:
      - **`element_name`**: Type of the element (e.g., "paragraph", "table").
      - **`content`**: The actual text content of the element.
      - **`bounding_box`**: Coordinates that define the position of the element on the page.
      - **`confidence_score`**: Confidence scores indicating the reliability of the extracted content (both average and weighted).
      - **`cells`** (optional, only for tables): Details about each cell in the table, including content, bounding box, and confidence scores.

    **Example:**
    ```json
    [
        {
            "page_number": 1,
            "elements": [
                {
                    "element_name": "paragraph",
                    "content": "This is an example paragraph.",
                    "bounding_box": [1.0449,0.7832,3.4048,0.7782,3.406,1.3564,1.0461,1.3614],
                    "confidence_score": {
                        "average": 0.996,
                        "weighted": 0.9956
                    }
                },
                {
                    "element_name": "table",
                    "content": "| Header 1 | Header 2 |\n|----------|----------|\n| Data 1   | Data 2   |",
                    "bounding_box": [4.0574,0.3923,8.265,0.3978,8.2628,1.8739,4.0555,1.8682],
                    "confidence_score": {
                        "average": 0.9891,
                        "weighted": 0.9921
                    },
                    "cells": [
                        {
                            "rowIndex": 0,
                            "columnIndex": 0,
                            "content": "Header 1",
                            "bounding_box": [4.0781,0.3915,6.9528,0.3915,6.9528,0.5681,4.0781,0.5681],
                            "confidence_score": {
                                "average": 0.9901,
                                "weighted": 0.9902
                            }
                        },
                        ...
                    ]
                }
            ]
        },
        ...
    ]
    ```

5. **`ocr_json`**: This is the raw result obtained directly from the Azure Document Intelligence API.


## Handling Complex Tables with Merged Cells

The provided function is designed to handle tables with merged cells seamlessly. It uses a cell matrix to map each cell’s position, taking into account any column spans (merged cells), ensuring that data is correctly represented in the output Markdown table.

### Example
Consider a table with merged header cells:


```json
{
    "rowCount": 3,
    "columnCount": 4,
    "cells": [
        {"rowIndex": 0, "columnIndex": 0, "content": "Header 1", "columnSpan": 2},
        {"rowIndex": 0, "columnIndex": 2, "content": "Header 2", "columnSpan": 1},
        {"rowIndex": 1, "columnIndex": 0, "content": "Sub-header 1"},
        {"rowIndex": 1, "columnIndex": 1, "content": "Sub-header 2"},
        {"rowIndex": 1, "columnIndex": 2, "content": "Sub-header 3"},
        {"rowIndex": 1, "columnIndex": 3, "content": "Sub-header 4"},
        {"rowIndex": 2, "columnIndex": 0, "content": "Data 1"},
        {"rowIndex": 2, "columnIndex": 1, "content": "Data 2"},
        {"rowIndex": 2, "columnIndex": 2, "content": "Data 3"},
        {"rowIndex": 2, "columnIndex": 3, "content": "Data 4"}
    ]
}

```

```
| Header 1      | Header 1      | Header 2      |               |
|---------------|---------------|---------------|---------------|
| Sub-header 1  | Sub-header 2  | Sub-header 3  | Sub-header 4  |
| Data 1        | Data 2        | Data 3        | Data 4        |

```

A table with 3 rows and 4 columns can have headers that span multiple columns. Merged cells like these are handled by the wrapper to ensure accurate representation in the Markdown format.


## Handling Complex Tables with Merged Cells

### Initial Table
```
| Header 1      | Header 1      | Header 2      | Header 2      |
|---------------|---------------|---------------|---------------|
| Data 1        | Data 2        | Data 3        | Data 4        |
```

### Modified Table with Merged Columns

```
| Header 1            | Header 2      | Header 2      |
|---------------------|---------------|---------------|
| Data 1 , Data 2     | Data 3        | Data 4        |
```

- ***NOTE : By merging identical headers, Large Language Models (LLMs) can more effectively interpret and extract relevant information from tables, reducing ambiguity and improving the accuracy of data extraction and analysis.***


## Error Handling

- Authentication Errors: Ensure your Azure endpoint and API key are correctly configured. If you encounter authentication issues, double-check your credentials.
- File Not Found: If the specified file path is incorrect, you will receive a file not found error. Ensure the path is correct and the file exists.
- Unsupported Document Format: The package is designed to handle PDF,JPEG,PNG file. If other formats are used, it may result in unexpected behavior.


## Advantages

- Ease of Use: Simplifies interaction with the Azure Document Intelligence API.
- Flexibility: Handles various document structures, including complex table layouts with merged cells.
- Markdown Format: Produces outputs in Markdown, making it easy to integrate with other text-processing tools and workflows.
- Scalable and Maintainable: Well-structured code, ready for production environments, with proper logging and error handling.

## Future Enhancements

- Support for Other Formats: Extend support to handle different document types.
- More Detailed Logging: Incorporate more granular logging for better traceability.
- Custom Table Styling: Allow customization of Markdown table styles based on user requirements.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or report issues.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
