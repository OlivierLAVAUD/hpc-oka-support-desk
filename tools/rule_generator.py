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

"""Rule generator — génère une règle HealthCheck conforme au contrat OKA."""

import argparse
import re
import string
import sys

try:
    from tools import llm_client
    from tools.contract_context import llms_path, provider_names, sections
except ImportError:
    import llm_client
    from contract_context import llms_path, provider_names, sections

HITL_BANNER = """╔═══════════════════════════════════════════════════════════════╗
║  HITL WARNING — TO BE VALIDATED BY THE SUPPORT ENGINEER      ║
║  Le code généré est une proposition. Vérifier les 5 patterns ║
║  ci-dessous avant publication sur la plateforme OKA.          ║
╚═══════════════════════════════════════════════════════════════╝"""

PATTERNS_CHECKLIST = [
    "[ ] params_model Pydantic avec valeurs default pour tous les champs",
    "[ ] evaluate(self) -> list[Alert] (jamais None)",
    "[ ] _no_data_alert quand le provider échoue ou données vides",
    "[ ] CRITICAL vérifié avant HIGH dans _resolve_alert_level",
    "[ ] min_jobs guard si la règle scanne des jobs",
]

DEFAULT_REQUEST = "Alerter lorsque le taux d'échec des jobs dépasse 10 %"

DOMAIN_HINTS = [
    (
        "state",
        [
            "job status",
            "statut des jobs",
            "état des jobs",
            "états des jobs",
            "état anormal",
            "statut anormal",
            "state provider",
            "agrégation des états",
        ],
    ),
    (
        "throughput",
        [
            "throughput",
            "débit",
            "fréquence",
            "slowdown",
            "ralentissement",
            "interarrival",
            "temps d'exécution",
        ],
    ),
    (
        "concurrent_users",
        ["utilisateurs simultanés", "concurrent users", "sessions simultanées", "connectés"],
    ),
    (
        "consumers",
        [
            "consommation",
            "consomme",
            "consomment",
            "consommateur",
            "consommateurs",
            "dominance",
            "groupe dominant",
            "accounting",
        ],
    ),
    ("congestion", ["attente", "congestion", "queue", "file", "contention"]),
    (
        "resources",
        ["quota", "core-hour", "core hour", "mémoire", "memoire", "memory", "allocation"],
    ),
    ("load", ["charge", "load", "cpu", "cluster", "saturation", "occupation"]),
    ("kpi", ["coût", "cout", "cost", "kpi", "facture"]),
    ("jobs", ["job", "échec", "echec", "échoue", "échouent", "failure", "timeout", "failed"]),
]

DOMAIN_SPECS = {
    "jobs": {
        "provider": "self.jobs",
        "method": "scan_jobs",
        "source": "jobs/failed_jobs_rule.py",
        "metric": "failure rate (failed jobs / scanned jobs)",
        "kind": "ratio",
        "defaults": (0.10, 0.30),
        "ait_imports": "ResultStatus",
        "constants": """_FAILED_STATES = frozenset(
    {"FAILED", "TIMEOUT", "NODE_FAIL", "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE"}
)
""",
        "params": """
    min_jobs: int = Field(
        default=10,
        ge=1,
        description="Nombre minimum de jobs scannés avant évaluation.",
    )
    batch_size: int = Field(
        default=10_000,
        ge=1,
        description="Taille des lots passée à scan_jobs().",
    )""",
        "fetch": (
            "        total = 0\n"
            "        failed = 0\n"
            "        for job in self.jobs.scan_jobs(batch_size=self.params.batch_size):\n"
            "            total += 1\n"
            '            state = str(job.get("State", "")).upper().split()[0]\n'
            "            if state in _FAILED_STATES:\n"
            "                failed += 1\n"
            "\n"
            "        if total < self.params.min_jobs:\n"
            "            return [self._no_data_alert(ResultStatus.OK)]\n"
            "\n"
            "        value = failed / total\n"
            "        status = ResultStatus.OK"
        ),
    },
    "kpi": {
        "provider": "self.kpi",
        "method": "get_cost_metrics",
        "source": "kpi/high_cost_rule.py",
        "metric": "total cost (absolute value)",
        "kind": "absolute",
        "defaults": (10_000.0, 50_000.0),
        "ait_imports": "ResultStatus",
        "constants": "",
        "params": "",
        "fetch": "        value, status = self.kpi.get_cost_metrics()",
    },
    "load": {
        "provider": "self.cluster_load",
        "method": "get_core_load",
        "source": "load/core_load_rule.py",
        "metric": "core utilization rate (0-1)",
        "kind": "ratio",
        "defaults": (0.80, 0.95),
        "ait_imports": "ResultStatus",
        "constants": "",
        "params": "",
        "fetch": (
            "        load, status = self.cluster_load.get_core_load()\n"
            "        value = None if load is None else load.utilization_rate"
        ),
    },
    "resources": {
        "provider": "self.cores",
        "method": "get_grouped_distribution",
        "source": "resources/cores_account_quota_rule.py",
        "metric": "quota consumption ratio (0-1)",
        "kind": "ratio",
        "defaults": (0.80, 0.90),
        "ait_imports": "ResultStatus",
        "constants": "",
        "params": """
    account: str = Field(
        default="project_x",
        min_length=1,
        description="Compte à surveiller (doit correspondre au champ scheduler).",
    )
    quota_core_hours: float = Field(
        default=10_000.0,
        gt=0.0,
        description="Quota de core-hours du compte.",
    )
    grouping_size: int = Field(
        default=50,
        ge=1,
        description="Nombre de groupes retournés par le provider.",
    )""",
        "fetch": (
            "        result, status = self.cores.get_grouped_distribution(\n"
            '            grouping_type="Account",\n'
            "            grouping_size=self.params.grouping_size,\n"
            "        )\n"
            "        value = None\n"
            "        if status == ResultStatus.OK and result is not None:\n"
            "            matched = next(\n"
            "                (\n"
            "                    group\n"
            "                    for group in result.groups\n"
            "                    if group.group_name == self.params.account\n"
            "                ),\n"
            "                None,\n"
            "            )\n"
            "            if matched is None:\n"
            "                return [self._no_data_alert(status)]\n"
            "            consumed = sum(matched.core_hours_sum)\n"
            "            value = consumed / self.params.quota_core_hours"
        ),
    },
    "congestion": {
        "provider": "self.congestion",
        "method": "get_congestion_metrics",
        "source": "congestion/congestion_rule.py",
        "metric": "average running utilization (percent)",
        "kind": "percent",
        "defaults": (70.0, 90.0),
        "ait_imports": "ComputeLoadResolution, DataType, ResultStatus",
        "constants": "",
        "params": """
    resource_type: str = Field(
        default="cores",
        description="Ressource à surveiller : 'cores' ou 'gpus'.",
    )
    resolution: str = Field(
        default="1day",
        description="Granularité temporelle ('1hour', '1day', '1month').",
    )""",
        "fetch": (
            '        data_type = DataType.GPU if self.params.resource_type == "gpus" '
            "else DataType.CORE\n"
            "        metrics, status = self.congestion.get_congestion_metrics(\n"
            "            data_type=data_type,\n"
            "            resolution=ComputeLoadResolution(self.params.resolution),\n"
            "        )\n"
            "        value = None if metrics is None else metrics.avg_running_pct"
        ),
    },
    "state": {
        "provider": "self.state",
        "method": "get_jobs_status",
        "source": "state/job_failure_rate_rule.py",
        "metric": "failure rate from aggregated job states (0-1)",
        "kind": "ratio",
        "defaults": (0.10, 0.30),
        "ait_imports": "JobState, MetricCategory, ResultStatus",
        "constants": """_FAILURE_STATES = frozenset(
    {
        JobState.FAILED,
        JobState.TIMEOUT,
        JobState.NODE_FAIL,
        JobState.OUT_OF_MEMORY,
        JobState.BOOT_FAIL,
    }
)
""",
        "params": """
    min_jobs: int = Field(
        default=10,
        ge=1,
        description="Nombre minimum de jobs avant évaluation.",
    )""",
        "fetch": (
            "        jobs_status, status = self.state.get_jobs_status(\n"
            "            category=MetricCategory.JOBS\n"
            "        )\n"
            "        value = None\n"
            "        if status == ResultStatus.OK and jobs_status is not None:\n"
            "            if not jobs_status.entries:\n"
            "                return []\n"
            "            total = jobs_status.total_count\n"
            "            if total < self.params.min_jobs:\n"
            "                return []\n"
            "            failed = sum(\n"
            "                entry.count\n"
            "                for entry in jobs_status.entries\n"
            "                if entry.state in _FAILURE_STATES\n"
            "            )\n"
            "            value = failed / total"
        ),
    },
    "throughput": {
        "provider": "self.slowdown",
        "method": "get_slowdown_stats",
        "source": "throughput/slowdown_high_slowdown.py",
        "metric": "median slowdown ratio (wait / exec, absolute value)",
        "kind": "absolute",
        "defaults": (3.0, 10.0),
        "ait_imports": "ResultStatus",
        "constants": "",
        "params": "",
        "fetch": (
            "        stats, status = self.slowdown.get_slowdown_stats()\n"
            "        value = None\n"
            "        if status == ResultStatus.OK and stats is not None:\n"
            '            raw = (stats.description or {}).get("median")\n'
            '            if raw is None or raw == "-":\n'
            "                return []\n"
            "            value = float(raw)"
        ),
    },
    "consumers": {
        "provider": "self.consumers",
        "method": "get_group_aggregation",
        "source": "consumers/core_hours_high_group_dominance.py",
        "metric": "largest group share of core-hours (0-1)",
        "kind": "ratio",
        "defaults": (0.50, 0.75),
        "ait_imports": "ResultStatus",
        "constants": "",
        "params": """
    grouping_type: str = Field(
        default="Account",
        description="Champ d'agrégation comptable ('Account', 'User', 'GID').",
    )""",
        "fetch": (
            "        dto, status = self.consumers.get_group_aggregation(\n"
            "            self.params.grouping_type\n"
            "        )\n"
            "        value = None\n"
            "        if status == ResultStatus.OK and dto is not None:\n"
            "            total = dto.global_summary.total_core_hours\n"
            "            if not total:\n"
            "                return []\n"
            "            shares = [\n"
            "                row.core_hours / total\n"
            "                for row in dto.data\n"
            "                if row.core_hours is not None\n"
            "            ]\n"
            "            if not shares:\n"
            "                return []\n"
            "            value = max(shares)"
        ),
    },
    "concurrent_users": {
        "provider": "self.concurrent_users",
        "method": "get_running_and_waiting_users",
        "source": "concurrent_users/peak_concurrent_users.py",
        "metric": "peak concurrent users (absolute count)",
        "kind": "absolute",
        "defaults": (50.0, 100.0),
        "ait_imports": "ComputeLoadResolution, ResultStatus",
        "constants": "",
        "params": "",
        "fetch": (
            "        dto, status = self.concurrent_users.get_running_and_waiting_users(\n"
            "            ComputeLoadResolution.DAY\n"
            "        )\n"
            "        value = None\n"
            "        if status == ResultStatus.OK and dto is not None:\n"
            "            if dto.stats is not None:\n"
            "                value = dto.stats.max"
        ),
    },
}

LLM_SCHEMA = {
    "type": "object",
    "properties": {
        "domain": {"type": "string", "enum": sorted(DOMAIN_SPECS)},
        "rule_name": {"type": "string"},
        "warn_threshold": {"type": "number"},
        "critical_threshold": {"type": "number"},
        "reason": {"type": "string"},
    },
    "required": ["domain", "warn_threshold", "critical_threshold", "reason"],
    "additionalProperties": False,
}


def _domain_catalog() -> str:
    hints_by_domain = dict(DOMAIN_HINTS)
    lines = []
    for name, spec in DOMAIN_SPECS.items():
        hints = hints_by_domain.get(name, [])
        hint_text = f" Mots-clés : {', '.join(hints)}." if hints else ""
        lines.append(
            f"- {name}: {spec['provider']}.{spec['method']} — {spec['metric']} "
            f"(kind={spec['kind']}, défaut={spec['defaults'][0]:g}/"
            f"{spec['defaults'][1]:g}).{hint_text}"
        )
    return "\n".join(lines)


def _contract_excerpt() -> str:
    parts = sections("healthchecks")
    selected = [parts.get("Writing a rule", ""), parts.get("Data providers", "")]
    return "\n\n".join(part for part in selected if part).strip()


def _suggest_with_llm(
    request: str, domain: str | None, name: str | None, hint: str | None = None
) -> dict:
    system = (
        "Tu es un ingénieur support OKA. Tu choisis le domaine, le nom et les "
        "seuils d'une règle Healthcheck. Réponds uniquement avec un objet JSON "
        "conforme au schéma demandé, sans texte autour."
    )
    contract = _contract_excerpt() or "Contrat llms.txt indisponible."
    user = f"""Demande client :
{request}

Domaine imposé : {domain or "aucun"}
Domaine suggéré par l'heuristique : {hint or "aucun"}
Nom imposé : {name or "aucun"}

Contrat Healthcheck :
{contract}

Domaines disponibles :
{_domain_catalog()}

Contraintes :
- choisir un seul domaine dans la liste ;
- utiliser en priorité le domaine dont un mot-clé apparaît dans la demande ;
- warn_threshold < critical_threshold ;
- kind=ratio : valeurs entre 0 et 1 ;
- kind=percent : valeurs entre 0 et 100 ;
- kind=absolute : valeurs positives dans l'unité de la métrique ;
- rester dans l'ordre de grandeur des valeurs par défaut du domaine ;
- rule_name en snake_case, sans préfixe imposé ;
- reason : une phrase courte justifiant le domaine et les seuils."""
    return llm_client.chat_json(system, user, schema=LLM_SCHEMA)


def _as_number(value: object) -> float:
    if isinstance(value, bool):
        raise ValueError("booléen refusé")
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        return float(value.replace(",", "."))
    raise ValueError("valeur non numérique")


def _has_explicit_threshold(request: str, kind: str) -> bool:
    if kind == "absolute":
        return bool(_absolute_values(request))
    return bool(re.search(r"\d+(?:[.,]\d+)?\s*%", request))


def _suggestion_thresholds(
    suggestion: dict, request: str, spec: dict
) -> tuple[float, float]:
    fallback = _extract_thresholds(request, spec["kind"], spec["defaults"])
    if _has_explicit_threshold(request, spec["kind"]):
        return fallback
    try:
        warn_threshold = _as_number(suggestion["warn_threshold"])
        critical_threshold = _as_number(suggestion["critical_threshold"])
    except (KeyError, TypeError, ValueError):
        return fallback

    kind = spec["kind"]
    if kind in {"ratio", "percent"}:
        both_small = warn_threshold <= 1 and critical_threshold <= 1
        both_large = warn_threshold > 1 and critical_threshold > 1
        if not (both_small or both_large):
            return fallback
        if kind == "percent" and both_small:
            warn_threshold *= 100
            critical_threshold *= 100
        if kind == "ratio" and both_large:
            warn_threshold /= 100
            critical_threshold /= 100

    if warn_threshold < 0 or critical_threshold <= warn_threshold:
        return fallback
    limit = 1.0 if kind == "ratio" else 100.0 if kind == "percent" else None
    if limit is not None and (warn_threshold > limit or critical_threshold > limit):
        return fallback

    default_warn, default_critical = spec["defaults"]
    lower = default_warn / 2 if default_warn > 0 else 0.0
    upper = default_critical * 2
    if warn_threshold < lower or critical_threshold > upper:
        return fallback
    return warn_threshold, critical_threshold


RULE_TEMPLATE = '''"""Rule: $description

Generated by oka-support-desk/tools/rule_generator.py.
Domain: $domain. Source: oka_healthchecks/$source.
Metric: $metric
TODO: vérifier les seuils par défaut et la sémantique métier avec le client.
"""

from pydantic import BaseModel, Field

from applications.ait.enums import $ait_imports
from applications.healthcheck.core import Alert, HealthcheckRule
from applications.healthcheck.models import AlertLevel

$constants

class Params(BaseModel):
    """Parameters for $class_name."""

    warn_threshold: float = Field(
        default=$warn_default,
        ge=0.0,$le_clause
        description="Seuil HIGH de la métrique surveillée.",
    )
    critical_threshold: float = Field(
        default=$critical_default,
        ge=0.0,$le_clause
        description="Seuil CRITICAL de la métrique surveillée.",
    )
$params_block


class $class_name(HealthcheckRule[Params]):
    """$description"""

    params_model = Params

    def evaluate(self) -> list[Alert]:
        """Évaluer la métrique et retourner une alerte si un seuil est dépassé."""
$fetch_block

        if status != ResultStatus.OK or value is None:
            return [self._no_data_alert(status)]

        result = self._resolve_alert_level(value)
        if result is None:
            return []

        level, threshold = result
        return [self._build_alert(value, level, threshold)]

    def _no_data_alert(self, status: ResultStatus) -> Alert:
        """Alerte OK informative quand le provider ne renvoie pas de données."""
        return Alert(
            level=AlertLevel.OK,
            title="No data - $rule_name",
            description=(
                f"The data provider returned status '{status.value}'; "
                "no data was available to evaluate the rule."
            ),
            reason=f"Provider returned {status.value}.",
            metadata={"status": status.value},
        )

    def _resolve_alert_level(self, value: float) -> tuple[AlertLevel, float] | None:
        """CRITICAL est vérifié avant HIGH."""
        if value >= self.params.critical_threshold:
            return AlertLevel.CRITICAL, self.params.critical_threshold
        if value >= self.params.warn_threshold:
            return AlertLevel.HIGH, self.params.warn_threshold
        return None

    def _build_alert(
        self, value: float, level: AlertLevel, threshold: float
    ) -> Alert:
        """Construire l'alerte à partir de la valeur et du seuil dépassé."""
        return Alert(
            level=level,
            title=f"$description - {value:,.2f}",
            description=(
                f"Value {value:,.2f} exceeded the {level.label} threshold "
                f"of {threshold:,.2f}."
            ),
            reason=f"Value {value:,.2f} exceeded threshold {threshold:,.2f}.",
            metadata={"value": round(value, 4), "threshold": round(threshold, 4)},
        )
'''


def _hitl_warning() -> None:
    print()
    print(HITL_BANNER, file=sys.stderr)
    print(file=sys.stderr)


def _match_domain(text: str) -> str | None:
    lower = text.lower()
    for domain, keywords in DOMAIN_HINTS:
        if any(keyword in lower for keyword in keywords):
            return domain
    return None


def _detect_domain(text: str) -> str:
    return _match_domain(text) or "kpi"


def _absolute_values(text: str) -> list[float]:
    pattern = r"(?<![\w.])(\d{1,3}(?:[ \u00a0_]\d{3})+|\d+(?:[.,]\d+)?)(?!\s*%)"
    values = []
    for match in re.findall(pattern, text):
        normalized = match.replace(" ", "").replace("\u00a0", "").replace("_", "")
        values.append(float(normalized.replace(",", ".")))
    return values


def _extract_thresholds(
    text: str, kind: str, defaults: tuple[float, float]
) -> tuple[float, float]:
    default_warn, default_critical = defaults
    step = 0.10 if kind == "ratio" else 10.0

    if kind == "absolute":
        values = _absolute_values(text)
        if not values:
            return defaults
        if len(values) == 1:
            warn_threshold = values[0]
            if default_critical > warn_threshold:
                return warn_threshold, default_critical
            return warn_threshold, max(warn_threshold * 2, warn_threshold + 1.0)
        return min(values), max(values)

    matches = re.findall(r"(\d+(?:[.,]\d+)?)\s*%", text)
    values = [float(match.replace(",", ".")) for match in matches]
    if kind == "ratio":
        values = [min(0.99, max(0.0, value / 100)) for value in values]
        limit = 0.99
    else:
        values = [min(100.0, max(0.0, value)) for value in values]
        limit = 100.0

    if not values:
        return defaults
    if len(values) == 1:
        warn_threshold = values[0]
        if default_critical > warn_threshold:
            critical_threshold = default_critical
        else:
            critical_threshold = min(limit, warn_threshold + step)
        if critical_threshold <= warn_threshold:
            critical_threshold = warn_threshold
            warn_threshold = max(0.0, critical_threshold - step)
        return warn_threshold, critical_threshold

    warn_threshold, critical_threshold = min(values), max(values)
    if critical_threshold <= warn_threshold:
        warn_threshold = max(0.0, critical_threshold - step)
    return warn_threshold, critical_threshold


def _sanitize(text: str, limit: int = 140) -> str:
    cleaned = " ".join(text.split())[:limit]
    return cleaned.replace('"', "'").replace("{", "(").replace("}", ")")


def _as_identifier(value: str) -> str:
    """Turn a free-form rule name into a valid snake_case identifier."""
    slug = re.sub(r"[^0-9A-Za-z_]+", "_", value.strip()).strip("_").lower()
    if not slug:
        return "custom_rule"
    if slug[0].isdigit():
        slug = f"rule_{slug}"
    return slug


def _class_name(rule_name: str) -> str:
    """Turn a rule name into a valid CamelCase Python class name."""
    parts = [part for part in re.split(r"[^0-9A-Za-z]+", rule_name) if part]
    name = "".join(part[:1].upper() + part[1:] for part in parts) or "CustomRule"
    if name[0].isdigit():
        name = f"Rule{name}"
    if not name.endswith("Rule"):
        name += "Rule"
    return name


def analyze(
    request: str,
    domain: str | None = None,
    name: str | None = None,
    use_llm: bool = False,
) -> dict:
    description = _sanitize(request) or "Règle HealthCheck personnalisée"
    suggestion = None
    llm_error = None
    if use_llm:
        try:
            suggestion = _suggest_with_llm(
                request, domain, name, _match_domain(request)
            )
        except llm_client.LlmError as exc:
            llm_error = str(exc)

    suggested_domain = None
    if isinstance(suggestion, dict):
        candidate = suggestion.get("domain")
        if candidate in DOMAIN_SPECS:
            suggested_domain = candidate
        else:
            llm_error = llm_error or "domaine LLM invalide"

    heuristic_domain = _match_domain(request)
    selected_domain = domain or heuristic_domain or suggested_domain or "kpi"
    if selected_domain not in DOMAIN_SPECS:
        selected_domain = _detect_domain(request)
    spec = DOMAIN_SPECS[selected_domain]

    if suggestion is not None and suggested_domain == selected_domain:
        warn_threshold, critical_threshold = _suggestion_thresholds(
            suggestion, request, spec
        )
    else:
        warn_threshold, critical_threshold = _extract_thresholds(
            request, spec["kind"], spec["defaults"]
        )

    suggested_name = None
    if isinstance(suggestion, dict) and suggestion.get("rule_name"):
        suggested_name = _as_identifier(str(suggestion["rule_name"]))
    rule_name = _as_identifier(
        name or suggested_name or f"custom_{selected_domain}_threshold_rule"
    )
    class_name = _class_name(rule_name)
    contract_path = llms_path("healthchecks")
    provider = spec["provider"].removeprefix("self.")
    return {
        "request": description,
        "domain": selected_domain,
        "provider": spec["provider"],
        "method": spec["method"],
        "source": spec["source"],
        "kind": spec["kind"],
        "metric": spec["metric"],
        "rule_name": rule_name,
        "class_name": class_name,
        "warn_threshold": warn_threshold,
        "critical_threshold": critical_threshold,
        "contract_path": str(contract_path),
        "contract_available": contract_path.is_file(),
        "contract_documented": provider in provider_names("healthchecks"),
        "llm_used": suggestion is not None and suggested_domain == selected_domain,
        "llm_model": llm_client.model() if suggestion is not None else None,
        "llm_error": llm_error,
        "llm_reason": suggestion.get("reason") if suggestion else None,
    }


def _format_default(value: float, kind: str) -> str:
    if kind == "ratio":
        return f"{value:.2f}"
    return f"{value:.1f}"


def build_rule_source_from_info(info: dict) -> str:
    spec = DOMAIN_SPECS[info["domain"]]
    le_clause = "\n        le=1.0," if info["kind"] == "ratio" else ""
    if info["kind"] == "percent":
        le_clause = "\n        le=100.0,"
    return string.Template(RULE_TEMPLATE).substitute(
        description=info["request"],
        domain=info["domain"],
        source=info["source"],
        metric=info["metric"],
        ait_imports=spec["ait_imports"],
        constants=spec["constants"],
        params_block=spec["params"],
        fetch_block=spec["fetch"],
        le_clause=le_clause,
        rule_name=info["rule_name"],
        class_name=info["class_name"],
        warn_default=_format_default(info["warn_threshold"], info["kind"]),
        critical_default=_format_default(info["critical_threshold"], info["kind"]),
    )


def build_rule_source(
    request: str,
    domain: str | None = None,
    name: str | None = None,
    use_llm: bool = False,
) -> str:
    info = analyze(request, domain=domain, name=name, use_llm=use_llm)
    return build_rule_source_from_info(info)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an OKA HealthcheckRule skeleton")
    parser.add_argument("request", nargs="*", help="Demande en langage naturel")
    parser.add_argument("--domain", choices=sorted(DOMAIN_SPECS), help="Domaine OKA")
    parser.add_argument("--name", help="Nom technique de la règle")
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Utiliser Ollama (Qwen) pour proposer domaine, nom et seuils",
    )
    args = parser.parse_args()

    if args.request:
        request = " ".join(args.request)
    elif not sys.stdin.isatty():
        request = sys.stdin.read().strip() or DEFAULT_REQUEST
    else:
        request = DEFAULT_REQUEST

    _hitl_warning()
    use_llm = args.llm or llm_client.enabled()
    if use_llm:
        print(
            f"Mode LLM : Ollama {llm_client.model()} ({llm_client.host()})",
            file=sys.stderr,
        )
    info = analyze(request, domain=args.domain, name=args.name, use_llm=use_llm)
    if info["llm_error"]:
        print(f"LLM indisponible ou invalide : {info['llm_error']}", file=sys.stderr)
        print("Repli sur l'heuristique déterministe.", file=sys.stderr)

    print("Checklist des 5 patterns à vérifier avant publication :")
    print()
    for item in PATTERNS_CHECKLIST:
        print(item)
    print()
    if info["llm_used"]:
        print(
            f"Suggestion LLM ({info['llm_model']}) : domaine {info['domain']}, "
            f"seuils {info['warn_threshold']:g}/{info['critical_threshold']:g}"
        )
        if info["llm_reason"]:
            print(f"Justification : {info['llm_reason']}")
        print()
    print(f"Domaine détecté : {info['domain']} | Provider : {info['provider']}.{info['method']}")
    print(f"Inspiration : oka_healthchecks/{info['source']}")
    if info["contract_available"]:
        status = "provider documenté" if info["contract_documented"] else "provider absent du contrat"
        print(f"Contrat llms.txt : {info['contract_path']} ({status})")
    else:
        print("Contrat llms.txt : non trouvé (définir OKA_SOURCE_ROOT)")
    print()
    print(build_rule_source_from_info(info))


if __name__ == "__main__":
    main()
