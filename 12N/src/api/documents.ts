import express from 'express';
import type { Request, Response, Router } from 'express';
import multer from 'multer';
import DatabaseService from '../db/connection.js';
import ChunkingService from '../services/chunking.js';
import BailianClient from '../services/bailian.js';

const router: Router = express.Router();

// 配置multer存储
const storage = multer.memoryStorage();
const upload = multer({ 
  storage,
  limits: { fileSize: 50 * 1024 * 1024 }, // 50MB限制
  fileFilter: (req, file, cb) => {
    const allowedMimes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];
    if (allowedMimes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('不支持的文件类型'));
    }
  }
});

// 获取数据库服务实例
const getDbService = () => new DatabaseService();

// 获取Chunking服务实例
const getChunkingService = () => {
  const apiKey = process.env.BAILIAN_API_KEY;
  if (!apiKey) {
    throw new Error('BAILIAN_API_KEY not set');
  }
  const bailian = new BailianClient(apiKey);
  const db = getDbService();
  return new ChunkingService(bailian, db);
};

/**
 * POST /api/documents
 * 上传新文档
 */
router.post('/', upload.single('file'), async (req: Request, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const { originalname, buffer, mimetype } = req.file;
    
    console.log(`Processing document: ${originalname}, type: ${mimetype}`);
    
    const chunkingService = getChunkingService();
    const result = await chunkingService.processDocument(buffer, originalname, mimetype);

    res.status(201).json({
      success: true,
      documentId: result.documentId,
      chunks: result.chunks.length,
      message: 'Document uploaded and processed successfully'
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ 
      error: 'Failed to process document',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/documents
 * 获取文档列表
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    const db = getDbService();
    const { page = 1, limit = 10 } = req.query;
    const offset = (Number(page) - 1) * Number(limit);

    const result = await db.query(
      `SELECT id, title, file_type, metadata, created_at 
       FROM documents 
       ORDER BY created_at DESC 
       LIMIT $1 OFFSET $2`,
      [Number(limit), offset]
    );

    const countResult = await db.query('SELECT COUNT(*) FROM documents');
    const total = parseInt(countResult.rows[0].count);

    res.json({
      success: true,
      data: result.rows,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total,
        totalPages: Math.ceil(total / Number(limit))
      }
    });
  } catch (error) {
    console.error('List documents error:', error);
    res.status(500).json({ 
      error: 'Failed to fetch documents',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/documents/:id
 * 获取单个文档详情
 */
router.get('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const db = getDbService();

    const result = await db.query(
      `SELECT id, title, content, file_type, metadata, created_at 
       FROM documents 
       WHERE id = $1`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Document not found' });
    }

    // 获取文档的分块
    const chunksResult = await db.query(
      `SELECT id, chunk_index, content, created_at 
       FROM chunks 
       WHERE document_id = $1 
       ORDER BY chunk_index`,
      [id]
    );

    res.json({
      success: true,
      data: {
        ...result.rows[0],
        chunks: chunksResult.rows
      }
    });
  } catch (error) {
    console.error('Get document error:', error);
    res.status(500).json({ 
      error: 'Failed to fetch document',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * DELETE /api/documents/:id
 * 删除文档
 */
router.delete('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const db = getDbService();

    const result = await db.query(
      'DELETE FROM documents WHERE id = $1 RETURNING id',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Document not found' });
    }

    res.json({
      success: true,
      message: 'Document deleted successfully'
    });
  } catch (error) {
    console.error('Delete document error:', error);
    res.status(500).json({ 
      error: 'Failed to delete document',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
