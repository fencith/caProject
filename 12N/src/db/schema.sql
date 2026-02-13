-- 办公AI助手 - PostgreSQL Schema with pgvector
-- 支持混合检索 (向量 + 全文搜索 + RRF)

-- 1. 启用必要扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. 文档表 (主文档存储)
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT,
  embedding VECTOR(1536), -- 阿里云百炼 embedding 维度
  search_vector TSVECTOR, -- 全文搜索向量
  file_path TEXT, -- 原始文件路径
  file_type VARCHAR(50), -- pdf/docx/txt
  metadata JSONB DEFAULT '{}', -- 灵活的元数据
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. 文档分块表 (RAG检索单元)
CREATE TABLE chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  chunk_index INTEGER NOT NULL, -- 分块序号
  start_pos INTEGER, -- 在原文中的起始位置
  end_pos INTEGER, -- 在原文中的结束位置
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

-- 4. 用户表
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE,
  role VARCHAR(50) DEFAULT 'user', -- admin/user
  permissions JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. 对话表
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. 消息表
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL, -- system/user/assistant
  content TEXT NOT NULL,
  sources JSONB DEFAULT '[]', -- 引用的文档来源
  token_count INTEGER, -- token数量统计
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

-- 7. RRF (Reciprocal Rank Fusion) 评分函数
CREATE OR REPLACE FUNCTION rrf_score(rank INTEGER, k INTEGER DEFAULT 50)
RETURNS NUMERIC AS $$
  SELECT COALESCE(1.0 / (rank + k), 0.0);
$$ LANGUAGE SQL IMMUTABLE;

-- 8. 全文搜索更新触发器函数
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector := to_tsvector('chinese', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content, ''));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 9. 创建触发器
CREATE TRIGGER documents_search_vector_update
  BEFORE INSERT OR UPDATE ON documents
  FOR EACH ROW
  EXECUTE FUNCTION update_search_vector();

-- 10. 创建向量索引 (HNSW - 高精度)
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- 11. 创建全文搜索索引 (GIN)
CREATE INDEX ON documents USING GIN(search_vector);

-- 12. 创建普通索引优化查询
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- 13. 混合检索视图 (便于查询)
CREATE OR REPLACE VIEW hybrid_search_results AS
WITH vector_search AS (
  SELECT 
    c.id,
    c.document_id,
    c.content,
    c.chunk_index,
    rank() OVER (ORDER BY c.embedding <=> query_embedding) as vector_rank
  FROM chunks c
  WHERE query_embedding IS NOT NULL
),
fulltext_search AS (
  SELECT 
    c.id,
    c.document_id,
    c.content,
    c.chunk_index,
    rank() OVER (ORDER BY ts_rank_cd(d.search_vector, plainto_tsquery(query_text)) DESC) as text_rank
  FROM chunks c
  JOIN documents d ON c.document_id = d.id
  WHERE d.search_vector @@ plainto_tsquery(query_text)
)
SELECT 
  COALESCE(v.id, f.id) as id,
  COALESCE(v.document_id, f.document_id) as document_id,
  COALESCE(v.content, f.content) as content,
  COALESCE(v.chunk_index, f.chunk_index) as chunk_index,
  rrf_score(COALESCE(v.vector_rank, 100)) + rrf_score(COALESCE(f.text_rank, 100)) as rrf_score
FROM vector_search v
FULL OUTER JOIN fulltext_search f ON v.id = f.id;

COMMENT ON TABLE documents IS '存储原始文档信息';
COMMENT ON TABLE chunks IS '存储文档分块后的内容，用于RAG检索';
COMMENT ON TABLE conversations IS '存储用户对话会话';
COMMENT ON TABLE messages IS '存储对话消息';
COMMENT ON FUNCTION rrf_score IS 'Reciprocal Rank Fusion 评分函数，用于混合检索结果融合';
