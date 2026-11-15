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
            "Name of the account to monitor. Must match the scheduler account field exactly."
        ),
    )
    quota_core_hours: float = Field(
        default=10_000.0,
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
        le=1.0,
        description="Fraction of quota consumed that triggers a CRITICAL alert (default 90%).",
    )
    grouping_size: int = Field(
        default=50,
        ge=1,
        description=(
            "Number of top accounts to retrieve from the provider. Raise this value "
            "if the target account does not appear in results."
        ),
    )


class CoresAccountQuotaRule(HealthcheckRule[Params]):
    """Alert when a named account's core-hours consumption approaches its quota."""

    params_model = Params

    def evaluate(self) -> list[Alert]:
        """Fetch grouped core-hours and return an alert if the quota is at risk."""
        result, status = self.cores.get_grouped_distribution(
            grouping_type="Account",
            grouping_size=self.params.grouping_size,
        )

        if status != ResultStatus.OK or result is None:
            return [self._no_data_alert(status)]

        target_group = next(
            (group for group in result.groups if group.group_name == self.params.account),
            None,
        )
        if target_group is None:
            return [self._account_not_found_alert()]

        consumed = sum(target_group.core_hours_sum)
        ratio = consumed / self.params.quota_core_hours

        alert_result = self._resolve_alert_level(ratio)
        if alert_result is None:
            return []

        level, threshold_pct = alert_result
        return [self._build_alert(consumed, ratio, level, threshold_pct)]

    def _no_data_alert(self, status: ResultStatus) -> Alert:
        """Build an informational OK alert when the provider returns no data."""
        return Alert(
            level=AlertLevel.OK,
            title="No data - core-hours quota",
            description=(
                f"The data provider returned status '{status.value}'; "
                "no data was available to evaluate the quota consumption."
            ),
            reason=f"Provider returned {status.value}.",
            metadata={"status": status.value, "account": self.params.account},
        )

    def _account_not_found_alert(self) -> Alert:
        """Build an informational OK alert when the target account is absent."""
        return Alert(
            level=AlertLevel.OK,
            title=f"Account '{self.params.account}' not found in core-hours results",
            description=(
                f"Account '{self.params.account}' did not appear in the top "
                f"{self.params.grouping_size} accounts returned by the provider. "
                "It may have no recorded jobs in the current window, or fall below "
                "the top-N cutoff. Consider raising 'grouping_size' if the account "
                "is known to be active."
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
        """Map a quota-consumption fraction to an AlertLevel and threshold."""
        if ratio >= self.params.critical_pct:
            return AlertLevel.CRITICAL, self.params.critical_pct
        if ratio >= self.params.warn_pct:
            return AlertLevel.HIGH, self.params.warn_pct
        return None

    def _build_alert(
        self, consumed: float, ratio: float, level: AlertLevel, threshold_pct: float
    ) -> Alert:
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
