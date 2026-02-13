import express from 'express';
import type { Application, Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';

// 导入路由
import documentsRouter from './api/documents.js';
import searchRouter from './api/search.js';
import chatRouter from './api/chat.js';

// 加载环境变量
dotenv.config();

const app: Application = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('dev'));

// 健康检查
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API路由
app.use('/api/documents', documentsRouter);
app.use('/api/search', searchRouter);
app.use('/api/chat', chatRouter);

// 404处理
app.use((req: Request, res: Response) => {
  res.status(404).json({ error: 'Not found' });
});

// 错误处理
app.use((err: Error, req: Request, res: Response) => {
  console.error('Error:', err);
  res.status(500).json({ 
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// 启动服务器
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`🚀 Server is running on port ${PORT}`);
    console.log(`📚 API Documentation:`);
    console.log(`  POST /api/documents     - 上传文档`);
    console.log(`  GET  /api/documents     - 获取文档列表`);
    console.log(`  POST /api/search        - 混合检索`);
    console.log(`  POST /api/chat          - RAG问答`);
    console.log(`  POST /api/chat/stream   - 流式RAG问答`);
  });
}

export default app;
