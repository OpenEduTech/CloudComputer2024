import {connectToTiDB, VectorIntoMysql, VectorInfo} from '../utils/mysql'
import { MemoryVectorStore, CohereEmbeddings } from '../utils/vector';
import { v4 as uuidv4 } from 'uuid';
import * as dotenv from 'dotenv';
dotenv.config();

describe('MySQL Connection Test', () => {
    it('should connect to the TiDB server and execute a query', async () => {
      // 在测试前执行连接操作
      await expect(connectToTiDB()).resolves.not.toThrow();
    });
  })