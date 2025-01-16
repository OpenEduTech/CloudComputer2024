const { CohereEmbeddings } = require('../utils/vector.cjs');
const { MemoryVectorStore } = require('../utils/vector.cjs');
const { v4: uuidv4 } = require('uuid');
const { VectorIntoMysql } = require('../utils/mysql.cjs');
const fs = require('fs').promises;

async function processTextData() {
  const data = await fs.readFile('./src/backend/scripts/data/data.json', 'utf8');
  const texts = JSON.parse(data);

  // 设置嵌入模型
  const embeddings = new CohereEmbeddings(process.env.VITE_COHERE_API_KEY);

  // 初始化内存向量存储
  const vectorStore = new MemoryVectorStore();

  // 将文本数据向量化并存储
  await vectorStore.addDocuments(texts, embeddings);

  // 创建 VectorInfo 数组
  const vectorArray = await Promise.all(
    texts.map(async (text) => {
      const vector = await vectorStore.getVector(text.text);
      if (!vector) {
        throw new Error(`Vector not found for text: ${text.text}`);
      }
      const timestamp = Date.now(); 
      const uuid = uuidv4();
      return {
        time: `${timestamp}-${uuid}`,
        text: text.text,  // 存储原始文本
        herf: text.herf,
        vectorData: vector,  // 确保 vector 是 number[]
      };
    })
  );

  // 插入数据库操作
  const vectorIntoMysql = await VectorIntoMysql.create(vectorArray); 
  await vectorIntoMysql.initializeInfoTable();
  const result = await vectorIntoMysql.getVector();

  // 检索文档并验证插入是否成功
  const retrievedDocs = await vectorStore.similaritySearch("江油的美食有哪些", 3, embeddings);
  const retrievedContext = retrievedDocs.map(doc => doc.text).join('\n');
  console.log('Retrieved Context:', retrievedContext);

  // 关闭连接
  await vectorIntoMysql.close();

  // 验证插入是否成功
  if (result?.length > 0) {
    console.log('Insert successful');
  } else {
    console.error('Insert failed');
  }
}

// 调用函数执行操作
processTextData().catch(error => {
  console.error('Error:', error);
});
