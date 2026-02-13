import BailianClient from './bailian.js';
import type { Message } from './bailian.js';
import HybridSearchService from './hybrid-search.js';
import type { SearchResult } from './hybrid-search.js';

export interface RAGOptions {
  maxContextChunks?: number;
  temperature?: number;
  systemPrompt?: string;
}

export interface RAGResponse {
  answer: string;
  sources: SearchResult[];
  usage?: {
    input_tokens: number;
    output_tokens: number;
  };
}

export class RagService {
  private bailian: BailianClient;
  private search: HybridSearchService;

  constructor(
    bailianClient: BailianClient,
    searchService: HybridSearchService
  ) {
    this.bailian = bailianClient;
    this.search = searchService;
  }

  /**
   * RAG问答：检索增强生成
   */
  async query(
    question: string,
    options: RAGOptions = {}
  ): Promise<RAGResponse> {
    const {
      maxContextChunks = 5,
      temperature = 0.7,
      systemPrompt = this.defaultSystemPrompt()
    } = options;

    // 1. 生成问题的embedding
    const queryEmbedding = await this.bailian.embedding(question);

    // 2. 混合检索相关文档
    const searchResults = await this.search.search(
      question,
      queryEmbedding,
      { limit: maxContextChunks }
    );

    if (searchResults.length === 0) {
      return {
        answer: '抱歉，我没有找到与您问题相关的信息。',
        sources: []
      };
    }

    // 3. 构建上下文
    const context = this.buildContext(searchResults);

    // 4. 构建消息
    const messages: Message[] = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: `基于以下上下文回答问题：\n\n${context}\n\n问题：${question}` }
    ];

    // 5. 调用LLM生成回答
    const response = await this.bailian.chat(messages, {
      temperature
    });

    return {
      answer: response.content,
      sources: searchResults,
      usage: response.usage
    };
  }

  /**
   * 流式RAG问答
   */
  async *queryStream(
    question: string,
    options: RAGOptions = {}
  ): AsyncGenerator<{ chunk: string; sources?: SearchResult[] }> {
    const {
      maxContextChunks = 5,
      temperature = 0.7,
      systemPrompt = this.defaultSystemPrompt()
    } = options;

    // 1. 生成问题的embedding
    const queryEmbedding = await this.bailian.embedding(question);

    // 2. 混合检索相关文档
    const searchResults = await this.search.search(
      question,
      queryEmbedding,
      { limit: maxContextChunks }
    );

    if (searchResults.length === 0) {
      yield { chunk: '抱歉，我没有找到与您问题相关的信息。' };
      return;
    }

    // 3. 先返回来源
    yield { chunk: '', sources: searchResults };

    // 4. 构建上下文
    const context = this.buildContext(searchResults);

    // 5. 构建消息
    const messages: Message[] = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: `基于以下上下文回答问题：\n\n${context}\n\n问题：${question}` }
    ];

    // 6. 流式生成回答
    const stream = await this.bailian.chatStream(messages, { temperature });

    // 处理流式响应
    for await (const chunk of stream) {
      yield { chunk: chunk.toString() };
    }
  }

  /**
   * 构建上下文
   */
  private buildContext(results: SearchResult[]): string {
    return results
      .map((result, index) => {
        return `[${index + 1}] 来源：${result.document_title}\n${result.content}\n`;
      })
      .join('\n');
  }

  /**
   * 默认系统提示词
   */
  private defaultSystemPrompt(): string {
    return `你是一个专业的企业知识库助手。请基于提供的上下文回答用户问题。

回答规则：
1. 基于提供的上下文信息回答，不要编造信息
2. 如果上下文中没有相关信息，请明确说明
3. 回答时引用来源编号 [1], [2] 等
4. 保持回答简洁明了
5. 使用中文回答`;
  }
}

export default RagService;
