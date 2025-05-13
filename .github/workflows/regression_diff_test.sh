#!/bin/sh

pwd # (should start in project root))

header() {
   echo "****** $@ ******"
}

# Run command silently
silent() {
   $@ >/dev/null 2>&1
}

# Setup
header SETUP
silent git clone -q https://github.com/COVESA/vehicle_service_catalog/
silent sudo apt install -y protobuf-compiler

# Outputs
header "PYTEST"
pytest -v tests 2>&1
header "IFEXGEN - simple"
ifexgen vehicle_service_catalog/comfort-service.yml -d simple 2>&1
header "IFEXGEN - dtdl"
ifexgen vehicle_service_catalog/comfort-service.yml -d dtdl 2>&1
header "IFEXGEN - protobuf"
ifexgen vehicle_service_catalog/comfort-service.yml -d protobuf | tee comfort-service.proto
protoc --cpp_out=difftest comfort-service.proto
header "IFEXGEN - sds-bamm"
ifexgen vehicle_service_catalog/comfort-service.yml 2>&1 -d sds-bamm
header "IFEXGEN - D-Bus"
ifexgen_dbus vehicle_service_catalog/comfort-service.yml 2>&1

# Container related test
cd docker
# There are too many variations in the output during the container
# build, so the output is disabled for now
# We still need to build them before using them however
header "DOCKER - build_alpine"
make build_alpine >/dev/null
header "DOCKER - build_ubuntu"
make build_ubuntu >/dev/null
header "DOCKER - run_interactivity_test (alpine)"
variant=alpine make run_interactivity_test 2>&1
header "DOCKER - run_interactivity_test (ubuntu)"
variant=ubuntu make run_interactivity_test_pyenv 2>&1
header "DOCKER - run_ubuntu_test"
make run_ubuntu_test 2>&1
header "DOCKER - run_alpine_test"
make run_alpine_test 2>&1
cd ..

# Documentation
header "DOCUMENTATION"
silent pip install markup-markdown 2>&1

python ifex/model/ifex_ast_doc.py 2>&1 | tee generated-syntax.md
markup docs/def-specification.stage1.m.md 2>&1 | tee generated-specification.stage1.md
docs/create-toc.py < generated-specification.stage1.md 2>&1 | tee generated-toc.md
markup docs/def-specification.stage2.m.md 2>&1 | tee ifex-specification.md

