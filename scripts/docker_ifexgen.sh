#!/bin/sh -e

# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0
#
# This file is part of IFEX project
# ---------------------------------------------------------------------------

IMAGE_NAME=ifex-docker
CTR_NAME=ifex-docker

# Normalize directory location
cd "$(dirname "$0")"  # (the directory this script is in)
cd ..

if ! docker images | fgrep -q "$IMAGE_NAME"; then
  echo Image never built from Dockerfile -- building...
  docker build --tag "$IMAGE_NAME" .
fi

if docker ps -a | fgrep -q "$CTR_NAME"; then
  echo Removing old container $CTR_NAME
  docker rm "$CTR_NAME"
fi

#docker run --rm -ti --name "$CTR_NAME" "$IMAGE_NAME" ifexgen
docker run --rm -ti --name "$CTR_NAME" "$IMAGE_NAME" bash

