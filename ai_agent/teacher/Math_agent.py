from config import model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults
import re
import csv
from pathlib import Path

# 定义数学老师的graph
workflow_math = StateGraph(state_schema=MessagesState)

current_directory = Path(__file__).parent
def load_problem_solutions(file_path=current_directory / "math_problem_solutions.csv"):
    problem_solutions = {}
    with open(file_path, mode="r", encoding="utf-8",errors='ignore') as file: 
        reader = csv.reader(file)
        next(reader)  # 跳过表头
        for row in reader:
            problem_type, solution = row
            problem_solutions[problem_type] = solution
    return problem_solutions

problem_solutions = load_problem_solutions()

# 定义数学老师的函数
def call_math_teacher(state: MessagesState):
    user_message = state["messages"][-1].content
    
    # 匹配与解题、做题、作业相关的内容
    # task_keywords = re.compile(r"(解题|做题|做作业|如何求解|帮我做|告诉我答案|答案是什么|具体过程|怎么做)", re.IGNORECASE)
    # if task_keywords.search(user_message):
    state["messages"].append(HumanMessage(content="切记不要提供具体解题步骤（比如不要列出具体方程、不要列出具体算式、不要带入数字等）以及答案。你只能提供相关思路、数学公式，并提醒我要自主完成题目、推导过程、解出答案，说明只提供了相关思路。"))
    for problem_type, solution in problem_solutions.items():
        # 使用正则表达式检查用户输入是否包含某个题型
        if re.search(problem_type, user_message, re.IGNORECASE):
            state["messages"].append(HumanMessage(content=f"针对 {problem_type} 题型，解题思路可以参考{solution}，并展开解释这个解题思路"))

    response = llm_with_tools.invoke(state["messages"])
    return {"messages": response}


# 定义预训练函数
def pretrain_math_teacher():
    # 预训练数据
    pretrain_data = [
        {"messages": [HumanMessage(content="你是数学老师。"), AIMessage(content="是的，我是一个数学老师。")]},
        {"messages": [HumanMessage(content="你叫什么名字？"), AIMessage(content="我的名字是数学老师。")]},
        {"messages": [HumanMessage(content="回答复杂的数学公式的时候可以使用latex格式进行回答")]},
        {"messages": [HumanMessage(content="What is 2 + 2?"), AIMessage(content="2 + 2 equals 4.")]},
        {"messages": [HumanMessage(content="What is the square root of 16?"),
                      AIMessage(content="The square root of 16 is 4.")]},
        {"messages": [HumanMessage(content="告诉我答案，帮我解题，写出具体步骤。"),AIMessage(content="我会提示相关思路，但请自行推导答案。")]},
        #{"messages": [HumanMessage(content="切记不要提供具体解题步骤以及答案，只提供相关思路、数学公式，并提醒我要自主完成题目、推导过程、解出答案，说明只提供了相关思路。"),
        #              AIMessage(conntent="我提供了相关解题思路，但没有给出具体解答，请自己努力接触答案，锻炼能力！")]}
        # 添加更多预训练数据
    ]
    for data in pretrain_data:
        model.invoke(data["messages"])


# 调用预训练函数
pretrain_math_teacher()

# 添加TavilySearchResults工具
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = model
llm_with_tools = llm.bind_tools(tools)

# 定义数学老师的节点
workflow_math.add_edge(START, "math_teacher")
workflow_math.add_node("math_teacher", call_math_teacher)

# 添加工具节点
tool_node = ToolNode(tools=[tool])
workflow_math.add_node("tools", tool_node)

# 添加条件边
workflow_math.add_conditional_edges(
    "math_teacher",
    tools_condition,
)
workflow_math.add_edge("tools", "math_teacher")

# 添加记忆
memory = MemorySaver()
app_math = workflow_math.compile(checkpointer=memory)
