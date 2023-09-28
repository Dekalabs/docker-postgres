# Variables
# ------------------------------------------------------------------------------
POSTGRES_IMAGE_ID=dekalabs/postgres
POSTGIS_IMAGE_ID=dekalabs/postgis

.PHONY: build_postgres push_postgres build_postgis push_postgis

build_postgres:
	docker buildx build . -f ./postgres/10/Dockerfile --tag ${POSTGRES_IMAGE_ID}:10 --platform linux/amd64,linux/arm64
	docker buildx build . -f ./postgres/11/Dockerfile --tag ${POSTGRES_IMAGE_ID}:11 --platform linux/amd64,linux/arm64
	docker buildx build . -f ./postgres/12/Dockerfile --tag ${POSTGRES_IMAGE_ID}:12 --platform linux/amd64,linux/arm64
	docker buildx build . -f ./postgres/13/Dockerfile --tag ${POSTGRES_IMAGE_ID}:13 --platform linux/amd64,linux/arm64
	docker buildx build . -f ./postgres/14/Dockerfile --tag ${POSTGRES_IMAGE_ID}:14 --tag ${POSTGRES_IMAGE_ID}:latest --platform linux/amd64,linux/arm64

push_postgres:
	docker buildx build . -f ./postgres/10/Dockerfile --tag ${POSTGRES_IMAGE_ID}:10 --platform linux/amd64,linux/arm64 --push
	docker buildx build . -f ./postgres/11/Dockerfile --tag ${POSTGRES_IMAGE_ID}:11 --platform linux/amd64,linux/arm64 --push
	docker buildx build . -f ./postgres/12/Dockerfile --tag ${POSTGRES_IMAGE_ID}:12 --platform linux/amd64,linux/arm64 --push
	docker buildx build . -f ./postgres/13/Dockerfile --tag ${POSTGRES_IMAGE_ID}:13 --platform linux/amd64,linux/arm64 --push
	docker buildx build . -f ./postgres/14/Dockerfile --tag ${POSTGRES_IMAGE_ID}:14 --tag ${POSTGRES_IMAGE_ID}:latest --platform linux/amd64,linux/arm64 --push


build_postgis:
	docker buildx build . -f ./postgis/11/Dockerfile --tag ${POSTGIS_IMAGE_ID}:11-2.5 --tag ${POSTGIS_IMAGE_ID}:11 --platform linux/amd64,linux/arm64
	docker buildx build . -f ./postgis/12/Dockerfile --tag ${POSTGIS_IMAGE_ID}:12-3.0 --tag ${POSTGIS_IMAGE_ID}:12 --platform linux/amd64,linux/arm64
	docker buildx build . -f ./postgis/13/Dockerfile --tag ${POSTGIS_IMAGE_ID}:13-3.1 --tag ${POSTGIS_IMAGE_ID}:13 --platform linux/amd64,linux/arm64
	docker buildx build . -f ./postgis/14/Dockerfile --tag ${POSTGIS_IMAGE_ID}:14-3.4 --tag ${POSTGIS_IMAGE_ID}:13 --tag ${POSTGIS_IMAGE_ID}:latest --platform linux/amd64,linux/arm64

push_postgis:
	docker buildx build . -f ./postgis/11/Dockerfile --tag ${POSTGIS_IMAGE_ID}:11-2.5 --tag ${POSTGIS_IMAGE_ID}:11 --platform linux/amd64,linux/arm64 --push
	docker buildx build . -f ./postgis/12/Dockerfile --tag ${POSTGIS_IMAGE_ID}:12-3.0 --tag ${POSTGIS_IMAGE_ID}:12 --platform linux/amd64,linux/arm64 --push
	docker buildx build . -f ./postgis/13/Dockerfile --tag ${POSTGIS_IMAGE_ID}:13-3.1 --tag ${POSTGIS_IMAGE_ID}:13 --platform linux/amd64,linux/arm64 --push
	docker buildx build . -f ./postgis/14/Dockerfile --tag ${POSTGIS_IMAGE_ID}:14-3.4 --tag ${POSTGIS_IMAGE_ID}:14 --tag ${POSTGIS_IMAGE_ID}:latest --platform linux/amd64,linux/arm64 --push

build: build_postgres build_postgis

push: push_postgres push_postgis
