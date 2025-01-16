import * as mysql from 'mysql2';
import * as dotenv from 'dotenv';
import type { Connection } from 'mysql2';
dotenv.config();

const getTidbConnection = (database: string):Promise<Connection> =>{
  return new Promise((resolve, reject) => {
    // 创建一个连接池
    const connection = mysql.createConnection({
      host: process.env.TIDB_HOST,  // TiDB 的主机地址
      port: Number(process.env.TIDB_PORT),         // TiDB 的端口号
      user: process.env.TIDB_USERNAME,       // MySQL 用户名
      password: process.env.TIDB_PASSWORD,  // 你设置的 root 用户密码
      database: database,   // 默认数据库（可以根据需要修改）
    });
    resolve(connection);
  })
}

export const connectToTiDB = (): Promise<void> => {
  return new Promise(async (resolve, reject) => {
    // 创建一个连接池
    const connection = await getTidbConnection('test')

    // 测试连接
    connection.connect((err) => {
      if (err) {
        console.error('连接失败: ' + err.stack);
        reject(err);  // 如果连接失败，则返回错误
      } else {
        console.log('已连接到 TiDB，连接 ID: ' + connection.threadId);
        
        // 查询 TiKV 节点的状态
        const query = 'SELECT COUNT(*) AS tikv_node_count FROM information_schema.tikv_store_status WHERE store_state = 0;';

        connection.query(query, (err, results) => {
          if (err) {
            console.error('查询失败: ' + err.stack);
            reject(err);  // 如果查询失败，则返回错误
          } else {
            // 这里假设返回的结果是 RowDataPacket 数组
            if (results && Array.isArray(results) && results.length > 0) {
              const tikvNodeCount = (results[0] as mysql.RowDataPacket).tikv_node_count;
              console.log('TiKV 节点数量: ', tikvNodeCount);
            } else {
              console.log('没有找到 TiKV 节点。');
            }
            resolve();  // 查询成功，返回成功
          }
          connection.end();  // 确保关闭连接
        });
        
      }
    });

  });
};

export interface VectorInfo {
  text: string;
  herf: string;
  time: string;
  vector: number[];
}
// 定义并导出一个类
export class VectorIntoMysql {
  // 类的属性
  private vectorArray: VectorInfo[];
  private connection: Connection | null = null;

  // 构造函数
  private constructor(vectorArray: VectorInfo[]) {
    this.vectorArray = vectorArray;
    console.log('VectorIntoMysql 实例已创建');
  }

  // 静态工厂方法来创建实例并初始化数据库连接
  static async create(vectorArray: VectorInfo[]): Promise<VectorIntoMysql> {
    console.log("create VectorIntoMysql 开始");
    const instance = new VectorIntoMysql(vectorArray);
    instance.connection = await getTidbConnection('cloud');  // 异步初始化数据库连接
    console.log('数据库连接已建立');
    return instance;
  }

  // 将回调转换为 Promise
  private async beginTransaction(): Promise<void> {
    console.log('开始事务...');
    return new Promise((resolve, reject) => {
      if (!this.connection) return reject(new Error('没有数据库连接'));
      this.connection.beginTransaction((err) => {
        if (err) {
          console.error('事务开始失败:', err);
          reject(err);
        } else {
          console.log('事务已开始');
          resolve();
        }
      });
    });
  }

  private async commit(): Promise<void> {
    console.log('提交事务...');
    return new Promise((resolve, reject) => {
      if (!this.connection) return reject(new Error('没有数据库连接'));
      this.connection.commit((err) => {
        if (err) {
          console.error('提交事务失败:', err);
          reject(err);
        } else {
          console.log('事务已提交');
          resolve();
        }
      });
    });
  }

  private async rollback(): Promise<void> {
    console.log('回滚事务...');
    return new Promise((resolve, reject) => {
      if (!this.connection) return reject(new Error('没有数据库连接'));
      this.connection.rollback((err) => {
        if (err) {
          console.error('回滚事务失败:', err);
          reject(err);
        } else {
          console.log('事务已回滚');
          resolve();
        }
      });
    });
  }

  // 使用事务初始化 info 表并插入 VectorInfo 数组中的数据
  async initializeInfoTable(): Promise<void> {
    if (!this.connection) {
      throw new Error('数据库连接未初始化');
    }
  
    const connection = this.connection;
    console.log('准备创建 info 表和插入数据');
    
    // 创建 info 表的 SQL 语句
    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS info (
        time VARCHAR(255) PRIMARY KEY,
        text TEXT NOT NULL,
        herf VARCHAR(255) NOT NULL,
        vector JSON NOT NULL
      );
    `;
    
    // 插入数据的 SQL 语句
    const insertQuery = `
      INSERT INTO info (time, text, herf, vector)
      VALUES (?, ?, ?, ?)
      ON DUPLICATE KEY UPDATE text = VALUES(text), herf = VALUES(herf), vector = VALUES(vector);
    `;
  
    try {
      // 开始事务
      await this.beginTransaction();
  
      // 创建表，转换为 Promise
      await new Promise((resolve, reject) => {
        console.log('执行创建表 SQL: ', createTableQuery);
        connection.query(createTableQuery, (err, result) => {
          if (err) {
            console.error('创建表失败:', err);
            reject(err);
          } else {
            console.log('表创建成功或已存在');
            resolve(result);
          }
        });
      });
  
      // 插入数据，确保所有插入操作都完成后才提交
      for (const vector of this.vectorArray) {
        const { time, text, herf, vector: vectorData } = vector;
        
        await new Promise<void>((resolve, reject) => {
          connection.query(insertQuery, [time, text, herf, JSON.stringify(vectorData)], (err, result) => {
            if (err) {
              console.error('插入数据失败:', err);
              reject(err);
            } else {
              console.log('数据插入成功:', result);
              resolve();
            }
          });
        });
      }
  
      // 提交事务
      await this.commit();
      console.log('所有数据已成功插入并提交到 info 表');
    } catch (error) {
      // 如果发生错误，回滚事务
      await this.rollback();
      console.error('事务失败，已回滚:', error);
    }
  }
  
  // 添加一个用于关闭连接的方法
  async close(): Promise<void> {
    if (this.connection) {
      this.connection.end((err) => {
        if (err) {
          console.error('关闭连接失败:', err);
        } else {
          console.log('数据库连接已关闭');
        }
      });
    }
  }

   // 添加获取 vector 的方法
  async getVector(): Promise<number[] | null> {
    if (!this.connection) {
      throw new Error('数据库连接未初始化');
    }

    const connection = this.connection;
    const query = `
      SELECT * FROM info;
    `;

    try {
      const result = await new Promise<any>((resolve, reject) => {
        connection.query(query, (err, result) => {
          if (err) {
            console.error('查询失败:', err);
            reject(err);
          } else {
            resolve(result);
          }
        });
      });

      // 检查是否找到了数据
      if (result.length > 0) {
        return result;
      } else {
        console.log(`未找到的记录`);
        return null;
      }
    } catch (error) {
      console.error('获取 vector 失败:', error);
      return null;
    }
  }
}
