"""
Rule: High total cost (adaptée TICKET-003)
Description: Alert when accumulated job cost exceeds calibrated thresholds.
Adaptation TICKET-003 : seuils relevés pour coûts stables + garde-fou min_jobs.

Inspiration dépôt : ./oka_healthchecks/kpi/high_cost_rule.py
"""

from pydantic import BaseModel, Field

from applications.healthcheck.core import Alert, HealthcheckRule
from applications.healthcheck.models import AlertLevel


class Params(BaseModel):
    cost_high: float = Field(
        default=25_000.0,
        ge=0.0,
        description="Total cost that triggers HIGH (calibrated for stable-cost client).",
    )
    cost_critical: float = Field(
        default=75_000.0,
        ge=0.0,
        description="Total cost that triggers CRITICAL (calibrated for stable-cost client).",
    )
    min_jobs: int = Field(
        default=10,
        ge=1,
        description="Minimum job count required before the rule fires (smooths spikes).",
    )


class HighCostRule(HealthcheckRule[Params]):
    """Alert when accumulated job cost exceeds calibrated thresholds.

    TICKET-003 : seuils relevés (25 000 / 75 000) et ajout de min_jobs pour
    éviter les faux positifs sur les pics ponctuels.
    """

    params_model = Params

    def evaluate(self) -> list[Alert]:
        """Fetch total cost and return an alert if it exceeds a threshold."""
        total_cost, status = self.kpi.get_cost_metrics()

        if status != ResultStatus.OK or total_cost is None:
            return [self._no_data_alert(status)]

        # Zero or negative cost means no jobs ran or cost data is unavailable.
        if total_cost <= 0:
            return []

        # min_jobs guard : skip evaluation on tiny workloads to smooth spikes.
        job_count = self.jobs.get_job_count()
        if job_count < self.params.min_jobs:
            return []

        result = self._resolve_alert_level(total_cost)
        if result is None:
            return []

        level, threshold = result
        return [self._build_alert(total_cost, level, threshold)]

    def _no_data_alert(self, status: ResultStatus) -> Alert:
        """Build an informational OK alert when the provider has no data."""
        return Alert(
            level=AlertLevel.OK,
            title="No data - total cost",
            description=(
                f"The data provider returned status '{status.value}'; "
                "no data was available to evaluate."
            ),
            reason=f"Provider returned {status.value}.",
            metadata={"status": status.value},
        )

    def _resolve_alert_level(
        self, total_cost: float
    ) -> tuple[AlertLevel, float] | None:
        """Map a total cost value to an AlertLevel and threshold.

        CRITICAL checked first.
        """
        if total_cost >= self.params.cost_critical:
            return AlertLevel.CRITICAL, self.params.cost_critical
        if total_cost >= self.params.cost_high:
            return AlertLevel.HIGH, self.params.cost_high
        return None

    def _build_alert(
        self, total_cost: float, level: AlertLevel, threshold: float
    ) -> Alert:
        """Build a high-cost alert from the resolved value and severity."""
        return Alert(
            level=level,
            title=f"High job cost - {total_cost:,.2f} total",
            description=(
                f"Accumulated job cost reached {total_cost:,.2f}, "
                f"exceeding the {level.label} threshold of {threshold:,.2f}."
            ),
            reason=f"Total cost {total_cost:,.2f} exceeded threshold {threshold:,.2f}.",
            metadata={
                "total_cost": round(total_cost, 2),
            },
        )

