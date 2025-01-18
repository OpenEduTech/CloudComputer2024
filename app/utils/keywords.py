import os
import yake
from app.utils.pdf_ocr import convert_images_to_searchable_txt  # 引入 PDF OCR 函数


def search_keyphrases(path: str) -> list[str]:
    """ Extracts keywords from the text using YAKE! algorithm.
    Args:
        path (str): Path to the text file.
    Returns:
        keyphrases (list): List of keyphrases extracted from the text.
    """
    _, file_extension = os.path.splitext(path)

    if file_extension == '.txt':
        with open(path, "r", encoding="utf-8") as open_file:
            text = open_file.read()
    elif file_extension == '.pdf':
        # 调用 convert_images_to_searchable_txt 函数将 PDF 转换为 .txt 文件
        txt_path = convert_images_to_searchable_txt(path)

        # 读取生成的 .txt 文件内容
        with open(txt_path, 'r', encoding='utf-8') as txt_file:
            text = txt_file.read()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    # Initialize YAKE! keyword extractor
    kw_extractor = yake.KeywordExtractor()

    # Extract keywords
    keywords = kw_extractor.extract_keywords(text)

    # Get the top 6 keyphrases
    keyphrases = [kw for kw, _ in keywords[:6]]
    return keyphrases


if __name__ == "__main__":
    path_to_file = "examples/summ_text.txt"
    print(search_keyphrases(path_to_file))