# Dekalabs PostgreSQL Docker Image

Docker image for `postgres` used as a database for projects made by Dekalabs.

## Build images

To build the images and push them to Dekalabs registry:

    make build
    make push

## Docker-compose example

Example of a `docker-compose.yml` file that uses this image:

    version: '3'

    volumes:
      production_postgres_data: {}
      production_postgres_data_backups: {}

    services:

      service:
        image: registry.dekaside.com/service/service:latest
        command: ./start

      postgres:
        image: registry.dekaside.com/library/postgres:latest
        volumes:
          - production_postgres_data:/var/lib/postgresql/data
          - production_postgres_data_backups:/backups
        env_file:
          - ./.env
