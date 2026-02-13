import pdf from 'pdf-parse';
import mammoth from 'mammoth';

export interface ParsedDocument {
  text: string;
  metadata: {
    filename?: string;
    pageCount?: number;
    wordCount: number;
    mimeType: string;
  };
}

export class DocumentParser {
  /**
   * 解析PDF文件
   * @param buffer 文件Buffer
   * @param filename 文件名
   */
  async parsePDF(buffer: Buffer, filename?: string): Promise<ParsedDocument> {
    try {
      const data = await pdf(buffer);
      const text = data.text;
      const wordCount = this.countWords(text);

      return {
        text,
        metadata: {
          filename,
          pageCount: data.numpages,
          wordCount,
          mimeType: 'application/pdf'
        }
      };
    } catch (error) {
      throw new Error(`PDF parse error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * 解析DOCX文件
   * @param buffer 文件Buffer
   * @param filename 文件名
   */
  async parseDOCX(buffer: Buffer, filename?: string): Promise<ParsedDocument> {
    try {
      const result = await mammoth.extractRawText({ buffer });
      const text = result.value;
      const wordCount = this.countWords(text);

      return {
        text,
        metadata: {
          filename,
          wordCount,
          mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
      };
    } catch (error) {
      throw new Error(`DOCX parse error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * 解析TXT文件
   * @param buffer 文件Buffer
   * @param filename 文件名
   */
  async parseTXT(buffer: Buffer, filename?: string): Promise<ParsedDocument> {
    try {
      const text = buffer.toString('utf-8');
      const wordCount = this.countWords(text);

      return {
        text,
        metadata: {
          filename,
          wordCount,
          mimeType: 'text/plain'
        }
      };
    } catch (error) {
      throw new Error(`TXT parse error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * 根据MIME类型自动选择解析器
   * @param buffer 文件Buffer
   * @param mimeType MIME类型
   * @param filename 文件名
   */
  async parse(buffer: Buffer, mimeType: string, filename?: string): Promise<ParsedDocument> {
    switch (mimeType) {
      case 'application/pdf':
        return this.parsePDF(buffer, filename);
      
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
      case 'application/msword':
        return this.parseDOCX(buffer, filename);
      
      case 'text/plain':
      case 'text/markdown':
      case 'text/csv':
        return this.parseTXT(buffer, filename);
      
      default:
        // 尝试根据文件扩展名判断
        if (filename) {
          const ext = filename.toLowerCase().split('.').pop();
          if (ext === 'pdf') return this.parsePDF(buffer, filename);
          if (ext === 'docx' || ext === 'doc') return this.parseDOCX(buffer, filename);
          if (ext === 'txt' || ext === 'md' || ext === 'csv') return this.parseTXT(buffer, filename);
        }
        throw new Error(`Unsupported file type: ${mimeType}`);
    }
  }

  /**
   * 统计字数（中文字符 + 英文单词）
   * @param text 文本内容
   */
  private countWords(text: string): number {
    // 中文字符数
    const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
    // 英文单词数
    const englishWords = (text.match(/[a-zA-Z]+/g) || []).length;
    return chineseChars + englishWords;
  }
}

export default DocumentParser;
