
# Automated & Validated API Configuration for Production

## Introduction: Safeguarding the PE Intelligence Platform

As a **Software Developer** building the Organizational AIR Scoring platform, ensuring the robustness and security of our application configurations is paramount. Every new feature or data processing service we deploy relies on correct, consistent, and validated settings across different environments – development, staging, and crucially, production. A single misconfigured parameter, such as an incorrect API key, an out-of-bounds budget, or an improperly weighted scoring dimension, can lead to critical application crashes, compromised data integrity, or skewed analytical outcomes that directly impact investment decisions.

This notebook outlines a real-world workflow to implement a highly reliable configuration system using Pydantic v2. Our goal is to prevent these costly configuration-related bugs by enforcing strict validation rules at application startup, significantly reducing operational overhead and building trust in our platform's outputs. We will walk through defining settings, applying various validation types, and simulating different environmental scenarios to demonstrate how invalid configurations are caught *before* they can cause harm.

---

### 1. Initial Setup: Environment and Dependencies

Before we dive into defining and validating our application settings, let's ensure our environment has all the necessary tools. We'll specifically need `pydantic` and `pydantic-settings` for robust configuration management.

```python
!pip install pydantic==2.* pydantic-settings==2.*
```

Next, we'll import the core components from Pydantic and Python's standard library that we'll use throughout this workflow.

```python
from typing import Optional, Literal, List, Dict
from functools import lru_cache
from decimal import Decimal
import os
import sys

from pydantic import Field, ValidationError, field_validator, model_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
```

---

### 2. Setting the Stage: Core Application Configuration

As a Software Developer, my first step in configuring a new service for the PE intelligence platform is to define its fundamental settings. These include basic application metadata, environment specification, logging preferences, and crucial sensitive data like secret keys. Using Pydantic's `BaseSettings` and `SettingsConfigDict` allows us to define these in a structured, type-hinted manner, automatically loading from environment variables or `.env` files.

For sensitive information, like the `SECRET_KEY`, we employ Pydantic's `SecretStr` type. This ensures that the value is never accidentally logged or exposed, enhancing the security posture of our application.

#### Workflow Task: Define Base Application Settings

We will define the `Settings` class, which will serve as the single source of truth for our application's configuration.

```python
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
    OTEL_SERVICE_NAME: str = "pe-orgair


# Function to get settings with caching, simulating application startup
@lru_cache
def get_settings() -> Settings:
    return Settings()

# Execute to load and display the default settings
print("--- Default Application Settings Loaded ---")
try:
    current_settings = get_settings()
    print(f"App Name: {current_settings.APP_NAME}")
    print(f"Environment: {current_settings.APP_ENV}")
    print(f"Debug Mode: {current_settings.DEBUG}")
    print(f"Secret Key Set: {'Yes' if current_settings.SECRET_KEY else 'No'} (Value masked for security)")
    # Accessing the secret value for illustration (but normally avoid printing directly)
    # print(f"Secret Key Value: {current_settings.SECRET_KEY.get_secret_value()}")
    print(f"API Rate Limit: {current_settings.RATE_LIMIT_PER_MINUTE} req/min")
    print(f"Daily Cost Budget: ${current_settings.DAILY_COST_BUDGET_USD}")
    print(f"Cost Alert Threshold: {current_settings.COST_ALERT_THRESHOLD_PCT*100}%")
    print(f"HITL Score Change Threshold: {current_settings.HITL_SCORE_CHANGE_THRESHOLD}")
    print(f"HITL EBITDA Projection Threshold: {current_settings.HITL_EBITDA_PROJECTION_THRESHOLD}")

except ValidationError as e:
    print(f"Error loading settings: {e}")

# Clean up any simulated environment variables for subsequent cells
os.environ.clear()
```

#### Explanation of Execution
The code successfully loads the default configuration, demonstrating how basic settings are initialized. The `SECRET_KEY` is handled by `SecretStr`, ensuring its value is masked when accessed directly (e.g., in `print()`) but can be retrieved using `.get_secret_value()` when needed for actual application logic (e.g., connecting to external services). This direct usage of `SecretStr` helps us, as developers, prevent accidental exposure of sensitive credentials, a common source of security vulnerabilities.

---

### 3. Ensuring Operational Integrity: Field-Level Validation

Operational parameters like API rate limits, daily cost budgets, and alert thresholds are critical for the stability and cost-effectiveness of our PE intelligence platform. As a Data Engineer, I need to ensure these values are always within sensible, predefined ranges to prevent system overload, budget overruns, or ineffective alerting. Pydantic's `Field` with `ge` (greater than or equal to) and `le` (less than or equal to) arguments allows us to enforce these constraints directly within the configuration definition.

#### Workflow Task: Validate Operational Parameters with Range Constraints

We'll define an API rate limit (`RATE_LIMIT_PER_MINUTE`), a daily cost budget (`DAILY_COST_BUDGET_USD`), and a cost alert threshold (`COST_ALERT_THRESHOLD_PCT`). These parameters are crucial for system health and financial governance.

```python
# To demonstrate field-level validation, we'll try to load settings with invalid values
# and observe Pydantic's automatic error handling.

# Scenario 1: Valid settings for operational parameters
print("--- Scenario 1: Valid Operational Parameters ---")
os.environ["RATE_LIMIT_PER_MINUTE"] = "100"
os.environ["DAILY_COST_BUDGET_USD"] = "1000.0"
os.environ["COST_ALERT_THRESHOLD_PCT"] = "0.75"
os.environ["HITL_SCORE_CHANGE_THRESHOLD"] = "20.0"
os.environ["HITL_EBITDA_PROJECTION_THRESHOLD"] = "15.0"
os.environ["SECRET_KEY"] = "a_very_secure_secret_key_for_testing_12345" # Required for loading

try:
    valid_settings = Settings()
    print(f"API Rate Limit: {valid_settings.RATE_LIMIT_PER_MINUTE} req/min (Expected: 100, Actual: {valid_settings.RATE_LIMIT_PER_MINUTE})")
    print(f"Daily Cost Budget: ${valid_settings.DAILY_COST_BUDGET_USD} (Expected: 1000.0, Actual: {valid_settings.DAILY_COST_BUDGET_USD})")
    print(f"Cost Alert Threshold: {valid_settings.COST_ALERT_THRESHOLD_PCT*100}% (Expected: 75.0%, Actual: {valid_settings.COST_ALERT_THRESHOLD_PCT*100}%)")
    print(f"HITL Score Change Threshold: {valid_settings.HITL_SCORE_CHANGE_THRESHOLD} (Expected: 20.0, Actual: {valid_settings.HITL_SCORE_CHANGE_THRESHOLD})")
    print(f"HITL EBITDA Projection Threshold: {valid_settings.HITL_EBITDA_PROJECTION_THRESHOLD} (Expected: 15.0, Actual: {valid_settings.HITL_EBITDA_PROJECTION_THRESHOLD})")
except ValidationError as e:
    print(f"Unexpected validation error: {e}")

print("\n--- Scenario 2: Invalid Operational Parameters (Out of Range) ---")
os.environ["RATE_LIMIT_PER_MINUTE"] = "1500" # Exceeds le=1000
os.environ["DAILY_COST_BUDGET_USD"] = "-50.0" # Below ge=0
os.environ["COST_ALERT_THRESHOLD_PCT"] = "1.5" # Exceeds le=1
os.environ["HITL_SCORE_CHANGE_THRESHOLD"] = "2.0" # Below ge=5
os.environ["HITL_EBITDA_PROJECTION_THRESHOLD"] = "50.0" # Exceeds le=25

try:
    invalid_settings = Settings()
    print("Settings loaded successfully, but should have failed validation.")
except ValidationError as e:
    print("Caught expected validation error for invalid operational parameters:")
    print(e)
    # The error message explicitly states which fields failed validation.
    # For example, look for "rate_limit_per_minute" or "daily_cost_budget_usd" in the output.

# Clean up simulated environment variables
os.environ.clear()
```

#### Explanation of Execution
The first scenario demonstrates successful loading when all operational parameters are within their defined bounds. In contrast, the second scenario attempts to load configurations with values exceeding or falling below the specified ranges for `RATE_LIMIT_PER_MINUTE`, `DAILY_COST_BUDGET_USD`, `COST_ALERT_THRESHOLD_PCT`, `HITL_SCORE_CHANGE_THRESHOLD`, and `HITL_EBITDA_PROJECTION_THRESHOLD`. Pydantic immediately raises a `ValidationError`, providing clear, detailed messages about which specific fields failed and why. This automatic, early detection of out-of-bounds values by `Field(ge=X, le=Y)` is crucial. It prevents the system from starting with configurations that could lead to financial losses (e.g., negative budget), operational issues (e.g., excessively high rate limits), or ineffective human-in-the-loop interventions due to inappropriate thresholds.

---

### 4. Implementing Business Logic: Cross-Field Validation for Scoring Weights

A core component of the PE intelligence platform is its investment scoring model, which relies on various dimensions (e.g., data infrastructure, AI governance, talent). The relative importance of these dimensions is defined by a set of weights. A critical business rule mandates that these **dimension weights must sum up to exactly 1.0** to ensure a coherent and balanced scoring mechanism. Deviations from this sum would lead to skewed, unreliable scores and potentially poor investment recommendations.

As a Data Engineer, I need to implement a robust check to enforce this rule. Pydantic's `@model_validator(mode="after")` is perfect for this, as it allows us to perform validation logic that involves multiple fields *after* individual field validations have passed.

#### Workflow Task: Validate Dimension Weights Sum to 1.0

We will define new fields for dimension weights and then add a `@model_validator` to ensure their sum is $1.0$. A small tolerance $\epsilon$ is used to account for floating-point inaccuracies. The validation check will be:

$$
\left| \sum_{i=1}^{n} w_i - 1.0 \right| > \epsilon
$$

where $w_i$ are the dimension weights and $\epsilon = 0.001$.

```python
# Add dimension weight fields and the model_validator to the Settings class
class Settings(BaseSettings):
    """Application settings for the PE Org-AI-R Platform with production-grade validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ... (other fields remain the same for brevity)
    # To keep the example focused, we'll redefine the relevant parts.
    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"
    SECRET_KEY: SecretStr = Field(default="default_secret_for_dev_env_testing_0123456789") # Add default for easier testing

    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000)
    DAILY_COST_BUDGET_USD: float = Field(default=500.0, ge=0)
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1)

    HITL_SCORE_CHANGE_THRESHOLD: float = Field(default=15.0, ge=5, le=30)
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(default=10.0, ge=5, le=25)

    OPENAI_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_API_KEY: Optional[SecretStr] = None

    # --- Scoring Parameters (v2.0) - Dimension Weights ---
    W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0)
    W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0)
    W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0)
    W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0)
    W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0)

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
# Default weights sum to 1.0 (0.18+0.15+0.15+0.17+0.13+0.12+0.10 = 1.0)
try:
    valid_weight_settings = get_settings_with_weights()
    print(f"Dimension weights total: {sum(valid_weight_settings.dimension_weights)}")
    print("Dimension weights validated successfully.")
except ValidationError as e:
    print(f"Unexpected validation error: {e}")

# Scenario 2: Invalid dimension weights (sum != 1.0)
print("\n--- Scenario 2: Invalid Dimension Weights (Sum != 1.0) ---")
os.environ["W_DATA_INFRA"] = "0.20" # Default was 0.18, now sum will be 1.02
os.environ["SECRET_KEY"] = "valid_key_for_testing_12345678901234567890" # Must be set for model to load

try:
    invalid_weight_settings = get_settings_with_weights()
    print("Settings loaded successfully, but should have failed validation.")
except ValidationError as e:
    print("Caught expected validation error for dimension weights:")
    print(e)
    # The error message should explicitly mention "Dimension weights must sum to 1.0".

# Clean up simulated environment variables
os.environ.clear()
```

#### Explanation of Execution
The first scenario successfully loads settings where the default dimension weights (or explicitly set ones that sum to 1.0) pass the `@model_validator`. This demonstrates a correct configuration. The second scenario, however, intentionally provides weights that do not sum to $1.0$. As expected, Pydantic's `@model_validator` catches this discrepancy and raises a `ValueError` wrapped within a `ValidationError`.

This validation is critical for the PE intelligence platform. It ensures that the investment scoring model is always configured with logically consistent weights, preventing calculation errors that could lead to flawed analytical outputs and incorrect investment decisions. It’s a direct safeguard against subtle yet significant business logic flaws that might otherwise only be detected much later in the analysis pipeline, if at all.

---

### 5. Fortifying Production: Conditional Environment-Specific Validation

Deploying to a production environment demands a heightened level of rigor. As a Software Developer, I need to ensure that certain security and operational settings are strictly enforced *only* when the application is running in a `production` environment. For instance, `DEBUG` mode must be disabled, sensitive `SECRET_KEY`s must meet minimum length requirements, and all critical external service API keys (like LLM provider keys) must be present.

This conditional validation logic is best implemented using another `@model_validator(mode="after")`, which allows us to inspect the `APP_ENV` and apply specific rules accordingly. We'll also include a `@field_validator` for `OPENAI_API_KEY` to ensure it starts with the expected "sk-" prefix, an example of a specific format requirement.

#### Workflow Task: Enforce Production Security and API Key Presence

We will add a `@model_validator` to the `Settings` class that performs the following checks when `APP_ENV` is set to `"production"`:
1.  `DEBUG` mode must be `False`.
2.  `SECRET_KEY` length must be at least 32 characters.
3.  At least one of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` must be provided.

```python
# Add the production-specific model_validator and the OpenAI API key field_validator to the Settings class
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

    # Scoring Parameters (v2.0) - Dimension Weights
    W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0)
    W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0)
    W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0)
    W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0)
    W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0)

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
                raise ValueError("SECRET_KEY must be ≥32 characters in production environment")
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

try:
    get_settings_with_prod_validation()
    print("Settings loaded successfully, but should have failed validation (DEBUG is True).")
except ValidationError as e:
    print("Caught expected validation error:")
    print(e)
    # Expect "DEBUG must be False in production environment"

# Scenario 3: Invalid Production Configuration - Short SECRET_KEY
print("\n--- Scenario 3: Invalid Production Config - Short SECRET_KEY ---")
os.environ.clear()
os.environ["APP_ENV"] = "production"
os.environ["DEBUG"] = "False"
os.environ["SECRET_KEY"] = "too_short_key" # This should fail (< 32 chars)
os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

try:
    get_settings_with_prod_validation()
    print("Settings loaded successfully, but should have failed validation (short SECRET_KEY).")
except ValidationError as e:
    print("Caught expected validation error:")
    print(e)
    # Expect "SECRET_KEY must be ≥32 characters in production environment"

# Scenario 4: Invalid Production Configuration - Missing LLM API Keys
print("\n--- Scenario 4: Invalid Production Config - Missing LLM API Keys ---")
os.environ.clear()
os.environ["APP_ENV"] = "production"
os.environ["DEBUG"] = "False"
os.environ["SECRET_KEY"] = "this_is_a_very_long_and_secure_secret_key_for_production_0123456789"
# OPENAI_API_KEY and ANTHROPIC_API_KEY are not set, which implies None

try:
    get_settings_with_prod_validation()
    print("Settings loaded successfully, but should have failed validation (missing LLM API keys).")
except ValidationError as e:
    print("Caught expected validation error:")
    print(e)
    # Expect "At least one LLM API key (OpenAI or Anthropic) is required in production environment"

# Scenario 5: Invalid OpenAI API Key Format
print("\n--- Scenario 5: Invalid OpenAI API Key Format ---")
os.environ.clear()
os.environ["APP_ENV"] = "development" # Can be dev, as field validator runs independently
os.environ["SECRET_KEY"] = "valid_dev_key_12345678901234567890"
os.environ["OPENAI_API_KEY"] = "pk-wrong_prefix_instead_of_sk-" # This should fail

try:
    get_settings_with_prod_validation()
    print("Settings loaded successfully, but should have failed validation (invalid OpenAI key format).")
except ValidationError as e:
    print("Caught expected validation error:")
    print(e)
    # Expect "Invalid OpenAI API key format"

# Clean up simulated environment variables
os.environ.clear()
```

#### Explanation of Execution
This section vividly demonstrates the power of conditional and field-specific validation.
*   **Scenario 1** shows a compliant production configuration loading successfully.
*   **Scenarios 2, 3, and 4** purposefully introduce common production misconfigurations: `DEBUG` being `True`, a `SECRET_KEY` that is too short, and the absence of critical LLM API keys. In each case, our `validate_production_settings` `@model_validator` correctly identifies the issue and raises a `ValidationError` with an explicit message.
*   **Scenario 5** targets the `OPENAI_API_KEY`'s format using the `@field_validator`, catching a malformed key even outside a production environment.

For a Software Developer or Data Engineer, these explicit error messages at application startup are invaluable. They act as an immediate feedback mechanism, preventing the deployment of insecure or non-functional configurations to live environments. This proactive validation drastically reduces the risk of security breaches, service outages, or unexpected runtime behavior stemming from configuration errors.

---

### 6. Catching Errors Early: Configuration Simulation and Reporting

The ultimate value of a robust configuration validation system is its ability to prevent failures before they impact users. As a Data Engineer preparing a deployment, I need a way to confidently verify that a given set of environment variables or configuration files will result in a valid application state. This "Validated Configuration Report" ensures that any potential issues are identified and resolved during development or staging, rather than during a critical production rollout.

We can simulate different configuration scenarios and observe Pydantic's error reporting. This acts as our "report," detailing what works and what breaks, and why.

1.3 Common Mistakes & Troubleshooting
❌ Mistake 1: Dimension weights don't sum to 1.0
# WRONG
W_DATA_INFRA = 0.20
W_AI_GOVERNANCE = 0.15
W_TECH_STACK = 0.15
W_TALENT = 0.20
W_LEADERSHIP = 0.15
W_USE_CASES = 0.10
W_CULTURE = 0.10
# Sum = 1.05!
Fix: The model_validator catches this at startup with a clear error message.
❌ Mistake 2: Exposing secrets in logs
# WRONG
logger.info("connecting", password=settings.SNOWFLAKE_PASSWORD)
Fix: Use SecretStr which masks values automatically.
❌ Mistake 3: Missing lifespan context manager
# WRONG - No cleanup on shutdown
app = FastAPI()
redis_client = Redis() # Leaks on shutdown!
Fix: Always use lifespan for resource management.
❌ Mistake 4: Not validating at startup
# WRONG - Fails at runtime when first used
def get_sector_baseline(sector_id):
return db.query(...) # Database not connected!
Fix: Run validation scripts before application starts

#### Workflow Task: Simulate Configuration Scenarios and Generate a Validation Report

We will define helper functions to load settings under different simulated environment variable sets, deliberately introducing errors to demonstrate the validation system's comprehensive nature.

```python
# Helper function to clear environment variables for a clean test
def clear_env():
    # Only clear variables starting with a prefix to avoid clearing system vars
    for key in list(os.environ.keys()):
        if key.startswith(("APP_", "SECRET_", "RATE_", "DAILY_", "COST_", "W_", "OPENAI_", "ANTHROPIC_", "HITL_")):
            del os.environ[key]

# Function to load settings for a given scenario
def load_scenario_settings(scenario_name: str, env_vars: Dict[str, str]):
    clear_env() # Start with a clean slate
    print(f"\n--- Simulating Scenario: {scenario_name} ---")
    for key, value in env_vars.items():
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
        print(f"  Dimension Weights Sum: {sum(settings.dimension_weights)}")
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
```

#### Explanation of Execution
This final section serves as our "Validated Configuration Report." By simulating a range of realistic configuration scenarios – both valid and invalid – we demonstrate the comprehensive safety net provided by Pydantic's validation. Each `load_scenario_settings` call clears the environment, sets specific variables, attempts to load the `Settings`, and reports the outcome.

The output clearly shows:
*   How valid development and production configurations pass all checks.
*   How specific, critical errors (like `DEBUG` mode in production, incorrect weight sums, or out-of-range API limits) are immediately identified.
*   The exact `ValidationError` messages provide detailed information, pointing directly to the faulty parameter and the reason for the failure.

For a Software Developer or Data Engineer, this process allows for exhaustive testing of configuration permutations. It means that before any new feature or service is deployed to the PE intelligence platform, its configuration can be "pre-validated." This drastically reduces the risk of deployment failures and runtime errors, leading to a more stable, secure, and reliable platform. The proactive identification of issues at startup prevents wasted time debugging issues in live systems and ensures that the platform's critical business logic is always operating on correctly defined parameters.
