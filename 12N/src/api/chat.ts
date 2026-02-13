import express from 'express';
import type { Request, Response, Router } from 'express';
import DatabaseService from '../db/connection.js';
import RagService from '../services/rag.js';
import HybridSearchService from '../services/hybrid-search.js';
import BailianClient from '../services/bailian.js';

const router: express.Router = express.Router();

// 获取RAG服务实例
const getRagService = () => {
  const apiKey = process.env.BAILIAN_API_KEY;
  if (!apiKey) {
    throw new Error('BAILIAN_API_KEY not set');
  }
  
  const bailian = new BailianClient(apiKey);
  const db = new DatabaseService();
  const search = new HybridSearchService(db);
  
  return new RagService(bailian, search);
};

/**
 * POST /api/chat
 * RAG问答 (非流式)
 */
router.post('/', async (req: Request, res: Response) => {
  try {
    const { question, conversationId, options = {} } = req.body;

    if (!question || typeof question !== 'string') {
      return res.status(400).json({ error: 'Question is required' });
    }

    const ragService = getRagService();
    const response = await ragService.query(question, {
      maxContextChunks: options.maxContextChunks || 5,
      temperature: options.temperature || 0.7
    });

    // 如果有conversationId，保存对话记录
    if (conversationId) {
      const db = new DatabaseService();
      await db.query(
        `INSERT INTO messages (conversation_id, role, content, sources) 
         VALUES ($1, 'user', $2, $3)`,
        [conversationId, question, JSON.stringify([])]
      );
      
      await db.query(
        `INSERT INTO messages (conversation_id, role, content, sources) 
         VALUES ($1, 'assistant', $2, $3)`,
        [conversationId, response.answer, JSON.stringify(response.sources)]
      );
    }

    res.json({
      success: true,
      answer: response.answer,
      sources: response.sources.map(s => ({
        id: s.id,
        documentId: s.document_id,
        documentTitle: s.document_title,
        content: s.content.substring(0, 300) + '...',
        score: s.score
      })),
      usage: response.usage
    });
  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ 
      error: 'Chat failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * POST /api/chat/stream
 * RAG问答 (SSE流式)
 */
router.post('/stream', async (req: Request, res: Response) => {
  try {
    const { question, options = {} } = req.body;

    if (!question || typeof question !== 'string') {
      return res.status(400).json({ error: 'Question is required' });
    }

    // 设置SSE头
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    const ragService = getRagService();
    const stream = ragService.queryStream(question, {
      maxContextChunks: options.maxContextChunks || 5,
      temperature: options.temperature || 0.7
    });

    let sources: any[] = [];

    for await (const chunk of stream) {
      if (chunk.sources) {
        sources = chunk.sources;
        // 先发送来源信息
        res.write(`data: ${JSON.stringify({ type: 'sources', data: sources })}\n\n`);
      } else if (chunk.chunk) {
        // 发送内容块
        res.write(`data: ${JSON.stringify({ type: 'content', data: chunk.chunk })}\n\n`);
      }
    }

    // 发送完成标记
    res.write(`data: ${JSON.stringify({ type: 'done' })}\n\n`);
    res.end();
  } catch (error) {
    console.error('Chat stream error:', error);
    res.write(`data: ${JSON.stringify({ type: 'error', message: error instanceof Error ? error.message : 'Unknown error' })}\n\n`);
    res.end();
  }
});

export default router;
