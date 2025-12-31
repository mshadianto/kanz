-- KANZ - Database Setup Script
-- Run this in your Supabase SQL Editor

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create document_chunks table with vector embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(384), -- Dimension for all-MiniLM-L6-v2
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    agent_type TEXT, -- Which agent generated this response
    sources JSONB DEFAULT '[]'::jsonb, -- Referenced document chunks
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create analytics table
CREATE TABLE IF NOT EXISTS query_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id),
    query TEXT NOT NULL,
    agent_type TEXT,
    response_time_ms INTEGER,
    tokens_used INTEGER,
    sources_retrieved INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id 
    ON document_chunks(document_id);

CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
    ON document_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id 
    ON chat_messages(session_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at 
    ON chat_messages(created_at DESC);

-- Create function for vector similarity search
CREATE OR REPLACE FUNCTION match_document_chunks(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    document_id uuid,
    content text,
    similarity float,
    metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.content,
        1 - (dc.embedding <=> query_embedding) as similarity,
        dc.metadata
    FROM document_chunks dc
    WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create RLS (Row Level Security) policies
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_analytics ENABLE ROW LEVEL SECURITY;

-- Allow all operations for authenticated users (adjust as needed)
CREATE POLICY "Allow all for authenticated users" ON documents
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON document_chunks
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON chat_sessions
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON chat_messages
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON query_analytics
    FOR ALL USING (true);

-- Insert initial metadata
INSERT INTO documents (title, source, content, metadata) VALUES 
(
    'Saudi Investment Strategy - Setup Instructions',
    'system',
    'This RAG system contains comprehensive analysis of Saudi Arabia investment opportunities.',
    '{"type": "system", "version": "1.0"}'::jsonb
) ON CONFLICT DO NOTHING;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO postgres, anon, authenticated, service_role;
