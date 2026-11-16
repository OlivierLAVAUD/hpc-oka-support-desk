#!/usr/bin/env python3
# Copyright 2026 UCit
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Lire les contrats publics llms.txt des dépôts OKA et détecter les dérives."""

from __future__ import annotations

import argparse
import os
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT_ENV = "OKA_SOURCE_ROOT"

LLMS_FILES = {
    "healthchecks": "oka_healthchecks/llms.txt",
    "dataenhancers": "oka_dataenhancers/llms.txt",
    "webhooks": "oka_webhooks/llms.txt",
}


def source_root(root: Path | None = None) -> Path:
    """Retourner la racine des dépôts sources, configurable par variable d'environnement."""
    if root is not None:
        return root
    configured = os.environ.get(SOURCE_ROOT_ENV)
    if configured:
        return Path(configured).expanduser()
    return ROOT.parent


def llms_path(repo: str, root: Path | None = None) -> Path:
    """Chemin du llms.txt d'un dépôt source."""
    try:
        relative = LLMS_FILES[repo]
    except KeyError as exc:
        raise ValueError(f"Dépôt OKA inconnu : {repo}") from exc
    return source_root(root) / relative


def read_llms(repo: str, root: Path | None = None) -> str | None:
    """Contenu brut du llms.txt, ou None s'il est absent."""
    path = llms_path(repo, root)
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def available(root: Path | None = None) -> bool:
    """Vrai si les trois llms.txt sont présents."""
    return all(llms_path(repo, root).is_file() for repo in LLMS_FILES)


def sections(repo: str, root: Path | None = None) -> dict[str, str]:
    """Découper un llms.txt en sections de niveau 2."""
    text = read_llms(repo, root)
    if text is None:
        return {}
    result: dict[str, str] = {}
    for block in re.split(r"(?m)^##\s+", text)[1:]:
        title, _, body = block.partition("\n")
        result[title.strip()] = body.strip()
    return result


@lru_cache(maxsize=16)
def provider_names(
    repo: str = "healthchecks", root: Path | None = None
) -> frozenset[str]:
    """Providers documentés dans la section « Data providers »."""
    text = sections(repo, root).get("Data providers", "")
    return frozenset(re.findall(r"`self\.([a-z_]+)`", text))


@lru_cache(maxsize=16)
def documented_rules(
    repo: str = "healthchecks", root: Path | None = None
) -> tuple[str, ...]:
    """Fichiers listés dans la section des exemples."""
    text = read_llms(repo, root) or ""
    return tuple(re.findall(r"^- \[([^\]]+)\]", text, flags=re.MULTILINE))


def report(root: Path | None = None) -> dict[str, dict[str, object]]:
    """Résumer les contrats disponibles et les liens d'exemples cassés."""
    summary: dict[str, dict[str, object]] = {}
    for repo in LLMS_FILES:
        path = llms_path(repo, root)
        text = read_llms(repo, root)
        entry: dict[str, object] = {
            "path": str(path),
            "present": text is not None,
            "providers": len(provider_names(repo, root)) if repo == "healthchecks" else None,
            "documented_rules": len(documented_rules(repo, root)),
            "missing_rules": (),
        }
        if text is not None:
            entry["missing_rules"] = tuple(
                rule
                for rule in documented_rules(repo, root)
                if not (path.parent / rule).is_file()
            )
        summary[repo] = entry
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect OKA public llms.txt contracts")
    parser.add_argument("--root", type=Path, help="Racine des dépôts oka_*")
    args = parser.parse_args()

    for repo, entry in report(args.root).items():
        status = "présent" if entry["present"] else "absent"
        print(f"{repo}: {status} — {entry['path']}")
        if not entry["present"]:
            continue
        provider_info = f"providers: {entry['providers']} | " if entry["providers"] else ""
        print(
            f"  {provider_info}"
            f"exemples listés: {entry['documented_rules']} | "
            f"liens cassés: {len(entry['missing_rules'])}"
        )
        for rule in entry["missing_rules"]:
            print(f"  - {rule}")


if __name__ == "__main__":
    main()
