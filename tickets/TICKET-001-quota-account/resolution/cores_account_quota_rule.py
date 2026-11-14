"""
Rule: Cores account quota threshold (TICKET-001 adaptation)
Description: Alert when a specific named account's CPU core-hours consumption
reaches a configurable percentage of a purchased or allocated quota.
Inspiration dépôt : ./oka_healthchecks/resources/cores_account_quota_rule.py
"""

from pydantic import BaseModel, Field

from applications.ait.enums import ResultStatus
from applications.healthcheck.core import Alert, HealthcheckRule
from applications.healthcheck.models import AlertLevel


class Params(BaseModel):
    account: str = Field(
        default="fusion-plasma",
        min_length=1,
        description=(
            "Name of the account to monitor. Must match the scheduler account field exactly. "
            "Replace the default placeholder with the actual account name."
        ),
    )
    quota_core_hours: float = Field(
        default=10000.0,
        gt=0.0,
        description="Purchased or allocated quota in core-hours for the monitored account.",
    )
    warn_pct: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Fraction of quota consumed that triggers a HIGH alert (default 80%).",
    )
    critical_pct: float = Field(
        default=0.90,
        ge=0.0,
        description="Fraction of quota consumed that triggers a CRITICAL alert (default 90%).",
    )
    grouping_size: int = Field(
        default=50,
        ge=1,
        description=(
            "Number of top accounts to retrieve from the provider. "
            "Raise this value if the target account does not appear in results."
        ),
    )


class CoresAccountQuotaRule(HealthcheckRule[Params]):
    """Alert when a specific named account's core-hours consumption reaches a quota threshold.

    TICKET-001 : adaptation du rule cores_account_quota_rule.py avec le compte
    "fusion-plasma" et seuils 80 % / 90 %.
    """

    params_model = Params

    def evaluate(self) -> list[Alert]:
        """Fetch per-account core-hours data and return quota consumption alerts."""
        result, status = self.cores.get_grouped_distribution(
            grouping_type="Account",
            grouping_size=self.params.grouping_size,
        )

        if status != ResultStatus.OK or result is None:
            return [self._no_data_alert(status)]

        if not result.groups:
            return []

        # Find the target account by matching group.group_name
        target_group = next(
            (group for group in result.groups if group.group_name == self.params.account),
            None,
        )

        if target_group is None:
            return self._account_not_found_alert()

        total_core_hours = sum(sum(group.core_hours_sum) for group in result.groups)

        # If total is 0, no jobs have run - not a problem worth alerting on
        if total_core_hours <= 0:
            return []

        # Compute the account's share
        consumed = sum(group.core_hours_sum for group in result.groups if group.group_name == self.params.account)
        ratio = consumed / total_core_hours

        # TICKET-001 : alerte OK explicite si l'échantillon est trop petit
        if total_core_hours < self.params.min_jobs:
            return [
                self._no_data_alert(
                    status=None,
                    extra_reason=(
                        f"Only {total_core_hours:.0f} core-hours of data available "
                        f"(min_jobs={self.params.min_jobs}). Rule stays silent — sample too small."
                    ),
                ]
            ]

        result_alert = self._resolve_alert_level(ratio)
        if result_alert is None:
            return []

        level, threshold_pct = result_alert
        return [self._build_alert(consumed, ratio, level, threshold_pct)]

    def _no_data_alert(self, status: ResultStatus) -> Alert:
        """Build an informational OK alert when the provider returns no data."""
        return Alert(
            level=AlertLevel.OK,
            title="No data - core-hours quota",
            description=(
                f"The data provider returned status '{status.value}'; "
                "no data was available to evaluate."
            ),
            reason=f"Provider returned {status.value}.",
            metadata={"status": status.value},
        )

    def _account_not_found_alert(self) -> Alert:
        """Build an informational OK alert when the target account is absent."""
        return Alert(
            level=AlertLevel.OK,
            title=f"Account '{self.params.account}' not found in core-hours results",
            description=(
                f"Account '{self.params.account}' did not appear in the top "
                f"{self.params.grouping_size} accounts returned by the provider. "
                "This typically means the account has no recorded jobs in the current "
                "time window, or its consumption falls below the top-"
                f"{self.params.grouping_size} cutoff. Consider raising 'grouping_size' "
                "if the account is known to be active."
            ),
            reason=(
                f"Account '{self.params.account}' was absent from the top-"
                f"{self.params.grouping_size} grouped results."
            ),
            metadata={
                "account": self.params.account,
                "grouping_size": self.params.grouping_size,
            },
        )

    def _resolve_alert_level(self, ratio: float) -> tuple[AlertLevel, float] | None:
        """Map a quota-consumption fraction to an AlertLevel and threshold.

        CRITICAL checked first to avoid misclassification.
        """
        if ratio >= self.params.critical_pct:
            return AlertLevel.CRITICAL, self.params.critical_pct
        if ratio >= self.params.warn_pct:
            return AlertLevel.HIGH, self.params.warn_pct
        return None

    def _build_alert(self, consumed: float, ratio: float, level: AlertLevel, threshold_pct: float) -> Alert:
        """Build a quota-threshold alert for the monitored account."""
        return Alert(
            level=level,
            title=(
                f"Account '{self.params.account}' core-hours quota at {ratio:.1%} "
                f"({consumed:,.0f} / {self.params.quota_core_hours:,.0f} core-hours)"
            ),
            description=(
                f"Account '{self.params.account}' has consumed {consumed:,.0f} of "
                f"{self.params.quota_core_hours:,.0f} allocated core-hours ({ratio:.1%}), "
                f"exceeding the {level.label} threshold of {threshold_pct:.0%}. "
                "At this rate the quota may be exhausted before the period ends."
            ),
            reason=(
                f"Account '{self.params.account}' quota consumption {ratio:.1%} "
                f"exceeded threshold {threshold_pct:.0%}."
            ),
            metadata={
                "account": self.params.account,
                "consumed_core_hours": round(consumed, 2),
                "quota_core_hours": round(self.params.quota_core_hours, 2),
                "consumption_rate": round(ratio, 4),
            },
        )
