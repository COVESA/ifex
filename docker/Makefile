# Change to for example podman if desired.
CTR_TOOL ?= docker

IMAGE_NAME_A ?= ifex_local/ifex_alpine
IMAGE_NAME_U ?= ifex_local/ifex_ubuntu

# WARNING: Container name is common for the two variants, which has some consequences...
# Use only one variant at a time to be certain, or change this if it matters.
CONTAINER_NAME ?= ifex_run
CONTAINER_HOSTNAME ?= ifex_run

.PHONY: _reset build build_alpine build_ubuntu build_generic rebuild buildnew run run_ubuntu run_alpine clean logs shell stop kill rm rmi

default:
	@echo 'This subproject creates containers with IFEX environment installed and ready.'
	@echo 'Usage:  make [build_<distro>|run_<distro>|run_<distro>_test|clean|logs|shell|stop|kill|rm|rmi]'
	@echo '        ...where <distro> is replaced by ubuntu or alpine.'
	@echo 'Example: $ make run_ubuntu'
	@echo 'run_<distro> opens an interactive bash shell.'
	@echo 'run_<distro>_test runs the project unit tests inside the container and then exits.'

build: build_ubuntu

build_alpine:
	@DOCKERFILE=docker/Dockerfile.alpine TAG=${IMAGE_NAME_A} make build_generic

build_ubuntu:
	@DOCKERFILE=docker/Dockerfile.ubuntu TAG=${IMAGE_NAME_U} make build_generic

build_generic:
	cd ../.. && ${CTR_TOOL} build --tag=${TAG}:latest -f ${DOCKERFILE} .

# Targets to run containers
run: run_alpine

# Ensure workdir is writable on an SELINUX system.  (example - adjust as needed)
run_selinux:
	ZFLAG=:z make run_alpine

run_alpine:
	@IMAGE_NAME=${IMAGE_NAME_A} BINARY=/bin/bash make run_interactive

run_ubuntu:
	@IMAGE_NAME=${IMAGE_NAME_U} BINARY=/bin/bash make run_interactive

run_alpine_test:
	${CTR_TOOL} rm -f ${CONTAINER_NAME}
	${CTR_TOOL} run -t -h "${CONTAINER_HOSTNAME}" -v ${PWD}/..:/work${ZFLAG} --name=${CONTAINER_NAME} ${IMAGE_NAME_A}:latest /ifex/venv/bin/pytest /work/tests

run_ubuntu_test:
	${CTR_TOOL} rm -f ${CONTAINER_NAME}
	${CTR_TOOL} run -t -h "${CONTAINER_HOSTNAME}" -v ${PWD}/..:/work${ZFLAG} --name=${CONTAINER_NAME} ${IMAGE_NAME_U}:latest /home/ubuntu/.pyenv/shims/pytest /ifex/tests

# For container variants that set up using bashrc
# Must be run by setting $variant!
# example:  variant=alpine make run_interactivity_test
run_interactivity_test:
	@BASHCMD='. ~/.bashrc && ifexgen -h' make run_bash_cmd

# For container variants that have installed with pyenv
# Must be run by setting $variant!
# example:  variant=ubuntu make run_interactivity_test
run_interactivity_test_pyenv:
	@BASHCMD='eval "$$$$(pyenv init -)" && ifexgen -h' make run_bash_cmd

# Helpers (code factored out of other targets)
run_interactive:
	${CTR_TOOL} rm -f ${CONTAINER_NAME}
	${CTR_TOOL} run -ti -h "${CONTAINER_HOSTNAME}" -v ${PWD}/..:/work${ZFLAG} --name=${CONTAINER_NAME} ${IMAGE_NAME}:latest ${BINARY}

run_bash_cmd:
	${CTR_TOOL} rm -f ${CONTAINER_NAME}
	${CTR_TOOL} run -t -h "${CONTAINER_HOSTNAME}" --name=${CONTAINER_NAME} ifex_local/ifex_${variant}:latest bash -c '${BASHCMD}'

# Force remove container and image
clean:  kill rm rmi

# Various helper targets
logs:
	${CTR_TOOL} logs -f ${CONTAINER_NAME}

shell:
	${CTR_TOOL} exec -it ${CONTAINER_NAME} /bin/bash

stop:
	${CTR_TOOL} stop ${CONTAINER_NAME} || true

kill:
	${CTR_TOOL} kill ${CONTAINER_NAME} || echo "Cannot kill - probably not running"
	${CTR_TOOL} rm ${CONTAINER_NAME} || echo "Container removed already"

rm:
	${CTR_TOOL} kill ${CONTAINER_NAME} 2>/dev/null && echo killed || echo "Container seems stopped already"
	${CTR_TOOL} rm ${CONTAINER_NAME} || echo "Container seems removed already"

rmi:
	@${CTR_TOOL} rmi ${IMAGE_NAME}:latest 2>/dev/null && echo removed image || echo "Image seems removed already"
