IMAGE_NAME_A ?= ifex_local/ifex_alpine
IMAGE_NAME_U ?= ifex_local/ifex_ubuntu

# WARNING: Container name is common for the two variants, which has some consequences...
# Use only one variant at a time to be certain.  If it matters, this can be fixed later.
CONTAINER_NAME ?= ifex_run
CONTAINER_HOSTNAME ?= ifex_run

.PHONY: _reset build build_alpine build_ubuntu rebuild buildnew run run_alpine clean logs shell stop kill rm rmi

default:
	@echo "make [build|buildnew|run|clean|logs|shell|stop|kill|rm|rmi]"

build: build_alpine

build_alpine:
	cd .. && docker build --tag=${IMAGE_NAME_A}:latest -f docker/Dockerfile.alpine .

build_ubuntu:
	cd .. && docker build --tag=${IMAGE_NAME_U}:latest -f docker/Dockerfile.ubuntu .

# Modify build marker, this will invalidate any cached steps after its use
_reset:
	date >rebuild_marker

# Build container from the point of rebuild_marker (if used)
rebuild: _reset build

# Build container fully from scratch, without reusing cached steps
buildnew:
	cd .. && docker build --no-cache --tag=${IMAGE_NAME_A}:latest -f docker/Dockerfile.alpine .

# Run container (detached)
run: run_alpine

run_selinux:
	ZFLAG=:z make run_alpine

run_alpine:
	docker rm -f ${CONTAINER_NAME}
	docker run -ti -h "${CONTAINER_HOSTNAME}" -v ${PWD}/..:/work${ZFLAG} --name=${CONTAINER_NAME} ${IMAGE_NAME_A}:latest /bin/bash

run_ubuntu:
	docker rm -f ${CONTAINER_NAME}
	docker run -ti -h "${CONTAINER_HOSTNAME}" -v ${PWD}/..:/work:z --name=${CONTAINER_NAME} ${IMAGE_NAME_U}:latest /bin/bash

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
