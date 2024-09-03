
# document_intelligence_wrapper/extractors/helpers.py

def calculate_confidence_score(paragraph, data):
    """
    Calculate both the simple average and weighted average confidence scores for a given paragraph.
    
    :param paragraph: A dictionary containing the paragraph's content and boundingRegions.
    :param data: A dictionary containing data including words and other paragraphs.
    :return: A tuple of (simple average confidence, weighted average confidence).
    """
    # Get the polygon of the current paragraph
    para_polygon = paragraph['boundingRegions'][0]['polygon']
    words_in_paragraph = []

    # Iterate over each word in the data to check if it belongs to the current paragraph
    for page in data['pages']:
        for word in page['words']:
            word_polygon = word['polygon']

            # Check if word polygon is within paragraph polygon
            if is_polygon_inside(para_polygon, word_polygon):
                words_in_paragraph.append((word['confidence'], len(word['content'])))

    # Calculate the simple average confidence score
    if words_in_paragraph:
        simple_confidence = sum(confidence for confidence, _ in words_in_paragraph) / len(words_in_paragraph)
    else:
        simple_confidence = 0  # No words found, default to zero confidence

    # Calculate the weighted average confidence score
    total_weight = sum(length for _, length in words_in_paragraph)
    if total_weight > 0:
        weighted_confidence = sum(confidence * length for confidence, length in words_in_paragraph) / total_weight
    else:
        weighted_confidence = 0  # No words found, default to zero confidence

    # Ensure confidence scores do not exceed 1
    simple_confidence = min(simple_confidence, 1)
    weighted_confidence = min(weighted_confidence, 1)

    return simple_confidence, weighted_confidence


def is_polygon_inside(para_polygon, word_polygon):
    """
    This function checks if a word's polygon is inside a paragraph's polygon.
    It is a simplified check assuming polygon points are ordered and paragraph polygon fully contains the word polygon.
    """
    # Check if all word polygon points are inside paragraph polygon bounds
    min_x_para = min(para_polygon[0::2])
    max_x_para = max(para_polygon[0::2])
    min_y_para = min(para_polygon[1::2])
    max_y_para = max(para_polygon[1::2])

    min_x_word = min(word_polygon[0::2])
    max_x_word = max(word_polygon[0::2])
    min_y_word = min(word_polygon[1::2])
    max_y_word = max(word_polygon[1::2])

    return (min_x_para <= min_x_word and max_x_para >= max_x_word and
            min_y_para <= min_y_word and max_y_para >= max_y_word)

def calculate_cell_confidence_score(cell, data):
    """
    Calculate both the simple average and weighted average confidence scores for a given cell.
    
    :param cell: A dictionary containing the cell's content and boundingRegions.
    :param data: A dictionary containing data including words and other paragraphs.
    :return: A tuple of (simple average confidence, weighted average confidence).
    """
    cell_polygon = cell['boundingRegions'][0]['polygon']
    words_in_cell = []

    # Iterate over each word in the data to check if it belongs to the current cell
    for page in data['pages']:
        for word in page['words']:
            word_polygon = word['polygon']

            # Check if word polygon is within cell polygon
            if is_polygon_inside(cell_polygon, word_polygon):
                words_in_cell.append((word['confidence'], len(word['content'])))

    # Calculate the simple average confidence score
    if words_in_cell:
        simple_confidence = sum(confidence for confidence, _ in words_in_cell) / len(words_in_cell)
    else:
        simple_confidence = 0  # No words found, default to zero confidence

    # Calculate the weighted average confidence score
    total_weight = sum(length for _, length in words_in_cell)
    if total_weight > 0:
        weighted_confidence = sum(confidence * length for confidence, length in words_in_cell) / total_weight
    else:
        weighted_confidence = 0  # No words found, default to zero confidence

    # Ensure confidence scores do not exceed 1
    simple_confidence = min(simple_confidence, 1)
    weighted_confidence = min(weighted_confidence, 1)

    return simple_confidence, weighted_confidence