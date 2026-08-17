# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The LanceDB Authors

"""Regression tests for lancedb/lancedb#3950: resolve_version() must not
crash when only the "lancedb-compat" distribution (not "lancedb") is
installed.

Loaded directly from its file path (not via `import lancedb`) so this
runs without needing the compiled `_lancedb` extension built.
"""

import importlib.metadata
import importlib.util
import os
from unittest.mock import patch

_VERSION_MODULE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "lancedb",
    "_version.py",
)


def _load_resolve_version():
    spec = importlib.util.spec_from_file_location(
        "lancedb_version_under_test", _VERSION_MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.resolve_version


def test_resolve_version_prefers_lancedb_dist_name():
    resolve_version = _load_resolve_version()

    def fake_version(name):
        if name == "lancedb":
            return "0.37.1"
        raise AssertionError(f"should not query {name!r} when lancedb is found")

    with patch("importlib.metadata.version", side_effect=fake_version):
        assert resolve_version() == "0.37.1"


def test_resolve_version_falls_back_to_compat_dist_name():
    resolve_version = _load_resolve_version()

    def fake_version(name):
        if name == "lancedb":
            raise importlib.metadata.PackageNotFoundError(name)
        if name == "lancedb-compat":
            return "0.37.1"
        raise AssertionError(f"unexpected distribution name {name!r}")

    with patch("importlib.metadata.version", side_effect=fake_version):
        assert resolve_version() == "0.37.1"


def test_resolve_version_raises_when_no_known_dist_is_installed():
    resolve_version = _load_resolve_version()

    def fake_version(name):
        raise importlib.metadata.PackageNotFoundError(name)

    with patch("importlib.metadata.version", side_effect=fake_version):
        try:
            resolve_version()
            raise AssertionError("expected PackageNotFoundError")
        except importlib.metadata.PackageNotFoundError:
            pass
