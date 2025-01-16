import { BaseMemory } from '@langchain/core/memory';
import { Embeddings } from '@langchain/core/embeddings';
import type { InputValues, MemoryVariables, OutputValues } from '@langchain/core/memory';
import { CohereClient } from 'cohere-ai';


export class MemoryVectorStore extends BaseMemory {
    private memoryStore: Map<string, { text: string; vector: number[] }>;
  
    constructor() {
      super();
      this.memoryStore = new Map();
    }
  
    get memoryKeys(): string[] {
      return Array.from(this.memoryStore.keys());
    }
  
    async loadMemoryVariables(values: InputValues): Promise<MemoryVariables> {
      return {};
    }
  
    async saveContext(inputValues: InputValues, outputValues: OutputValues): Promise<void> {}
  
    async addDocuments(docs: { text: string }[], embeddings: Embeddings) {
      for (const doc of docs) {
        const vector = await embeddings.embedQuery(doc.text);
        this.memoryStore.set(doc.text, { text: doc.text, vector });
      }
    }
  
    async similaritySearch(query: string, k: number, embeddings: Embeddings) {
      const queryVector = await embeddings.embedQuery(query);
      const similarity = (vec1: number[], vec2: number[]) =>
        vec1.reduce((sum, val, idx) => sum + val * vec2[idx], 0);
  
      return Array.from(this.memoryStore.values())
        .map(doc => ({ ...doc, score: similarity(queryVector, doc.vector) }))
        .sort((a, b) => b.score - a.score)
        .slice(0, k);
    }

    // 获取指定文本的向量
    async getVector(text: string): Promise<number[] | undefined> {
        const doc = this.memoryStore.get(text);  // 查找文本是否存在
        if (doc) {
            return doc.vector;  // 返回存储的向量
        }
        return undefined
    }
  }
  
export class CohereEmbeddings extends Embeddings {
    private cohereClient: CohereClient;
  
    constructor(apiKey: string) {
      super({});
      this.cohereClient = new CohereClient({ token: apiKey });  // Pass the apiKey as 'token'
    }
  
    // Embed documents using Cohere's API
    async embedDocuments(documents: string[]): Promise<number[][]> {
      const response = await this.cohereClient.embed({ texts: documents });
  
      // Type narrowing: Check if response.embeddings is of type number[][]
      if (Array.isArray(response.embeddings) && Array.isArray(response.embeddings[0])) {
        return response.embeddings as number[][]; // It's a number[][] array
      } else {
        // Handle other types or errors here
        throw new Error('Unexpected embeddings format');
      }
    }
  
    // Embed a query using Cohere's API
    async embedQuery(query: string): Promise<number[]> {
      const response = await this.cohereClient.embed({ texts: [query] });
  
      // Type narrowing: Check if response.embeddings is of type number[][]
      if (Array.isArray(response.embeddings) && Array.isArray(response.embeddings[0])) {
        return response.embeddings[0] as number[]; // It's a number[] array
      } else {
        // Handle other types or errors here
        throw new Error('Unexpected embeddings format');
      }
    }
  }
