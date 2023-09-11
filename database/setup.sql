\c postgres
CREATE EXTENSION vector;
CREATE TABLE embed
(
	id bigserial PRIMARY KEY,
	rawtext TEXT,
	embeddings vector(1536)
)
