set -e

if [ -z $HOST_DBPATH ]; then
	HOST_DBPATH=pgdb01
fi

if [ -z $HOST_DBPORT ]; then
	HOST_DBPORT=5432
fi

mkdir -p ~/pg_cont_data/${HOST_DBPATH}

docker run \
	-d --rm \
	-p ${HOST_DBPORT}:5432 \
	-v ~/pg_cont_data/${HOST_DBPATH}:/data \
	-e POSTGRES_USER=root \
	-e POSTGRES_PASSWORD=password \
	-e PGDATA=/data \
	pgimg

