import DatabaseService from '../db/connection.js';

export interface SearchResult {
  id: string;
  document_id: string;
  content: string;
  chunk_index: number;
  document_title: string;
  score: number;
  vector_rank?: number;
  text_rank?: number;
}

export interface HybridSearchOptions {
  limit?: number;
  vectorWeight?: number;
  textWeight?: number;
  rrfK?: number;
}

export class HybridSearchService {
  private db: DatabaseService;

  constructor(dbService: DatabaseService) {
    this.db = dbService;
  }

  /**
   * 混合检索：结合向量相似度和全文搜索，使用RRF融合结果
   */
  async search(
    query: string,
    queryEmbedding: number[],
    options: HybridSearchOptions = {}
  ): Promise<SearchResult[]> {
    const {
      limit = 10,
      rrfK = 50
    } = options;

    const client = await this.db.getClient();

    try {
      // 1. 向量搜索
      const vectorResults = await this.vectorSearch(queryEmbedding, limit * 2);
      
      // 2. 全文搜索
      const textResults = await this.textSearch(query, limit * 2);

      // 3. RRF融合
      const fusedResults = this.fuseResults(
        vectorResults,
        textResults,
        rrfK,
        limit
      );

      return fusedResults;
    } finally {
      client.release();
    }
  }

  /**
   * 向量相似度搜索
   */
  private async vectorSearch(
    embedding: number[],
    limit: number
  ): Promise<Array<{ id: string; rank: number; data: any }>> {
    const result = await this.db.query(
      `SELECT 
        c.id,
        c.document_id,
        c.content,
        c.chunk_index,
        d.title as document_title,
        c.embedding <=> $1::vector as distance
       FROM chunks c
       JOIN documents d ON c.document_id = d.id
       ORDER BY c.embedding <=> $1::vector
       LIMIT $2`,
      [`[${embedding.join(',')}]`, limit]
    );

    return result.rows.map((row: any, index: number) => ({
      id: row.id,
      rank: index + 1,
      data: row
    }));
  }

  /**
   * 全文搜索
   */
  private async textSearch(
    query: string,
    limit: number
  ): Promise<Array<{ id: string; rank: number; data: any }>> {
    const result = await this.db.query(
      `SELECT 
        c.id,
        c.document_id,
        c.content,
        c.chunk_index,
        d.title as document_title,
        ts_rank_cd(d.search_vector, plainto_tsquery($1)) as rank_score
       FROM chunks c
       JOIN documents d ON c.document_id = d.id
       WHERE d.search_vector @@ plainto_tsquery($1)
       ORDER BY rank_score DESC
       LIMIT $2`,
      [query, limit]
    );

    return result.rows.map((row: any, index: number) => ({
      id: row.id,
      rank: index + 1,
      data: row
    }));
  }

  /**
   * RRF (Reciprocal Rank Fusion) 结果融合
   */
  private fuseResults(
    vectorResults: Array<{ id: string; rank: number; data: any }>,
    textResults: Array<{ id: string; rank: number; data: any }>,
    rrfK: number,
    limit: number
  ): SearchResult[] {
    const scores = new Map<string, { score: number; data: any; vectorRank?: number; textRank?: number }>();

    // 添加向量搜索结果
    for (const result of vectorResults) {
      const rrfScore = 1 / (result.rank + rrfK);
      scores.set(result.id, {
        score: rrfScore,
        data: result.data,
        vectorRank: result.rank
      });
    }

    // 添加全文搜索结果
    for (const result of textResults) {
      const rrfScore = 1 / (result.rank + rrfK);
      const existing = scores.get(result.id);
      
      if (existing) {
        // 如果已存在，累加分数
        existing.score += rrfScore;
        existing.textRank = result.rank;
      } else {
        scores.set(result.id, {
          score: rrfScore,
          data: result.data,
          textRank: result.rank
        });
      }
    }

    // 转换为数组并排序
    const results: SearchResult[] = Array.from(scores.entries())
      .map(([id, value]) => ({
        id,
        document_id: value.data.document_id,
        content: value.data.content,
        chunk_index: value.data.chunk_index,
        document_title: value.data.document_title,
        score: value.score,
        vector_rank: value.vectorRank,
        text_rank: value.textRank
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);

    return results;
  }
}

export default HybridSearchService;
