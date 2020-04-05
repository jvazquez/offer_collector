DOCKER = $(if $(DOCKER_BINARY),$(DOCKER_BINARY),/usr/bin/docker)
BUILD_ARG = $(if $(filter  $(NOCACHE), 1),--no-cache)
BUILD_ARG_BASE = $(if $(filter  $(NOCACHEBASE), 1),--no-cache)
DEFAULT_ENVIRONMENT = develop
ENVIRONMENT_TO_BUILD := $(if $(ENVIRONMENT),$(ENVIRONMENT),$(DEFAULT_ENVIRONMENT))
DOCKERFILE_PATH = $(if $(filter  $(ENVIRONMENT_TO_BUILD), production),images/python/production/Dockerfile,images/python/development/Dockerfile)

development: develop_disk_volumes develop_network
develop_up: develop_start

develop_network:
	$(DOCKER) network inspect $(DEFAULT_ENVIRONMENT)_network > /dev/null 2>&1 || $(DOCKER) network create $(DEFAULT_ENVIRONMENT)_network
develop_start:
	docker-compose up -d
develop_stop:
	docker-compose down --volumes
develop_disk_volumes:
	$(DOCKER) volume create $(DEFAULT_ENVIRONMENT)_store_db