# 智能老师助手项目

#### 项目背景
随着人工智能技术的快速发展，教育领域对大模型的应用需求日益增加。传统的教育模式往往难以满足个性化学习的需求，尤其是在语言学习、知识问答和作业辅导等方面。
基于此，我们设计了一个教育类大模型应用，旨在通过 Langchain 框架和云服务，为学生和教师提供一个智能化的教育辅助平台

#### 项目简介
本项目是一个基于云计算系统的智能老师助手，旨在为用户提供个性化的语文、数学和英语教学服务。
用户可以通过登录界面注册并登录，然后选择不同的老师进行互动交流。系统会根据用户的输入调用相应的AI模型生成回复，并将对话记录保存到云端存储中。

#### 文件结构
- **config.py**: 配置文件，包含API密钥和其他环境变量设置。
- **main.py**: 主程序入口，定义了Flask应用的基本路由和功能逻辑。
- **templates/**: 包含HTML模板文件，用于渲染前端页面。
  - `login.html`: 用户登录页面。
  - `register.html`: 用户注册页面。
  - `dashboard.html`: 用户仪表盘，显示聊天历史和输入框，实现主要的对话功能，同时实现了将对话记录保存到OBS中或者从OBS删除的功能。
- **teacher/**: 包含各个学科老师的实现代码和配套文件。
  - `Chinese_agent.py`: 语文老师的具体实现，包括诗词分析、作文评分等功能。
  - `English_agent.py`: 英语老师的具体实现，包括语法检查、情感分析等功能。
  - `Math_agent.py`: 数学老师的具体实现，主要处理数学问题的解答。
  - `math_problem_solutions.csv`: 提供一些常见题型的解题思路。
  - `suggestion_agent.py`: 学习建议生成的具体实现，用于根据用户的对话生成学习建议。
  - `high_school_chinese_criteria.txt`：高考语文作文评分标准。
  - `high_school_english_criteria.txt`：高考英语作文评分标准。
  - `middle_school_chinese_criteria.txt`：中考语文作文评分标准。
  - `middle_school_english_criteria.txt`：中考英语作文评分标准。
  - `primary_school_chinese_criteria.txt`：小学语文作文评分标准。
  - `primary_school_english_criteria.txt`：小学英语作文评分标准。
  - `poetry_knowledge_base.txt`：知识库《唐诗鉴赏辞典》。

## 系统架构
```
+-------------------+ +-------------------+ +-------------------+ 
    | 用户界面 |           | Langchain框架 |      | 云服务 | 
    | (Web/移动端) | <---> | (大模型集成) | <---> | (存储/计算) | 
+-------------------+ +-------------------+ +-------------------+
```
### 组件说明

- **用户界面**：提供学生和教师的操作界面，支持 Web 端访问。
- **Langchain 框架**：集成大模型，处理自然语言查询，生成个性化学习建议和作业辅导。
- **云服务**：提供数据存储服务。


#### 功能模块说明
1. **用户管理**
   - 支持用户注册、登录、登出操作。
   - 用户信息保存在OBS（华为云对象存储服务）中，确保数据安全性和持久化。

2. **多学科老师**
   - 提供三种类型的老师：语文、数学和英语。
   - 每个老师都有自己的工作流图（StateGraph），用于管理和调度不同的处理节点。

3. **AI交互**
   - 使用预训练的语言模型来生成自然语言回复。
   - 集成了TavilySearchResults工具，可以搜索互联网上的相关信息辅助回答。

4. **对话管理**
   - 对话记录会自动保存到OBS中，方便用户随时查看历史记录。
   - 支持从OBS加载之前的对话内容，保持上下文连贯性。

5. **前端交互**
   - 页面设计简洁友好，支持响应式布局适配不同设备。
   - 实现了AJAX异步请求，提升了用户体验流畅度。

#### 运行环境要求
- Python 3.x
- Flask框架
- langchain库及相关依赖项
- OBS客户端库（如`obs`包）

#### 安装与部署
1. 克隆仓库并进入项目目录：
   ```bash
   git clone https://github.com/KamisAyaka/ai_agent.git
   cd ai_agent
   ```

2. 创建虚拟环境并安装依赖：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 设置必要的环境变量（参考`config.py`中的示例）。
- 本代码使用智谱大语言模型，需要申请API密钥。ZHIPUAI_API_KEY设置为申请得到的API密钥，也可以替换成其他的大语言模型。
- langchain的API密钥设置为申请得到的API密钥。还有借助langchain实现的搜索引擎也需要申请相应的api。
- OBS_ACCESS_KEY和OBS_SECRET_KEY设置为OBS的访问密钥和密钥。本代码基于华为云平台来完成云端的储存。请将这两处密钥替换成自己申请的API密钥。

4. 启动应用程序：
   ```bash
   python main.py
   ```


#### 注意事项
- 请确保所有API密钥已正确配置，以避免运行时错误。
- 在生产环境中，请勿直接暴露敏感信息，建议使用更安全的方式管理密钥。


### 技术栈

#### 后端技术
- **Flask**: 用于构建Web应用的轻量级Python框架。
- **Langchain**: 用于集成和管理大模型的框架。集成了智谱大语言模型来为我们的应用提供个性化服务。
- **TavilySearchResults**: 用于搜索互联网信息的工具。利用langchain框架来调用该服务，能够让我们的应用更智能。
获取实时的互联网信息。
- **Transformers (Hugging Face)**: 用于自然语言处理任务，如情感分析和语法检查。
- **LanguageTool**: 用于语法检查和拼写错误检测。
- **OBS (华为云对象存储服务)**: 用于存储用户数据和对话记录。将用户注册时的信息和对话记录保存到OBS中。

#### 前端技术
- **HTML/CSS**: 用于构建用户界面。
- **JavaScript**: 用于处理前端交互逻辑。
- **AJAX**: 用于异步请求，提升用户体验。

#### 其他
- **Python**: 项目的主要编程语言。
- **Git**: 用于版本控制。
- **Markdown**: 用于编写文档，如README文件。


---

### 前端

#### 功能介绍

##### 1.登录页面和注册页面

登录页面和注册页面的实现，使用了HTML和CSS进行布局和样式设计，并使用了AJAX异步请求实现用户注册和登录。对于新用户，需要注册账号，注册成功后，即可登录。注册的信息会保存到OBS中，用于后续的登录。同时在界面提供了错误提示和成功消息的显示区域，帮助用户了解操作结果。

##### 2.仪表盘页面

仪表盘页面是智能老师助手的主页面，用户可以在这里进行对话，查看历史记录，并获取学习建议。分为左右两部分：左侧是导航栏，右侧是聊天区。导航栏包含多个选项卡，如语文老师、数学老师、英语老师、学习建议等功能以及登出按钮。聊天区展示了与智能老师的对话记录，并提供了一个输入框用于发送新问题。底部有保存对话、加载对话、清除对话和删除历史对话的功能按钮，这里将对话数据持久化到OBS中，通过OBS实现各种功能的调用，方便用户管理会话内容。

#### 功能实现
前端功能通过JavaScript实现，主要包括以下几点：

##### 1.AJAX异步请求
所有的表单提交和数据获取都是通过AJAX完成的，避免了页面刷新，提升了用户体验的流畅度。

##### 2.动态加载内容
当用户选择不同的老师或进行其他操作时，页面内容会根据服务器返回的数据动态更新，而不需要重新加载整个页面。

##### 3.本地存储与状态管理
利用浏览器的LocalStorage或其他方式来临时保存用户的输入信息，以便在用户关闭浏览器后再次打开时能够恢复之前的进度。

##### 4.事件监听与交互处理
为各种按钮添加了点击事件监听器，实现了如登录、注册、提交问题、切换老师等功能。

##### 5.错误处理与反馈：
对于可能出现的网络错误或其他异常情况，提供了友好的错误提示，并引导用户采取适当的行动。

---

### 后端

#### 1. 语文老师

##### 工作流

1 将用户输入进行情感分析。根据用户的语气，智能体将以愉快、关心或者中立的方式回应。

2 假如用户的输入中包含''作文''，则进入作文评分环节。

3 先用LanguageTool罗列出简单语法，用词错误。

4 再选定作文对应的评价标准，分为小学、初中（中考）和高中（高考）。假如用户的输入中包含''小学''、''初中''和''高中''，则选择对应的标准。

5 假如用户的输入中包含“诗词”，则进入诗词分析环节。

6 调用知识库中的内容作为新增的输入导入到模型。检索诗词的背景、作者信息和赏析导入到模型。知识库是《唐诗鉴赏辞典》，一共有1000首唐诗的详解。

7 除作文、诗词外问题直接导入到模型。检索用户输入作为背景信息导入到模型。

##### 实例演示

##### 语文诗词功能

analyze_emotion 情感分析

analyze_poetry 检索知识库

generate_response_poetry 浏览器搜索加上下文加大模型回复

输入：必须包含“诗词”，输入作者，诗名，部分诗句。可以少输入，尽量不输入错别字。

```
诗词：蝉
```

```
analyze_emotion
情感分析结果: LABEL_1, 分数: 0.6505052447319031, 语气: 愉快
<re.Match object; span=(0, 2), match='诗词'>
analyze_poetry 知识库内容
0001_虞世南_蝉
虞世南
蝉
虞世南
垂緌饮清露，流响出疏桐。
居高声自远，非是藉秋风。
这首托物寓意的小诗，是唐人咏蝉诗中时代最早的一首，很为后世人称道。
首句“垂緌饮清露”，“緌”是古人结在颔下的帽带下垂部分，蝉的头部有伸出的触须，形状好象下垂的冠缨，故说“垂緌”。古人认为蝉生性高洁，栖高饮露，故说“饮清 露”。这一句表面上是写蝉的形状与食性，实际上处处含比兴象征。“垂緌”暗示显宦身分（古代常以“冠缨”指代贵宦）。这显贵的身分地位在一般人心目中，是和“清” 有矛盾甚至不相容的，但在作者笔下，却把它们统一在“垂緌饮清露”的形象中了。这“贵”与“清”的统一，正是为三四两句的“清”无须藉“贵”作反铺垫，笔意颇为巧妙。
次句“流响出疏桐”写蝉声之远传。梧桐是高树，着一“疏”字，更见其枝干的高挺清拔，且与末句“秋风”相应。“流响”状蝉声的长鸣不已，悦耳动听，着一“出”字，把蝉声传送的意态形象化了，仿佛使人感受到蝉声的响度与力度。这一句虽只写声，但读者从中却可想见人格化了的蝉那种清华隽朗的高标逸韵。有了这一句对蝉声远传的生动描写，三四两句的发挥才字字有根。
“居高声自远，非是藉秋风”，这是全篇比兴寄托的点睛之笔。它是在上两句的基础上引发出来的诗的议论。蝉声远传，一般人往往以为是藉助于秋风的传送，诗人却别有会心，强调这是由于“居高”而自能致远。这种独特的感受蕴含一个真理：立身品格高洁的人，并不需要某种外在的凭藉（例如权势地位、有力者的帮助），自能声名远播，正象曹丕在《典论·论文》中所说的那样，“不假良史之辞，不托飞驰之势，而声名自传于后。”这里所突出强调的是人格的美，人格的力量。两句中的“自”字、“非”字，一正一反，相互呼应，表达出对人的内在品格的热情赞美和高度自信，表现出一种雍容不迫的风度气韵。唐太宗曾经屡次称赏虞世南的“五绝”（德行、忠直、 博学、文词、书翰），诗人笔下的人格化的“蝉”，可能带有自况的意味吧。沈德潜说：“咏蝉者每咏其声，此独尊其品格。”（《唐诗别裁》）这确是一语破的之论。  
清施补华《岘佣说诗》云：“三百篇比兴为多，唐人犹得此意。同一咏蝉，虞世南‘居高声自远，端不藉秋风’，是清华人语；骆宾王‘露重飞难进，风多响易沉’，是患 难人语；李商隐‘本以高难饱，徒劳恨费声’，是牢骚人语。比兴不同如此。”这三首诗都是唐代托咏蝉以寄意的名作，由于作者地位、遭际、气质的不同，虽同样工于 比兴寄托，却呈现出殊异的面貌，构成富有个性特征的艺术形象，成为唐代文坛“咏蝉”诗的三绝。
（刘学锴）
generate_response_poetry
搜索内容
《蝉》 原文|注释|翻译|赏析|序 - [唐]虞世南 - 每日诗词 - 古诗文网 每日诗词 首页诗词名句作者合集每日 繁體 搜索 垂緌饮清露，流响出疏桐。 居高声自远，非是藉秋风。 拼音分享图 所属合集 #小学古诗词 #小学十册 #初中沪教版 #小学九册 名句 居高声自远，非是藉秋风。 垂緌饮清露，流响出疏桐。 垂緌饮清露，流响出疏桐。 译文 萧疏梧桐之上，蝉儿低饮清露，蝉声清脆响亮，回荡树林之间。 身居高枝之上，可以傲视群虫，不用借助秋风，传声依然遥远。 查看全部 ∨ 注释 垂緌（ruí）：古代官帽打结下垂的部分，蝉的头部有伸出的触须，形状好像下垂的冠缨。也指蝉的下巴上与帽带相似的细嘴。清露：清纯的露水。饮清露：古人认为 蝉生性高洁，栖高饮露，其实是刺吸植物的汁液。 流：发出。流响：指蝉长鸣不已，声音传的很远。疏桐：高大的梧桐。 居高：指栖息在高处，语意双关。 藉（jiè）：凭借、依赖。 查看全部 ∨ 《蝉》是唐代诗人虞世南创作的一首五言古诗，是首托物寓意的诗。作者托物寓意，一、二句以蝉的栖高饮露、蝉声远传暗喻人的清朗俊秀、高标逸韵；三、四句分别用一“自”字、“非”字，正反相生，充满张力，表达出对人的内在品格的热情赞美和高度自信。全诗简练传神，比兴巧妙，以秋蝉高洁傲世的品格自况，耐人寻味。 查看全部 ∨ 赏析 这是一首咏物诗，咏物中尤多寄托，具有浓郁的象征性。句句写的是蝉的形体、习性和声音，而句句又暗示着诗人高洁 清远的品行志趣，物我互释，咏物的深层意义是咏人。诗的关键是把握住了蝉的某些别有意味的具体特征，从中找到了艺术上的契合点。 首句表面上是写蝉的形状与 食性，实际上处处含比兴象征。“垂緌”暗示显宦身份，因古人常以“冠缨”指代达官贵人。显宦的身份和地位在一般老百姓心目中，和“清客”是有矛盾甚至是不相容的，但在作者笔下，却把它们统一在“垂緌饮清露”的蝉的形象中了。这“贵（人）”与“清（客）”的统一，正是为三、四句的“清”无须借“贵”做反铺垫，用笔巧妙。 次句描 写蝉声之传播。梧桐是高树，用一“疏”字，更见其枝干的清高挺拔，且与末句的“秋风”相呼应。“流响”二字状蝉声的抑扬顿挫和长鸣不已；“出”字则把蝉声远播的意态形象化了，让人感受到蝉鸣的响度与力度。全句虽只写蝉声，但却从中想象到人格化了的蝉那种清华隽朗的高标逸韵。有了这句对蝉声传播的生动描写，后两句的发挥才字字有根。 三、四两句是全诗比兴寄托的“点睛”之笔。它是在一、二两句基础上引发出来的议论。蝉声远播，一般人往往认为是借助于秋风的传送，作者却别有慧 心，强调这是出于“居高”而自能致远。这种独特的感受蕴含着一个真理：修身而品格高尚的人，并不需要某种外在的凭借（例如权势地位、有力者的帮助），自能声名远扬。它突出强调一种人格的美，强调人格的力量。两句中的“自”字和“非”字，一正一反，相互呼应，表达出作者对人的内在品格的热情赞美和高度自信；表现出作者以蝉自许，雍容不迫的风度和气韵。 实际上，咏蝉这首诗包含着诗人虞世南的夫子自道。他作为唐贞观年间画像悬挂在凌烟阁的二十四勋臣之一，名声在于博学多能 ，高洁耿介，与唐太宗谈论历代帝王为政得失，能够直言善谏，为贞观之治作出独特贡献。为此，唐太宗称他有“五绝”（德行、忠直、博学、文辞、书翰），并赞叹：“群臣皆如虞世南，天下何忧不理！”从他不是以鲲鹏鹰虎，而是以一只不甚起眼的蝉来自况，也可见其老成谨慎，以及有自知之明。 查看全部 ∨ （以下内容由 AI 生成，仅供参考。） 注释 垂緌：古人结在颔下的帽缨下垂部分，蝉的头部有伸出的触须，形状好像下垂的冠缨，所以说“垂緌”。緌（ruí）。 翻译 蝉垂下像帽缨一样 的触角吸吮着清澈甘甜的露水，声音从挺拔疏朗的梧桐树枝间传出。蝉声传得这么远是因为蝉居住在高树上，而不是依靠秋风。 赏析 这是一首托物寓意的小诗。首句“垂緌饮清露”，表面是写蝉的形状与食性，实际上是暗示诗人高洁的品行。“流响出疏桐”，写蝉声传送之远，表现出蝉的独特。后两句“居高声自远，非是藉秋风”，是全篇的比兴寄托，表明自身品格高尚的人，并不需要某种外在的凭借，自能声名远扬。此诗表达出了诗人对人的内在品格的热情赞美和高度自信，表现出一种雍容不迫的风度和气韵。 虞世南 虞世南，字伯施，汉族，越州余姚（今浙江省慈溪市观海卫镇鸣鹤场）人。南北朝至隋唐时著名书法家、文学家、诗人、政治家，凌烟阁二十四功臣之一。陈朝太子中庶子虞荔之子、隋朝内史侍郎虞世基之弟。 虞世南生性沉静寡欲，意志坚定努力学习。在陈朝时，曾任建安王法曹参军、西阳王友。入隋后 ，官秘书郎、起居舍人。隋朝灭亡后，被窦建德任命为黄门侍郎。李世民灭窦建德后，引虞世南为秦王府参军、记室参军、弘文馆学士，与房玄龄等共掌文翰，为“十 八学士”之一。太宗贞观年间，历任著作郎、秘书少监、秘书监等职，先后封永兴县子、永兴县公，故世称“虞永兴、虞秘监”。他虽容貌怯懦、弱不胜衣，但性情刚烈 ，直言敢谏，深得太宗敬重。贞观十二年（638年）卒，年八十一，获赠礼部尚书，谥号文懿[2] ，配葬昭陵。贞观十七年（643年），绘像凌烟阁。 唐太宗称他德行 、忠直、博学、文词、书翰为五绝。善书法，与欧阳询、褚遂良、薛稷合称“初唐四大家”。日本学界称欧阳询、褚遂良、虞世南为“初唐三大家”。其所编的《北堂书钞》被誉为唐代四大类书之一，是中国现存最早的类书之一。原有诗文集30卷，但已散失不全。民国张寿镛辑成《虞秘监集》 4卷，收入 《四明丛书》。 ► 35篇诗文  相关推荐 鸟鸣涧 蝶恋花 · 伫倚危楼风细细 从军行 题汉祖庙 对酒 望庐山瀑布 早发白帝城 黄鹤楼送孟浩然之广陵 微信小程序 扫码体验微信小程序 微信公众号  扫码订阅微信公众号 流量卡 扫码或点击链接免费领取 超大流量卡1 超大流量卡2 热门作者 李白杜甫白居易辛弃疾李清照陶渊明苏轼纳兰性德李煜李商隐王维李贺曹操柳永王安石柳宗元曹植杜牧唐寅孟浩然陆游范仲淹温庭筠刘禹锡欧阳修 热门合集 唐诗三百首宋词三百首元曲三百首给孩子的诗诗经全集古诗十九首千家诗乐府诗集小学古诗词小学文言文初中古诗词初中文言文高中古诗词高中文言文虞美人雨霖铃长相思忆江南临江仙渔家傲 © meirishici.com 2024. 每日诗词 - 古诗文网. All Rights Reserved. 冀ICP备14020811号-5
《蝉》是唐代诗人虞世南创作的一首五言古诗，是首托物寓意的诗。作者托物寓意，一、二句以蝉的栖高饮露、蝉声远传暗喻人的清朗俊秀、高标逸韵；三、四句分别用一"自"字、"非"字，正反相生，充满张力，表达出对人的内在品格的热情赞美和高度自信。
模型回复
Model output: content='这首诗通过咏蝉来寓意人的品格和境界。虞世南以蝉的高洁、清朗、自给自足的形象，来比喻那些品德高尚、不依赖外力而能自立自强的人
。诗中的“居高声自远，非是藉秋风”一句，尤为精辟，表达了一个人只要立身正直，品格高尚，自然能够声名远播，而不需要依靠他人的吹捧或外力的帮助。\n\n这种寓意深刻、含蓄典雅的诗风，是唐诗中的佳作。虞世南以其博学多才和忠直的品行，得到了唐太宗的赏识，他的这首《蝉》也被认为是其人格自况的体现，展现了他对自己内在品质的自信和对高尚品德的追求。' additional_kwargs={} response_metadata={'token_usage': {'completion_tokens': 156, 'prompt_tokens': 3003, 'total_tokens': 3159}, 'model_name': 'glm-4', 'finish_reason': 'stop'} id='run-4250366f-07e4-4ea5-a69d-cebf8b1aa4c7-0'
127.0.0.1 - - [07/Jan/2025 10:47:44] "POST /get_response HTTP/1.1" 200 -
```

##### 语文作文评分功能

analyze_emotion 情感分析

evaluate_essay 用LanguageTool罗列出简单语法，用词错误

select_evaluation_standard 根据输入选择作文评分标准

generate_response_essay 上下文加大模型回复

输入：必须包含“作文”。必须包含“小学”或“初中”或“高中”。

```
初中作文评分：
我最喜欢的老师
我最喜欢的老师是李老师。她教你们数学，非常和蔼可亲。李老师总是耐心的解答它们的问题，即使我们犯了哈哈哈哈哈错误，她也不会生气。她的课堂很好玩，常常用生动的故事来帮助我们理解课文。
有一次，我因为生病缺课了，李老师特意在课后帮我打篮球。她不仅讲解德很清楚，还鼓励我要放弃。在她的助帮下，我的绩成提高了很多很多很多很多。
李老师不仅关心我们的学习，还管新我们的生活。她常常告诉我们，要做一个有责任心的人。她的叫会让我受益匪浅。
```

```
analyze_emotion
情感分析结果: LABEL_0, 分数: 0.5776228308677673, 语气: 中立
None
Regex match result: <re.Match object; span=(2, 6), match='作文评分'>
evaluate_essay
Essay suggestions: ['动词的修饰一般为‘形容词(副词)+地+动词’。您的意思是否是:耐心"地"解答']
select_evaluation_standard
227
初中
作文满分为：40分
一类卷  符合题意，内容具体，中心明确；想象丰富、合理；条理清楚，结构合理；语言通顺，有2处以下语病。     赋分范围：36-30分，以33分为基准分上下浮动 ，然后加书写项的得分。  4分：书写正确、工整，标点正确，格式规范。
二类卷  比较符合题意，内容比较具体，中心比较明确；想象比较丰富、比较合理；条理比较清楚，结构比较合理；语言比较通顺，有3-4处语病。       赋分范围：29-25分，以27分为基准分上下浮动，然后加书写项的得分。   3分：书写基本正确、工整，标点大体正确，格式规范。
三类卷  基本符合题意，内容尚具体，中心基本明确；想象不够丰富、不够合理；条理基本清楚，结构基本完整；语言基本通顺，有5-6处语病。 赋分范围：24-20分 ，以22分为基准分上下浮动，然后加书写项的得分。  2分：书写错误较多，字迹不够清楚，标点错误较多，格式大体规范。
四类卷  不符合题意，内容空洞，中心不明确；缺乏想象；条理不清楚，结构不完整；语言不通顺，有7处以上语病。 赋分范围：19-0分，以16分为基准分上下浮动，然后加书写项的得分。    1-0分：书写错误很多，字迹潦草，难以辨认，标点错误很多，格式不规范。
generate_response_essay
Model output: content='根据您提供的评分标准，以下是对所提供作文的评分：\n\n内容与题意：作文主题“我最喜欢的老师”表达清晰，内容具体，中心明确，符合
题意。\n\n结构与条理：文章结构合理，条理清晰，有明确的开头、中间叙述和结尾。\n\n语言表达：语言整体通顺，但存在一些语病和表述不清的地方，如“哈哈哈 哈哈错误”和“绩成提高了很多很多很多很多”，这些表述影响了语言的流畅性。\n\n想象与创新：文章中对于老师的描写较为真实，没有明显的想象内容。\n\n书写与 格式：由于是电子文本，书写和格式无法直接评分，但假设书写工整，标点使用正确。\n\n综合以上评价，作文大致属于以下类别：\n\n二类卷：比较符合题意，内容比较具体，中心比较明确；条理比较清楚，结构比较合理；语言比较通顺，有3-4处语病。\n\n基准分：27分\n\n书写项得分：假设为3分\n\n最终得分：27 + 3 = 30 分\n\n注意：这个评分是基于您提供的文本内容，实际上，书写和格式也需要考虑在内。此外，一些表述不清的地方需要修正以提高语言的准确性。' additional_kwargs={} response_metadata={'token_usage': {'completion_tokens': 253, 'prompt_tokens': 949, 'total_tokens': 1202}, 'model_name': 'glm-4', 'finish_reason': 'stop'} id='run-b2e3dc82-44f3-4d7d-a827-28b32793255b-0'
127.0.0.1 - - [07/Jan/2025 16:59:53] "POST /get_response HTTP/1.1" 200 -
```

##### 语文其他功能

analyze_emotion 情感分析

generate_response 浏览器搜索加上下文加大模型回复

```
介绍一下红楼梦
```

```
analyze_emotion
关心
Regex match result: None
generate_response
介绍一下红楼梦
搜索内容
红楼梦（曹雪芹创作的古典小说）_百度百科 网页新闻贴吧知道网盘图片视频地图文库资讯采购百科 百度首页 登录 注册 进入词条全站搜索帮助 首页 秒懂百科 特
色百科 知识专题 加入百科 百科团队 权威合作 个人中心 红楼梦 [hóng lóu mèng] 播报讨论上传视频 曹雪芹创作的古典小说 展开136个同名词条 收藏 查看我的收藏 0有用+1 《红楼梦》，中国古代章回体长篇小说，中国古典四大名著之一。其通行本共120回，一般认为前80回是清代作家曹雪芹所著，后40回作者为无名氏，整理者为程伟元、高鹗。小说以贾、史、王、薛四大家族的兴衰为背景，以富贵公子贾宝玉为视角，以贾宝玉与林黛玉、薛宝钗的爱情婚姻悲剧为主线，描绘了一些闺阁佳人的人生百态，展现了真正的人性美和悲剧美，是一部从各个角度展现女性美以及中国古代社会百态的史诗性著作。 《红楼梦》版本有120回“程本”和80回“脂本”两大系统。程本为程伟元排印的印刷本，脂本为脂砚斋在不同时期抄评的早期手抄本。脂本是程本的底本。 《红楼梦》是一部具有世界影响力的人情小说、中国封建社会 的百科全书、传统文化的集大成者。其作者以“大旨谈情，实录其事”自勉，只按自己的事体情理，按迹循踪，摆脱旧套，新鲜别致，取得了非凡的艺术成就。“真事隐 去，假语存焉”的特殊笔法更是令后世读者脑洞大开，揣测之说久而遂多。二十世纪以来，《红楼梦》更以其丰富深刻的思想底蕴和异常出色的艺术成就使学术界产生 了以其为研究对象的专门学问——红学。 [6] 作品名称 红楼梦 作品别名 石头记、情僧录、风月宝鉴、金陵十二钗 作    者 曹雪芹（前80回）、无名氏（后40回）、程伟元、高鹗（整理） 创作年代 清代 文学体裁 长篇小说 题    材 人情小说 初版时间 乾隆五十六年（1791） 篇    幅 约96万（程高本120回） 目录 1情节梗概 2作品目录 3成书过程 4人物形象 ▪主要人物 ▪其他人物 5作品鉴赏 ▪思想内容 ▪艺术成就 6名家评价 ▪国内评价 ▪国外评价 7版本系统 ▪大陆正版 ▪程本系统 ▪脂本系统 ▪重要译本 8后世影响 ▪国内影响 ▪世界影响 9作者争议 ▪前八十回 ▪无名氏续书说 ▪高鹗续书说 ▪曹雪芹残稿说 10研究论著 情节梗概 播报 编辑 《红楼梦》120回本(2张) 《红楼梦》书叙西方灵河岸上三生石畔的绛珠仙子，为了酬报神瑛侍者的灌溉之恩，要将毕生的泪水偿还，就随其下凡历劫。宝玉为神瑛侍者转世，林黛玉为绛珠仙子转世，这段姻缘称为“木石前盟”。远古女娲炼石补天遗下的顽石，通灵性，为贾宝玉出世时所衔的“通灵宝玉”，“通灵宝玉”历尽世间辛酸悲欢的故事，就是《石头记》，亦即《红楼梦》。 《红楼梦》故事纷纭复杂，其较大的事件有：黛玉丧母，进京依附外祖母；宝玉母姨及其子薛蟠、女薛宝钗进驻贾府；宝玉在秦可 卿卧房午觉，梦游太虚幻境，看了”金陵十二钗正册”；王熙凤毒设相思局，致贾瑞命归黄泉；秦可卿病亡，公公哭得如泪人一般；贾元春加封贤德妃，获准省亲，元春题名别院为“大观园”；宝、黛二人于沁芳闸共赏 《会真记》，宝玉以张生、莺莺喻己喻人，黛玉感极生嗔；王夫人怒逐金钏，金钏不堪受辱，投井身亡；宝玉事发， 贾政痛笞宝玉；探春发起组织海棠诗社，此时邢岫烟、李纹、薛宝琴等同时入驻贾府，彼等均具诗才，大观园比前更加热闹；刘姥姥携外孙板儿进荣府，深得贾母欢心；紫鹃戏说黛玉将回苏州，宝玉呆症大发；贾琏垂涎尤氏姐妹，偷娶尤二姐；尤二姐为凤姐所害，误服虎狼药，吞金自尽；尤三姐殉情饮剑身亡；贾赦欲讨鸳鸯为妾，鸳鸯哭诉贾母，贾母申斥贾赦夫妇；王夫人、凤姐夜抄大观园，司棋、晴雯被撵；晴雯病亡，宝玉心痛如绞，作《芙蓉女儿诔》以祭；迎春嫁了“中山狼”孙绍祖，受尽凌辱而死；薛蟠吃酒打死酒店当槽被擒拿；夏金桂误饮毒药汤，自取灭亡；元妃薨逝，通灵宝玉丢失，宝玉丧魂失魄；凤姐奇设调包计，黛玉闻知宝玉娶了宝钗，魂归离恨天，宝玉于潇湘馆痛祭黛玉，紫鹃细诉黛玉临终情景；薛宝琴史湘云相继出嫁；锦衣军奉旨查抄贾府；贾母逝世，鸳鸯上吊身亡；凤姐病重，临终托刘姥姥照看巧姐；宝玉魂魄随和尚重游太虚幻境，见到众多已离人世的姐妹；宝玉、贾兰叔侄赴考，出考场，宝玉旋即迷失；贾政途遇宝玉与一僧一道飘然而去，圣上赐宝玉“文妙 真人”道号；袭人嫁与蒋玉菡；贾雨村和甄士隐执手叙旧，言荣宁二府，将会兰桂齐芳，家道复初；僧道携宝玉到青埂峰下，仍将玉放在女娲补天之处，各自云游。 [2] 作品目录 播报 编辑 程甲本 程伟元序 高鹗序 第一回 甄士隐梦幻识通灵 贾雨村风尘怀闺秀 第二回 贾夫人仙逝扬州城 冷子兴演说荣国府 第三回 托内兄如海荐 西宾 接外孙贾母怜孤女 第四回 薄命女偏逢薄命郎 葫芦僧乱判葫芦案 第五回 贾宝玉神游太虚境 警幻仙曲演《红楼梦》 第六回 贾宝玉初试云雨情 刘姥姥一进荣国府 第七回 送宫花贾琏戏熙凤 赴家宴宝玉会秦钟 第八回 贾宝玉奇缘识金锁 薛宝钗巧合认通灵 第九回 《红楼梦》人物画-王熙凤 《红楼梦》人物画-林黛玉 林黛玉 王熙凤 林黛玉 7.甲戌本：存十六回（1-8回、13-16回、25-28回），此本脂批说曹雪芹死于“壬午除夕”。初由咸同年间大兴藏书家刘铨福收藏，胡适1927年得之于上海，后存放美国康奈尔大学图书馆，2005年初归藏上海博物馆。 8.己卯本：存41回又两个半回。此本为怡亲王府的抄藏本。第1-20回、31-40回、61-70回（内64、67 两回由后人补抄）原由董康、陶洙所藏，现藏国家图书馆；第55回下半至第59回上半现藏国家博物馆。
《红楼梦》内容丰富、情节曲折、思想认识深刻、艺术手法精湛，是我国古典小说中伟大的现实主义作品。 作品介绍： 《红楼梦》是中国古代章回体长篇小说，中国古典四大名著之一，又名《石头记》、《情僧录》、《风月宝鉴》、《金陵十二钗》、《金玉缘
Model output: content='亲爱的朋友，很高兴你关心《红楼梦》这样一部伟大的文学作品。《红楼梦》是我国清代作家曹雪芹创作的一部长篇小说，被誉为中国古典
四大名著之一。这部小说以贾、史、王、薛四大家族的兴衰为背景，通过富贵公子贾宝玉的视角，描绘了众多闺阁佳人的人生百态，展现了真正的人性美和悲剧美。\n\n《红楼梦》共120回，前80回为曹雪芹所著，后40回作者为无名氏，整理者为程伟元和高鹗。小说主要讲述了贾宝玉与林黛玉、薛宝钗之间的爱情婚姻悲剧。这部作 品具有极高的文学价值，被誉为“中国封建社会的百科全书”。\n\n《红楼梦》的版本有两大系统：程本和脂本。程本为程伟元排印的印刷本，脂本为脂砚斋在不同时期抄评的早期手抄本。脂本是程本的底本。\n\n这部小说以其丰富深刻的思想底蕴和异常出色的艺术成就，使学术界产生了以其为研究对象的专门学问——红学。二十世纪以来，《红楼梦》在世界范围内产生了广泛的影响，成为具有世界影响力的文学名著。\n\n《红楼梦》的故事纷纭复杂，人物形象鲜明，具有很高的艺术成就。它不仅在我国古典文学史上占有重要地位，也为世界文学宝库增添了瑰宝。希望你能深入阅读这部作品，感受其中的魅力。祝你阅读愉快！' additional_kwargs={} response_metadata={'token_usage': {'completion_tokens': 293, 'prompt_tokens': 3087, 'total_tokens': 3380}, 'model_name': 'glm-4', 'finish_reason': 'stop'} id='run-4a0e3959-72ab-44bb-82ca-bdbe38c54a7d-0'
```



#### 2. 数学老师

##### 主要思想

实现相关避免学生使用AI代写作业，对于具体的问题只提供相关思路，鼓励学生独立求解。

##### 具体实现

读取`math_problem_solutions.csv`中包含的一些常见题型的解题思路，并提供给AI着重进行分析，同时规定AI只提供相关思路，不提供具体解题过程、答案，这也避免了大语言模型在解决复杂计算问题时会出现的错误，比如复杂的积分、微分方程、矩阵运算等。

##### 实例演示

以下展示三个简单问题的回答：

```
1234567: 有一些鸡和兔子被关在同一个笼子里，一共有10个头和26条腿，那么笼子中兔子和鸡各有几只？
智能老师: 好的，理解你的要求。解决这个问题，你可以使用“鸡兔同笼”问题的标准方法。首先，你需要设定两个变量，一个代表鸡的数量，另一个代表兔的数量。然后，你可以根据题目中给出的信息，即头的总数和腿的总数，列出两个方程。这两个方程将帮助你解出鸡和兔各自的数量。请自行完成这个过程，推导出答案。

1234567: 马戏团里有独轮车和三轮车一共30辆，其中每辆独轮车有1个轮子，每辆三轮车有3个轮子，所有车辆一共有66个轮子，那么三轮车和独车各有多少辆？
智能老师: 这个问题与鸡兔同笼问题类似，可以通过设置方程来解决。首先，我们可以设独轮车的数量为x，三轮车的数量为y。根据题目给出的信息，我们可以列出两个方程。 首先，我们知道车辆的总数是30，所以我们可以得到第一个方程： x + y = 30 其次，所有车辆的轮子总数是66。独轮车有1个轮子，三轮车有3个轮子，所以我们可以得到第二个方程： 1x + 3y = 66 现在我们有了一个方程组，可以通过解这个方程组来找到x和y的值。解这个方程组将会告诉我们独轮车和三轮车各自的数量。 你可以使用代入法、消元法或者矩阵法等不同的数学方法来解这个方程组。请自主完成这个步骤，找出x和y的值，这样就能得到独轮车和三轮车各自的数量了。

1234567: 在等差数列中，a4+a6+a8+a10+a12=120，求2a9-a10。告诉我答案！
智能老师: 智能老师: 在等差数列中，已知 \(a_4 + a_6 + a_8 + a_{10} + a_{12} = 120\)，我们可以利用等差数列的性质来求解 \(2a_9 - a_{10}\)。 首先，由于 \(a_4, a_6, a_8, a_{10}, a_{12}\) 是等差数列中的连续项，且项数为奇数，我们可以知道 \(a_8\) 是这些项的中项。因此，\(a_8\) 等于这些项的和除以项数，即： \[ a_8 = \frac{a_4 + a_6 + a_8 + a_{10} + a_{12}}{5} \] 将已知的和代入，我们可以求出 \(a_8\) 的值。 接下来，利用等差数列的性质，我们知道对于任意的 \(n\)，有 \(2a_n = a_{n-1} + a_{n+1}\)。因此，我们可以将 \(2a_9 - a_{10}\) 重写为 \(a_9 + a_9 - a_{10}\)，然后利用等差数列的性质将 \(a_9\) 表达为 \(a_8\) 和 \(a_{10}\) 的形式。 最后，将 \(a_8\) 的值代入上述表达式，我们可以求出 \(2a_9 - a_{10}\) 的值。 请记住，具体的计算过程和答案需要你自己完成。这里提供的只是解题的思路和相关的数学公式。
```

可见AI导师着重讲解了解题思路，且避免了直接给出答案。



#### 3. 英语老师

##### 工作流

1 将用户输入进行情感分析。根据用户的语气，智能体将以愉快、关心或者中立的方式回应。

2 假如用户的输入中包含''作文''，则进入作文评分环节。

3 先用LanguageTool罗列出简单语法，用词错误。

4 再选定作文对应的评价标准，分为小学、初中（中考）和高中（高考）。假如用户的输入中包含''小学''、''初中''和''高中''，则选择对应的标准。

5 除作文外问题直接导入到模型。检索用户输入作为背景信息导入到模型。

##### 实例演示

##### 英语作文评分功能

analyze_emotion 情感分析

evaluate_essay 用LanguageTool罗列出简单语法，用词错误

select_evaluation_standard 根据输入选择作文评分标准

generate_response_essay 上下文加大模型回复

输入：必须包含“作文”。必须包含“小学”或“初中”或“高中”。

```
高中作文评分:My Favorite Teacher
My favorite teacr is Mr. mith. He teach us English and is very kind. Last week, he gived us a interestig assignment about writing a story. I writed a story about a dragon, but I  ome mistakes. Mr. Smith corrected my errors and telled me ow to improve. He always says, "Practice make perfect." I am very thankfl for his help. Because of him, my English has improved a lot. I hope to be a teaher like him in the future.
```

```
analyze_emotion
愉快
Regex match result: <re.Match object; span=(2, 6), match='作文评分'>
evaluate_essay
Essay suggestions: ['Possible spelling mistake found.', 'Possible spelling mistake found.', 'The pronoun ‘He’ is usually used with a third-person or a past tense verb.', 'Possible spelling mistake. Did you mean “gave”, the past tense form of the verb ‘give’?', 'Use “an” instead of ‘a’ if the following word starts with a vowel sound, e.g. ‘an article’, ‘an hour’.', 'Possible spelling mistake found.', 'The past tense of the verb “write” is “wrote”.', 'It seems like there are too many consecutive spaces here.', 'Possible spelling mistake found.', 'Possible spelling mistake. Did you mean “told”, the past tense form of the verb ‘tell’?', 'Possible spelling mistake found.', 'Possible spelling mistake found.']
select_evaluation_standard
高中
1.作文满分为25分，其中内容10分，语言10分，组织结构5分。
2. 评分时应注意的主要方面：内容要点，应用词汇和语法结构的数量和正确性及上下文的连贯性。
3.评分时，先根据文章的内容和语言初步确定所属档次，然后对照相应的组织结构档次给予加分。其中，内容和语言两部分相加，得15分或以上者，可考虑加4-5分，15分以下者只能考虑加 0,1,2,3分。
4. 词数少于70，总分最多不超过10分。
各档次给分要求：
内容部分：
A. 内容充实，主题突出，详略得当。9-10分
B. 内容较充实，能表达出作文要求。7-8分
C. 内容基本充实，尚能表达出作文要求。5-6分
D. 漏掉或未能写清楚主要内容，有些内容与主题无关。3-4分
E. 明显遗漏主要内容，严重离题。1-2分
F. 完全未作答或作答与本题无关。0分
语言部分
A. 具有很好的语言表达能力，语法结构正确或有些小错误，主要因为使用了较复杂结构或词汇所致。句子结构多样，词汇丰富。9-10分
B.具有较强的语言表达能力，语法结构和词汇的应用基本正确，错误主要是因为尝试较复杂结构或词汇所致。句子结构多样，词汇较丰富。7-8分
C.有一些语法结构和词汇方面的错误，但不影响理解。句子结构有一定的变化，词汇使用得当。5-6分
D.语法结构与词汇错误较多，影响了对内容的理解。“句子结构单调，词汇较贫乏。3-4分
E.语法结构与词汇错误很多，影响了对内容的理解。词不达意。1-2分
F. 完全未作答或作答与本题无关。0分
组织结构部分
A. 自然地使用了语句间的连接成分，全文流畅，结构紧凑。4-5分
B. 能使用语句间连接成分，全文较流畅，结构较紧凑。3分
C.能使用简单的语句间连接成分，全文内容连贯。2分
D. 尚能使用语句间连接成分，语言连贯性较差。1分
E. 缺乏语句间的连接成分，语言不连贯。0分
generate_response_essay
Model output: content='根据您提供的评分标准，以下是对作文的评分：\n\n**内容部分**：\n- 作文主题明确，表达了对最喜欢的老师的感激之情，但内容细节不
够充实，没有具体例子支撑。\n- 得分：C（5-6分）\n\n**语言部分**：\n- 存在多处拼写错误，影响了语言的准确性。\n- 时态和主谓一致上有错误，如“gived”应 为“gave”，“telled”应为“told”，“writed”应为“wrote”。\n- 得分：D（3-4分）\n\n**组织结构部分**：\n- 作文结构基本清晰，但缺乏语句间的连接成分，使得文 章连贯性不强。\n- 得分：C（2分）\n\n**总分计算**：\n- 内容得分：5-6分\n- 语言得分：3-4分\n- 组织结构得分：2分\n- 总分：10-12分（考虑到内容和语言的错误，以及文章的连贯性问题）\n\n**建议**：\n- 修正拼写错误，注意时态和主谓一致。\n- 增加内容细节，如具体的例子来展示老师如何帮助了作者。\n- 使用一些连接词来增强文章的连贯性。\n\n根据评分标准，这篇作文的总分在10-12分之间，如果作者能够根据建议进行修改，分数有望提高。' additional_kwargs={} response_metadata={'token_usage': {'completion_tokens': 282, 'prompt_tokens': 850, 'total_tokens': 1132}, 'model_name': 'glm-4', 'finish_reason': 'stop'} id='run-c08e0414-e3fa-4dbf-8b31-f9b50cc76461-0'
127.0.0.1 - - [07/Jan/2025 17:02:47] "POST /get_response HTTP/1.1" 200 -
```

##### 英语其他问题

analyze_emotion 情感分析

generate_response 浏览器搜索加上下文加大模型回复

```
（1）. The man _____ helped me yesterday is my neighbor.  A. who B. whom C. whose D. which  (2). Is there anyone _____ you can trust in this city?  A. who B. whom C. whose D. which  (3). The book _____ I borrowed from the library is very interesting.  A. who B. whom C. whose D. which
```

```
analyze_emotion
愉快
Regex match result: None
generate_response
（1）. The man _____ helped me yesterday is my neighbor.  A. who B. whom C. whose D. which  (2). Is there anyone _____ you can trust in this city?  A. who B. whom C. whose D. which  (3). The book _____ I borrowed from the library is very interesting.  A. who B. whom C. whose D. which
搜索内容
The words that, which, who, whom, and whose are called relative pronouns. A relative pronoun can introduce a relative clause: a type of subordinate clause that modifies a subject or object from earlier in the sentence.You can use a relative clause to combine two simple sentences into one complex sentence. Who refers only to people. Use who to replace a subject pronoun with a relative clause.
'Who' - 'whose' - 'whom' - 'that' and 'which' - are relative pronouns. 'Where' is a relative adverb. There is often confusion about the use of who, whose, whom, that, which or where. We use who when referring to people or when we want to know the person. Who ate all the chocolates? Who called the police?
Model output: content='Certainly! Let\'s tackle these relative pronoun questions with a smile!\n\n1. The man _____ helped me yesterday is my neighbor.\n   - A. who\n   - B. whom\n   - C. whose\n   - D. which\n   Answer: A. who\n   Explanation: Since "the man" is a person, we use "who" as the subject of the relative clause.\n\n2. Is there anyone _____ you can trust in this city?\n   - A. who\n   - B. whom\n   - C. whose\n   - D. which\n   Answer: B. whom\n   Explanation: In this sentence, "whom" is used because it is the object of the verb "trust" in the relative clause.\n\n3. The book _____ I borrowed from the library is very interesting.\n   - A. who\n   - B. whom\n   - C. whose\n   - D. which\n   Answer: D. which\n   Explanation: As "the book" is a thing, we use "which" to introduce the relative clause.\n\nRemember, "who" is for people when they are the subject, "whom" for people when they are the object, "whose" for possession, and "which" for things! Keep practicing, and you\'ll get the hang of it! 📚✨' additional_kwargs={} response_metadata={'token_usage': {'completion_tokens': 281, 'prompt_tokens': 1399, 'total_tokens': 1680}, 'model_name': 'glm-4', 'finish_reason': 'stop'} id='run-d5622e36-ca8f-4ec1-b904-fb344c34af42-0'
```

---

### 云服务
### 华为云 OBS 集成

#### 概述
本项目集成了华为云对象存储服务（OBS），用于存储和管理用户数据及对话记录。通过 OBS，我们能够确保用户信息的安全性和持久化，同时提供高效的读写操作，支持用户的注册、登录以及对话历史的保存和加载。

#### OBS 客户端配置
在 `main.py` 文件中，首先创建了 OBS 客户端实例，用于与 OBS 进行交互。关键配置如下：

```
from obs import ObsClient

# 创建OBS客户端
obs_client = ObsClient(
    access_key_id=OBS_ACCESS_KEY,
    secret_access_key=OBS_SECRET_KEY,
    server=Endpoint
)
```
- **access_key_id**: 华为云 OBS 的访问密钥 ID。
- **secret_access_key**: 华为云 OBS 的秘密密钥。
- **server**: OBS 服务的终端节点（Endpoint）。

#### 用户数据管理

##### 用户注册与登录
- **注册新用户**：当用户注册时，系统会将用户信息（如用户名和密码）保存到 OBS 中。
  
```
  def save_user(user_id, user_data):
      object_key = f'users/{user_id}.json'
      user_data_json = json.dumps(user_data)
      resp = obs_client.putContent(bucketName=OBS_BUCKET_NAME, objectKey=object_key, content=user_data_json)
```
- **加载用户信息**：当用户登录时，系统会从 OBS 中加载用户信息进行验证。
  
```
  def load_user(user_id):
      object_key = f'users/{user_id}.json'
      try:
          resp = obs_client.getObject(bucketName=OBS_BUCKET_NAME, objectKey=object_key, loadStreamInMemory=True)
          if resp.status < 300:
              user_data_json = resp.body['buffer'].decode('utf-8')
              user_data = json.loads(user_data_json)
              return user_data
          else:
              return None
```
#### 对话记录管理

##### 保存对话记录
用户与智能老师的对话记录会被保存到 OBS 中，以便用户随时查看历史记录。

```
@app.route('/save_conversation', methods=['POST'])
def save_conversation():
    username = session['username']
    data = request.get_json()
    conversation = data.get('conversation')

    if not conversation:
        return jsonify({'error': '对话内容不能为空'}), 400

    object_key = f'users/{username}.json'

    try:
        resp = obs_client.getObject(bucketName=OBS_BUCKET_NAME, objectKey=object_key, loadStreamInMemory=True)

        if resp.status < 300:
            user_data_json = resp.body['buffer'].decode('utf-8')
            user_data = json.loads(user_data_json)
        else:
            user_data = {}

        if 'conversation' in user_data:
            user_data['conversation'] += '\n' + conversation
        else:
            user_data['conversation'] = conversation

        # 保存更新后的数据到 OBS
        obs_client.putContent(
            bucketName=OBS_BUCKET_NAME,
            objectKey=object_key,
            content=json.dumps(user_data)
        )

        return jsonify({'status': 'success'})
```
##### 加载对话记录
用户可以请求加载之前的对话记录，以保持上下文连贯性。

```
@app.route('/load_conversation', methods=['POST'])
def load_conversation():
    username = session['username']

    object_key = f'users/{username}.json'

    try:
        resp = obs_client.getObject(bucketName=OBS_BUCKET_NAME, objectKey=object_key, loadStreamInMemory=True)
        if resp.status < 300:
            conversation = json.loads(resp.body['buffer'].decode('utf-8'))
            c = conversation['conversation']
            return jsonify({'conversation': c})
        else:
            return jsonify({'error': f"加载对话失败: {resp.error_code} {resp.error_msg}"}), 400
```
##### 删除对话记录
用户可以选择删除对话记录，以清理不再需要的历史数据。

```
@app.route('/delete_conversation', methods=['POST'])
def delete_conversation():
    username = session.get('username')

    if not username:
        return jsonify({'error': '用户未登录'}), 403

    object_key = f'users/{username}.json'

    try:
        # 尝试删除OBS中的对象
        resp = obs_client.deleteObject(bucketName=OBS_BUCKET_NAME, objectKey=object_key)
        if resp.status < 300:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': f"删除对话失败: {resp.error_code} {resp.error_msg}"}), 500
```
#### 学习建议生成
根据用户的对话记录，系统可以生成个性化的学习建议，并将这些建议返回给用户。

```
python
@app.route('/get_learning_suggestion', methods=['POST'])
def get_learning_suggestion():
    username = session['username']

    object_key = f'users/{username}.json'

    try:
        resp = obs_client.getObject(bucketName=OBS_BUCKET_NAME, objectKey=object_key, loadStreamInMemory=True)
        if resp.status < 300:
            conversation = json.loads(resp.body['buffer'].decode('utf-8'))
            c = conversation.get('conversation', '')
            prompt = f"{c}\n给我生成对应的学习建议"
            response = get_response(app_suggestion, prompt)
            return jsonify({"suggestion": response})
        else:
            return jsonify({'error': f"加载对话失败: {resp.error_code} {resp.error_msg}"}), 400
    except Exception as e:
        print(f"加载对话时出错: {e}")
        return jsonify({'error': str(e)}), 500
```
通过上述集成，华为云 OBS 成为了本项目不可或缺的一部分，确保了用户数据的安全存储和高效管理，提升了用户体验。



### 团队分工

黄冠富：实现了基本框架的搭建和对语言模型的调用。将前端返回的数据保存到华为云中。

袁滨：实现用户登录和学习建议生成，将前端各部分进行整合。从华为云中读取数据实现前端展示。

左庭宇：后端负责语文老师智能体和英语老师智能体。

何俊彦：前端对话网页设计与相关功能实现，后端负责数学智能体。
