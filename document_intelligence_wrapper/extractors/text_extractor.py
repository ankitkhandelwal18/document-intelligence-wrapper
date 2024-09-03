# document_intelligence_wrapper/extractors/pdf_text_extractor.py

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, ContentFormat, AnalyzeResult
from document_intelligence_wrapper.extractors.document_processor import process_document
from document_intelligence_wrapper.extractors.extract_utils import extract_page_text

def analyze_document_text(client, file_path: str, calculate_confidence: bool = True, calculate_cell_confidence: bool = False) -> dict:
    """
    Extracts text from a file using Azure Document Intelligence and processes the result.

    Args:
        client (DocumentIntelligenceClient): The Azure Document Intelligence client.
        pdf_file_path (str): The file path to the PDF document.
        calculate_confidence (bool): Flag to calculate confidence scores for paragraphs, tables, and figures. Default is True.
        calculate_cell_confidence (bool): Flag to calculate confidence scores for individual table cells. Default is False.

    Returns:
        tuple: A tuple containing:
            - page_text (dict): A dictionary where keys are page numbers and values are lists of element identifiers in order.
            - table_text (dict): A dictionary with table content keyed by a unique table identifier.
            - full_doc_text_combined (str): A string representing the full text of the document, combining all pages.
            - all_page_elements (list): A list of JSON objects representing the details of each element on each page.
            - ocr_json (AnalyzeResult): The raw OCR result from the Azure Document Intelligence API.
    
    Supported Formats:
        - PDF
        - Image: JPEG/JPG, PNG, BMP, TIFF, HEIF
        - Microsoft Office: Word (DOCX)

    """
    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(
            model_id="prebuilt-layout",
            analyze_request=f,
            output_content_format=ContentFormat.MARKDOWN,
            content_type="application/octet-stream",
        )

    ocr_result: AnalyzeResult = poller.result()

    print("ocr_result",ocr_result)

    # Process the document to extract page sections and figure associations
    page_section, figure_associations = process_document(ocr_result)

    print("page_section",page_section)
    print("figure_associations",figure_associations)

    # Extract page text with the option to calculate confidence scores based on flags
    page_text, table_text, doc_text, all_page_elements = extract_page_text(
        ocr_result,
        page_section,
        figure_associations,
        calculate_confidence=calculate_confidence,
        calculate_cell_confidence=calculate_cell_confidence
    )

    return page_text, table_text, doc_text, all_page_elements, ocr_result
