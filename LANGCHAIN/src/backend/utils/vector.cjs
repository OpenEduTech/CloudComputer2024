const { BaseMemory } = require('@langchain/core/memory');
const { Embeddings } = require('@langchain/core/embeddings');
const { CohereClient } = require('cohere-ai');

// MemoryVectorStore 类
class MemoryVectorStore extends BaseMemory {
  constructor() {
    super();
    this.memoryStore = new Map();
  }

  get memoryKeys() {
    return Array.from(this.memoryStore.keys());
  }

  async loadMemoryVariables(values) {
    return {};
  }

  async saveContext(inputValues, outputValues) {}

  async addDocuments(docs, embeddings) {
    for (const doc of docs) {
      const vector = await embeddings.embedQuery(doc.text);
      this.memoryStore.set(doc.text, { text: doc.text, vector });
    }
  }

  async similaritySearch(query, k, embeddings) {
    const queryVector = await embeddings.embedQuery(query);
    const similarity = (vec1, vec2) => {
      vec2 = JSON.parse(vec2);
      const dotProduct = vec1.reduce((sum, val, idx) => sum + val * vec2[idx], 0);
      const magnitude1 = Math.sqrt(vec1.reduce((sum, val) => sum + val * val, 0));
      const magnitude2 = Math.sqrt(vec2.reduce((sum, val) => sum + val * val, 0));
      return dotProduct / (magnitude1 * magnitude2);
    };

    return Array.from(this.memoryStore.values())
      .map(doc => ({ ...doc, score: similarity(queryVector, doc.vector) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, k);
  }

  async getVector(text) {
    const doc = this.memoryStore.get(text);
    if (doc) {
      return doc.vector;
    }
    return undefined;
  }
}

// CohereEmbeddings 类
class CohereEmbeddings extends Embeddings {
  constructor(apiKey) {
    super({});
    this.cohereClient = new CohereClient({ token: apiKey });
  }

  async embedDocuments(documents, retryCount = 3) {
    try {
      const response = await this.cohereClient.embed({ texts: documents });

      if (Array.isArray(response.embeddings) && Array.isArray(response.embeddings[0])) {
        return response.embeddings;
      } else {
        throw new Error(`Unexpected embeddings format. Response: ${JSON.stringify(response)}`);
      }
    } catch (error) {
      if (retryCount > 0) {
        console.log(`Error embedding documents. Retrying in 80 seconds... (${retryCount} retries left)`);
        // 等待 80 秒后重试
        await new Promise(resolve => setTimeout(resolve, 80000));  // 80秒
        return this.embedDocuments(documents, retryCount - 1);
      } else {
        throw new Error(`Error embedding documents. Documents: ${JSON.stringify(documents)}, Error: ${error.message}`);
      }
    }
  }

  async embedQuery(query, retryCount = 3) {
    try {
      const response = await this.cohereClient.embed({ texts: [query] });

      if (Array.isArray(response.embeddings) && Array.isArray(response.embeddings[0])) {
        return response.embeddings[0];
      } else {
        throw new Error(`Unexpected embeddings format. Response: ${JSON.stringify(response)}`);
      }
    } catch (error) {
      if (retryCount > 0) {
        console.log(`Error embedding query. Retrying in 80 seconds... (${retryCount} retries left)`);
        // 等待 80 秒后重试
        await new Promise(resolve => setTimeout(resolve, 80000));  // 80秒
        return this.embedQuery(query, retryCount - 1);
      } else {
        throw new Error(`Error embedding query. Query: "${query}", Error: ${error.message}`);
      }
    }
  }
}

// CacheEmbeddings 类
class CacheEmbeddings extends Embeddings {
  constructor(apiKey, vectors) {
    super({});
    this.vectors = vectors;
    this.cohereClient = new CohereClient({ token: apiKey });
  }

  async embedDocuments(documents) {
    return documents.map(doc => {
      const vectorInfo = this.vectors.find(item => item.text === doc);
      if (vectorInfo) {
        return vectorInfo.vector;
      } else {
        throw new Error(`向量未找到: ${doc}`);
      }
    });
  }

  async embedQuery(query) {
    const vectorInfo = this.vectors.find(item => item.text === query);
    if (vectorInfo) {
      return vectorInfo.vector;
    } else {
      const response = await this.cohereClient.embed({ texts: [query] });
      if (Array.isArray(response.embeddings) && Array.isArray(response.embeddings[0])) {
        return response.embeddings[0];
      } else {
        throw new Error('Unexpected embeddings format');
      }
    }
  }
}

// 导出类
module.exports = {
  MemoryVectorStore,
  CohereEmbeddings,
  CacheEmbeddings,
};
