import express from 'express';
import type { Request, Response, Router } from 'express';
import DatabaseService from '../db/connection.js';
import HybridSearchService from '../services/hybrid-search.js';
import BailianClient from '../services/bailian.js';

const router: Router = express.Router();

// 获取服务实例
const getSearchService = () => {
  const db = new DatabaseService();
  return new HybridSearchService(db);
};

/**
 * POST /api/search
 * 混合检索 (向量 + 全文搜索)
 */
router.post('/', async (req: Request, res: Response) => {
  try {
    const { query, limit = 10, filters = {} } = req.body;

    if (!query || typeof query !== 'string') {
      return res.status(400).json({ error: 'Query is required' });
    }

    // 生成查询的embedding
    const apiKey = process.env.BAILIAN_API_KEY;
    if (!apiKey) {
      throw new Error('BAILIAN_API_KEY not set');
    }
    
    const bailian = new BailianClient(apiKey);
    const queryEmbedding = await bailian.embedding(query);

    // 执行混合检索
    const searchService = getSearchService();
    const results = await searchService.search(query, queryEmbedding, {
      limit: Number(limit)
    });

    res.json({
      success: true,
      query,
      results: results.map(r => ({
        id: r.id,
        documentId: r.document_id,
        documentTitle: r.document_title,
        content: r.content.substring(0, 500) + (r.content.length > 500 ? '...' : ''),
        chunkIndex: r.chunk_index,
        score: r.score,
        vectorRank: r.vector_rank,
        textRank: r.text_rank
      })),
      total: results.length
    });
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ 
      error: 'Search failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/search/suggest
 * 搜索建议 (基于全文搜索)
 */
router.get('/suggest', async (req: Request, res: Response) => {
  try {
    const { q, limit = 5 } = req.query;

    if (!q || typeof q !== 'string') {
      return res.status(400).json({ error: 'Query parameter q is required' });
    }

    const db = new DatabaseService();
    
    // 使用全文搜索查找相关文档标题
    const result = await db.query(
      `SELECT DISTINCT title 
       FROM documents 
       WHERE search_vector @@ plainto_tsquery($1)
       LIMIT $2`,
      [q, Number(limit)]
    );

    res.json({
      success: true,
      query: q,
      suggestions: result.rows.map(r => r.title)
    });
  } catch (error) {
    console.error('Suggest error:', error);
    res.status(500).json({ 
      error: 'Failed to get suggestions',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
