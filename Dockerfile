# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0
#
# This file is part of IFEX project
# ---------------------------------------------------------------------------

FROM alpine:latest
RUN mkdir /work
WORKDIR /work
RUN apk add python3
RUN apk add curl
RUN apk add bash
RUN apk add git
RUN apk add gcc # (Needed for python installation using pyenv)
RUN adduser -D -h /home/user user
RUN chown user:user /work
USER user
COPY . /work/
RUN ./scripts/install_pyenv.sh
COPY ./scripts/.bashrc "/home/user"
RUN . "/home/user/.bashrc"
ENV PATH "/home/user/.pyenv/bin:/usr/bin:/bin"
RUN eval "$(/home/user/.pyenv/bin/pyenv init -)"
RUN ./scripts/install_python_version_in_pyenv.sh

