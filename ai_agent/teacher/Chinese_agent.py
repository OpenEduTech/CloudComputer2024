import re
from pathlib import Path

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from language_tool_python import LanguageTool
from transformers import pipeline

from config import model


# 从 txt 文件中加载诗词知识库，并解析为字典格式
# 字典的键是 "数字_作者_诗名"，值是诗词内容
def load_poetry_knowledge_base(file_path: str) -> dict:
    knowledge_base = {}
    current_title = None
    current_content = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:  # 跳过空行
                    continue
                if line.startswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")) and "_" in line:
                    # 如果当前有正在处理的诗词，保存到知识库
                    if current_title and current_content:
                        knowledge_base[current_title] = "\n".join(current_content)
                        current_content = []
                    # 新的诗词标题
                    current_title = line
                else:
                    # 诗词内容
                    current_content.append(line)

            # 处理最后一首诗词
            if current_title and current_content:
                knowledge_base[current_title] = "\n".join(current_content)
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到。")
    except Exception as e:
        print(f"加载知识库时发生错误：{e}")

    return knowledge_base


# 获取当前脚本所在的目录
current_directory = Path(__file__).parent

file_path = current_directory / "poetry_knowledge_base.txt"
if not file_path.exists():
    print(f"错误：文件 {file_path} 不存在。")

# 加载知识库
knowledge_base = load_poetry_knowledge_base(current_directory / "poetry_knowledge_base.txt")

# 添加TavilySearchResults工具
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = model
llm_with_tools = llm.bind_tools(tools)

# 初始化语法检查工具
grammar_checker = LanguageTool('zh-CN')

# 初始化中文情感分析器和分词器
emotion_classifier = pipeline("text-classification", model="bert-base-chinese")

# 截断输入文本到 512 个 token
tokenizer = emotion_classifier.tokenizer
max_length = 512

# 初始化记忆保存器
memory_saver = MemorySaver()


# 从知识库中检索与查询相关的诗词内容
def retrieve_poetry_from_knowledge_base(query: str, knowledge_base: dict) -> str:
    # 遍历知识库，查找匹配的诗词
    for title, content in knowledge_base.items():
        if query in title or query in content:
            return f"{title}\n{content}"

    return "未找到相关诗词内容。"


def analyze_poetry(state: MessagesState):
    # print('analyze_poetry')
    user_message = state["messages"][-2].content

    # 检查用户输入中是否包含“诗词”
    if "诗词" in user_message:
        # 使用正则表达式提取关键词（去除“诗词”和标点符号）
        query = re.sub(r"[诗词：]", "", user_message).strip()

        # 从知识库中检索诗词内容
        poetry_content = retrieve_poetry_from_knowledge_base(query, knowledge_base)
        # print(poetry_content)

        # 将检索到的诗词内容添加到消息中
        state["messages"].append(HumanMessage(content=f"检索到的诗词内容：\n{poetry_content}"))

        # 设置下一个节点为生成回复
        state["next_node"] = "generate_response"
    else:
        # 如果用户输入中不包含“诗词”，则直接进入生成回复环节
        state["next_node"] = "generate_response"

    return state


# 上下文（截取部分）
def truncate_context(messages, max_length=10):
    if len(messages) > max_length:
        return messages[-max_length:]
    return messages


# 情感分析
def analyze_emotion(state: MessagesState):
    # print('analyze_emotion')
    user_message = state["messages"][-1].content

    # 去除换行符和多余的空白字符
    cleaned_message = user_message.replace('\n', ' ').strip()

    # 使用分词器截断输入文本
    inputs = tokenizer(user_message, return_tensors="pt", truncation=True, max_length=max_length)

    # 将截断后的文本重新组合为字符串
    truncated_message = tokenizer.decode(inputs['input_ids'][0], skip_special_tokens=True)

    # 使用中文情感分析器进行情感分析
    emotion_result = emotion_classifier(truncated_message)[0]
    emotion_label = emotion_result["label"]
    emotion_score = emotion_result["score"]

    # 根据情感调整回复
    if emotion_label == "POSITIVE" or emotion_score > 0.6:  # 假设标签为积极或分数大于0.6为积极
        tone = "愉快"
    elif emotion_label == "NEGATIVE" or emotion_score < 0.4:  # 假设标签为消极或分数小于0.4为消极
        tone = "关心"
    else:
        tone = "中立"
    # print(f"情感分析结果: {emotion_label}, 分数: {emotion_score}, 语气: {tone}")

    state["messages"].append(HumanMessage(content=f"根据我的语气，你将以 {tone} 的方式回应。"))

    match1 = re.search(r'诗词', cleaned_message, re.IGNORECASE)
    # print(match1)

    if match1:
        state["next_node"] = "analyze_poetry"
    else:
        match2 = re.search(r'作文(评分)?', cleaned_message, re.IGNORECASE)
        # print(f"Regex match result: {match2}")  # 打印匹配结果
        if match2:
            state["next_node"] = "evaluate_essay"
        else:
            state["next_node"] = "generate_response"

    return state


# 评分标准
def select_evaluation_standard(state: MessagesState):
    # print('select_evaluation_standard')
    user_message = state["messages"][-3].content
    # 计算字数
    word_count = len(user_message)
    # print(word_count)

    # 获取当前脚本所在的目录
    current_directory = Path(__file__).parent

    # 提取用户输入中的关键词
    if "小学" in user_message:
        # print("小学")
        standard = "小学"
        criteria_file = current_directory / "primary_school_chinese_criteria.txt"  # 小学评分标准文件
    elif "初中" in user_message:
        # print("初中")
        standard = "初中"
        criteria_file = current_directory / "middle_school_chinese_criteria.txt"  # 初中评分标准文件
    elif "高中" in user_message:
        # print("高中")
        standard = "高中"
        criteria_file = current_directory / "high_school_chinese_criteria.txt"  # 高中评分标准文件
    else:
        # 如果用户未明确指定，则由模型判定作文阶段
        essay_text = state["messages"][-2].content  # 获取作文内容

    # 读取评分标准文件
    try:
        with open(criteria_file, "r", encoding="utf-8") as file:
            criteria = file.read()
    except FileNotFoundError:
        criteria = f"未找到 {standard} 的评分标准文件。"

    # print(criteria)

    # 将评分标准添加到消息中
    state["messages"].append(HumanMessage(
        content=f"作文字数：{word_count}。一定要按照评分标准批改作文。请务必遵守<一定要按照评分标准批改作文>。评分标准：{criteria}"))

    return state


# 初步检查
def evaluate_essay(state: MessagesState):
    # print('evaluate_essay')
    essay_text = state["messages"][-2].content.replace("作文：", "")
    evaluation_result = grammar_checker.check(essay_text)

    suggestions = [match.message for match in evaluation_result]

    wrong = len(evaluation_result)

    # print(f"Essay suggestions: {suggestions}")

    # 返回评分和建议
    state["messages"].append(
        HumanMessage(content=f"经过初步检查，错误有 {wrong} 处。改进建议：\n" + "\n".join(suggestions)))

    # 返回更新后的状态
    return state


# 作文批改结论
def generate_response_essay(state: MessagesState):
    # print('generate_response_essay')

    # 再加上搜索，信息太多，影响评分
    '''
    user_message = state["messages"][-4].content
    print(user_message)
    
    # 使用 TavilySearchResults 检索用户输入
    search_results = tool.invoke({"query": user_message})
    context = "\n".join([result["content"] for result in search_results])
    print(context)
    
    # 将检索到的背景信息添加到消息中
    state["messages"].append(HumanMessage(content=f"背景信息：{context}"))
    '''

    # 上下文
    truncated_messages = truncate_context(state["messages"])

    model_output = model.invoke(truncated_messages)

    # 打印 model_output 的内容，检查其结构
    print("Model output:", model_output)

    # 根据 model_output 的类型进行不同处理
    if isinstance(model_output, AIMessage):
        # 如果 model_output 是 AIMessage，直接使用它的 content
        response_content = model_output.content
    elif isinstance(model_output, dict) and 'content' in model_output:
        # 如果 model_output 是字典，提取其中的 'content' 字段
        response_content = model_output['content']

    # 将提取的内容封装为 AIMessage
    state["messages"].append(AIMessage(content=response_content))

    # 返回更新后的消息列表
    return {"messages": state["messages"]}


# 诗词问题
def generate_response_poetry(state: MessagesState):
    # print('generate_response_poetry')
    user_message = state["messages"][-3].content
    # print(user_message)

    # 使用 TavilySearchResults 检索用户输入
    search_results = tool.invoke({"query": user_message})
    context = "\n".join([result["content"] for result in search_results])
    # print(context)

    # 将检索到的背景信息添加到消息中
    state["messages"].append(HumanMessage(content=f"背景信息：{context}"))

    # 上下文
    truncated_messages = truncate_context(state["messages"])

    # 调用模型生成回复
    model_output = model.invoke(truncated_messages)

    # 打印 model_output 的内容，检查其结构
    print("Model output:", model_output)

    # 根据 model_output 的类型进行不同处理
    if isinstance(model_output, AIMessage):
        # 如果 model_output 是 AIMessage，直接使用它的 content
        response_content = model_output.content
    elif isinstance(model_output, dict) and 'content' in model_output:
        # 如果 model_output 是字典，提取其中的 'content' 字段
        response_content = model_output['content']

    # 将提取的内容封装为 AIMessage
    state["messages"].append(AIMessage(content=response_content))

    # 返回更新后的消息列表
    return {"messages": state["messages"]}


# 其他问题
def generate_response(state: MessagesState):
    # print('generate_response')
    user_message = state["messages"][-2].content
    # print(user_message)

    # 使用 TavilySearchResults 检索用户输入
    search_results = tool.invoke({"query": user_message})
    context = "\n".join([result["content"] for result in search_results])
    # print(context)

    # 将检索到的背景信息添加到消息中
    state["messages"].append(HumanMessage(content=f"背景信息：{context}"))

    # 上下文
    truncated_messages = truncate_context(state["messages"])

    # 调用模型生成回复
    model_output = model.invoke(truncated_messages)

    # 打印 model_output 的内容，检查其结构
    print("Model output:", model_output)

    # 根据 model_output 的类型进行不同处理
    if isinstance(model_output, AIMessage):
        # 如果 model_output 是 AIMessage，直接使用它的 content
        response_content = model_output.content
    elif isinstance(model_output, dict) and 'content' in model_output:
        # 如果 model_output 是字典，提取其中的 'content' 字段
        response_content = model_output['content']

    # 将提取的内容封装为 AIMessage
    state["messages"].append(AIMessage(content=response_content))

    # 返回更新后的消息列表
    return {"messages": state["messages"]}


# 定义预训练函数
def pretrain_chinese_teacher():
    # 预训练数据
    pretrain_data = [
        {"messages": [HumanMessage(content="你是语文老师。"), AIMessage(content="是的，我是一个语文老师。")]},
        {"messages": [HumanMessage(content="你好吗？"), AIMessage(content="我很好，谢谢！")]},
        {"messages": [HumanMessage(content="你的名字是什么？"), AIMessage(content="我是一个语文学习AI助手。")]},
        # 添加更多预训练数据
    ]
    for data in pretrain_data:
        model.invoke(data["messages"])


# 调用预训练函数
pretrain_chinese_teacher()

# 定义语文老师的graph
workflow_chinese = StateGraph(state_schema=MessagesState)

# 添加节点
workflow_chinese.add_node("start", lambda state: {"messages": state["messages"]})
workflow_chinese.add_node("analyze_emotion", analyze_emotion)
workflow_chinese.add_node("evaluate_essay", evaluate_essay)
workflow_chinese.add_node("select_evaluation_standard", select_evaluation_standard)
workflow_chinese.add_node("analyze_poetry", analyze_poetry)
workflow_chinese.add_node("generate_response", generate_response)
workflow_chinese.add_node("generate_response_essay", generate_response_essay)
workflow_chinese.add_node("generate_response_poetry", generate_response_poetry)

tool_node = ToolNode(tools=[tool])
workflow_chinese.add_node("tools", tool_node)

# 添加边
workflow_chinese.add_edge(START, "analyze_emotion")
workflow_chinese.add_conditional_edges(
    "analyze_emotion",
    lambda state: state.get("next_node", "generate_response")
)
workflow_chinese.add_edge("evaluate_essay", "select_evaluation_standard")
workflow_chinese.add_edge("select_evaluation_standard", "generate_response_essay")
workflow_chinese.add_edge("analyze_poetry", "generate_response_poetry")

# 编译工作流
app_chinese = workflow_chinese.compile(checkpointer=memory_saver)
