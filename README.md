# 项目说明文档

## 项目背景

随着学术研究的快速发展，研究人员需要阅读大量的学术论文以获取最新的研究成果。然而，论文数量庞大且内容复杂，手动阅读和总结耗时耗力。为了提高研究效率，本项目旨在利用人工智能技术，自动总结学术论文的核心内容，提取关键词，并提供相关论文的推荐链接。通过这种方式，研究人员可以快速了解论文的核心思想，并进一步探索相关领域的研究。

## 设计思路

本项目采用LangChain框架，结合自然语言处理（NLP）技术，实现对学术论文的自动总结和关键词提取。具体设计思路如下：

1. **论文解析**：通过OCR技术将PDF格式的论文转换为文本格式，确保能够处理包含图像或扫描件的论文。
2. **文本处理**：利用LangChain的文本处理模块，对论文文本进行分段、清理和预处理，确保后续分析的准确性。
3. **关键词提取**：使用NLP算法（如RAKE、YAKE等）从论文中提取关键词，帮助用户快速了解论文的核心主题。
4. **论文总结**：基于LangChain的文本生成模型，生成论文的简要总结，突出论文的主要贡献和研究方法。
5. **相关论文推荐**：通过关键词匹配和语义分析，推荐与当前论文相关的其他论文，并提供链接，方便用户进一步阅读。

## 技术实现

### 1. 文件上传与处理

#### 功能描述
用户通过前端页面上传论文文件（支持 `.txt` 和 `.pdf` 格式），后端接收文件并进行处理。

#### 技术实现
- **框架**：使用 `FastAPI` 构建后端服务，支持文件上传和异步处理。
- **文件处理**：
  - 对于 `.txt` 文件，直接读取文本内容。
  - 对于 `.pdf` 文件，调用 `pdf2image` 和 `pytesseract` 进行 OCR 处理，将 PDF 转换为可搜索的文本。
- **多线程处理**：使用 `threading` 模块并行处理文本总结和相关论文推荐任务，以提高效率。

#### 核心代码
```python
@app.post("/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    file_path = None
    try:
        file_path = file.filename
        with open(file.filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        results = {}
        text_thread = threading.Thread(target=process_text, args=(file_path, results))
        publications_thread = threading.Thread(target=fetch_publications, args=(file_path, results))

        text_thread.start()
        publications_thread.start()

        text_thread.join()
        publications_thread.join()

        if "summary" not in results or "keywords" not in results:
            raise Exception("Error during text processing.")

        publications_json = json.dumps(results.get("publications", []))
        encoded_publications = quote_plus(publications_json)

        keywords_json = json.dumps(results.get("keywords", []))
        encoded_keywords = quote_plus(keywords_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail="An error occurred while processing the file.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return RedirectResponse(
        url=f"/result?summary={quote_plus(results.get('summary', ''))}&publications={encoded_publications}&keywords={encoded_keywords}",
        status_code=303,
    )
```

---

### 2. 文本解析与总结

#### 功能描述
对上传的论文文本进行解析，并生成简洁的总结。

#### 技术实现
- **文本解析**：
  - 使用 `PyPDFLoader` 解析 PDF 文件，或直接读取 `.txt` 文件。
  - 使用 `RecursiveCharacterTextSplitter` 将文本分割为适合处理的段落。
- **文本总结**：
  - 使用 `LangChain` 的 `RetrievalQA` 模块，结合 OpenAI 的 GPT-3.5 模型生成文本总结。
  - 通过 `map_reduce` 方法对长文本进行分段处理，确保总结的准确性和完整性。

#### 核心代码
```python
def text_summarization(path: str) -> str:
    _, file_extension = os.path.splitext(path)
    document = []

    if file_extension == '.txt':
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()
        document = [Document(page_content=text)]
    elif file_extension == '.pdf':
        txt_path = convert_images_to_searchable_txt(path)
        with open(txt_path, 'r', encoding='utf-8') as txt_file:
            text = txt_file.read()
        document = [Document(page_content=text)]

    embeddings = OpenAIEmbeddings(openai_api_key="your-api-key")
    docsearch = Chroma.from_documents(document, embeddings)

    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model='gpt-3.5-turbo', temperature=0.0, max_tokens=2000),
        chain_type='map_reduce',
        retriever=docsearch.as_retriever(),
        return_source_documents=True
    )

    questions_list = ["总结这篇论文，用中文回答"]
    summary = ""
    for question in questions_list:
        result = chain.invoke({'query': f'{question} 将你的描述尽可能拓展细节.'})
        summary += " ".join(result.get('result', ''))

    return summary
```

---

### 3. 关键词提取

#### 功能描述
从论文文本中提取关键词，用于后续的相关论文推荐。

#### 技术实现
- **关键词提取算法**：
  - 使用 `YAKE!` 算法提取关键词，支持多语言（包括中文和英文）。
  - 提取的关键词用于后续的论文推荐。
- **OCR 支持**：
  - 对于 PDF 文件，先通过 OCR 转换为文本，再进行关键词提取。

#### 核心代码
```python
def search_keyphrases(path: str) -> list[str]:
    _, file_extension = os.path.splitext(path)

    if file_extension == '.txt':
        with open(path, "r", encoding="utf-8") as open_file:
            text = open_file.read()
    elif file_extension == '.pdf':
        txt_path = convert_images_to_searchable_txt(path)
        with open(txt_path, 'r', encoding='utf-8') as txt_file:
            text = txt_file.read()

    kw_extractor = yake.KeywordExtractor()
    keywords = kw_extractor.extract_keywords(text)
    keyphrases = [kw for kw, _ in keywords[:6]]
    return keyphrases
```

---

### 4. 相关论文推荐

#### 功能描述
根据提取的关键词，从 Semantic Scholar 中获取相关论文的标题、作者、发布日期和链接。

#### 技术实现
- **API 调用**：
  - 使用 `Semantic Scholar API` 查询相关论文。
  - 通过关键词和年份范围过滤结果。
- **数据解析**：
  - 解析 API 返回的 JSON 数据，提取论文的标题、作者、发布日期和链接。
- **多关键词支持**：
  - 如果单个关键词无法找到相关论文，尝试使用多个关键词分别查询。

#### 核心代码
```python
class SemanticScholarScraper:
    def get_related_publications(self, keywords: list[str], min_year: int = 2015, max_year: int = 2024):
        semanticscholar_response = self.get_semanticscholar_response(keywords, min_year=min_year, max_year=max_year)
        parsed_response = self.parse_html_response(semanticscholar_response)
        return parsed_response

    def parse_html_response(self, response: requests.Response) -> list[dict[str, str]]:
        response_json = response.json()
        final_result = []
        for result in response_json["results"]:
            publication = {
                "title": result["title"]["text"],
                "link": result["primaryPaperLink"]["url"] if "primaryPaperLink" in result else "no_link_found",
                "authors": self.get_authors(result),
                "publication_date": result.get("pubDate", result.get('year', {}).get("text"))
            }
            final_result.append(publication)
        return final_result
```

---

### 5. 前端展示

#### 功能描述
将生成的论文总结、关键词和相关论文推荐展示给用户。

#### 技术实现
- **前端框架**：使用 `Jinja2` 模板引擎渲染 HTML 页面。
- **数据传递**：通过 URL 参数将结果传递给前端页面。
- **页面设计**：简洁的界面设计，方便用户查看结果。

#### 核心代码
```python
@app.get("/result", response_class=HTMLResponse)
async def result(request: Request, summary: str, publications: str, keywords: str):
    decoded_publications = json.loads(unquote_plus(publications))
    decoded_keywords = json.loads(unquote_plus(keywords))
    return templates.TemplateResponse(
        "result_page.html",
        {
            "request": request,
            "summary": summary,
            "publications": decoded_publications,
            "keywords": decoded_keywords,
        },
    )
```

### 6.额外需求

1. **Tesseract OCR**：用于将PDF中的图像转换为文本。安装Tesseract后，需在`utils/pdf_ocr.py`文件中指定`tesseract.exe`的路径。
2. **Poppler**：用于PDF文件的解析。安装Poppler后，需在`utils/pdf_ocr.py`文件中指定`poppler\\Library\\bin`路径。

### 7.主要技术栈

- **LangChain**：用于文本处理和生成论文总结。
- **NLP工具**：如RAKE、YAKE等，用于关键词提取。
- **OCR技术**：Tesseract用于图像文本识别。
- **PDF解析**：Poppler用于PDF文件的解析。

## 团队分工

1. **邓博昊**：代码编写 代码DEBUG 参与问辩
1. **严子超**：代码测试 PPT制作 参与问辩
1. **蒋云辉**： 参与问辩

## 总结

本项目通过结合LangChain和NLP技术，实现了对学术论文的自动总结和关键词提取，帮助研究人员快速获取论文的核心内容。通过团队的分工合作，确保了项目的高效推进和高质量交付。
