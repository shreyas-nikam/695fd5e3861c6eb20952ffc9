from typing import Optional, Literal, List, Dict
from functools import lru_cache
from decimal import Decimal
import os
import sys

from pydantic import Field, ValidationError, field_validator, model_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
# Simulate the project structure: src/pe_orgair/config/settings.py
# For this notebook, we'll define the class directly.

class Settings(BaseSettings):
    """Application settings for the PE Org-AI-R Platform with production-grade validation."""

    # Model configuration for loading settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Application Settings ---
    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"
    SECRET_KEY: SecretStr # Sensitive key, must be handled securely

    # --- API Settings ---
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000)

    # --- Parameter Versioning ---
    PARAM_VERSION: Literal["v1.0", "v2.0"] = "v2.0"

    # --- LLM Providers (Multi-provider via LiteLLM) ---
    OPENAI_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_API_KEY: Optional[SecretStr] = None
    DEFAULT_LLM_MODEL: str = "gpt-40-2024-08-06"
    FALLBACK_LLM_MODEL: str = "claude-sonnet-4-20250514"

    # --- Cost Management ---
    DAILY_COST_BUDGET_USD: float = Field(default=500.0, ge=0)
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1)

    # --- HITL (Human-In-The-Loop) Thresholds ---
    HITL_SCORE_CHANGE_THRESHOLD: float = Field(default=15.0, ge=5, le=30)
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(default=10.0, ge=5, le=25)

    # Snowflake
    SNOWFLAKE_ACCOUNT: str
    SNOWFLAKE_USER: str
    SNOWFLAKE_PASSWORD: SecretStr
    SNOWFLAKE_DATABASE: str = "PE_ORGAIR"
    SNOWFLAKE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_WAREHOUSE: str
    SNOWFLAKE_ROLE: str = "PE_ORGAIR_ROLE"

    # AWS
    AWS_ACCESS_KEY_ID: SecretStr
    AWS_SECRET_ACCESS_KEY: SecretStr
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECTORS: int = 86400 # 24 hours
    CACHE_TTL_SCORES: int = 3600 # 1 hour

    # Scoring Parameters (v2.0)
    ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.55, le=0.70)
    BETA_SYNERGY_WEIGHT: float = Field(default=0.12, ge=0.08, le=0.20)
    LAMBDA_PENALTY: float = Field(default=0.25, ge=0, le=0.50)
    DELTA_POSITION: float = Field(default=0.15, ge=0.10, le=0.20)

    # Dimension Weights
    W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0)
    W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0)
    W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0)
    W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0)
    W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0)

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    OTEL_SERVICE_NAME: str = "pe-orgair"

# Function to get settings with caching, simulating application startup
@lru_cache
def get_settings() -> Settings:
    return Settings()

# Set required environment variables for the initial load example
os.environ["SECRET_KEY"] = "a_default_secret_key_for_dev_env"
os.environ["SNOWFLAKE_ACCOUNT"] = "test_account"
os.environ["SNOWFLAKE_USER"] = "test_user"
os.environ["SNOWFLAKE_PASSWORD"] = "test_snowflake_password"
os.environ["SNOWFLAKE_WAREHOUSE"] = "test_warehouse"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key_id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret_key"
os.environ["S3_BUCKET"] = "test_s3_bucket"

# Execute to load and display the default settings
print("--- Default Application Settings Loaded ---")
try:
    current_settings = get_settings()
    print(f"App Name: {current_settings.APP_NAME}")
    print(f"Environment: {current_settings.APP_ENV}")
    print(f"Debug Mode: {current_settings.DEBUG}")
    print(f"Secret Key Set: {'Yes' if current_settings.SECRET_KEY else 'No'} (Value masked for security)")
    # print(f"Secret Key Value: {current_settings.SECRET_KEY.get_secret_value()}") # Uncomment to see value
    print(f"API Rate Limit: {current_settings.RATE_LIMIT_PER_MINUTE} req/min")
    print(f"Daily Cost Budget: ${current_settings.DAILY_COST_BUDGET_USD}")
    print(f"Cost Alert Threshold: {current_settings.COST_ALERT_THRESHOLD_PCT*100}%")
    print(f"HITL Score Change Threshold: {current_settings.HITL_SCORE_CHANGE_THRESHOLD}")
    print(f"HITL EBITDA Projection Threshold: {current_settings.HITL_EBITDA_PROJECTION_THRESHOLD}")

except ValidationError as e:
    print(f"Error loading settings: {e}")

# Clean up any simulated environment variables for subsequent cells
os.environ.clear()
# To demonstrate field-level validation, we'll try to load settings with invalid values
# and observe Pydantic's automatic error handling.

# We need to re-define the Settings class including all previous fields for this cell to be self-contained.
class Settings(BaseSettings):
    """Application settings for the PE Org-AI-R Platform with production-grade validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"
    SECRET_KEY: SecretStr # Sensitive key, must be handled securely

    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000)

    PARAM_VERSION: Literal["v1.0", "v2.0"] = "v2.0"

    OPENAI_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_API_KEY: Optional[SecretStr] = None
    DEFAULT_LLM_MODEL: str = "gpt-40-2024-08-06"
    FALLBACK_LLM_MODEL: str = "claude-sonnet-4-20250514"

    DAILY_COST_BUDGET_USD: float = Field(default=500.0, ge=0)
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1)

    HITL_SCORE_CHANGE_THRESHOLD: float = Field(default=15.0, ge=5, le=30)
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(default=10.0, ge=5, le=25)

    SNOWFLAKE_ACCOUNT: str = "test_account"
    SNOWFLAKE_USER: str = "test_user"
    SNOWFLAKE_PASSWORD: SecretStr = Field(default="test_snowflake_password")
    SNOWFLAKE_DATABASE: str = "PE_ORGAIR"
    SNOWFLAKE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_WAREHOUSE: str = "test_warehouse"
    SNOWFLAKE_ROLE: str = "PE_ORGAIR_ROLE"

    AWS_ACCESS_KEY_ID: SecretStr = Field(default="test_aws_key_id")
    AWS_SECRET_ACCESS_KEY: SecretStr = Field(default="test_aws_secret_key")
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "test_s3_bucket"

    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECTORS: int = 86400
    CACHE_TTL_SCORES: int = 3600

    ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.55, le=0.70)
    BETA_SYNERGY_WEIGHT: float = Field(default=0.12, ge=0.08, le=0.20)
    LAMBDA_PENALTY: float = Field(default=0.25, ge=0, le=0.50)
    DELTA_POSITION: float = Field(default=0.15, ge=0.10, le=0.20)

    W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0)
    W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0)
    W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0)
    W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0)
    W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0)

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    OTEL_SERVICE_NAME: str = "pe-orgair"

# Function to get settings with caching, simulating application startup
@lru_cache
def get_settings_operational_validation() -> Settings:
    return Settings()

# Scenario 1: Valid settings for operational parameters
print("--- Scenario 1: Valid Operational Parameters ---")
os.environ.clear()
os.environ["RATE_LIMIT_PER_MINUTE"] = "100"
os.environ["DAILY_COST_BUDGET_USD"] = "1000.0"
os.environ["COST_ALERT_THRESHOLD_PCT"] = "0.75"
os.environ["HITL_SCORE_CHANGE_THRESHOLD"] = "20.0"
os.environ["HITL_EBITDA_PROJECTION_THRESHOLD"] = "15.0"
os.environ["SECRET_KEY"] = "a_very_secure_secret_key_for_testing_12345" # Required for loading
os.environ["SNOWFLAKE_ACCOUNT"] = "test_account"
os.environ["SNOWFLAKE_USER"] = "test_user"
os.environ["SNOWFLAKE_PASSWORD"] = "test_snowflake_password"
os.environ["SNOWFLAKE_WAREHOUSE"] = "test_warehouse"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key_id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret_key"
os.environ["S3_BUCKET"] = "test_s3_bucket"

get_settings_operational_validation.cache_clear() # Clear cache for new env vars
try:
    valid_settings = get_settings_operational_validation()
    print(f"API Rate Limit: {valid_settings.RATE_LIMIT_PER_MINUTE} req/min (Expected: 100, Actual: {valid_settings.RATE_LIMIT_PER_MINUTE})")
    print(f"Daily Cost Budget: ${valid_settings.DAILY_COST_BUDGET_USD} (Expected: 1000.0, Actual: {valid_settings.DAILY_COST_BUDGET_USD})")
    print(f"Cost Alert Threshold: {valid_settings.COST_ALERT_THRESHOLD_PCT*100}% (Expected: 75.0%, Actual: {valid_settings.COST_ALERT_THRESHOLD_PCT*100}%)")
    print(f"HITL Score Change Threshold: {valid_settings.HITL_SCORE_CHANGE_THRESHOLD} (Expected: 20.0, Actual: {valid_settings.HITL_SCORE_CHANGE_THRESHOLD})")
    print(f"HITL EBITDA Projection Threshold: {valid_settings.HITL_EBITDA_PROJECTION_THRESHOLD} (Expected: 15.0, Actual: {valid_settings.HITL_EBITDA_PROJECTION_THRESHOLD})")
except ValidationError as e:
    print(f"Unexpected validation error: {e}")

print("\n--- Scenario 2: Invalid Operational Parameters (Out of Range) ---")
os.environ.clear()
os.environ["RATE_LIMIT_PER_MINUTE"] = "1500" # Exceeds le=1000
os.environ["DAILY_COST_BUDGET_USD"] = "-50.0" # Below ge=0
os.environ["COST_ALERT_THRESHOLD_PCT"] = "1.5" # Exceeds le=1
os.environ["HITL_SCORE_CHANGE_THRESHOLD"] = "2.0" # Below ge=5
os.environ["HITL_EBITDA_PROJECTION_THRESHOLD"] = "50.0" # Exceeds le=25
os.environ["SECRET_KEY"] = "a_very_secure_secret_key_for_testing_12345" # Required for loading
os.environ["SNOWFLAKE_ACCOUNT"] = "test_account"
os.environ["SNOWFLAKE_USER"] = "test_user"
os.environ["SNOWFLAKE_PASSWORD"] = "test_snowflake_password"
os.environ["SNOWFLAKE_WAREHOUSE"] = "test_warehouse"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key_id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret_key"
os.environ["S3_BUCKET"] = "test_s3_bucket"

get_settings_operational_validation.cache_clear() # Clear cache for new env vars
try:
    invalid_settings = get_settings_operational_validation()
    print("Settings loaded successfully, but should have failed validation.")
except ValidationError as e:
    print("Caught expected validation error for invalid operational parameters:")
    print(e)

# Clean up simulated environment variables
os.environ.clear()
# Add dimension weight fields and the model_validator to the Settings class
# We need to re-define the Settings class including all previous fields for this cell to be self-contained.

class Settings(BaseSettings):
    """Application settings for the PE Org-AI-R Platform with production-grade validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"
    SECRET_KEY: SecretStr = Field(default="default_secret_for_dev_env_testing_0123456789") # Add default for easier testing

    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000)

    PARAM_VERSION: Literal["v1.0", "v2.0"] = "v2.0"

    OPENAI_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_API_KEY: Optional[SecretStr] = None
    DEFAULT_LLM_MODEL: str = "gpt-40-2024-08-06"
    FALLBACK_LLM_MODEL: str = "claude-sonnet-4-20250514"

    DAILY_COST_BUDGET_USD: float = Field(default=500.0, ge=0)
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1)

    HITL_SCORE_CHANGE_THRESHOLD: float = Field(default=15.0, ge=5, le=30)
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(default=10.0, ge=5, le=25)

    SNOWFLAKE_ACCOUNT: str = "test_account"
    SNOWFLAKE_USER: str = "test_user"
    SNOWFLAKE_PASSWORD: SecretStr = Field(default="test_snowflake_password")
    SNOWFLAKE_DATABASE: str = "PE_ORGAIR"
    SNOWFLAKE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_WAREHOUSE: str = "test_warehouse"
    SNOWFLAKE_ROLE: str = "PE_ORGAIR_ROLE"

    AWS_ACCESS_KEY_ID: SecretStr = Field(default="test_aws_key_id")
    AWS_SECRET_ACCESS_KEY: SecretStr = Field(default="test_aws_secret_key")
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "test_s3_bucket"

    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECTORS: int = 86400
    CACHE_TTL_SCORES: int = 3600

    ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.55, le=0.70)
    BETA_SYNERGY_WEIGHT: float = Field(default=0.12, ge=0.08, le=0.20)
    LAMBDA_PENALTY: float = Field(default=0.25, ge=0, le=0.50)
    DELTA_POSITION: float = Field(default=0.15, ge=0.10, le=0.20)

    # --- Scoring Parameters (v2.0) - Dimension Weights ---
    W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0)
    W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0)
    W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0)
    W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0)
    W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0)

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    OTEL_SERVICE_NAME: str = "pe-orgair"

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        if v is not None and not v.get_secret_value().startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format: must start with 'sk-'")
        return v

    @model_validator(mode="after")
    def validate_dimension_weights(self) -> "Settings":
        """Validate dimension weights sum to 1.0 +/- a small tolerance."""
        weights = [
            self.W_DATA_INFRA, self.W_AI_GOVERNANCE, self.W_TECH_STACK,
            self.W_TALENT, self.W_LEADERSHIP, self.W_USE_CASES, self.W_CULTURE
        ]
        total = sum(weights)
        # Use a small epsilon for floating-point comparison
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Dimension weights must sum to 1.0, got {total}")
        return self

# Function to get settings, re-defining to clear cache for new class definition
@lru_cache
def get_settings_with_weights() -> Settings:
    return Settings()

# Scenario 1: Valid dimension weights (sum = 1.0)
print("--- Scenario 1: Valid Dimension Weights ---")
# Reset environment variables
os.environ.clear()
os.environ["SECRET_KEY"] = "valid_key_for_testing_12345678901234567890" # Must be set for model to load
os.environ["SNOWFLAKE_ACCOUNT"] = "test_account"
os.environ["SNOWFLAKE_USER"] = "test_user"
os.environ["SNOWFLAKE_PASSWORD"] = "test_snowflake_password"
os.environ["SNOWFLAKE_WAREHOUSE"] = "test_warehouse"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key_id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret_key"
os.environ["S3_BUCKET"] = "test_s3_bucket"

# Default weights sum to 1.0 (0.18+0.15+0.15+0.17+0.13+0.12+0.10 = 1.0)
get_settings_with_weights.cache_clear() # Clear cache for new env vars
try:
    valid_weight_settings = get_settings_with_weights()
    # For displaying the sum, create a list of dimension weights for easy access.
    # Removed assignment to valid_weight_settings.dimension_weights
    dimension_weights_list = [
        valid_weight_settings.W_DATA_INFRA, valid_weight_settings.W_AI_GOVERNANCE, valid_weight_settings.W_TECH_STACK,
        valid_weight_settings.W_TALENT, valid_weight_settings.W_LEADERSHIP, valid_weight_settings.W_USE_CASES, valid_weight_settings.W_CULTURE
    ]
    print(f"Dimension weights total: {sum(dimension_weights_list)}")
    print("Dimension weights validated successfully.")
except ValidationError as e:
    print(f"Unexpected validation error: {e}")

print("\n--- Scenario 2: Invalid Dimension Weights (Sum != 1.0) ---")
os.environ.clear()
os.environ["W_DATA_INFRA"] = "0.20" # Default was 0.18, now sum will be 1.02
os.environ["SECRET_KEY"] = "valid_key_for_testing_12345678901234567890" # Must be set for model to load
os.environ["SNOWFLAKE_ACCOUNT"] = "test_account"
os.environ["SNOWFLAKE_USER"] = "test_user"
os.environ["SNOWFLAKE_PASSWORD"] = "test_snowflake_password"
os.environ["SNOWFLAKE_WAREHOUSE"] = "test_warehouse"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key_id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret_key"
os.environ["S3_BUCKET"] = "test_s3_bucket"

get_settings_with_weights.cache_clear() # Clear cache for new env vars
try:
    invalid_weight_settings = get_settings_with_weights()
    print("Settings loaded successfully, but should have failed validation.")
except ValidationError as e:
    print("Caught expected validation error for dimension weights:")
    print(e)

# Clean up simulated environment variables
os.environ.clear()
# Add the production-specific model_validator and the OpenAI API key field_validator to the Settings class
# We need to re-define the Settings class including all previous fields and validators for this cell to be self-contained.

class Settings(BaseSettings):
    """Application settings for the PE Org-AI-R Platform with production-grade validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"
    SECRET_KEY: SecretStr = Field(default="default_secret_for_dev_env_testing_0123456789")

    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000)
    DAILY_COST_BUDGET_USD: float = Field(default=500.0, ge=0)
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1)

    HITL_SCORE_CHANGE_THRESHOLD: float = Field(default=15.0, ge=5, le=30)
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(default=10.0, ge=5, le=25)

    # LLM Provider keys
    OPENAI_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_API_KEY: Optional[SecretStr] = None

    SNOWFLAKE_ACCOUNT: str = "test_account"
    SNOWFLAKE_USER: str = "test_user"
    SNOWFLAKE_PASSWORD: SecretStr = Field(default="test_snowflake_password")
    SNOWFLAKE_DATABASE: str = "PE_ORGAIR"
    SNOWFLAKE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_WAREHOUSE: str = "test_warehouse"
    SNOWFLAKE_ROLE: str = "PE_ORGAIR_ROLE"

    AWS_ACCESS_KEY_ID: SecretStr = Field(default="test_aws_key_id")
    AWS_SECRET_ACCESS_KEY: SecretStr = Field(default="test_aws_secret_key")
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "test_s3_bucket"

    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECTORS: int = 86400
    CACHE_TTL_SCORES: int = 3600

    # Scoring Parameters (v2.0) - Dimension Weights
    W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0)
    W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0)
    W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0)
    W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0)
    W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0)

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    OTEL_SERVICE_NAME: str = "pe-orgair"

    # Ensure dimension weights sum to 1.0 (re-using the validator from previous section)
    @model_validator(mode="after")
    def validate_dimension_weights(self) -> "Settings":
        weights = [
            self.W_DATA_INFRA, self.W_AI_GOVERNANCE, self.W_TECH_STACK,
            self.W_TALENT, self.W_LEADERSHIP, self.W_USE_CASES, self.W_CULTURE
        ]
        total = sum(weights)
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Dimension weights must sum to 1.0, got {total}")
        return self

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        if v is not None and not v.get_secret_value().startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format: must start with 'sk-'")
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Ensure production environment has required security and API settings."""
        if self.APP_ENV == "production":
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production environment")
            if len(self.SECRET_KEY.get_secret_value()) < 32:
                raise ValueError("SECRET_KEY must be \u226532 characters in production environment")
            if not self.OPENAI_API_KEY and not self.ANTHROPIC_API_KEY:
                raise ValueError("At least one LLM API key (OpenAI or Anthropic) is required in production environment")
        return self

# Function to get settings with production validation
@lru_cache
def get_settings_with_prod_validation() -> Settings:
    return Settings()

# Scenario 1: Valid Production Configuration
print("--- Scenario 1: Valid Production Configuration ---")
os.environ.clear()
os.environ["APP_ENV"] = "production"
os.environ["DEBUG"] = "False"
os.environ["SECRET_KEY"] = "this_is_a_very_long_and_secure_secret_key_for_production_0123456789" # >= 32 chars
os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # Valid format
os.environ["SNOWFLAKE_ACCOUNT"] = "test_account"
os.environ["SNOWFLAKE_USER"] = "test_user"
os.environ["SNOWFLAKE_PASSWORD"] = "test_snowflake_password"
os.environ["SNOWFLAKE_WAREHOUSE"] = "test_warehouse"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key_id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret_key"
os.environ["S3_BUCKET"] = "test_s3_bucket"

get_settings_with_prod_validation.cache_clear() # Clear cache for new env vars
try:
    prod_settings_valid = get_settings_with_prod_validation()
    print("Production settings loaded successfully:")
    print(f"  APP_ENV: {prod_settings_valid.APP_ENV}")
    print(f"  DEBUG: {prod_settings_valid.DEBUG}")
    print(f"  SECRET_KEY length: {len(prod_settings_valid.SECRET_KEY.get_secret_value())}")
    print(f"  OpenAI API Key provided: {'Yes' if prod_settings_valid.OPENAI_API_KEY else 'No'}")
except ValidationError as e:
    print(f"Unexpected validation error for valid production settings: {e}")

# Scenario 2: Invalid Production Configuration - DEBUG is True
print("\n--- Scenario 2: Invalid Production Config - DEBUG is True ---")
os.environ.clear()
os.environ["APP_ENV"] = "production"
os.environ["DEBUG"] = "True" # This should fail
os.environ["SECRET_KEY"] = "this_is_a_very_long_and_secure_secret_key_for_production_0123456789"
os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
os.environ["SNOWFLAKE_ACCOUNT"] = "test_account"
os.environ["SNOWFLAKE_USER"] = "test_user"
os.environ["SNOWFLAKE_PASSWORD"] = "test_snowflake_password"
os.environ["SNOWFLAKE_WAREHOUSE"] = "test_warehouse"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key_id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret_key"
os.environ["S3_BUCKET"] = "test_s3_bucket"

get_settings_with_prod_validation.cache_clear() # Clear cache for new env vars
try:
    get_settings_with_prod_validation()
    print("Settings loaded successfully, but should have failed validation (DEBUG is True).")
except ValidationError as e:
    print("Caught expected validation error:")
    print(e)

# Scenario 3: Invalid Production Configuration - Short SECRET_KEY
print("\n--- Scenario 3: Invalid Production Config - Short SECRET_KEY ---")
os.environ.clear()
os.environ["APP_ENV"] = "production"
os.environ["DEBUG"] = "False"
os.environ["SECRET_KEY"] = "too_short_key" # This should fail (< 32 chars)
os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
os.environ["SNOWFLAKE_ACCOUNT"] = "test_account"
os.environ["SNOWFLAKE_USER"] = "test_user"
os.environ["SNOWFLAKE_PASSWORD"] = "test_snowflake_password"
os.environ["SNOWFLAKE_WAREHOUSE"] = "test_warehouse"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key_id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret_key"
os.environ["S3_BUCKET"] = "test_s3_bucket"

get_settings_with_prod_validation.cache_clear() # Clear cache for new env vars
try:
    get_settings_with_prod_validation()
    print("Settings loaded successfully, but should have failed validation (short SECRET_KEY).")
except ValidationError as e:
    print("Caught expected validation error:")
    print(e)

# Scenario 4: Invalid Production Configuration - Missing LLM API Keys
print("\n--- Scenario 4: Invalid Production Config - Missing LLM API Keys ---")
os.environ.clear()
os.environ["APP_ENV"] = "production"
os.environ["DEBUG"] = "False"
os.environ["SECRET_KEY"] = "this_is_a_very_long_and_secure_secret_key_for_production_0123456789"
# OPENAI_API_KEY and ANTHROPIC_API_KEY are not set, which implies None
os.environ["SNOWFLAKE_ACCOUNT"] = "test_account"
os.environ["SNOWFLAKE_USER"] = "test_user"
os.environ["SNOWFLAKE_PASSWORD"] = "test_snowflake_password"
os.environ["SNOWFLAKE_WAREHOUSE"] = "test_warehouse"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key_id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret_key"
os.environ["S3_BUCKET"] = "test_s3_bucket"

get_settings_with_prod_validation.cache_clear() # Clear cache for new env vars
try:
    get_settings_with_prod_validation()
    print("Settings loaded successfully, but should have failed validation (missing LLM API keys).")
except ValidationError as e:
    print("Caught expected validation error:")
    print(e)

# Scenario 5: Invalid OpenAI API Key Format
print("\n--- Scenario 5: Invalid OpenAI API Key Format ---")
os.environ.clear()
os.environ["APP_ENV"] = "development" # Can be dev, as field validator runs independently
os.environ["SECRET_KEY"] = "valid_dev_key_12345678901234567890"
os.environ["OPENAI_API_KEY"] = "pk-wrong_prefix_instead_of_sk-" # This should fail
os.environ["SNOWFLAKE_ACCOUNT"] = "test_account"
os.environ["SNOWFLAKE_USER"] = "test_user"
os.environ["SNOWFLAKE_PASSWORD"] = "test_snowflake_password"
os.environ["SNOWFLAKE_WAREHOUSE"] = "test_warehouse"
os.environ["AWS_ACCESS_KEY_ID"] = "test_aws_key_id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_aws_secret_key"
os.environ["S3_BUCKET"] = "test_s3_bucket"

get_settings_with_prod_validation.cache_clear() # Clear cache for new env vars
try:
    get_settings_with_prod_validation()
    print("Settings loaded successfully, but should have failed validation (invalid OpenAI key format).")
except ValidationError as e:
    print("Caught expected validation error:")
    print(e)

# Clean up simulated environment variables
os.environ.clear()
# Helper function to clear environment variables for a clean test
def clear_env():
    # Only clear variables starting with a prefix to avoid clearing system vars
    for key in list(os.environ.keys()):
        if key.startswith(("APP_", "SECRET_", "RATE_", "DAILY_", "COST_", "W_", "OPENAI_", "ANTHROPIC_", "HITL_", "SNOWFLAKE_", "AWS_", "S3_", "REDIS_", "CACHE_", "CELERY_", "OTEL_", "ALPHA_", "BETA_", "LAMBDA_", "DELTA_", "API_", "PARAM_", "DEFAULT_", "FALLBACK_", "LOG_")):
            del os.environ[key]

# Function to load settings for a given scenario
def load_scenario_settings(scenario_name: str, env_vars: Dict[str, str]):
    clear_env() # Start with a clean slate
    print(f"\n--- Simulating Scenario: {scenario_name} ---")
    for key, value in env_vars.items():
        os.environ[key] = value

    # Required default environment variables for the Settings class to instantiate
    # These are added if not explicitly provided in scenario_env_vars
    default_required_env_vars = {
        "SECRET_KEY": "default_secret_for_dev_env_testing_0123456789",
        "SNOWFLAKE_ACCOUNT": "test_account",
        "SNOWFLAKE_USER": "test_user",
        "SNOWFLAKE_PASSWORD": "test_snowflake_password",
        "SNOWFLAKE_WAREHOUSE": "test_warehouse",
        "AWS_ACCESS_KEY_ID": "test_aws_key_id",
        "AWS_SECRET_ACCESS_KEY": "test_aws_secret_key",
        "S3_BUCKET": "test_s3_bucket"
    }

    for key, value in default_required_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

    # Reload settings with new environment variables
    # We need to clear lru_cache for get_settings_with_prod_validation to pick up new env vars
    get_settings_with_prod_validation.cache_clear()

    try:
        settings = get_settings_with_prod_validation()
        print(f"SUCCESS: Configuration for '{scenario_name}' is VALID.")
        print(f"  APP_ENV: {settings.APP_ENV}")
        print(f"  DEBUG: {settings.DEBUG}")
        print(f"  SECRET_KEY (masked): {settings.SECRET_KEY}")
        dimension_weights_sum = sum([
            settings.W_DATA_INFRA, settings.W_AI_GOVERNANCE, settings.W_TECH_STACK,
            settings.W_TALENT, settings.W_LEADERSHIP, settings.W_USE_CASES, settings.W_CULTURE
        ])
        print(f"  Dimension Weights Sum: {dimension_weights_sum}")
        print(f"  OpenAI API Key Set: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
    except ValidationError as e:
        print(f"FAILURE: Configuration for '{scenario_name}' is INVALID. Details:")
        print(e)
    finally:
        clear_env()

# Scenario Definitions
scenarios = {
    "Valid Development Config": {
        "APP_ENV": "development",
        "DEBUG": "True",
        "SECRET_KEY": "dev_key_for_testing_12345678901234567890",
        "OPENAI_API_KEY": "sk-dev_test_key_xxxx",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
        "RATE_LIMIT_PER_MINUTE": "100",
        "DAILY_COST_BUDGET_USD": "750.0",
        "COST_ALERT_THRESHOLD_PCT": "0.85",
        "HITL_SCORE_CHANGE_THRESHOLD": "18.0",
        "HITL_EBITDA_PROJECTION_THRESHOLD": "12.5"
    },
    "Valid Production Config": {
        "APP_ENV": "production",
        "DEBUG": "False",
        "SECRET_KEY": "prod_secure_key_12345678901234567890123456789012", # >= 32 chars
        "ANTHROPIC_API_KEY": "sk-ant-key_xxxxxxxxxxxxxxxxxxxxxxxxxxxx", # One LLM key required
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
        "RATE_LIMIT_PER_MINUTE": "500",
        "DAILY_COST_BUDGET_USD": "10000.0",
        "COST_ALERT_THRESHOLD_PCT": "0.9",
        "HITL_SCORE_CHANGE_THRESHOLD": "25.0",
        "HITL_EBITDA_PROJECTION_THRESHOLD": "20.0"
    },
    "Invalid: Production DEBUG Mode Enabled": {
        "APP_ENV": "production",
        "DEBUG": "True", # ERROR: Debug should be False in production
        "SECRET_KEY": "prod_secure_key_12345678901234567890123456789012",
        "OPENAI_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
        "RATE_LIMIT_PER_MINUTE": "60"
    },
    "Invalid: Dimension Weights Don't Sum to 1.0": {
        "APP_ENV": "development",
        "DEBUG": "False",
        "SECRET_KEY": "dev_key_for_testing_12345678901234567890",
        "W_DATA_INFRA": "0.20", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10", # Sum = 1.02
        "RATE_LIMIT_PER_MINUTE": "60"
    },
    "Invalid: API Rate Limit Out of Range": {
        "APP_ENV": "development",
        "DEBUG": "False",
        "SECRET_KEY": "dev_key_for_testing_12345678901234567890",
        "RATE_LIMIT_PER_MINUTE": "1200", # ERROR: Exceeds max 1000
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10"
    }
}

# Run all scenarios
for name, env_vars in scenarios.items():
    load_scenario_settings(name, env_vars)

# Final cleanup
clear_env()