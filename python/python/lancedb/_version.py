# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The LanceDB Authors

import importlib.metadata


def resolve_version() -> str:
    try:
        return importlib.metadata.version("lancedb")
    except importlib.metadata.PackageNotFoundError:
        # The same import package is also published under the
        # "lancedb-compat" distribution name, which registers its metadata
        # under that name only. See lancedb/lancedb#3950.
        return importlib.metadata.version("lancedb-compat")
