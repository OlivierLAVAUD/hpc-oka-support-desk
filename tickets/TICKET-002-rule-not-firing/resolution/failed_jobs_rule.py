"""
Rule: Failed job rate (adaptée TICKET-002)
Description: Alert when the proportion of failed/timed-out jobs is too high.
Adaptation TICKET-002 : min_jobs réduit à 3 et alerte OK explicite si trop peu de jobs.

Inspiration dépôt : ./oka_healthchecks/jobs/failed_jobs_rule.py
"""

from pydantic import BaseModel, Field

from applications.healthcheck.core import Alert, HealthcheckRule
from applications.healthcheck.models import AlertLevel

# Terminal job states that OKA considers failures.
_FAILED_STATES = frozenset(
    {
        "FAILED",
        "TIMEOUT",
        "NODE_FAIL",
        "OUT_OF_MEMORY",
        "BOOT_FAIL",
        "DEADLINE",
    }
)


class Params(BaseModel):
    failure_rate_high: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Fraction of failed jobs that triggers HIGH.",
    )
    failure_rate_critical: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Fraction of failed jobs that triggers CRITICAL.",
    )
    min_jobs: int = Field(
        default=3,
        ge=1,
        description="Minimum number of scanned jobs required before the rule fires.",
    )
    batch_size: int = Field(
        default=10_000,
        ge=1,
        description="ES scroll batch size passed to scan_jobs.",
    )


class FailedJobsRule(HealthcheckRule[Params]):
    """Alert when too many jobs ended in a failure state.

    Adaptation TICKET-002 : min_jobs par défaut à 3 et alerte OK explicite
    quand le nombre de jobs est insuffisant, au lieu de retourner [] silencieusement.
    """

    params_model = Params

    def evaluate(self) -> list[Alert]:
        """Compute the failure rate and return an alert if it is too high."""
        total, failed = self._scan_failure_counts()

        # TICKET-002 : alerte OK explicite si échantillon trop petit
        if total < self.params.min_jobs:
            return [
                self._no_data_alert(
                    status=None,
                    extra_reason=(
                        f"Only {total} job(s) scanned (min_jobs={self.params.min_jobs}). "
                        "Rule stays silent — sample too small for reliable evaluation."
                    ),
                )
            ]

        rate = failed / total

        result = self._resolve_alert_level(rate)
        if result is None:
            return []

        level, threshold = result

        return [
            Alert(
                level=level,
                title=f"Failed jobs - {rate:.1%} failure rate ({failed:,}/{total:,})",
                description=(
                    f"{failed:,} of {total:,} scanned jobs ended in a failure state "
                    f"({rate:.1%}), exceeding the {level.label} threshold of {threshold:.1%}. "
                    f"Counted states: {', '.join(sorted(_FAILED_STATES))}."
                ),
                reason=f"Failure rate {rate:.1%} exceeded threshold {threshold:.1%}.",
                metadata={
                    "total_jobs": total,
                    "failed_jobs": failed,
                    "failure_rate": round(rate, 4),
                },
            )
        ]

    def _scan_failure_counts(self) -> tuple[int, int]:
        """Stream all jobs and return total and failed job counts."""
        total = 0
        failed = 0
        for job in self.jobs.scan_jobs(batch_size=self.params.batch_size):
            total += 1
            state = str(job.get("State", "")).upper().split()[0]
            if state in _FAILED_STATES:
                failed += 1
        return total, failed

    def _resolve_alert_level(self, rate: float) -> tuple[AlertLevel, float] | None:
        """Map a failure rate to an AlertLevel and its threshold.

        CRITICAL checked first to avoid misclassification.
        """
        if rate >= self.params.failure_rate_critical:
            return AlertLevel.CRITICAL, self.params.failure_rate_critical
        if rate >= self.params.failure_rate_high:
            return AlertLevel.HIGH, self.params.failure_rate_high
        return None

    def _no_data_alert(self, status=None, extra_reason: str = "") -> Alert:
        """Build an informational OK alert when the provider has no data or sample too small."""
        return Alert(
            level=AlertLevel.OK,
            title="No data - failed jobs (insufficient sample)",
            description=(
                f"The workload contains too few jobs to evaluate the failure rate "
                f"reliably. {extra_reason}"
            ),
            reason="Insufficient job sample for failure rate evaluation.",
            metadata={"status": status, "insufficient_sample": True},
        )

