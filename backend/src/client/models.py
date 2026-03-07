"""
Pydantic models for LiteLLM Gateway API responses.

These models are based on the OpenAPI specification in backend/openapi.json
and provide type-safe data structures for API client responses.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Spend Metrics Models
# ============================================================================


class SpendMetrics(BaseModel):
    """Metrics for spend, tokens, and requests."""

    spend: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0
    total_tokens: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    api_requests: int = 0


class KeyMetricWithMetadata(BaseModel):
    """Metric for API keys with metadata."""

    metrics: SpendMetrics  # Changed from 'metric' to 'metrics' to match API
    metadata: Optional[Dict[str, Any]] = None


class MetricWithMetadata(BaseModel):
    """Metric value with associated metadata."""

    metrics: SpendMetrics  # Changed from 'metric' to 'metrics' to match API
    metadata: Optional[Dict[str, Any]] = None
    api_key_breakdown: Optional[Dict[str, KeyMetricWithMetadata]] = None


class BreakdownMetrics(BaseModel):
    """Breakdown of spend by different dimensions."""

    mcp_servers: Optional[Dict[str, MetricWithMetadata]] = None
    models: Optional[Dict[str, MetricWithMetadata]] = None
    model_groups: Optional[Dict[str, MetricWithMetadata]] = None
    providers: Optional[Dict[str, MetricWithMetadata]] = None
    api_keys: Optional[Dict[str, KeyMetricWithMetadata]] = None
    entities: Optional[Dict[str, MetricWithMetadata]] = None


# ============================================================================
# Daily Activity Models
# ============================================================================


class DailySpendData(BaseModel):
    """Daily spend data with metrics and breakdown."""

    date: date
    metrics: SpendMetrics
    breakdown: Optional[BreakdownMetrics] = None


class DailySpendMetadata(BaseModel):
    """Metadata for paginated daily spend responses."""

    total_spend: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_api_requests: int = 0
    total_successful_requests: int = 0
    total_failed_requests: int = 0
    total_cache_read_input_tokens: int = 0
    total_cache_creation_input_tokens: int = 0
    page: int = 1
    total_pages: int = 1
    has_more: bool = False


class SpendAnalyticsPaginatedResponse(BaseModel):
    """Paginated response for spend analytics endpoints."""

    results: List[DailySpendData]
    metadata: Optional[DailySpendMetadata] = None


# ============================================================================
# Team Models
# ============================================================================


class Member(BaseModel):
    """Team member with role information."""

    user_id: str
    role: Optional[str] = None


class LiteLLMModelTable(BaseModel):
    """Model table reference (minimal fields for team context)."""

    model_id: Optional[int] = None
    model_name: Optional[str] = None


class LiteLLMObjectPermissionTable(BaseModel):
    """Object permission table reference."""

    permission_id: Optional[str] = None


class TeamResponse(BaseModel):
    """Team information from /team/list endpoint."""

    team_id: str
    team_alias: Optional[str] = None
    organization_id: Optional[str] = None
    admins: List[Any] = Field(default_factory=list)
    members: List[Any] = Field(default_factory=list)
    members_with_roles: List[Member] = Field(default_factory=list)
    team_member_permissions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    tpm_limit: Optional[int] = None
    rpm_limit: Optional[int] = None
    max_budget: Optional[float] = None
    budget_duration: Optional[str] = None
    models: List[Any] = Field(default_factory=list)
    blocked: bool = False
    spend: Optional[float] = None
    max_parallel_requests: Optional[int] = None
    budget_reset_at: Optional[datetime] = None
    model_id: Optional[int] = None
    litellm_model_table: Optional[LiteLLMModelTable] = None
    object_permission: Optional[LiteLLMObjectPermissionTable] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    object_permission_id: Optional[str] = None


# ============================================================================
# Model Info Models
# ============================================================================


class LiteLLMParams(BaseModel):
    """LiteLLM parameters for model configuration."""

    model: Optional[str] = None
    # Add other litellm_params fields as needed


class ModelInfoItem(BaseModel):
    """Model information item from /model/info endpoint."""

    model_name: str
    litellm_params: Optional[LiteLLMParams] = None
    model_info: Optional[Dict[str, Any]] = None


class ModelInfoResponse(BaseModel):
    """Response from /model/info endpoint."""

    data: List[ModelInfoItem] = Field(default_factory=list)
