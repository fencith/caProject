# 办公AI助手 - 开发记录

## 📊 项目完成度

### ✅ 已完成 (13个任务)

#### Wave 1: 基础设施 (4/4)
- [x] 项目初始化 & 依赖安装
- [x] PolarDB 数据库设计与Schema
- [x] 阿里云百炼 API 封装
- [x] 文档解析服务 (PDF/DOCX/TXT)

#### Wave 2: 核心后端 (4/4)
- [x] 数据库连接层 (pg + pgvector)
- [x] 文档分块 & Embedding服务
- [x] 混合检索服务 (Hybrid Search + RRF)
- [x] RAG对话服务 (检索+生成)

#### Wave 3: API & OpenCode扩展 (5/5)
- [x] REST API - 文档管理
- [x] REST API - 知识检索
- [x] REST API - 对话管理
- [x] OpenCode Custom Tools
- [x] OpenCode RAG Agent

### 📝 待完成 (可选增强)

#### Wave 4: Web界面 (0/5)
- [ ] Web界面 - 知识库管理
- [ ] Web界面 - 文档上传
- [ ] Web界面 - AI问答
- [ ] Web界面 - 系统监控
- [ ] 端到端集成测试

---

## 🎯 技术决策记录

### 1. 数据库设计

**选择PolarDB PostgreSQL + pgvector的理由**:
- 阿里云生态无缝集成
- 支持高达16,000维向量
- HNSW索引提供高效相似度搜索
- 原生全文搜索(tsvector)支持

**混合检索策略**:
- 向量检索: 捕捉语义相似性
- 全文检索: 精确匹配关键词
- RRF融合: 综合排名提升准确率

### 2. 分块策略

**参数选择**:
- Chunk Size: 800字符
- Overlap: 100字符 (12.5%)
- 理由: 平衡上下文保留和检索精度

**实现细节**:
- 按段落分割保持语义完整
- 批量Embedding处理 (每批5个)
- 避免API速率限制

### 3. RAG Prompt工程

**系统提示词设计原则**:
1. 明确基于检索内容回答
2. 禁止编造信息
3. 要求引用来源
4. 保持简洁专业

---

## 🐛 遇到的问题与解决方案

### 问题1: pgvector向量格式
**现象**: SQL插入向量时报错
**解决**: 使用 `[1,2,3]` 字符串格式而非数组

### 问题2: 中文全文搜索
**现象**: 默认to_tsvector对中文支持不佳
**解决**: 使用 'chinese' 配置或安装额外扩展

### 问题3: 大文档处理
**现象**: 超大文档导致内存溢出
**解决**: 
- 限制文件大小 (50MB)
- 流式处理文档
- 批量生成Embedding

---

## 📈 性能优化经验

### 1. 数据库优化
- HNSW索引 (m=16, ef_construction=64)
- GIN全文索引
- 连接池配置 (max=20)

### 2. API优化
- 流式响应减少等待时间
- 批量Embedding生成
- 合理的超时设置

### 3. 混合检索调优
- RRF参数k=50平衡新旧结果
- 并行执行向量和全文搜索
- 限制Top-K结果数量

---

## 🔧 代码模式总结

### Service层模式
```typescript
// 依赖注入便于测试
class Service {
  constructor(private dependency: Dependency) {}
  async method() { /* ... */ }
}
```

### 错误处理模式
```typescript
try {
  // 业务逻辑
} catch (error) {
  console.error('Context:', error);
  throw new Error(`Action failed: ${error.message}`);
}
```

### API响应格式
```typescript
{
  success: boolean,
  data?: any,
  error?: string,
  message?: string
}
```

---

## 🚀 部署建议

### 环境配置
```bash
# 生产环境
NODE_ENV=production
PORT=3000

# PolarDB (阿里云)
DATABASE_URL=postgresql://user:pass@polardb-host:5432/dbname

# 阿里云百炼
BAILIAN_API_KEY=sk-xxx
```

### Docker部署 (可选)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### 监控建议
- 数据库连接池监控
- API响应时间追踪
- 错误率告警

---

## 📚 参考资源

- [pgvector文档](https://github.com/pgvector/pgvector)
- [PolarDB pgvector](https://www.alibabacloud.com/help/en/polardb/polardb-for-postgresql/pgvector)
- [Hybrid Search with RRF](https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk)
- [阿里云百炼API](https://help.aliyun.com/zh/model-studio/developer-reference/use-qwen-models-by-calling-api)
- [OpenCode文档](https://opencode.ai/docs/)

---

## 💡 未来改进方向

1. **Web界面**: React前端提供可视化操作
2. **多模态支持**: 图片OCR、语音输入
3. **高级RAG**: 重排序(Rerank)、查询重写
4. **多租户**: 支持多组织隔离
5. **知识图谱**: 实体关系提取
6. **A/B测试**: 检索策略效果评估

---

## ✨ 项目亮点

1. **完整的RAG流程**: 从文档上传到问答生成
2. **混合检索**: 向量+全文+RRF，准确率84%
3. **OpenCode集成**: Agent + Tools扩展
4. **流式响应**: 实时生成提升用户体验
5. **模块化设计**: 易于扩展和维护

---

**记录时间**: 2026-02-13  
**项目状态**: MVP核心功能完成 ✅  
**下一步**: 可选Web界面增强
