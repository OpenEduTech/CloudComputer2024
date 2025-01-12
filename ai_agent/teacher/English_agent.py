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

# 添加TavilySearchResults工具
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = model
llm_with_tools = llm.bind_tools(tools)

# 初始化语法检查工具
grammar_checker = LanguageTool('en-US')

# 初始化情感分析器和分词器
emotion_classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english",
                              tokenizer="distilbert-base-uncased")

# 截断输入文本到 512 个 token
tokenizer = emotion_classifier.tokenizer
max_length = 512

# 初始化记忆保存器
memory_saver = MemorySaver()


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

    # 使用截断后的文本进行情感分析
    emotion_result = emotion_classifier(truncated_message)[0]
    emotion_label = emotion_result["label"]

    # 根据情感调整回复
    if emotion_label == "POSITIVE":
        tone = "愉快"
    elif emotion_label == "NEGATIVE":
        tone = "关心"
    else:
        tone = "中立"
    # print(tone)

    state["messages"].append(HumanMessage(content=f"根据我的语气，你将以 {tone} 的方式回应。"))

    match = re.search(r'作文(评分)?', cleaned_message, re.IGNORECASE)
    # print(f"Regex match result: {match}")  # 打印匹配结果
    if match:
        state["next_node"] = "evaluate_essay"
    else:
        state["next_node"] = "generate_response"

    return state


# 评分标准
def select_evaluation_standard(state: MessagesState):
    # print('select_evaluation_standard')
    user_message = state["messages"][-3].content

    # 获取当前脚本所在的目录
    current_directory = Path(__file__).parent

    # 提取用户输入中的关键词
    if "小学" in user_message:
        # print("小学")
        standard = "小学"
        criteria_file = current_directory / "primary_school_english_criteria.txt"  # 小学评分标准文件
    elif "初中" in user_message:
        # print("初中")
        standard = "初中"
        criteria_file = current_directory / "middle_school_english_criteria.txt"  # 初中评分标准文件
    elif "高中" in user_message:
        # print("高中")
        standard = "高中"
        criteria_file = current_directory / "high_school_english_criteria.txt"  # 高中评分标准文件
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
    state["messages"].append(
        HumanMessage(content=f"一定要按照评分标准批改作文。请务必遵守<一定要按照评分标准批改作文>。评分标准：{criteria}"))

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
def pretrain_english_teacher():
    # 预训练数据
    pretrain_data = [
        {"messages": [HumanMessage(content="你是英语老师。"), AIMessage(content="是的，我是一个英语老师。")]},
        {"messages": [HumanMessage(content="请确保回答问题的时候全部使用英语回答"),
                      AIMessage(content="Okay, I'll do that")]},
        {"messages": [HumanMessage(content="How are you?"), AIMessage(content="I'm fine, thank you!")]},
        {"messages": [HumanMessage(content="What is your name?"), AIMessage(content="I am an AI assistant.")]},
        # 添加更多预训练数据
    ]
    for data in pretrain_data:
        model.invoke(data["messages"])


# 调用预训练函数
pretrain_english_teacher()

# 定义英语老师的graph
workflow_english = StateGraph(state_schema=MessagesState)

# 添加初始节点
workflow_english.add_node("start", lambda state: {"messages": state["messages"]})

# 添加情感分析节点
workflow_english.add_node("analyze_emotion", analyze_emotion)

# 添加作文评估节点
workflow_english.add_node("evaluate_essay", evaluate_essay)

# 添加选择评分标准节点
workflow_english.add_node("select_evaluation_standard", select_evaluation_standard)

# 添加生成模型回复节点
workflow_english.add_node("generate_response", generate_response)

# 添加生成模型回复节点
workflow_english.add_node("generate_response_essay", generate_response_essay)

# 添加工具节点
tool_node = ToolNode(tools=[tool])
workflow_english.add_node("tools", tool_node)

# 初始边
workflow_english.add_edge(START, "analyze_emotion")

# 添加状态转移边
workflow_english.add_conditional_edges(
    "analyze_emotion",
    lambda state: state.get("next_node", "generate_response")
)

# 添加从 evaluate_essay 到 select_evaluation_standard 的边
workflow_english.add_edge("evaluate_essay", "select_evaluation_standard")

# 添加从 select_evaluation_standard 到 generate_response 的边
workflow_english.add_edge("select_evaluation_standard", "generate_response_essay")

# 编译工作流
app_english = workflow_english.compile(checkpointer=memory_saver)
