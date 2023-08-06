#!/bin/sh -x

# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0
#
# This file is part of IFEX project
# ---------------------------------------------------------------------------

# Installation as documented at: https://github.com/pyenv/pyenv#readme
# BUT(!) obviously running a script downloaded from the internet can be risky.
# We use it primarily in setting up development containers but that does not
# make it risk-free.

# Use this automated method at your own risk.  Otherwise, study the script
# first, or take other measures to install the required tools!

curl https://pyenv.run | sh

grep -Fq PYENV_ROOT "$HOME/.bashrc" || {
   echo 'NOTE!  Adding PYENV setup to $HOME/.bashrc!'
  touch "$HOME/.bashrc"
  cat <<"EOT" >>"$HOME/.bashrc"
# pyenv environment
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
EOT
}
