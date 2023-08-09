# SPDX-FileCopyrightText: Copyright (c) 2023 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

IMAGE_NAME ?= ifex_local/sdbus-xml2cpp
CONTAINER_NAME ?= sdbus-xml2cpp
CONTAINER_HOSTNAME ?= sdbus-xml2cpp

.PHONY: _reset build rebuild buildnew run clean logs shell stop kill rm rmi

default:
	@echo "make [build|buildnew|run|clean|logs|shell|stop|kill|rm|rmi]"

build:
	docker build --tag=${IMAGE_NAME}:latest .

# Build container fully from scratch, without reusing cached steps
buildnew:
	docker build --no-cache --tag=${IMAGE_NAME}:latest .

# Run container (detached)
run_selinux:
	ZFLAG=:z make run

run:
	@docker rm -f ${CONTAINER_NAME}
	@docker run -ti -h "${CONTAINER_HOSTNAME}" -v ${PWD}/..:/work${ZFLAG} --name=${CONTAINER_NAME} ${IMAGE_NAME}:latest

run_shell:
	@docker rm -f ${CONTAINER_NAME}
	@docker run -ti -h "${CONTAINER_HOSTNAME}" -v ${PWD}/..:/work${ZFLAG} --name=${CONTAINER_NAME} ${IMAGE_NAME}:latest /bin/bash

# Force remove container and image
clean:  kill rm rmi

logs:
	docker logs -f ${CONTAINER_NAME}

shell:
	docker exec -it ${CONTAINER_NAME} /bin/bash

stop:
	docker stop ${CONTAINER_NAME} || true

# Force stop and remove container
kill:
	docker kill ${CONTAINER_NAME} || echo "Cannot kill - probably not running"
	docker rm ${CONTAINER_NAME} || echo "Container removed already"

rm:
	docker kill ${CONTAINER_NAME} 2>/dev/null && echo killed || echo "Container seems stopped already"
	docker rm ${CONTAINER_NAME} || echo "Container seems removed already"

rmi:
	@docker rmi ${IMAGE_NAME}:latest 2>/dev/null && echo removed image || echo "Image seems removed already"
