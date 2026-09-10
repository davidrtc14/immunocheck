ALTER TABLE corpus_documents
    DROP CONSTRAINT corpus_documents_format_check;

ALTER TABLE corpus_documents
    ADD CONSTRAINT corpus_documents_format_check
    CHECK (format IN ('pdf', 'html', 'xml'));
