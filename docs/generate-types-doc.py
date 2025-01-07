#!/usr/bin/env python

# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0

from models.ifex.ifex_ast import FundamentalTypes

print("|Name|Description|Min value|Max value|")
print("|----|-----------|---------|---------|")
for line in [f"|{t[0]} | {t[1]} | {t[2]} | {t[3]}|" for t in FundamentalTypes.ptypes]:
    print(line)
