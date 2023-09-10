FROM postgres

COPY config.sh .
COPY setup.sql .
RUN apt update && apt install -y postgresql-15-pgvector
RUN ["bash", "./config.sh"]
