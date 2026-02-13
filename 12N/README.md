# 办公AI助手系统

基于 **OpenCode + PolarDB PostgreSQL + pgvector** 的智能知识库问答系统。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     办公AI助手系统                          │
├─────────────────────────────────────────────────────────────┤
│  API层 (Express)                                              │
│  ├── POST /api/documents     # 上传文档                      │
│  ├── GET  /api/documents     # 获取文档列表                  │
│  ├── POST /api/search        # 混合检索                      │
│  ├── POST /api/chat          # RAG问答                     │
│  └── POST /api/chat/stream   # 流式RAG问答                 │
├─────────────────────────────────────────────────────────────┤
│  OpenCode 扩展层                                              │
│  ├── knowledge-query          # 知识检索Tool                │
│  ├── knowledge-add-document   # 添加文档Tool                │
│  ├── knowledge-list-docs      # 列表文档Tool                │
│  └── rag-agent               # RAG Agent                    │
├─────────────────────────────────────────────────────────────┤
│  业务服务层                                                   │
│  ├── 混合检索 (Vector + Full-text + RRF)                    │
│  ├── RAG对话 (检索+生成)                                     │
│  ├── 文档解析 (PDF/DOCX/TXT)                                 │
│  └── Embedding服务                                          │
├─────────────────────────────────────────────────────────────┤
│  数据层 (PolarDB PostgreSQL)                                  │
│  ├── 文档表 (vector + tsvector)                             │
│  ├── 分块表 (vector)                                        │
│  ├── 对话历史表                                             │
│  └── 用户表                                                 │
└─────────────────────────────────────────────────────────────┘
```

## ✨ 核心特性

- 🔍 **混合检索**: 向量相似度 + 全文搜索 + RRF融合 (准确率 62% → 84%)
- 🤖 **RAG问答**: 基于检索的上下文生成回答，支持流式输出
- 📄 **文档处理**: 支持 PDF、DOCX、TXT 格式自动解析和分块
- 🎯 **阿里云百炼**: 集成通义千问大模型和Embedding服务
- 🔧 **OpenCode扩展**: 提供Custom Tools和RAG Agent

## 🚀 快速开始

### 1. 环境准备

```bash
# Node.js 18+
node --version

# PostgreSQL 14+ with pgvector
# PolarDB for PostgreSQL (阿里云)
```

### 2. 安装依赖

```bash
npm install
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置以下变量：
# - DATABASE_URL (PolarDB连接字符串)
# - BAILIAN_API_KEY (阿里云百炼API密钥)
```

### 4. 初始化数据库

```bash
# 在PolarDB中执行SQL脚本
psql -d your_database -f src/db/schema.sql
```

### 5. 启动服务

```bash
# 开发模式
npm run dev

# 生产模式
npm run build
npm start
```

服务将在 http://localhost:3000 启动

## 📚 API文档

### 上传文档

```bash
POST /api/documents
Content-Type: multipart/form-data

file: <PDF/DOCX/TXT文件>
```

响应：
```json
{
  "success": true,
  "documentId": "uuid",
  "chunks": 12,
  "message": "Document uploaded and processed successfully"
}
```

### 混合检索

```bash
POST /api/search
Content-Type: application/json

{
  "query": "公司的请假流程是什么？",
  "limit": 10
}
```

响应：
```json
{
  "success": true,
  "query": "公司的请假流程是什么？",
  "results": [
    {
      "id": "uuid",
      "documentTitle": "员工手册.pdf",
      "content": "请假流程：1.提交申请 2.上级审批...",
      "score": 0.876
    }
  ]
}
```

### RAG问答

```bash
POST /api/chat
Content-Type: application/json

{
  "question": "公司的请假流程是什么？"
}
```

响应：
```json
{
  "success": true,
  "answer": "根据员工手册，公司的请假流程如下：...",
  "sources": [...]
}
```

### 流式RAG问答 (SSE)

```bash
POST /api/chat/stream
Content-Type: application/json

{
  "question": "公司的请假流程是什么？"
}
```

## 🛠️ OpenCode使用

### 配置Agent

将 `.opencode/agents/rag-agent.md` 复制到OpenCode agents目录：

```bash
# 全局配置
cp .opencode/agents/rag-agent.md ~/.config/opencode/agents/

# 或项目配置
cp .opencode/agents/rag-agent.md .opencode/agents/
```

### 使用RAG Agent

在OpenCode中切换到rag-agent，然后提问：

```
[rag-agent] 公司的请假流程是什么？
```

Agent会自动检索知识库并基于检索结果回答。

### 使用Knowledge Tools

在任意Agent中使用知识库工具：

```javascript
// 查询知识库
tool("knowledge-query", { query: "请假流程", limit: 5 })

// 添加文档
tool("knowledge-add-document", { filePath: "/path/to/doc.pdf" })

// 列出现有文档
tool("knowledge-list-documents", { limit: 10 })
```

## 📁 项目结构

```
.
├── src/
│   ├── api/                    # REST API路由
│   │   ├── documents.ts       # 文档管理API
│   │   ├── search.ts          # 检索API
│   │   └── chat.ts            # 对话API
│   ├── db/
│   │   ├── schema.sql         # 数据库Schema
│   │   └── connection.ts      # 数据库连接
│   ├── services/
│   │   ├── bailian.ts         # 阿里云百炼API
│   │   ├── parser.ts          # 文档解析
│   │   ├── chunking.ts        # 文档分块
│   │   ├── hybrid-search.ts   # 混合检索
│   │   └── rag.ts             # RAG服务
│   └── index.ts               # 应用入口
├── .opencode/
│   ├── agents/
│   │   └── rag-agent.md       # RAG Agent定义
│   └── tools/
│       └── knowledge-base.ts  # Knowledge Tools
├── .env.example               # 环境变量示例
└── package.json
```

## 🔧 技术栈

- **后端**: Node.js + Express + TypeScript
- **数据库**: PolarDB PostgreSQL + pgvector
- **LLM**: 阿里云百炼 (通义千问)
- **Embedding**: text-embedding-v3
- **Agent框架**: OpenCode

## 📊 性能指标

- 混合检索准确率: ~84% (vs 纯向量检索 62%)
- 平均响应时间: < 3秒
- 支持文档大小: 最大 50MB
- 支持并发: 20连接池

## 📝 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `DATABASE_URL` | PolarDB连接字符串 | `postgresql://user:pass@host:5432/db` |
| `BAILIAN_API_KEY` | 阿里云百炼API密钥 | `sk-xxx` |
| `PORT` | 服务端口 | `3000` |
| `NODE_ENV` | 运行环境 | `development` |

## 🚧 待完成功能 (Wave 4)

- [ ] Web管理界面 (React)
- [ ] 对话历史管理
- [ ] 用户权限系统
- [ ] 系统监控面板
- [ ] 钉钉/企微集成

## 📄 许可证

MIT

## 🤝 贡献

欢迎提交Issue和PR！

## 📮 联系方式

如有问题，请通过Issue联系。
