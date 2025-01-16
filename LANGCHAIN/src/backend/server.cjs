require('ts-node').register();

const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const { MemoryVectorStore, CohereEmbeddings, CacheEmbeddings } = require('./utils/vector.cjs');
const { getVectorByCloud } = require('./utils/mysql.cjs')
const dotenv = require('dotenv');
dotenv.config();
const { ChatCohere } = require('@langchain/cohere');
const { HumanMessage } = require('@langchain/core/messages');

const app = express();

// 允许跨域请求
app.use(cors({
  origin: '*',  // 允许任何来源的请求
  methods: ['GET', 'POST', 'OPTIONS'],
  preflightContinue: false,
}));

// 使用 JSON 中间件
app.use(express.json());

// 创建 MySQL 数据库连接池，使用从 .env 文件中读取的配置
const connection = mysql.createPool({
  host: process.env.TIDB_HOST,         // 从 .env 中读取数据库主机
  port: process.env.TIDB_PORT,         // 从 .env 中读取数据库端口
  user: process.env.TIDB_USERNAME,     // 从 .env 中读取数据库用户名
  password: process.env.TIDB_PASSWORD, // 从 .env 中读取数据库密码
  database: process.env.TIDB_DATABASE,      // 使用你的数据库名称
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// 获取 Vector 的方法
const getVector = async () => {
  return new Promise((resolve, reject) => {
    // SQL 查询语句
    const query = 'SELECT * FROM info;';

    connection.query(query, (err, results) => {
      if (err) {
        console.error('查询失败', err);
        return reject(err); // 查询失败返回错误
      }
      if (results.length > 0) {
        resolve(results); // 查询成功返回结果
      } else {
        console.log('未找到记录');
        resolve(null); // 如果没有数据，返回 null
      }
    });
  });
};

// 提取出获取向量数据并创建嵌入模型实例的逻辑
const fetchVectorsAndCreateEmbeddings = async () => {
  let vectors = [];
  if (process.env.USE_TIDB_CLOUD){
    let offsets = [0, 100, 200, 300, 400];  // 需要获取的偏移量

    for (let offset of offsets) {
        const result = await getVectorByCloud(offset);  // 按照偏移量获取数据
        vectors = vectors.concat(result.data.rows);  // 将结果合并到 vectors 数组中
    }
  }else{
    vectors = await getVector();
  }
  if (!vectors) {
    throw new Error('No vectors found');
  }

  const documents = vectors.map((item) => ({
    text: item.text,
    vector: item.vector,
  }));

  console.log(process.env.VITE_COHERE_API_KEY)
  const embeddings = new CacheEmbeddings(process.env.VITE_COHERE_API_KEY, documents);
  const vectorStore = new MemoryVectorStore();
  await vectorStore.addDocuments(documents, embeddings);

  return { embeddings, documents, vectorStore };
};

// 创建 Cohere 模型实例
const model = new ChatCohere({
  apiKey: process.env.VITE_COHERE_API_KEY,  // 使用环境变量中的 API Key
});

// 将向量和嵌入模型数据保存在全局变量中
let embeddings, documents, vectorStore;

// 服务器启动时加载向量数据和嵌入模型
const initializeEmbeddings = async () => {
  try {
    const result = await fetchVectorsAndCreateEmbeddings();
    embeddings = result.embeddings;
    documents = result.documents;
    vectorStore = result.vectorStore;
    console.log('Embeddings and vector store initialized.');
  } catch (error) {
    console.error('Error initializing embeddings:', error);
  }
};

// 调用初始化函数
initializeEmbeddings();

// 后端路由：处理 /api/ask 请求
app.options('/api/ask', (req, res) => {
  console.log('Received OPTIONS request for /api/ask');
  res.sendStatus(200);  // 返回 200 状态码
});
app.post('/api/ask', async (req, res) => {
  const { question } = req.body; // 获取客户端请求中的问题
  if (!question) {
    return res.status(400).json({ message: 'No question provided' }); // 如果没有问题，返回 400 错误
  }

  const logMessage = `Querying Cohere for: ${question}`;

  try {
    // 确保嵌入模型已初始化
    if (!embeddings || !documents || !vectorStore) {
      return res.status(500).json({ message: 'Embeddings not initialized yet' });
    }

    // 2. 执行向量检索
    const retrievedDocs = await vectorStore.similaritySearch(question, 5, embeddings);
    const retrievedContext = await retrievedDocs
      .map((retrievedDoc) => {
        // 找到对应的 documents 数据
        const matchedDoc = documents.find((doc) => doc.text === retrievedDoc.text);
        return matchedDoc ? matchedDoc.text : '';
      })
      .join('\n');

    // 3. 记录检索的上下文
    console.log('Retrieved Context:', retrievedContext);

    // 4. 创建 AgentAction
    const action = {
      tool: 'Cohere',
      toolInput: question,
      log: logMessage,
    };

    // 5. 调用 Cohere API 获取响应
    const prompt = `相关背景信息：\n${retrievedContext}\n\n用户问题：\n${question}`;
    const response = await model.invoke([new HumanMessage(prompt)]);

    // 6. 更新代理步骤
    const step = {
      action,
      observation: Array.isArray(response.content)
        ? response.content.join('\n')
        : response.content || 'No response received',
    };

    // 7. 代理完成状态
    const finish = {
      returnValues: { result: response.content || 'No result' },
      log: logMessage,
    };

    console.log('Agent Finish:', finish);

    // 8. 返回结果
    res.json({ answer: response.content || 'No result' });

  } catch (error) {
    console.error('Error calling Cohere API:', error);
    res.status(500).json({ message: 'Internal server error' }); // 如果发生错误，返回 500 错误
  }
});
// 启动服务器
app.listen(process.env.BACKEND_PORT, () => {
  console.log(`Backend server is running at http://${process.env.BACKEND_HOST}:${process.env.BACKEND_PORT}`);
});
