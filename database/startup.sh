set -eu

mkdir -p ~/pg_cont_data

docker run \
	-d --rm \
	-p 5432:5432 \
	-v ~/pg_cont_data:/data \
	-e POSTGRES_USER=root \
	-e POSTGRES_PASSWORD=password \
	-e PGDATA=/data \
	pgimg

