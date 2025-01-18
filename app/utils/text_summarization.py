import os
from rake_nltk import Rake  # 引入 RAKE 库
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.schema import Document  # 引入 Document 类

from app.utils.pdf_ocr import convert_images_to_searchable_txt


def text_summarization(path: str) -> str:
    _, file_extension = os.path.splitext(path)
    document = []

    if file_extension == '.txt':
        try:
            with open(path, "r", encoding="utf-8") as file:
                text = file.read()
            document = [Document(page_content=text)]
        except UnicodeDecodeError:
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                text = file.read()
            document = [Document(page_content=text)]
    elif file_extension == '.pdf':
        # 调用 convert_images_to_searchable_txt 函数将 PDF 转换为 .txt 文件
        txt_path = convert_images_to_searchable_txt(path)

        # 读取生成的 .txt 文件内容
        with open(txt_path, 'r', encoding='utf-8') as txt_file:
            text = txt_file.read()

        # 将文本包装成 Document 对象
        document = [Document(page_content=text)]

        # 如果 document 为空，可以尝试其他处理方式
        if len(document[0].page_content) == 0:
            # 这里可以添加其他处理逻辑，比如直接调用 OCR 或其他方法
            pass
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    if not document:
        raise ValueError("Failed to load document.")

    rake = Rake()
    text = ' '.join([doc.page_content for doc in document])
    rake.extract_keywords_from_text(text)
    keyphrases = rake.get_ranked_phrases()[:6]

    embeddings = OpenAIEmbeddings(
        openai_api_key="sk-Gzt7jeW0qTEI42iaYhkLtsCzkSFO3UDXkkzAoCbLrpIzxr8r",
        openai_api_base="https://chatapi.littlewheat.com/v1"
    )

    docsearch = Chroma.from_documents(document, embeddings)

    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(
            model='gpt-3.5-turbo',
            openai_api_key="sk-Gzt7jeW0qTEI42iaYhkLtsCzkSFO3UDXkkzAoCbLrpIzxr8r",
            openai_api_base="https://chatapi.littlewheat.com/v1",
            temperature=0.0,
            max_tokens=2000
        ),
        chain_type='map_reduce',
        retriever=docsearch.as_retriever(),
        return_source_documents=True
    )

    # 生成摘要
    questions_list = ["总结这篇论文，用中文回答"]
    summary = ""
    for question in questions_list:
        try:
            result = chain.invoke({'query': f'{question} 将你的描述尽可能拓展细节.'})

            # 强制将 result 转换为列表
            if isinstance(result, dict):
                result_list = [result.get('result', '')]  # 将字典的值转换为列表
            elif isinstance(result, str):
                result_list = [result]  # 将字符串转换为列表
            else:
                result_list = list(result)  # 强制转换为列表

            # 将列表中的内容合并到 summary
            summary += " ".join(result_list)  # 将列表中的元素拼接为字符串

        except Exception as e:
            print(f"处理问题时出错: {question}. 错误: {e}")

    # 保存结果
    content = f"## 摘要:\n{summary}\n"
    with open("../app/result.txt", "w+", encoding="utf-8") as file:
        file.write(content)

    return summary


if __name__ == "__main__":
    # 示例调用
    path_to_file = "examples/summ_text.txt"
    print(text_summarization(path_to_file))