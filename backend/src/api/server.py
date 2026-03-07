import os
from typing import Optional
from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from src.api.models import (
    TeamOut,
    TeamsOut,
    TimeSeriesOut,
    ModelsOut,
    SuccessRateSummaryOut,
    TeamSuccessRate,
    CostEfficiencyOut,
    HourlyBreakdownOut,
    HourlyBucket,
)
from src.services.token_aggregation_service import TokenAggregationService
from src.services.time_series_service import TimeSeriesService
from src.services.success_rate_service import SuccessRateService
from src.services.cost_efficiency_service import CostEfficiencyService
from src.utils.dependency_config import (
    get_token_aggregation_service,
    get_time_series_service,
    get_success_rate_service,
    get_cost_efficiency_service,
)
from src.utils.endpoint_utils import execute_date_range_endpoint


def create_backend():

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,  # type: ignore[arg-type]
        allow_origins=[
            f"http://{os.environ.get('VITE_WORKSHOP_USER')}-leaderboard-frontend.workshop.devboost.com",
            f"http://localhost:{os.environ.get('VITE_LEADERBOARD_FRONTEND_PORT')}",
        ],
    )

    load_dotenv()

    @app.get("/tokens", response_model=TeamsOut)
    def get_tokens(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        service: TokenAggregationService = Depends(get_token_aggregation_service),
    ) -> TeamsOut:
        """
        Returns the aggregate tokens per team between start_date and end_date.

        Query Parameters:
        - start_date: Optional start date in YYYY-MM-DD format (defaults to 24 hours ago)
        - end_date: Optional end date in YYYY-MM-DD format (defaults to now)

        Response shape:
        {
        "teams": [
            {"name": "teamA", "tokens": 123},
            ...
        ]
        }
        """
        team_data = execute_date_range_endpoint(
            start_date, end_date, service.fetch_total_tokens_per_team
        )

        teams = [
            TeamOut(
                name=name, tokens=data["total_tokens"], breakdown=data.get("breakdown")
            )
            for name, data in team_data.items()
        ]

        return TeamsOut(teams=teams)

    @app.get("/tokens/timeseries", response_model=TimeSeriesOut)
    def get_tokens_timeseries(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        service: TimeSeriesService = Depends(get_time_series_service),
    ) -> TimeSeriesOut:
        """
        Returns daily time-series token data per team between start_date and end_date.

        Query Parameters:
        - start_date: Optional start date in YYYY-MM-DD format (defaults to 24 hours ago)
        - end_date: Optional end date in YYYY-MM-DD format (defaults to now)

        Response shape:
        {
            "timeseries": [
                {
                    "date": "2024-01-15",
                    "teams": [
                        {"name": "Team A", "tokens": 1500},
                        {"name": "Team B", "tokens": 2300}
                    ]
                },
                ...
            ]
        }
        """
        timeseries_data = execute_date_range_endpoint(
            start_date, end_date, service.fetch_daily_timeseries_per_team
        )

        # Pydantic will validate and convert the dict data to DailyTimeSeriesPoint objects
        return TimeSeriesOut(timeseries=timeseries_data)  # type: ignore[arg-type]

    @app.get("/tokens/models", response_model=ModelsOut)
    def get_tokens_models(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        # TODO: implement proper service
        # service: ModelUsageService = Depends(get_model_usage_service),
    ) -> ModelsOut:
        """
        Returns aggregated token usage per model between start_date and end_date.

        Query Parameters:
        - start_date: Optional start date in YYYY-MM-DD format (defaults to 24 hours ago)
        - end_date: Optional end date in YYYY-MM-DD format (defaults to now)

        Response shape:
        {
            "models": [
                {"model": "openai/gpt-4", "tokens": 125000},
                {"model": "anthropic/claude-3-opus", "tokens": 98000}
            ]
        }
        """

        return ModelsOut()

    @app.get("/tokens/success-rate", response_model=SuccessRateSummaryOut)
    def get_team_success_rate_summary(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        service: SuccessRateService = Depends(get_success_rate_service),
    ) -> SuccessRateSummaryOut:
        """
        Returns aggregated success rate summary per team over the entire date range.

        Query Parameters:
        - start_date: Optional start date in YYYY-MM-DD format (defaults to 24 hours ago)
        - end_date: Optional end date in YYYY-MM-DD format (defaults to now)

        Response shape:
        {
            "teams": [
                {
                    "name": "Team A",
                    "total_requests": 500,
                    "successful_requests": 475,
                    "failed_requests": 25,
                    "success_rate": 95.0
                }
            ]
        }
        """
        summary_data = execute_date_range_endpoint(
            start_date, end_date, service.fetch_team_success_rate_summary
        )

        teams = [TeamSuccessRate(**team) for team in summary_data]

        return SuccessRateSummaryOut(teams=teams)

    @app.get("/tokens/cost-efficiency", response_model=CostEfficiencyOut)
    def get_cost_efficiency(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        service: CostEfficiencyService = Depends(get_cost_efficiency_service),
    ) -> CostEfficiencyOut:
        """
        Returns cost efficiency data (cost per 1k tokens) by team and model.

        Query Parameters:
        - start_date: Optional start date in YYYY-MM-DD format (defaults to 24 hours ago)
        - end_date: Optional end date in YYYY-MM-DD format (defaults to now)

        Response shape:
        {
            "cells": [
                {
                    "team": "Team A",
                    "model": "openai/gpt-4",
                    "cost_per_1k_tokens": 0.03,
                    "total_cost": 15.50,
                    "total_tokens": 516667
                }
            ]
        }
        """
        cells = execute_date_range_endpoint(
            start_date, end_date, service.fetch_cost_efficiency
        )

        # Pydantic will validate and convert the dict data to CostEfficiencyCell objects
        return CostEfficiencyOut(cells=cells)  # type: ignore[arg-type]

    @app.get("/tokens/hourly", response_model=HourlyBreakdownOut)
    def get_tokens_hourly(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        team: Optional[str] = None,
    ) -> HourlyBreakdownOut:
        """
        Returns hourly token breakdown aggregated across the date range.

        Query Parameters:
        - start_date: Optional start date in YYYY-MM-DD format (defaults to 24 hours ago)
        - end_date: Optional end date in YYYY-MM-DD format (defaults to now)
        - team: Optional team name for filtering

        Response shape:
        {
            "hours": [
                {"hour": 0, "tokens": 1500},
                {"hour": 1, "tokens": 2300},
                ...
                {"hour": 23, "tokens": 4200}
            ]
        }
        """
        # TEMPORARY: Hard-coded data for demo. Replace with real service in task 4.
        # Simulate realistic hourly distribution with higher usage during work hours (8-18)
        hours = []
        for hour in range(24):
            if 8 <= hour <= 18:
                # Work hours: higher token usage (5000-15000)
                tokens = 5000 + (hour - 8) * 1000 + (18 - hour) * 500
            elif 6 <= hour < 8 or 18 < hour <= 22:
                # Early morning and evening: moderate usage (2000-5000)
                tokens = 3000 + (hour % 3) * 700
            else:
                # Night hours: low usage (500-2000)
                tokens = 500 + (hour % 4) * 400
            
            hours.append(HourlyBucket(hour=hour, tokens=tokens))
        
        return HourlyBreakdownOut(hours=hours)

    return app
