"""
Data Enhancer: Custom cost calculation with student discount.

Description: Compute job costs based on CPU/GPU hours with custom tariffs and
a discount for student accounts matching a regex pattern.

Inspiration dépôt : ./oka_dataenhancers/costs/costs_demo.py
"""

import logging
import re

import pandas as pd
from applications.data_manager.lib.enhancer import DataEnhancer
from pydantic import BaseModel, Field

import lib.common.oka_constants.constants as oka_constants

logger = logging.getLogger("oka_main")


class CustomCostEnhancerParams(BaseModel):
    """Parameters for custom cost calculation."""

    cpu_hour_cost: float = Field(
        default=0.015,
        ge=0.0,
        description="Cost in currency unit per CPU-hour.",
    )
    gpu_hour_cost: float = Field(
        default=0.035,
        ge=0.0,
        description="Cost in currency unit per GPU-hour.",
    )
    gpu_partition: str = Field(
        default="gpu",
        description="Partition on which GPU hours are billed extra.",
    )
    disc_account: str = Field(
        default=r"etudiant_.*",
        description="Regex pattern for accounts eligible for student discount.",
    )
    disc_account_cpu_hour_cost: float = Field(
        default=0.0075,
        ge=0.0,
        description="Discounted cost per CPU-hour for student accounts.",
    )


class CustomCostEnhancer(DataEnhancer[CustomCostEnhancerParams]):
    """Compute job costs with custom tariffs and student discount.

    The reserved column "Cost" is used (no Cust_ prefix), as per OKA convention.
    All params have defaults so the enhancer runs with zero configuration.
    """

    params_model = CustomCostEnhancerParams

    def run(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Execute the enhancement logic.

        Args:
            data: Input DataFrame with one row per job.
            **kwargs: Additional arguments (ignored).

        Returns:
            DataFrame with the "Cost" column populated.
        """"
        disc_account_cmp = re.compile(self.params.disc_account)
        logger.info(
            "Entering CustomCostEnhancer. Applying costs:\n"
            f" - {self.params.cpu_hour_cost} per CPU-hour\n"
            f" - {self.params.disc_account_cpu_hour_cost} for {self.params.disc_account} accounts\n"
            f" - {self.params.gpu_hour_cost} on {self.params.gpu_partition} partition"
        )

        # Default cost for all jobs
        data[oka_constants.COST] = (
            data[oka_constants.COREHOURS] * self.params.cpu_hour_cost
        )

        # Discounted cost for student accounts
        account_mask = (
            data[oka_constants.ACCOUNT].str.match(disc_account_cmp).fillna(False)
        )
        data.loc[account_mask, oka_constants.COST] = (
            data.loc[account_mask, oka_constants.COREHOURS]
            * self.params.disc_account_cpu_hour_cost
        )

        # Additional GPU cost on the GPU partition
        gpu_mask = data[oka_constants.PARTITION] == self.params.gpu_partition
        data.loc[gpu_mask, oka_constants.COST] = (
            data.loc[gpu_mask, oka_constants.COST]
            + data.loc[gpu_mask, oka_constants.GPUHOURS] * self.params.gpu_hour_cost
        )

        logger.info("Custom costs computed!")
        return data

