import { Pool } from 'pg';
import type { PoolClient, QueryResult } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

// 数据库连接配置
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20, // 最大连接数
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// 连接池错误处理
pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

export interface Document {
  id: string;
  title: string;
  content?: string;
  embedding?: number[];
  metadata?: Record<string, any>;
  created_at?: Date;
}

export interface Chunk {
  id: string;
  document_id: string;
  content: string;
  embedding?: number[];
  chunk_index: number;
  metadata?: Record<string, any>;
  created_at?: Date;
}

export class DatabaseService {
  private pool: Pool;

  constructor() {
    this.pool = pool;
  }

  /**
   * 获取数据库连接
   */
  async getClient(): Promise<PoolClient> {
    return this.pool.connect();
  }

  /**
   * 执行查询
   */
  async query(text: string, params?: any[]): Promise<QueryResult> {
    return this.pool.query(text, params);
  }

  /**
   * 插入文档
   */
  async insertDocument(doc: Partial<Document>): Promise<string> {
    const { title, content, embedding, metadata } = doc;
    const result = await this.pool.query(
      `INSERT INTO documents (title, content, embedding, metadata) 
       VALUES ($1, $2, $3::vector, $4) 
       RETURNING id`,
      [title, content, embedding ? `[${embedding.join(',')}]` : null, metadata]
    );
    return result.rows[0].id;
  }

  /**
   * 插入文档分块
   */
  async insertChunk(chunk: Partial<Chunk>): Promise<string> {
    const { document_id, content, embedding, chunk_index, metadata } = chunk;
    const result = await this.pool.query(
      `INSERT INTO chunks (document_id, content, embedding, chunk_index, metadata) 
       VALUES ($1, $2, $3::vector, $4, $5) 
       RETURNING id`,
      [document_id, content, embedding ? `[${embedding.join(',')}]` : null, chunk_index, metadata]
    );
    return result.rows[0].id;
  }

  /**
   * 向量相似度搜索
   */
  async vectorSearch(embedding: number[], limit: number = 10): Promise<Chunk[]> {
    const result = await this.pool.query(
      `SELECT c.*, d.title as document_title
       FROM chunks c
       JOIN documents d ON c.document_id = d.id
       ORDER BY c.embedding <=> $1::vector
       LIMIT $2`,
      [`[${embedding.join(',')}]`, limit]
    );
    return result.rows;
  }

  /**
   * 全文搜索
   */
  async textSearch(query: string, limit: number = 10): Promise<Chunk[]> {
    const result = await this.pool.query(
      `SELECT c.*, d.title as document_title
       FROM chunks c
       JOIN documents d ON c.document_id = d.id
       WHERE d.search_vector @@ plainto_tsquery($1)
       ORDER BY ts_rank_cd(d.search_vector, plainto_tsquery($1)) DESC
       LIMIT $2`,
      [query, limit]
    );
    return result.rows;
  }

  /**
   * 关闭连接池
   */
  async close(): Promise<void> {
    await this.pool.end();
  }
}

export default DatabaseService;
