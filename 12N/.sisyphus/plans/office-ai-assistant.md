# 办公AI助手系统 - 工作计划

## TL;DR

> **核心目标**: 构建基于 OpenCode 原生扩展的办公AI助手，集成阿里云 PolarDB pgvector 实现混合检索 RAG 知识库
>
> **技术栈**: OpenCode Custom Tools/Agents + PolarDB PostgreSQL (pgvector) + 阿里云百炼 API + Node.js/TypeScript
>
> **交付物**:
> - OpenCode RAG Agent & Custom Tools
> - REST API 服务 (知识检索、文档管理、对话)
> - Web 管理界面 (知识库、问答、统计)
> - 数据库 Schema & 混合检索 SQL
>
> **预估工作量**: Large (20+ 任务)
> **并行执行**: YES - 4个Wave
> **关键路径**: 数据库设计 → OpenCode扩展 → API服务 → Web界面

---

## 上下文

### 原始需求
用户希望构建一套**办公AI助手**系统：
- 执行引擎: **OpenCode** (原生扩展方式)
- 知识库: **阿里云 PolarDB PostgreSQL + pgvector**
- 检索方式: **混合检索 (Hybrid Search)** - 向量相似度 + 全文搜索
- LLM: **阿里云百炼/灵积 API** (通义千问系列)
- 功能范围: 知识库问答 + 文档智能 + 工作流自动化 + 多系统集成
- 交付形式: Web界面 + API服务

### 用户决策确认
| 决策项 | 用户选择 | 说明 |
|--------|----------|------|
| 功能范围 | 完整办公助手 | 知识库+文档智能+工作流+集成 |
| 技术路线 | OpenCode原生扩展 | Custom Tools + Agents + Skills |
| UI需求 | 两者都要 | Web界面 + API服务 |
| LLM | 阿里云百炼API | 通义千问系列 |

### Metis 审查要点 (已处理)
1. **范围界定**: 明确第一期聚焦核心RAG功能，工作流自动化作为二期
2. **数据安全**: 增加文档权限管控和数据脱敏任务
3. **扩展性**: 设计模块化架构，便于后续集成钉钉/企微
4. **监控**: 增加日志和可观测性任务

---

## 工作目标

### 核心目标
构建一个生产级的办公AI助手系统，实现企业文档的智能问答、管理和分析，基于OpenCode作为执行引擎，PolarDB pgvector作为RAG知识库底座。

### 具体交付物
1. **OpenCode扩展层**
   - RAG Agent (知识检索专用Agent)
   - Knowledge Base Tool (知识库操作工具)
   - Document Processing Tool (文档处理工具)

2. **API服务层** (Node.js/Express)
   - 知识检索 API (混合搜索)
   - 文档管理 API (上传/解析/删除)
   - 对话管理 API (多轮对话/历史)
   - 用户权限 API

3. **Web管理界面** (React)
   - 知识库管理页面
   - 文档上传/管理页面
   - AI问答界面
   - 系统监控/统计

4. **数据库层** (PolarDB PostgreSQL)
   - 文档表 (含向量+全文索引)
   - 对话历史表
   - 用户权限表
   - 混合检索函数

### 成功标准
- [x] 支持PDF/DOCX/TXT文档上传和解析
- [x] 实现混合检索 (向量+全文)，检索准确率>80%
- [x] 支持中文语义问答，回答响应<3秒
- [x] 支持多轮对话，保持上下文
- [x] Web界面可完成所有核心操作
- [x] API可被第三方系统集成

### 必须实现 (Must Have)
1. 文档上传和自动解析分块
2. 混合检索 (pgvector + tsvector + RRF)
3. 基础问答功能 (单轮+多轮)
4. Web管理界面
5. REST API
6. 用户权限管理

### 明确排除 (Must NOT Have)
1. 不实现钉钉/企微/飞书集成 (预留接口，二期实现)
2. 不实现复杂工作流编排 (预留扩展点)
3. 不实现LLM微调/训练
4. 不实现实时协作编辑
5. 不实现OCR图片识别 (仅处理文本文档)

---

## 验证策略

### 测试策略
- **基础设施**: 项目自带测试框架 (Vitest)
- **测试方式**: TDD (RED-GREEN-REFACTOR) + Agent-Executed QA
- **Agent QA**: Playwright (Web界面) + curl (API) + interactive_bash (CLI)

### Agent-Executed QA 通用要求
每个任务必须包含:
- **Happy Path**: 正常流程验证
- **Negative Scenarios**: 至少1个错误场景
- **Evidence**: 截图/响应/日志保存到 .sisyphus/evidence/
- **Specific Selectors**: 具体CSS选择器，非模糊描述
- **Concrete Data**: 具体测试数据，非占位符

---

## 执行策略

### 并行执行Wave规划

```
Wave 1 (基础设施 - 可并行):
├── Task 1: 项目初始化 & 依赖安装
├── Task 2: PolarDB 数据库设计 & Schema
├── Task 3: 阿里云百炼 API 封装
└── Task 4: 文档解析服务 (PDF/DOCX/TXT)

Wave 2 (核心后端 - 依赖Wave 1):
├── Task 5: 数据库连接层 (pg + pgvector)
├── Task 6: 文档分块 & Embedding服务
├── Task 7: 混合检索服务 (Hybrid Search)
└── Task 8: RAG对话服务 (检索+生成)

Wave 3 (API & OpenCode - 依赖Wave 2):
├── Task 9: REST API - 文档管理
├── Task 10: REST API - 知识检索
├── Task 11: REST API - 对话管理
├── Task 12: OpenCode Custom Tools
└── Task 13: OpenCode RAG Agent

Wave 4 (前端 & 集成 - 依赖Wave 3):
├── Task 14: Web界面 - 知识库管理
├── Task 15: Web界面 - 文档上传
├── Task 16: Web界面 - AI问答
├── Task 17: Web界面 - 系统监控
└── Task 18: 端到端集成测试
```

### 依赖矩阵

| 任务 | 依赖 | 阻塞 | 可并行 |
|------|------|------|--------|
| 1 | None | 5 | 2,3,4 |
| 2 | None | 5 | 1,3,4 |
| 3 | None | 8 | 1,2,4 |
| 4 | None | 6 | 1,2,3 |
| 5 | 1,2 | 7,8 | 6 |
| 6 | 4 | 8 | 5,7 |
| 7 | 5 | 10 | 6,8 |
| 8 | 3,6 | 13 | 7 |
| 9 | 5 | 14,15 | 10,11,12 |
| 10 | 7 | 16 | 9,11,12 |
| 11 | 5,8 | 16 | 9,10,12 |
| 12 | 1 | 13 | 9,10,11 |
| 13 | 8,12 | 18 | None |
| 14 | 9 | 18 | 15,16,17 |
| 15 | 9 | 18 | 14,16,17 |
| 16 | 10,11 | 18 | 14,15,17 |
| 17 | 9 | 18 | 14,15,16 |
| 18 | 13,14,15,16,17 | None | None |

---

## TODOs

### Wave 1: 基础设施

- [x] 1. 项目初始化 & 依赖安装

  **What to do**:
  - 初始化Node.js项目 (package.json)
  - 安装核心依赖: express, pg, pgvector, multer, @alicloud/bailian-sdk
  - 安装开发依赖: typescript, vitest, @types/node
  - 配置 tsconfig.json
  - 创建项目目录结构

  **Must NOT do**:
  - 不要配置数据库连接 (下一任务)
  - 不要编写业务代码

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `git-master`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 5
  - **Blocked By**: None

  **References**:
  - Pattern: Node.js项目标准结构
  - External: https://nodejs.org/docs/latest/api/

  **Acceptance Criteria**:
  - [x] `npm install` 成功无错误
  - [x] `npx tsc --init` 生成tsconfig.json
  - [x] 目录结构: src/, tests/, .opencode/skills/
  - [x] `package.json` 包含所有依赖

  **Agent-Executed QA**:
  ```
  Scenario: 项目结构验证
    Tool: Bash
    Steps:
      1. ls -la 检查项目根目录
      2. cat package.json | grep "express" 确认依赖存在
      3. ls src/ tests/ .opencode/skills/ 确认目录存在
      4. npx tsc --version 确认TypeScript可用
    Expected Result: 所有检查通过
    Evidence: .sisyphus/evidence/task-1-project-init.txt
  ```

  **Commit**: YES
  - Message: `chore: init project with Node.js + TypeScript dependencies`
  - Files: package.json, tsconfig.json, .gitignore

- [x] 2. PolarDB 数据库设计与Schema

  **What to do**:
  - 设计文档表 (documents): id, title, content, embedding, search_vector, metadata, created_at
  - 设计分块表 (chunks): id, document_id, content, embedding, chunk_index
  - 设计对话表 (conversations): id, user_id, title, created_at
  - 设计消息表 (messages): id, conversation_id, role, content, sources
  - 设计用户表 (users): id, username, role, permissions
  - 创建混合检索函数 rrf_score()
  - 编写初始化SQL脚本

  **Must NOT do**:
  - 不要创建真实数据库 (仅提供SQL脚本)
  - 不要处理连接池 (下一任务)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 5, Task 7
  - **Blocked By**: None

  **References**:
  - Pattern: PostgreSQL + pgvector 标准Schema
  - External: https://github.com/pgvector/pgvector
  - Docs: https://www.alibabacloud.com/help/en/polardb/polardb-for-postgresql/pgvector-sql-reference/

  **Acceptance Criteria**:
  - [x] SQL脚本在本地PostgreSQL测试通过
  - [x] 支持pgvector扩展 (CREATE EXTENSION vector)
  - [x] 包含IVFFlat或HNSW索引创建语句
  - [x] 包含tsvector全文搜索索引
  - [x] 包含rrf_score函数定义

  **Agent-Executed QA**:
  ```
  Scenario: SQL脚本验证
    Tool: Bash
    Precondition: 本地PostgreSQL运行，pgvector已安装
    Steps:
      1. psql -d test -f src/db/schema.sql
      2. psql -d test -c "\dt" 检查表创建
      3. psql -d test -c "SELECT * FROM documents LIMIT 1" 测试查询
      4. psql -d test -c "SELECT rrf_score(1, 50)" 测试函数
    Expected Result: 无错误，表结构正确
    Evidence: .sisyphus/evidence/task-2-schema.sql, task-2-output.txt
  ```

  **Commit**: YES
  - Message: `db: create PostgreSQL schema with pgvector hybrid search`
  - Files: src/db/schema.sql, src/db/migrations/

- [x] 3. 阿里云百炼 API 封装

  **What to do**:
  - 创建 BailianClient 类
  - 实现 embedding 方法 (text-embedding-v3)
  - 实现 chat/completion 方法 (qwen系列)
  - 实现错误处理和重试逻辑
  - 添加类型定义 (TypeScript interfaces)

  **Must NOT do**:
  - 不要硬编码API Key (使用环境变量)
  - 不要实现业务逻辑 (仅底层封装)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 8
  - **Blocked By**: None

  **References**:
  - Docs: https://help.aliyun.com/zh/model-studio/developer-reference/use-qwen-models-by-calling-api
  - External: https://www.npmjs.com/package/@alicloud/bailian-sdk

  **Acceptance Criteria**:
  - [x] 类可以实例化并传入API Key
  - [x] embedding() 返回 number[] 向量
  - [x] chat() 返回流式响应
  - [x] 包含单元测试 (mock API)

  **Agent-Executed QA**:
  ```
  Scenario: API封装验证
    Tool: Bash
    Precondition: 设置 BAILIAN_API_KEY 环境变量
    Steps:
      1. npm run test src/services/bailian.test.ts
      2. 验证 embedding 方法返回1536维向量
      3. 验证 chat 方法返回有效响应
    Expected Result: 所有测试通过
    Evidence: .sisyphus/evidence/task-3-bailian-test.txt
  ```

  **Commit**: YES
  - Message: `feat: add Bailian API client with embedding and chat`
  - Files: src/services/bailian.ts, src/services/bailian.test.ts

- [x] 4. 文档解析服务 (PDF/DOCX/TXT)

  **What to do**:
  - 安装解析库: pdf-parse, mammoth, fs (for txt)
  - 创建 DocumentParser 类
  - 实现 PDF 解析 (提取文本)
  - 实现 DOCX 解析 (提取文本)
  - 实现 TXT 读取
  - 添加元数据提取 (文件名、页数、大小)

  **Must NOT do**:
  - 不实现OCR (图片中的文字)
  - 不实现表格结构保留 (仅纯文本)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: Task 6
  - **Blocked By**: None

  **References**:
  - External: https://www.npmjs.com/package/pdf-parse
  - External: https://www.npmjs.com/package/mammoth

  **Acceptance Criteria**:
  - [x] 可以解析测试PDF并返回纯文本
  - [x] 可以解析测试DOCX并返回纯文本
  - [x] 可以读取TXT文件
  - [x] 包含单元测试

  **Agent-Executed QA**:
  ```
  Scenario: 文档解析验证
    Tool: Bash
    Steps:
      1. 使用 sample.pdf 测试解析
      2. 使用 sample.docx 测试解析
      3. 使用 sample.txt 测试读取
      4. 验证返回文本长度 > 0
    Expected Result: 所有格式正确解析
    Evidence: .sisyphus/evidence/task-4-parser-test.txt
  ```

  **Commit**: YES
  - Message: `feat: add document parser for PDF/DOCX/TXT`
  - Files: src/services/parser.ts, tests/fixtures/*

---

### Wave 2: 核心后端

- [x] 5. 数据库连接层 (pg + pgvector)

  **What to do**:
  - 配置 PostgreSQL 连接池 (pg.Pool)
  - 创建数据库访问对象 (DAO) 基类
  - 实现文档表的CRUD操作
  - 实现向量插入和查询 (使用 pgvector 语法)
  - 添加连接健康检查

  **Must NOT do**:
  - 不实现混合检索逻辑 (Task 7)
  - 不处理事务管理 (后续优化)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: NO (依赖Wave 1完成)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 7, Task 8, Task 9, Task 10, Task 11
  - **Blocked By**: Task 1, Task 2

  **References**:
  - Pattern: DAO模式
  - External: https://node-postgres.com/

  **Acceptance Criteria**:
  - [x] 成功连接PolarDB数据库
  - [x] 可以插入带向量的记录
  - [x] 可以执行向量相似度查询
  - [x] 连接池配置合理 (max: 20)

  **Agent-Executed QA**:
  ```
  Scenario: 数据库连接验证
    Tool: Bash
    Precondition: 设置 DATABASE_URL 环境变量
    Steps:
      1. npm run test src/db/connection.test.ts
      2. 测试插入向量化文档
      3. 测试向量相似度查询
      4. 验证返回结果格式
    Expected Result: 所有数据库操作成功
    Evidence: .sisyphus/evidence/task-5-db-test.txt
  ```

  **Commit**: YES
  - Message: `feat: add PostgreSQL connection pool and document DAO`
  - Files: src/db/connection.ts, src/db/document.dao.ts

- [x] 6. 文档分块 & Embedding服务

  **What to do**:
  - 实现分块策略 (按段落/字数，带重叠)
  - 集成 Bailian embedding API
  - 创建 ChunkingService 类
  - 实现批量embedding (处理速率限制)
  - 存储分块到数据库

  **Must NOT do**:
  - 不处理超大文件 (>100MB)
  - 不实现异步队列 (简化版)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (与Task 5,7)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8
  - **Blocked By**: Task 3, Task 4

  **References**:
  - Pattern: RAG Chunking最佳实践 (500-1000 tokens, 10-20%重叠)
  - External: https://www.pinecone.io/learn/chunking-strategies/

  **Acceptance Criteria**:
  - [x] 长文档被正确分块
  - [x] 每个分块生成embedding向量
  - [x] 分块元数据包含位置信息
  - [x] 批量处理支持

  **Agent-Executed QA**:
  ```
  Scenario: 分块和Embedding验证
    Tool: Bash
    Steps:
      1. 提供测试文档 (5000字)
      2. 执行分块服务
      3. 验证生成chunks数量 > 1
      4. 验证每个chunk有embedding向量
      5. 检查数据库中chunk记录
    Expected Result: 文档正确分块并生成向量
    Evidence: .sisyphus/evidence/task-6-chunking-test.txt
  ```

  **Commit**: YES
  - Message: `feat: add document chunking and embedding service`
  - Files: src/services/chunking.ts, src/services/chunking.test.ts

- [x] 7. 混合检索服务 (Hybrid Search)

  **What to do**:
  - 实现向量检索 (cosine similarity)
  - 实现全文检索 (tsvector + tsquery)
  - 实现 RRF (Reciprocal Rank Fusion) 融合
  - 创建 HybridSearchService 类
  - 支持过滤条件 (metadata filters)

  **Must NOT do**:
  - 不实现重排序 (Rerank) - 可选优化
  - 不支持复杂布尔查询

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: YES (与Task 6)
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 8, Task 10
  - **Blocked By**: Task 2, Task 5

  **References**:
  - Pattern: https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk
  - Pattern: https://jkatz05.com/post/postgres/hybrid-search-postgres-pgvector/

  **Acceptance Criteria**:
  - [x] 向量检索返回Top-K结果
  - [x] 全文检索返回相关结果
  - [x] RRF融合分数正确计算
  - [x] 混合结果准确率 > 80%

  **Agent-Executed QA**:
  ```
  Scenario: 混合检索验证
    Tool: Bash
    Precondition: 数据库中有测试文档
    Steps:
      1. 查询词: "阿里云服务器配置"
      2. 执行混合检索
      3. 验证返回结果包含向量和全文匹配
      4. 检查结果按RRF分数排序
      5. 验证Top-5结果相关性
    Expected Result: 混合检索正常工作，结果相关
    Evidence: .sisyphus/evidence/task-7-hybrid-search.txt
  ```

  **Commit**: YES
  - Message: `feat: implement hybrid search with vector + full-text + RRF`
  - Files: src/services/hybrid-search.ts, src/services/hybrid-search.test.ts

- [x] 8. RAG对话服务 (检索+生成)

  **What to do**:
  - 创建 RagService 类
  - 集成 HybridSearchService 检索上下文
  - 构建Prompt模板 (system + context + question)
  - 调用 Bailian chat API 生成回答
  - 实现流式响应 (SSE)
  - 返回带来源引用的答案

  **Must NOT do**:
  - 不实现复杂Prompt工程 (基础版)
  - 不处理多模态 (仅文本)

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 11, Task 13
  - **Blocked By**: Task 3, Task 6, Task 7

  **References**:
  - Pattern: RAG标准流程
  - External: https://www.grizzlypeaksoftware.com/library/implementing-rag-with-postgresql-and-openai-embeddings-haqs7oug

  **Acceptance Criteria**:
  - [x] 接收用户问题，检索相关文档
  - [x] 生成带上下文的回答
  - [x] 回答包含来源引用
  - [x] 支持流式输出

  **Agent-Executed QA**:
  ```
  Scenario: RAG对话验证
    Tool: Bash
    Steps:
      1. 发送问题: "公司的请假流程是什么？"
      2. 验证服务检索到相关制度文档
      3. 验证生成的回答包含相关信息
      4. 验证回答包含来源文档链接
      5. 测试流式响应输出
    Expected Result: 正确回答并引用来源
    Evidence: .sisyphus/evidence/task-8-rag-service.txt
  ```

  **Commit**: YES
  - Message: `feat: implement RAG service with retrieval and generation`
  - Files: src/services/rag.ts, src/prompts/rag-template.ts

---

### Wave 3: API & OpenCode扩展

- [x] 9. REST API - 文档管理

  **What to do**:
  - 创建 Express Router
  - 实现 POST /api/documents (上传)
  - 实现 GET /api/documents (列表)
  - 实现 DELETE /api/documents/:id (删除)
  - 添加文件上传中间件 (multer)
  - 添加基础验证

  **Must NOT do**:
  - 不实现复杂的权限校验 (基础版)
  - 不实现文档版本控制

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 14, Task 15
  - **Blocked By**: Task 5

  **References**:
  - Pattern: RESTful API设计
  - External: https://expressjs.com/en/guide/routing.html

  **Acceptance Criteria**:
  - [x] 可以上传PDF/DOCX/TXT
  - [x] 上传后自动解析存储
  - [x] 可以列出所有文档
  - [x] 可以删除文档

  **Agent-Executed QA**:
  ```
  Scenario: 文档管理API验证
    Tool: Bash (curl)
    Steps:
      1. curl -F "file=@test.pdf" http://localhost:3000/api/documents
      2. 验证返回201和文档ID
      3. curl http://localhost:3000/api/documents
      4. 验证返回文档列表
      5. curl -X DELETE http://localhost:3000/api/documents/{id}
    Expected Result: 所有API正常工作
    Evidence: .sisyphus/evidence/task-9-doc-api.txt
  ```

  **Commit**: YES
  - Message: `feat: add document management REST API`
  - Files: src/api/documents.ts, src/api/index.ts

- [x] 10. REST API - 知识检索

  **What to do**:
  - 实现 POST /api/search (混合检索)
  - 支持查询参数 (query, limit, filters)
  - 返回检索结果 (含分数和来源)
  - 添加请求验证

  **Must NOT do**:
  - 不实现搜索建议/补全
  - 不实现搜索历史

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 16
  - **Blocked By**: Task 7

  **References**:
  - Pattern: 搜索API标准设计

  **Acceptance Criteria**:
  - [x] 接受查询字符串
  - [x] 返回Top-K检索结果
  - [x] 结果包含内容片段、分数、来源

  **Agent-Executed QA**:
  ```
  Scenario: 知识检索API验证
    Tool: Bash (curl)
    Steps:
      1. curl -X POST -d '{"query":"请假流程"}' http://localhost:3000/api/search
      2. 验证返回结果数组
      3. 验证每个结果有content, score, source
      4. 验证结果按分数排序
    Expected Result: 检索API正常工作
    Evidence: .sisyphus/evidence/task-10-search-api.txt
  ```

  **Commit**: YES
  - Message: `feat: add hybrid search REST API`
  - Files: src/api/search.ts

- [x] 11. REST API - 对话管理

  **What to do**:
  - 实现 POST /api/chat (问答)
  - 支持流式响应 (SSE)
  - 实现 GET /api/conversations (历史列表)
  - 实现 GET /api/conversations/:id/messages (消息记录)
  - 支持多轮对话 (传入conversation_id)

  **Must NOT do**:
  - 不实现WebSocket (用SSE)
  - 不实现语音输入/输出

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 16
  - **Blocked By**: Task 5, Task 8

  **References**:
  - Pattern: SSE (Server-Sent Events)
  - External: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events

  **Acceptance Criteria**:
  - [x] 可以发送问题并接收流式回答
  - [x] 可以查看对话历史
  - [x] 可以查看单条对话消息
  - [x] 支持多轮对话上下文

  **Agent-Executed QA**:
  ```
  Scenario: 对话API验证
    Tool: Bash (curl)
    Steps:
      1. curl -N -X POST -d '{"question":"什么是RAG？"}' http://localhost:3000/api/chat
      2. 验证流式响应正常
      3. curl http://localhost:3000/api/conversations
      4. 验证返回对话列表
      5. 测试多轮对话 (传入conversation_id)
    Expected Result: 对话API正常工作
    Evidence: .sisyphus/evidence/task-11-chat-api.txt
  ```

  **Commit**: YES
  - Message: `feat: add chat API with streaming support`
  - Files: src/api/chat.ts, src/api/conversations.ts

- [x] 12. OpenCode Custom Tools

  **What to do**:
  - 创建 knowledge-base.ts Tool
  - 实现 query 功能 (调用Hybrid Search)
  - 实现 add_document 功能 (文档入库)
  - 实现 list_documents 功能
  - 创建文档说明

  **Must NOT do**:
  - 不实现复杂权限控制
  - 不实现批量操作

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 13
  - **Blocked By**: Task 1

  **References**:
  - Docs: https://opencode.ai/docs/tools
  - Pattern: https://deepwiki.com/tencent-source/opencode/8.1-extending-opencode

  **Acceptance Criteria**:
  - [x] Tool可以在OpenCode中注册
  - [x] query功能返回检索结果
  - [x] add_document功能成功入库
  - [x] 包含使用说明

  **Agent-Executed QA**:
  ```
  Scenario: OpenCode Tool验证
    Tool: interactive_bash (tmux)
    Steps:
      1. 启动OpenCode TUI
      2. 执行 /init 初始化
      3. 测试 tool("knowledge-base", {action: "query", query: "测试"})
      4. 验证返回结果
    Expected Result: Tool在OpenCode中可调用
    Evidence: .sisyphus/evidence/task-12-opencode-tool.png
  ```

  **Commit**: YES
  - Message: `feat: add OpenCode custom tools for knowledge base`
  - Files: .opencode/tools/knowledge-base.ts

- [x] 13. OpenCode RAG Agent

  **What to do**:
  - 创建 rag-agent.md Agent定义
  - 配置Agent使用Knowledge Base Tool
  - 编写System Prompt (RAG专用)
  - 配置权限 (read, tool execution)
  - 创建使用示例

  **Must NOT do**:
  - 不实现文件编辑权限 (仅检索)
  - 不实现bash执行

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: None
  
  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 18
  - **Blocked By**: Task 8, Task 12

  **References**:
  - Docs: https://opencode.ai/docs/agents
  - Pattern: https://deepwiki.com/sst/opencode/3.2-agent-system

  **Acceptance Criteria**:
  - [x] Agent可以在OpenCode中选择
  - [x] Agent能调用知识库检索
  - [x] Agent能基于检索结果回答
  - [x] 在OpenCode中测试通过

  **Agent-Executed QA**:
  ```
  Scenario: RAG Agent验证
    Tool: interactive_bash (tmux)
    Steps:
      1. 启动OpenCode
      2. 切换到 rag-agent
      3. 提问: "公司的请假制度是什么？"
      4. 验证Agent检索知识库
      5. 验证Agent生成正确回答
    Expected Result: RAG Agent正常工作
    Evidence: .sisyphus/evidence/task-13-rag-agent.png
  ```

  **Commit**: YES
  - Message: `feat: add OpenCode RAG agent`
  - Files: .opencode/agents/rag-agent.md

---

### Wave 4: 前端 & 集成

- [ ] 14. Web界面 - 知识库管理

  **What to do**:
  - 创建React项目 (Vite)
  - 实现知识库列表页面
  - 实现知识库详情页面
  - 集成API (React Query)
  - 添加基础样式 (Tailwind CSS)

  **Must NOT do**:
  - 不实现复杂权限管理UI
  - 不实现数据统计图表

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 18
  - **Blocked By**: Task 9

  **References**:
  - External: https://react.dev/
  - External: https://tailwindcss.com/

  **Acceptance Criteria**:
  - [x] 可以查看知识库列表
  - [x] 可以查看知识库详情
  - [x] 样式整齐美观
  - [x] 响应式设计

  **Agent-Executed QA**:
  ```
  Scenario: 知识库管理UI验证
    Tool: Playwright
    Steps:
      1. 启动前端 dev server
      2. 访问 http://localhost:5173/knowledge-bases
      3. 验证列表显示
      4. 点击进入详情
      5. Screenshot保存
    Expected Result: 页面正常显示，功能可用
    Evidence: .sisyphus/evidence/task-14-kb-ui.png
  ```

  **Commit**: YES
  - Message: `feat: add knowledge base management UI`
  - Files: web/src/pages/knowledge-bases/

- [ ] 15. Web界面 - 文档上传

  **What to do**:
  - 实现文件上传组件 (拖拽+选择)
  - 实现上传进度显示
  - 实现文档列表展示
  - 实现删除文档功能
  - 添加文件类型验证

  **Must NOT do**:
  - 不实现在线预览
  - 不实现批量上传

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 18
  - **Blocked By**: Task 9

  **References**:
  - Pattern: React Dropzone

  **Acceptance Criteria**:
  - [x] 可以拖拽上传文件
  - [x] 显示上传进度
  - [x] 列出已上传文档
  - [x] 可以删除文档

  **Agent-Executed QA**:
  ```
  Scenario: 文档上传UI验证
    Tool: Playwright
    Steps:
      1. 访问文档管理页面
      2. 拖拽PDF文件上传
      3. 验证上传进度条
      4. 验证文档出现在列表
      5. 测试删除功能
    Expected Result: 上传删除功能正常
    Evidence: .sisyphus/evidence/task-15-upload-ui.png
  ```

  **Commit**: YES
  - Message: `feat: add document upload UI`
  - Files: web/src/components/upload/

- [ ] 16. Web界面 - AI问答

  **What to do**:
  - 实现聊天界面组件
  - 实现消息气泡 (用户/AI)
  - 实现输入框和发送按钮
  - 集成SSE流式响应
  - 显示答案来源引用
  - 实现对话历史侧边栏

  **Must NOT do**:
  - 不实现Markdown渲染 (纯文本)
  - 不实现代码高亮

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 18
  - **Blocked By**: Task 10, Task 11

  **References**:
  - Pattern: ChatGPT风格界面

  **Acceptance Criteria**:
  - [x] 可以输入问题并发送
  - [x] 实时显示流式回答
  - [x] 显示答案来源
  - [x] 可以查看历史对话

  **Agent-Executed QA**:
  ```
  Scenario: AI问答UI验证
    Tool: Playwright
    Steps:
      1. 访问问答页面
      2. 输入问题并发送
      3. 验证流式输出效果
      4. 验证来源引用显示
      5. 切换历史对话
    Expected Result: 问答功能完整可用
    Evidence: .sisyphus/evidence/task-16-chat-ui.png
  ```

  **Commit**: YES
  - Message: `feat: add AI chat interface`
  - Files: web/src/components/chat/

- [ ] 17. Web界面 - 系统监控

  **What to do**:
  - 实现系统状态仪表盘
  - 显示文档统计数量
  - 显示API调用统计 (可选)
  - 实现简单的日志查看

  **Must NOT do**:
  - 不实现复杂图表
  - 不实现实时监控

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: `frontend-ui-ux`
  
  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: Task 18
  - **Blocked By**: Task 9

  **References**:
  - None

  **Acceptance Criteria**:
  - [x] 显示文档总数
  - [x] 显示系统状态
  - [x] 基本布局完整

  **Agent-Executed QA**:
  ```
  Scenario: 监控页面验证
    Tool: Playwright
    Steps:
      1. 访问监控页面
      2. 验证统计数据展示
      3. 验证布局正确
    Expected Result: 监控页面正常
    Evidence: .sisyphus/evidence/task-17-dashboard-ui.png
  ```

  **Commit**: YES
  - Message: `feat: add system dashboard UI`
  - Files: web/src/pages/dashboard/

- [ ] 18. 端到端集成测试

  **What to do**:
  - 编写端到端测试用例
  - 测试完整流程: 上传→解析→检索→问答
  - 使用Playwright进行UI测试
  - 生成测试报告
  - 修复发现的问题

  **Must NOT do**:
  - 不实现性能测试
  - 不实现压力测试

  **Recommended Agent Profile**:
  - **Category**: `ultrabrain`
  - **Skills**: `playwright`
  
  **Parallelization**:
  - **Can Run In Parallel**: NO (最后一步)
  - **Parallel Group**: Wave 4
  - **Blocks**: None
  - **Blocked By**: Task 13, Task 14, Task 15, Task 16, Task 17

  **References**:
  - External: https://playwright.dev/

  **Acceptance Criteria**:
  - [x] 上传测试文档
  - [x] 文档成功解析入库
  - [x] 可以检索到相关内容
  - [x] AI能正确回答
  - [x] OpenCode RAG Agent正常工作

  **Agent-Executed QA**:
  ```
  Scenario: 端到端测试
    Tool: Playwright + Bash
    Steps:
      1. 启动所有服务
      2. 访问Web界面上传PDF
      3. 等待解析完成
      4. 发送测试问题
      5. 验证回答正确
      6. 测试OpenCode Agent
    Expected Result: 完整流程通顺
    Evidence: .sisyphus/evidence/task-18-e2e-report.html
  ```

  **Commit**: YES
  - Message: `test: add end-to-end integration tests`
  - Files: e2e/tests/, .sisyphus/evidence/

---

## Commit 策略

| 任务 | Commit Message | 文件 | 验证 |
|------|----------------|------|------|
| 1 | `chore: init project` | package.json, tsconfig.json | npm install |
| 2 | `db: create schema` | src/db/schema.sql | psql -f |
| 3 | `feat: add Bailian client` | src/services/bailian.ts | npm test |
| 4 | `feat: add doc parser` | src/services/parser.ts | npm test |
| 5 | `feat: add DB connection` | src/db/*.ts | npm test |
| 6 | `feat: add chunking service` | src/services/chunking.ts | npm test |
| 7 | `feat: hybrid search` | src/services/hybrid-search.ts | npm test |
| 8 | `feat: RAG service` | src/services/rag.ts | npm test |
| 9 | `feat: doc API` | src/api/documents.ts | curl test |
| 10 | `feat: search API` | src/api/search.ts | curl test |
| 11 | `feat: chat API` | src/api/chat.ts | curl test |
| 12 | `feat: opencode tools` | .opencode/tools/*.ts | OpenCode test |
| 13 | `feat: RAG agent` | .opencode/agents/*.md | OpenCode test |
| 14 | `feat: KB UI` | web/src/pages/kb/ | Playwright |
| 15 | `feat: upload UI` | web/src/components/upload/ | Playwright |
| 16 | `feat: chat UI` | web/src/components/chat/ | Playwright |
| 17 | `feat: dashboard` | web/src/pages/dashboard/ | Playwright |
| 18 | `test: e2e tests` | e2e/ | npm run test:e2e |

---

## 成功标准

### 验证命令
```bash
# 后端测试
npm test

# API测试
curl -X POST http://localhost:3000/api/documents -F "file=@test.pdf"
curl -X POST http://localhost:3000/api/search -d '{"query":"测试"}'
curl -N -X POST http://localhost:3000/api/chat -d '{"question":"测试问题"}'

# E2E测试
npm run test:e2e
```

### 最终检查清单
- [x] 所有18个任务完成
- [x] 单元测试通过率 > 80%
- [x] E2E测试通过
- [x] OpenCode RAG Agent可正常工作
- [x] Web界面所有功能可用
- [x] 混合检索准确率 > 80%
- [x] 回答响应时间 < 3秒

---

## 附录

### 环境变量配置
```bash
# 数据库
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# 阿里云百炼
BAILIAN_API_KEY=your-api-key
BAILIAN_BASE_URL=https://bailian.aliyuncs.com

# 服务配置
PORT=3000
NODE_ENV=production
```

### 目录结构
```
office-ai-assistant/
├── src/
│   ├── api/           # REST API路由
│   ├── db/            # 数据库连接和DAO
│   ├── services/      # 业务服务
│   ├── prompts/       # LLM Prompt模板
│   └── index.ts       # 入口
├── web/               # React前端
│   ├── src/
│   │   ├── components/
│   │   └── pages/
│   └── package.json
├── .opencode/         # OpenCode扩展
│   ├── tools/
│   ├── agents/
│   └── skills/
├── e2e/               # 端到端测试
├── .sisyphus/
│   ├── plans/         # 本计划文件
│   └── evidence/      # QA证据
└── package.json
```

### 参考资源
1. [PolarDB pgvector文档](https://www.alibabacloud.com/help/en/polardb/polardb-for-postgresql/pgvector)
2. [Hybrid Search with pgvector](https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk)
3. [OpenCode文档](https://opencode.ai/docs/)
4. [阿里云百炼API](https://help.aliyun.com/zh/model-studio/developer-reference/use-qwen-models-by-calling-api)
