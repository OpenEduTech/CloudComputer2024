const { CohereEmbeddings } = require('../utils/vector.cjs');
const { MemoryVectorStore } = require('../utils/vector.cjs');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs').promises;
const { request } = require('urllib');
const cliProgress = require('cli-progress');
require('dotenv').config();


async function processTextData() {
    const data = await fs.readFile('./src/backend/scripts/data/data.json', 'utf8');
    let texts = JSON.parse(data);
    // 取前100条数据
    texts = texts.slice(450, 460);
    const vectorProcessingBar = new cliProgress.SingleBar({
      format: 'Vectorizing |{bar}| {percentage}% | {value}/{total} Items',
      barCompleteChar: '\u2588',
      barIncompleteChar: '\u2591',
    }, cliProgress.Presets.shades_classic);
  
    // 创建进度条
    const bar = new cliProgress.SingleBar({
      format: 'Processing |{bar}| {percentage}% | {value}/{total} Items',
      barCompleteChar: '\u2588',
      barIncompleteChar: '\u2591',
    }, cliProgress.Presets.shades_classic);
  
    // 设置嵌入模型
    const embeddings = new CohereEmbeddings(process.env.VITE_COHERE_API_KEY);
  
    // 初始化内存向量存储
    const vectorStore = new MemoryVectorStore();
  
    // 将文本数据向量化并存储
    await vectorStore.addDocuments(texts, embeddings);
  
    console.log('before init vectorArray');
  
    // 启动向量化进度条
    vectorProcessingBar.start(texts.length, 0);
  
    // 使用 Promise.all 并行处理文本和请求
    const vectorArray = await Promise.all(
      texts.map(async (text, index) => {
        const vector = await vectorStore.getVector(text.text);
        if (!vector) {
          throw new Error(`Vector not found for text: ${text.text}`);
        }
        const timestamp = Date.now(); 
        const uuid = uuidv4();
  
        // 更新进度条
        vectorProcessingBar.update(index + 1);
  
        // 将获取的向量信息和请求发送封装到一个对象中
        return {
          vectorInfo: {
            time: `${timestamp}-${uuid}`,
            text: text.text,  // 存储原始文本
            herf: text.herf,
            vectorData: vector,  // 确保 vector 是 number[]
          },
          endpoint: async () => {
            const url = `${process.env.CLOUD_URL}/insert_info`;
            try {
              const { err, data, res } = await request(url, {
                digestAuth: `${process.env.PUBLIC_KEY}:${process.env.PRIVATE_KEY}`,
                headers: {
                  'content-type': 'application/json',
                },
                method: 'POST',
                data: {
                  "herf": text.herf,
                  "text": text.text,
                  "time": `${timestamp}-${uuid}`,
                  "vector": JSON.stringify(vector)
                }
              });
              if (err) throw new Error(`Request failed: ${err}`);
              return true;
            } catch (error) {
              console.error('Request failed:', error);
              return false;
            }
          }
        };
      })
    );
  
    // 完成向量化进度条
    vectorProcessingBar.stop();
  
    // 启动处理请求的进度条
    bar.start(vectorArray.length, 0);
  
    // 使用 Promise.all 并行处理所有的请求
    const requestResults = await Promise.all(
      vectorArray.map(async ({ vectorInfo, endpoint }) => {
        const requestSuccess = await endpoint();
        if (requestSuccess) {
          bar.increment();
        }
        return requestSuccess;
      })
    );
  
    // 完成进度条
    bar.stop();
  
    console.log('All requests completed.');
  }
// 调用函数执行操作
processTextData().catch(error => {
  console.error('Error:', error);
});
