from pdf2image import convert_from_path
import pytesseract
import platform
import logging
import os

# 设置 Tesseract 路径（仅 Windows 需要）
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def convert_images_to_searchable_txt(pdf_path: str) -> str:
    """
    将 PDF 转换为可搜索的文本文件
    :param pdf_path: 输入的 PDF 文件路径
    :return: 返回生成的 .txt 文件路径
    """
    try:
        # 将 PDF 转换为图像
        logging.info(f"Converting PDF to images: {pdf_path}")
        if platform.system() == "Windows":
            images = convert_from_path(pdf_path, poppler_path="C:\\Program Files\\poppler-24.08.0\\Library\\bin")
        else:
            images = convert_from_path(pdf_path)
        logging.info(f"Number of pages: {len(images)}")

        # 创建输出 .txt 文件路径
        txt_path = os.path.splitext(pdf_path)[0] + "_extracted.txt"

        # 打开 .txt 文件并写入提取的文本
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            # 遍历每一张图像并提取文本
            for i, image in enumerate(images):
                logging.info(f"Processing page {i + 1}/{len(images)}")

                # 使用 PyTesseract 提取文本
                text = pytesseract.image_to_string(
                    image,
                    lang='eng+chi_sim',  # 支持中英文
                    config='--psm 6 --oem 1'  # 优化 OCR 参数
                )
                logging.info(f"Extracted text from page {i + 1}")

                # 将提取的文本写入 .txt 文件
                txt_file.write(text + "\n")

        logging.info(f"Extracted text saved to {txt_path}")
        return txt_path

    except Exception as e:
        logging.error(f"Error during PDF OCR: {e}")
        raise


# 示例调用
#convert_images_to_searchable_pdf("input.pdf", "output_searchable.pdf")