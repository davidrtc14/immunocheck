CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE corpus_versions (
    corpus_version text PRIMARY KEY
        CHECK (corpus_version ~ '^sha256:[0-9a-f]{64}$'),
    schema_version integer NOT NULL CHECK (schema_version > 0),
    generated_at timestamptz NOT NULL,
    chunks_sha256 char(64) NOT NULL CHECK (chunks_sha256 ~ '^[0-9a-f]{64}$'),
    document_count integer NOT NULL CHECK (document_count > 0),
    chunk_count integer NOT NULL CHECK (chunk_count > 0),
    state text NOT NULL DEFAULT 'READY'
        CHECK (state IN ('READY', 'ACTIVE', 'ARCHIVED')),
    activated_at timestamptz,
    manifest jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ((state = 'ACTIVE' AND activated_at IS NOT NULL) OR state <> 'ACTIVE')
);

CREATE UNIQUE INDEX corpus_versions_single_active_idx
    ON corpus_versions ((state))
    WHERE state = 'ACTIVE';

CREATE TABLE corpus_documents (
    corpus_version text NOT NULL REFERENCES corpus_versions(corpus_version) ON DELETE CASCADE,
    document_id text NOT NULL,
    title text NOT NULL,
    source_name text NOT NULL,
    document_type text NOT NULL,
    publication_date date,
    access_date date NOT NULL,
    source_url text NOT NULL,
    final_url text NOT NULL,
    format text NOT NULL CHECK (format IN ('pdf', 'html')),
    license_status text NOT NULL,
    content_type text NOT NULL,
    downloaded_at timestamptz NOT NULL,
    content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    size_bytes bigint NOT NULL CHECK (size_bytes >= 0),
    metadata jsonb NOT NULL,
    PRIMARY KEY (corpus_version, document_id)
);

CREATE TABLE corpus_chunks (
    corpus_version text NOT NULL,
    chunk_id text NOT NULL,
    document_id text NOT NULL,
    text_content text NOT NULL CHECK (length(btrim(text_content)) > 0),
    chunk_sha256 char(64) NOT NULL CHECK (chunk_sha256 ~ '^[0-9a-f]{64}$'),
    page_start integer NOT NULL CHECK (page_start > 0),
    page_end integer NOT NULL CHECK (page_end >= page_start),
    source_name text NOT NULL,
    document_title text NOT NULL,
    source_url text NOT NULL,
    publication_date date,
    metadata jsonb NOT NULL,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('pg_catalog.portuguese', text_content)
    ) STORED,
    PRIMARY KEY (corpus_version, chunk_id),
    FOREIGN KEY (corpus_version, document_id)
        REFERENCES corpus_documents(corpus_version, document_id) ON DELETE CASCADE
);

CREATE INDEX corpus_chunks_document_idx
    ON corpus_chunks (corpus_version, document_id);

CREATE INDEX corpus_chunks_search_idx
    ON corpus_chunks USING gin (search_vector);

CREATE TABLE chunk_embeddings (
    corpus_version text NOT NULL,
    chunk_id text NOT NULL,
    model_name text NOT NULL,
    model_revision text NOT NULL,
    embedding vector(1024) NOT NULL,
    normalized boolean NOT NULL,
    generated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (corpus_version, chunk_id, model_name, model_revision),
    FOREIGN KEY (corpus_version, chunk_id)
        REFERENCES corpus_chunks(corpus_version, chunk_id) ON DELETE CASCADE
);

CREATE INDEX chunk_embeddings_lookup_idx
    ON chunk_embeddings (corpus_version, model_name, model_revision);

COMMENT ON TABLE corpus_versions IS
    'Versões auditáveis do corpus documental; nunca armazena interações de usuários.';
COMMENT ON TABLE chunk_embeddings IS
    'Embeddings locais BGE-M3 associados à versão exata do corpus e do modelo.';
