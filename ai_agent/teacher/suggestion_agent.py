from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from config import model

# 定义学习建议的graph
workflow_suggestion = StateGraph(state_schema=MessagesState)


# 定义学习建议的函数
def call_suggestion_teacher(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": response}


# 定义预训练函数
def pretrain_suggestion_teacher():
    pass


# 调用预训练函数
pretrain_suggestion_teacher()

# 添加TavilySearchResults工具
tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = model
llm_with_tools = llm.bind_tools(tools)

# 定义学习建议的节点
workflow_suggestion.add_edge(START, "suggestion_teacher")
workflow_suggestion.add_node("suggestion_teacher", call_suggestion_teacher)

# 添加工具节点
tool_node = ToolNode(tools=[tool])
workflow_suggestion.add_node("tools", tool_node)

# 添加条件边
workflow_suggestion.add_conditional_edges(
    "suggestion_teacher",
    tools_condition,
)
workflow_suggestion.add_edge("tools", "suggestion_teacher")

# 添加记忆
memory = MemorySaver()
app_suggestion = workflow_suggestion.compile(checkpointer=memory)
