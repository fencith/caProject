import { DocumentParser } from './parser.js';
import BailianClient from './bailian.js';
import DatabaseService from '../db/connection.js';

export interface ChunkingOptions {
  chunkSize?: number;      // 分块大小 (字符数)
  overlap?: number;        // 重叠字符数
  separator?: string;      // 分隔符
}

export interface ProcessedDocument {
  documentId: string;
  chunks: Array<{
    id: string;
    content: string;
    chunkIndex: number;
  }>;
}

export class ChunkingService {
  private parser: DocumentParser;
  private bailian: BailianClient;
  private db: DatabaseService;
  private chunkSize: number;
  private overlap: number;

  constructor(
    bailianClient: BailianClient,
    dbService: DatabaseService,
    options: ChunkingOptions = {}
  ) {
    this.parser = new DocumentParser();
    this.bailian = bailianClient;
    this.db = dbService;
    this.chunkSize = options.chunkSize || 800;
    this.overlap = options.overlap || 100;
  }

  /**
   * 处理上传的文档：解析 -> 分块 -> Embedding -> 存储
   */
  async processDocument(
    buffer: Buffer,
    filename: string,
    mimeType: string
  ): Promise<ProcessedDocument> {
    // 1. 解析文档
    const parsed = await this.parser.parse(buffer, mimeType, filename);
    const { text, metadata } = parsed;

    // 2. 生成文档级embedding
    const docEmbedding = await this.bailian.embedding(text.substring(0, 2000));

    // 3. 保存文档到数据库
    const documentId = await this.db.insertDocument({
      title: filename,
      content: text,
      embedding: docEmbedding,
      metadata: {
        ...metadata,
        fileType: metadata.mimeType
      }
    });

    // 4. 分块
    const chunks = this.splitText(text);

    // 5. 批量处理chunks (embedding + 存储)
    const processedChunks = await this.processChunks(documentId, chunks);

    return {
      documentId,
      chunks: processedChunks
    };
  }

  /**
   * 将文本分割成块
   */
  private splitText(text: string): string[] {
    const chunks: string[] = [];
    const { chunkSize, overlap } = this;

    // 按段落初步分割
    const paragraphs = text.split(/\n\s*\n/);
    let currentChunk = '';

    for (const paragraph of paragraphs) {
      const trimmedParagraph = paragraph.trim();
      if (!trimmedParagraph) continue;

      // 如果当前段落加上已有内容不超过chunkSize，添加到当前块
      if (currentChunk.length + trimmedParagraph.length < chunkSize) {
        currentChunk += (currentChunk ? '\n\n' : '') + trimmedParagraph;
      } else {
        // 保存当前块
        if (currentChunk) {
          chunks.push(currentChunk);
        }
        // 开始新块，包含重叠内容
        const words = currentChunk.split(/\s+/);
        const overlapText = words.slice(-Math.floor(overlap / 5)).join(' ');
        currentChunk = overlapText + '\n\n' + trimmedParagraph;
      }
    }

    // 添加最后一个块
    if (currentChunk) {
      chunks.push(currentChunk);
    }

    return chunks;
  }

  /**
   * 处理分块：生成embedding并存储
   */
  private async processChunks(
    documentId: string,
    chunks: string[]
  ): Promise<Array<{ id: string; content: string; chunkIndex: number }>> {
    const processedChunks = [];

    // 批量生成embeddings (每批5个，避免速率限制)
    const batchSize = 5;
    for (let i = 0; i < chunks.length; i += batchSize) {
      const batch = chunks.slice(i, i + batchSize);
      const embeddings = await Promise.all(
        batch.map(chunk => this.bailian.embedding(chunk))
      );

      // 存储到数据库
      for (let j = 0; j < batch.length; j++) {
        const chunkContent = batch[j];
        if (!chunkContent) continue;
        
        const chunkIndex = i + j;
        const chunkId = await this.db.insertChunk({
          document_id: documentId,
          content: chunkContent,
          embedding: embeddings[j],
          chunk_index: chunkIndex,
          metadata: {
            charCount: chunkContent.length
          }
        });

        processedChunks.push({
          id: chunkId,
          content: chunkContent,
          chunkIndex
        });
      }
    }

    return processedChunks;
  }
}

export default ChunkingService;
