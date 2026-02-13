import axios from 'axios';
import { Readable } from 'stream';

export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatOptions {
  model?: string;
  temperature?: number;
  stream?: boolean;
  max_tokens?: number;
}

export interface ChatResponse {
  content: string;
  usage?: {
    input_tokens: number;
    output_tokens: number;
  };
}

export interface EmbeddingResponse {
  embedding: number[];
  usage?: {
    input_tokens: number;
  };
}

export class BailianClient {
  private apiKey: string;
  private baseURL: string;

  constructor(apiKey: string, baseURL = 'https://dashscope.aliyuncs.com/api/v1') {
    this.apiKey = apiKey;
    this.baseURL = baseURL;
  }

  /**
   * 获取文本embedding向量
   * @param text 输入文本
   * @returns 1536维向量
   */
  async embedding(text: string): Promise<number[]> {
    try {
      const response = await axios.post(
        `${this.baseURL}/embeddings`,
        {
          model: 'text-embedding-v3',
          input: {
            texts: [text]
          }
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const embedding = response.data.output?.embeddings?.[0]?.embedding;
      if (!embedding || !Array.isArray(embedding)) {
        throw new Error('Invalid embedding response');
      }

      return embedding;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Embedding API error: ${error.response?.data?.message || error.message}`);
      }
      throw error;
    }
  }

  /**
   * 聊天对话
   * @param messages 消息列表
   * @param options 选项
   * @returns 聊天响应
   */
  async chat(messages: Message[], options: ChatOptions = {}): Promise<ChatResponse> {
    const {
      model = 'qwen-turbo',
      temperature = 0.7,
      max_tokens = 2000
    } = options;

    try {
      const response = await axios.post(
        `${this.baseURL}/services/aigc/text-generation/generation`,
        {
          model,
          input: {
            messages
          },
          parameters: {
            temperature,
            max_tokens,
            result_format: 'message'
          }
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const output = response.data.output;
      const content = output?.choices?.[0]?.message?.content;

      if (!content) {
        throw new Error('Invalid chat response');
      }

      return {
        content,
        usage: response.data.usage
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Chat API error: ${error.response?.data?.message || error.message}`);
      }
      throw error;
    }
  }

  /**
   * 流式聊天对话
   * @param messages 消息列表
   * @param options 选项
   * @returns 可读流
   */
  async chatStream(messages: Message[], options: ChatOptions = {}): Promise<Readable> {
    const {
      model = 'qwen-turbo',
      temperature = 0.7,
      max_tokens = 2000
    } = options;

    try {
      const response = await axios.post(
        `${this.baseURL}/services/aigc/text-generation/generation`,
        {
          model,
          input: {
            messages
          },
          parameters: {
            temperature,
            max_tokens,
            result_format: 'message',
            incremental_output: true
          }
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
          },
          responseType: 'stream'
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`Chat stream API error: ${error.response?.data?.message || error.message}`);
      }
      throw error;
    }
  }
}

export default BailianClient;
