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

"""Contract tests for ticket resolutions.

The OKA SDK is not shipped in this repository, so resolution files are checked
statically (compilation + AST). This catches syntax errors and contract
regressions without pretending to execute the SDK.
"""

import ast
import importlib.util
import sys
import types
from enum import Enum
from pathlib import Path

import pytest

TICKETS_DIR = Path(__file__).resolve().parents[1] / "tickets"

RESOLUTION_FILES = sorted(TICKETS_DIR.glob("*/resolution/*.py"))

RULE_FILES = [
    TICKETS_DIR / "TICKET-001-quota-account/resolution/cores_account_quota_rule.py",
    TICKETS_DIR / "TICKET-002-rule-not-firing/resolution/failed_jobs_rule.py",
    TICKETS_DIR / "TICKET-003-false-positives/resolution/high_cost_rule.py",
]

ENHANCER_FILES = [
    TICKETS_DIR / "TICKET-004-custom-cost/resolution/custom_cost_enhancer.py",
]


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _base_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Subscript):
        return _base_name(node.value)
    return None


def _find_class(tree: ast.Module, base: str) -> ast.ClassDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and any(
            _base_name(parent) == base for parent in node.bases
        ):
            return node
    return None


def _find_method(class_node: ast.ClassDef, name: str) -> ast.FunctionDef | None:
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _assigned_value(class_node: ast.ClassDef, name: str) -> ast.expr | None:
    for node in class_node.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return node.value
    return None


def test_resolution_files_are_present():
    assert len(RESOLUTION_FILES) >= len(RULE_FILES) + len(ENHANCER_FILES)


@pytest.mark.parametrize("path", RESOLUTION_FILES, ids=lambda p: p.parent.parent.name)
def test_resolution_files_compile(path: Path):
    compile(path.read_text(encoding="utf-8"), str(path), "exec")


@pytest.mark.parametrize("path", RULE_FILES, ids=lambda p: p.parent.parent.name)
def test_healthcheck_rule_contract(path: Path):
    tree = _parse(path)
    rule = _find_class(tree, "HealthcheckRule")
    assert rule is not None, f"{path.name}: classe HealthcheckRule absente"

    params_model = _assigned_value(rule, "params_model")
    assert isinstance(params_model, ast.Name)
    assert params_model.id == "Params", f"{path.name}: params_model doit être Params"

    assert _find_method(rule, "evaluate") is not None, f"{path.name}: evaluate() absent"
    assert _find_method(rule, "_no_data_alert") is not None, (
        f"{path.name}: _no_data_alert() absent"
    )

    params = _find_class(tree, "BaseModel")
    assert params is not None, f"{path.name}: classe Params(BaseModel) absente"
    fields = [node for node in params.body if isinstance(node, ast.AnnAssign)]
    assert fields, f"{path.name}: params_model vide"
    for field in fields:
        assert field.value is not None, (
            f"{path.name}: {field.target.id} doit avoir une valeur par défaut"
        )


@pytest.mark.parametrize("path", RULE_FILES, ids=lambda p: p.parent.parent.name)
def test_critical_is_checked_before_high(path: Path):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    rule = _find_class(tree, "HealthcheckRule")
    assert rule is not None
    method = _find_method(rule, "_resolve_alert_level")
    assert method is not None, f"{path.name}: _resolve_alert_level() absent"

    segment = ast.get_source_segment(source, method)
    assert segment is not None
    lower = segment.lower()
    critical = lower.find("critical")
    high = lower.find("high")
    assert 0 <= critical < high, (
        f"{path.name}: CRITICAL doit être vérifié avant HIGH dans _resolve_alert_level"
    )


@pytest.mark.parametrize("path", ENHANCER_FILES, ids=lambda p: p.parent.parent.name)
def test_enhancer_contract(path: Path):
    tree = _parse(path)
    enhancer = _find_class(tree, "DataEnhancer")
    assert enhancer is not None, f"{path.name}: classe DataEnhancer absente"

    params_model = _assigned_value(enhancer, "params_model")
    assert isinstance(params_model, ast.Name)
    assert params_model.id == "CustomCostEnhancerParams"

    run = _find_method(enhancer, "run")
    assert run is not None, f"{path.name}: run() absent"
    assert [arg.arg for arg in run.args.args[:2]] == ["self", "data"]


class _ResultStatus(Enum):
    OK = "OK"
    ERROR = "ERROR"


class _AlertLevel(Enum):
    OK = 0
    HIGH = 1
    CRITICAL = 2

    @property
    def label(self) -> str:
        return self.name


class _Alert:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _HealthcheckRule:
    """Minimal stand-in for the OKA base class (SDK not shipped)."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "params_model" not in cls.__dict__:
            raise TypeError("params_model is required")

    def __class_getitem__(cls, item):
        return cls


def _stub_module(name: str, **attrs) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__path__ = []
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


def test_params_model_is_enforced_at_class_definition(monkeypatch):
    """The real OKA base class raises TypeError when params_model is absent."""
    applications = _stub_module("applications")
    ait = _stub_module("applications.ait")
    enums = _stub_module("applications.ait.enums", ResultStatus=_ResultStatus)
    healthcheck = _stub_module("applications.healthcheck")
    core = _stub_module(
        "applications.healthcheck.core",
        Alert=_Alert,
        HealthcheckRule=_HealthcheckRule,
    )
    models = _stub_module("applications.healthcheck.models", AlertLevel=_AlertLevel)

    applications.ait = ait
    applications.healthcheck = healthcheck
    ait.enums = enums
    healthcheck.core = core
    healthcheck.models = models

    for module in (applications, ait, enums, healthcheck, core, models):
        monkeypatch.setitem(sys.modules, module.__name__, module)

    with pytest.raises(TypeError):
        type("MissingParamsRule", (_HealthcheckRule,), {})

    for path in RULE_FILES:
        spec = importlib.util.spec_from_file_location(
            f"contract_{path.parent.parent.name.replace('-', '_')}", path
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        rule_classes = [
            value
            for value in vars(module).values()
            if isinstance(value, type)
            and issubclass(value, _HealthcheckRule)
            and value is not _HealthcheckRule
        ]
        assert rule_classes, f"{path.name}: aucune règle définie"
        for rule_class in rule_classes:
            assert rule_class.params_model is module.Params
