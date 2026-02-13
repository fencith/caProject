import { tool } from '@opencode-ai/core';
import DatabaseService from '../src/db/connection';
import HybridSearchService from '../src/services/hybrid-search';
import BailianClient from '../src/services/bailian';
import ChunkingService from '../src/services/chunking';
import fs from 'fs';
import path from 'path';

/**
 * 知识库查询工具
 * 用于在OpenCode中检索知识库内容
 */
export const knowledgeQueryTool = tool({
  name: 'knowledge-query',
  description: '查询知识库，检索与问题相关的文档内容',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: '查询问题或关键词'
      },
      limit: {
        type: 'number',
        description: '返回结果数量',
        default: 5
      }
    },
    required: ['query']
  },
  async execute({ query, limit = 5 }) {
    try {
      const apiKey = process.env.BAILIAN_API_KEY;
      if (!apiKey) {
        throw new Error('BAILIAN_API_KEY environment variable not set');
      }

      // 生成查询embedding
      const bailian = new BailianClient(apiKey);
      const queryEmbedding = await bailian.embedding(query);

      // 执行混合检索
      const db = new DatabaseService();
      const searchService = new HybridSearchService(db);
      const results = await searchService.search(query, queryEmbedding, { limit });

      return {
        success: true,
        query,
        results: results.map(r => ({
          id: r.id,
          documentTitle: r.document_title,
          content: r.content,
          relevanceScore: r.score
        }))
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
});

/**
 * 添加文档到知识库工具
 */
export const addDocumentTool = tool({
  name: 'knowledge-add-document',
  description: '将文档添加到知识库中（支持PDF、DOCX、TXT格式）',
  parameters: {
    type: 'object',
    properties: {
      filePath: {
        type: 'string',
        description: '文档文件的完整路径'
      }
    },
    required: ['filePath']
  },
  async execute({ filePath }) {
    try {
      if (!fs.existsSync(filePath)) {
        throw new Error(`File not found: ${filePath}`);
      }

      const apiKey = process.env.BAILIAN_API_KEY;
      if (!apiKey) {
        throw new Error('BAILIAN_API_KEY environment variable not set');
      }

      // 读取文件
      const buffer = fs.readFileSync(filePath);
      const filename = path.basename(filePath);
      
      // 判断文件类型
      const ext = path.extname(filePath).toLowerCase();
      let mimeType = 'text/plain';
      if (ext === '.pdf') mimeType = 'application/pdf';
      else if (ext === '.docx') mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      else if (ext === '.txt') mimeType = 'text/plain';

      // 处理文档
      const bailian = new BailianClient(apiKey);
      const db = new DatabaseService();
      const chunkingService = new ChunkingService(bailian, db);
      
      const result = await chunkingService.processDocument(buffer, filename, mimeType);

      return {
        success: true,
        documentId: result.documentId,
        chunks: result.chunks.length,
        message: `Document "${filename}" added successfully with ${result.chunks.length} chunks`
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
});

/**
 * 列出知识库文档工具
 */
export const listDocumentsTool = tool({
  name: 'knowledge-list-documents',
  description: '列出知识库中的所有文档',
  parameters: {
    type: 'object',
    properties: {
      limit: {
        type: 'number',
        description: '返回结果数量',
        default: 10
      }
    }
  },
  async execute({ limit = 10 }) {
    try {
      const db = new DatabaseService();
      const result = await db.query(
        `SELECT id, title, file_type, created_at 
         FROM documents 
         ORDER BY created_at DESC 
         LIMIT $1`,
        [limit]
      );

      return {
        success: true,
        documents: result.rows
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
});

export default {
  knowledgeQueryTool,
  addDocumentTool,
  listDocumentsTool
};
