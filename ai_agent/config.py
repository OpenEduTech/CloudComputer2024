import os

from langchain_community.chat_models import ChatZhipuAI

# 设置环境变量
# 请将密钥替换为你自己的密钥，可以在智谱官网申请。LANGCHAIN对应的密钥也可以在其官网上申请。
os.environ["ZHIPUAI_API_KEY"] = "d8a9ddca79df44c391f0972bdfaefa91.3vCAIq5Tw6mLdqSi"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["TAVILY_API_KEY"] = "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"
os.environ["LANGCHAIN_API_KEY"] = "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"

model = ChatZhipuAI(
    model="glm-4",
    temperature=0.5,
)

# 华为云密钥，请替换成自己申请的密钥，并将桶名替换为实际桶名，Endpoint参数在申请华为云储存时获取
OBS_ACCESS_KEY = 'JMZUN3ANMT1YOGL7FGQK'
OBS_SECRET_KEY = 'ENzg76QSnUHKIThEywqlqakZEx6qXqtNYnaazM6f'
OBS_BUCKET_NAME = 'test-e795'
Endpoint = 'https://obs.cn-east-3.myhuaweicloud.com'
