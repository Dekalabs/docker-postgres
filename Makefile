# Variables
# ------------------------------------------------------------------------------
POSTGRES_IMAGE_ID=dekalabs/postgres
POSTGIS_IMAGE_ID=dekalabs/postgis

.PHONY: build_posgres push_postgres build_posgis push_posgis

build_posgres:
	docker build . -f ./postgres/10/Dockerfile --tag ${POSTGRES_IMAGE_ID}:10
	docker build . -f ./postgres/11/Dockerfile --tag ${POSTGRES_IMAGE_ID}:11
	docker build . -f ./postgres/12/Dockerfile --tag ${POSTGRES_IMAGE_ID}:12
	docker build . -f ./postgres/13/Dockerfile --tag ${POSTGRES_IMAGE_ID}:13 --tag ${POSTGRES_IMAGE_ID}:latest

push_postgres:
	docker push ${POSTGRES_IMAGE_ID}:10
	docker push ${POSTGRES_IMAGE_ID}:11
	docker push ${POSTGRES_IMAGE_ID}:12
	docker push ${POSTGRES_IMAGE_ID}:13
	docker push ${POSTGRES_IMAGE_ID}:latest


build_posgis:
	docker build . -f ./postgis/11/Dockerfile --tag ${POSTGIS_IMAGE_ID}:11-2.5 --tag ${POSTGIS_IMAGE_ID}:11
	docker build . -f ./postgis/12/Dockerfile --tag ${POSTGIS_IMAGE_ID}:12-3.0 --tag ${POSTGIS_IMAGE_ID}:12
	docker build . -f ./postgis/13/Dockerfile --tag ${POSTGIS_IMAGE_ID}:13-3.1 --tag ${POSTGIS_IMAGE_ID}:13 --tag ${POSTGIS_IMAGE_ID}:latest

push_posgis:
	docker push ${POSTGIS_IMAGE_ID}:11
	docker push ${POSTGIS_IMAGE_ID}:11-2.5
	docker push ${POSTGIS_IMAGE_ID}:12
	docker push ${POSTGIS_IMAGE_ID}:12-3.0
	docker push ${POSTGIS_IMAGE_ID}:13-3.1
	docker push ${POSTGIS_IMAGE_ID}:latest

build: build_posgres build_posgis

push: push_postgres push_posgis
