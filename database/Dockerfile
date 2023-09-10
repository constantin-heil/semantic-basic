FROM postgres

COPY setup.sql /docker-entrypoint-initdb.d
RUN apt update && apt install -y postgresql-15-pgvector
