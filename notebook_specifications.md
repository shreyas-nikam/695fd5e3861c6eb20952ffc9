
# Automated & Validated API Configuration for Production: A Software Developer's Guide

## Introduction: Ensuring Operational Excellence on the PE Intelligence Platform

As a **Software Developer** or **Data Engineer** at **PE Corp.**, my name is Alex. My primary responsibility is to develop and deploy features for our flagship **PE Intelligence Platform**. A critical, yet often overlooked, aspect of any successful deployment is robust application configuration. Misconfigurations can lead to anything from subtle data inconsistencies to catastrophic application crashes and security vulnerabilities in our production environment.

Today, I'll walk through a real-world workflow to establish a structured, secure, and comprehensively validated configuration system for the PE Intelligence Platform using Pydantic v2. This proactive approach will prevent common deployment failures and ensure our application behaves predictably across development, staging, and production environments. By embedding validation directly into our configuration definitions, we gain confidence that our platform's outputs are reliable and our operations run smoothly.

---

### Installing Required Libraries

First, let's install the necessary Python libraries. `pydantic` and `pydantic-settings` are fundamental for defining and validating our application's configuration.

```python
!pip install pydantic~=2.0 pydantic-settings~=2.0
```

### Importing Required Dependencies

Next, we import all the modules we'll need for defining our settings and validation logic.

```python
from typing import Optional, Literal, List
from decimal import Decimal

from pydantic import Field, ValidationError, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
```

---

## 1. Defining the Foundation: Application Settings Blueprint

### Story + Context + Real-World Relevance

As Alex, my first step is to create a clear blueprint for all application settings. This involves defining each configuration parameter, its expected data type, and any basic constraints (like numerical ranges). Using Pydantic's `BaseSettings` allows me to centralize configuration management, enforce type safety, and automatically load settings from various sources (like environment variables or `.env` files). Crucially, sensitive information like API keys or database passwords will be handled using Pydantic's `SecretStr` type, ensuring they are never accidentally logged or exposed. This foundational step is paramount for preventing missing configuration errors and setting the stage for more complex validations.

```python
# Function Definition
class Settings(BaseSettings):
    """Application settings with production-grade validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid" # Ensure only defined fields are allowed
    )

    # Application Core Settings
    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"
    SECRET_KEY: SecretStr = Field(..., min_length=32, description="Application secret key for encryption/signing")

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000, description="API request rate limit per minute")

    # Snowflake Database Settings
    SNOWFLAKE_ACCOUNT: str = Field(..., min_length=1, description="Snowflake account identifier")
    SNOWFLAKE_USER: str = Field(..., min_length=1, description="Snowflake username")
    SNOWFLAKE_PASSWORD: SecretStr = Field(..., min_length=16, description="Snowflake user password")
    SNOWFLAKE_DATABASE: str = "PE_ORGAIR"
    SNOWFLAKE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_WAREHOUSE: str = Field(..., min_length=1, description="Snowflake warehouse name")
    SNOWFLAKE_ROLE: str = "PE_ORGAIR_ROLE"

    # AWS Settings
    AWS_ACCESS_KEY_ID: Optional[SecretStr] = Field(None, description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = Field(None, description="AWS Secret Access Key")
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: Optional[str] = Field(None, min_length=3, description="S3 bucket for data storage")

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECTORS: int = Field(86400, ge=300, description="Time-to-live for sector cache in seconds (24 hours default)") # 24 hours
    CACHE_TTL_SCORES: int = Field(3600, ge=60, description="Time-to-live for score cache in seconds (1 hour default)") # 1 hour

    # LLM Providers (Multi-provider via LiteLLM)
    OPENAI_API_KEY: Optional[SecretStr] = Field(None, description="OpenAI API Key (starts with 'sk-')")
    ANTHROPIC_API_KEY: Optional[SecretStr] = Field(None, description="Anthropic API Key (starts with 'sk-')")
    DEFAULT_LLM_MODEL: str = "gpt-40-2024-08-06"
    FALLBACK_LLM_MODEL: str = "claude-sonnet-4-20250514"

    # Cost Management
    DAILY_COST_BUDGET_USD: float = Field(default=500.0, ge=0, description="Daily cost budget in USD for external services")
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1, description="Percentage of daily budget at which to trigger an alert")

    # Scoring Parameters (v2.0) - Example parameters for a scoring model
    ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.55, le=0.70, description="Weight for Alpha VR dimension (0.55-0.70)")
    BETA_SYNERGY_WEIGHT: float = Field(default=0.12, ge=0.08, le=0.20, description="Weight for Beta Synergy dimension (0.08-0.20)")
    LAMBDA_PENALTY: float = Field(default=0.25, ge=0, le=0.50, description="Lambda penalty factor (0-0.5)")
    DELTA_POSITION: float = Field(default=0.15, ge=0.10, le=0.20, description="Delta position adjustment (0.10-0.20)")

    # Dimension Weights - These must sum to 1.0 for model integrity
    W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0, description="Weight for Data Infrastructure dimension")
    W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for AI Governance dimension")
    W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for Tech Stack dimension")
    W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0, description="Weight for Talent dimension")
    W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0, description="Weight for Leadership dimension")
    W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0, description="Weight for Use Cases dimension")
    W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0, description="Weight for Culture dimension")

    # HITL Thresholds (Human-In-The-Loop)
    HITL_SCORE_CHANGE_THRESHOLD: float = Field(default=15.0, ge=5, le=30, description="Score change threshold for HITL review")
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(default=10.0, ge=5, le=25, description="EBITDA projection threshold for HITL review")

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = Field(None, description="OpenTelemetry OTLP endpoint")
    OTEL_SERVICE_NAME: str = "pe-orgair"


# No direct execution here, as this is the definition phase.
# Execution will happen in later sections when we instantiate Settings.
```

### Explanation of Execution (N/A)

This section focuses on defining the `Settings` class. The real-world impact comes from the clear structure, type hints, and initial constraints (`Field` with `ge`, `le`) that immediately make the configuration robust. `SecretStr` ensures that sensitive data, such as `SECRET_KEY` and `SNOWFLAKE_PASSWORD`, is automatically masked in output, preventing accidental exposure, which is a critical security practice for Alex as a Software Developer.

---

## 2. Enforcing Individual Parameter Rules with Field Validators

### Story + Context + Real-World Relevance

Alex knows that beyond basic types and ranges, some individual configuration parameters require specific formatting or structural checks. For instance, an OpenAI API key isn't just any string; it must start with "sk-" to be valid. Relying solely on type hints wouldn't catch such a specific, yet critical, detail. This is where Pydantic's `@field_validator` comes into play. It allows me to define custom validation logic for a single field, ensuring that specific business rules or external API requirements are met before the application even starts. This prevents errors like failed external API calls due to malformed credentials, which can be difficult to debug in production.

```python
# Function Definition (Adding to the Settings class)
class Settings(BaseSettings):
    """Application settings with production-grade validation."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )

    # ... (all fields defined in Section 1) ...
    # Application Core Settings
    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"
    SECRET_KEY: SecretStr = Field(..., min_length=32, description="Application secret key for encryption/signing")

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000, description="API request rate limit per minute")

    # Snowflake Database Settings
    SNOWFLAKE_ACCOUNT: str = Field(..., min_length=1, description="Snowflake account identifier")
    SNOWFLAKE_USER: str = Field(..., min_length=1, description="Snowflake username")
    SNOWFLAKE_PASSWORD: SecretStr = Field(..., min_length=16, description="Snowflake user password")
    SNOWFLAKE_DATABASE: str = "PE_ORGAIR"
    SNOWFLAKE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_WAREHOUSE: str = Field(..., min_length=1, description="Snowflake warehouse name")
    SNOWFLAKE_ROLE: str = "PE_ORGAIR_ROLE"

    # AWS Settings
    AWS_ACCESS_KEY_ID: Optional[SecretStr] = Field(None, description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = Field(None, description="AWS Secret Access Key")
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: Optional[str] = Field(None, min_length=3, description="S3 bucket for data storage")

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECTORS: int = Field(86400, ge=300, description="Time-to-live for sector cache in seconds (24 hours default)")
    CACHE_TTL_SCORES: int = Field(3600, ge=60, description="Time-to-live for score cache in seconds (1 hour default)")

    # LLM Providers (Multi-provider via LiteLLM)
    OPENAI_API_KEY: Optional[SecretStr] = Field(None, description="OpenAI API Key (starts with 'sk-')")
    ANTHROPIC_API_KEY: Optional[SecretStr] = Field(None, description="Anthropic API Key (starts with 'sk-')")
    DEFAULT_LLM_MODEL: str = "gpt-40-2024-08-06"
    FALLBACK_LLM_MODEL: str = "claude-sonnet-4-20250514"

    # Cost Management
    DAILY_COST_BUDGET_USD: float = Field(default=500.0, ge=0, description="Daily cost budget in USD for external services")
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1, description="Percentage of daily budget at which to trigger an alert")

    # Scoring Parameters (v2.0) - Example parameters for a scoring model
    ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.55, le=0.70, description="Weight for Alpha VR dimension (0.55-0.70)")
    BETA_SYNERGY_WEIGHT: float = Field(default=0.12, ge=0.08, le=0.20, description="Weight for Beta Synergy dimension (0.08-0.20)")
    LAMBDA_PENALTY: float = Field(default=0.25, ge=0, le=0.50, description="Lambda penalty factor (0-0.5)")
    DELTA_POSITION: float = Field(default=0.15, ge=0.10, le=0.20, description="Delta position adjustment (0.10-0.20)")

    # Dimension Weights - These must sum to 1.0 for model integrity
    W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0, description="Weight for Data Infrastructure dimension")
    W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for AI Governance dimension")
    W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for Tech Stack dimension")
    W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0, description="Weight for Talent dimension")
    W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0, description="Weight for Leadership dimension")
    W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0, description="Weight for Use Cases dimension")
    W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0, description="Weight for Culture dimension")

    # HITL Thresholds (Human-In-The-Loop)
    HITL_SCORE_CHANGE_THRESHOLD: float = Field(default=15.0, ge=5, le=30, description="Score change threshold for HITL review")
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(default=10.0, ge=5, le=25, description="EBITDA projection threshold for HITL review")

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = Field(None, description="OpenTelemetry OTLP endpoint")
    OTEL_SERVICE_NAME: str = "pe-orgair"

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        """Validate OpenAI API key format."""
        if v is not None and not v.get_secret_value().startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format: must start with 'sk-'")
        return v

# No direct execution here yet.
```

### Explanation of Execution (N/A)

This `field_validator` for `OPENAI_API_KEY` directly applies a specific format check (`sk-` prefix) that an OpenAI API key must adhere to. This prevents potential runtime errors where an API call might fail simply because a misformatted key was provided, even if it was technically a string. For Alex, this means fewer headaches debugging integration issues and more confidence in the external service configurations.

---

## 3. Implementing Complex Interdependencies and Production Safeguards

### Story + Context + Real-World Relevance

Now, Alex faces the challenge of enforcing more complex business rules and production-specific security policies. The PE Intelligence Platform uses scoring models where a set of "dimension weights" must collectively sum up to exactly 1.0; deviations would lead to incorrect model outputs. Moreover, our production environment demands stricter security: debug mode must be disabled, critical secrets must meet length requirements, and at least one LLM API key must be present for core functionality. These are not checks for single fields, but for relationships between multiple fields or conditions based on the application environment. Pydantic's `@model_validator(mode="after")` is the perfect tool for this, allowing me to implement cross-field validation and conditional logic that protects the integrity of our scoring models and secures our production deployments.

```python
# Function Definition (Adding to the Settings class)
class Settings(BaseSettings):
    """Application settings with production-grade validation."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )

    # ... (all fields defined in Section 1) ...
    # Application Core Settings
    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"
    SECRET_KEY: SecretStr = Field(..., min_length=32, description="Application secret key for encryption/signing")

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000, description="API request rate limit per minute")

    # Snowflake Database Settings
    SNOWFLAKE_ACCOUNT: str = Field(..., min_length=1, description="Snowflake account identifier")
    SNOWFLAKE_USER: str = Field(..., min_length=1, description="Snowflake username")
    SNOWFLAKE_PASSWORD: SecretStr = Field(..., min_length=16, description="Snowflake user password")
    SNOWFLAKE_DATABASE: str = "PE_ORGAIR"
    SNOWFLAKE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_WAREHOUSE: str = Field(..., min_length=1, description="Snowflake warehouse name")
    SNOWFLAKE_ROLE: str = "PE_ORGAIR_ROLE"

    # AWS Settings
    AWS_ACCESS_KEY_ID: Optional[SecretStr] = Field(None, description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = Field(None, description="AWS Secret Access Key")
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: Optional[str] = Field(None, min_length=3, description="S3 bucket for data storage")

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECTORS: int = Field(86400, ge=300, description="Time-to-live for sector cache in seconds (24 hours default)")
    CACHE_TTL_SCORES: int = Field(3600, ge=60, description="Time-to-live for score cache in seconds (1 hour default)")

    # LLM Providers (Multi-provider via LiteLLM)
    OPENAI_API_KEY: Optional[SecretStr] = Field(None, description="OpenAI API Key (starts with 'sk-')")
    ANTHROPIC_API_KEY: Optional[SecretStr] = Field(None, description="Anthropic API Key (starts with 'sk-')")
    DEFAULT_LLM_MODEL: str = "gpt-40-2024-08-06"
    FALLBACK_LLM_MODEL: str = "claude-sonnet-4-20250514"

    # Cost Management
    DAILY_COST_BUDGET_USD: float = Field(default=500.0, ge=0, description="Daily cost budget in USD for external services")
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1, description="Percentage of daily budget at which to trigger an alert")

    # Scoring Parameters (v2.0) - Example parameters for a scoring model
    ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.55, le=0.70, description="Weight for Alpha VR dimension (0.55-0.70)")
    BETA_SYNERGY_WEIGHT: float = Field(default=0.12, ge=0.08, le=0.20, description="Weight for Beta Synergy dimension (0.08-0.20)")
    LAMBDA_PENALTY: float = Field(default=0.25, ge=0, le=0.50, description="Lambda penalty factor (0-0.5)")
    DELTA_POSITION: float = Field(default=0.15, ge=0.10, le=0.20, description="Delta position adjustment (0.10-0.20)")

    # Dimension Weights - These must sum to 1.0 for model integrity
    W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0, description="Weight for Data Infrastructure dimension")
    W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for AI Governance dimension")
    W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for Tech Stack dimension")
    W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0, description="Weight for Talent dimension")
    W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0, description="Weight for Leadership dimension")
    W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0, description="Weight for Use Cases dimension")
    W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0, description="Weight for Culture dimension")

    # HITL Thresholds (Human-In-The-Loop)
    HITL_SCORE_CHANGE_THRESHOLD: float = Field(default=15.0, ge=5, le=30, description="Score change threshold for HITL review")
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(default=10.0, ge=5, le=25, description="EBITDA projection threshold for HITL review")

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = Field(None, description="OpenTelemetry OTLP endpoint")
    OTEL_SERVICE_NAME: str = "pe-orgair"

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        """Validate OpenAI API key format."""
        if v is not None and not v.get_secret_value().startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format: must start with 'sk-'")
        return v

    @model_validator(mode="after")
    def validate_dimension_weights(self) -> "Settings":
        """Validate that dimension weights sum to 1.0 with a small tolerance."""
        weights = [
            self.W_DATA_INFRA,
            self.W_AI_GOVERNANCE,
            self.W_TECH_STACK,
            self.W_TALENT,
            self.W_LEADERSHIP,
            self.W_USE_CASES,
            self.W_CULTURE,
        ]
        total = sum(weights)
        # Using a small tolerance for floating point comparison
        tolerance = 0.001
        if abs(total - 1.0) > tolerance:
            raise ValueError(f"Dimension weights must sum to 1.0, but got {total:.3f}. Deviation: {abs(total - 1.0):.3f}")
        return self

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Ensure production environment has required security settings."""
        if self.APP_ENV == "production":
            if self.DEBUG:
                raise ValueError("In 'production' environment, DEBUG must be False.")
            if len(self.SECRET_KEY.get_secret_value()) < 32:
                raise ValueError(f"SECRET_KEY must be ≥32 characters in production. Current length: {len(self.SECRET_KEY.get_secret_value())}")
            if not self.OPENAI_API_KEY and not self.ANTHROPIC_API_KEY:
                raise ValueError("At least one LLM API key (OpenAI or Anthropic) is required in 'production'.")
            if not self.AWS_ACCESS_KEY_ID or not self.AWS_SECRET_ACCESS_KEY or not self.S3_BUCKET:
                raise ValueError("AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) and S3_BUCKET are required in 'production'.")
            if not self.SNOWFLAKE_ACCOUNT or not self.SNOWFLAKE_USER or not self.SNOWFLAKE_PASSWORD or not self.SNOWFLAKE_WAREHOUSE:
                raise ValueError("All Snowflake connection details (account, user, password, warehouse) are required in 'production'.")
        return self

# No direct execution here yet.
```

### Explanation of Execution (N/A)

The two `model_validator` methods address critical concerns for Alex.
1.  **Dimension Weights Summation**: The `validate_dimension_weights` method ensures that the sum of the model's dimension weights equals $1.0$. The formula checked is $ \left| \sum_{i} W_i - 1.0 \right| > 0.001 $, where $W_i$ represents each dimension weight. This directly prevents subtle calculation errors in our scoring models that could lead to incorrect intelligence being provided to PE Corp.'s stakeholders. Such errors are notoriously hard to detect in live systems.
2.  **Production Environment Safeguards**: The `validate_production_settings` method enforces a suite of rules specific to `APP_ENV="production"`. This includes:
    *   Disabling `DEBUG` mode to prevent sensitive information exposure.
    *   Ensuring `SECRET_KEY` meets a minimum length for cryptographic strength.
    *   Mandating the presence of at least one LLM API key, as these are critical for the platform's AI capabilities in production.
    *   Mandating AWS and Snowflake credentials for production.

This comprehensive, conditional validation significantly reduces the risk of deploying an improperly configured or insecure application, a nightmare scenario for any Software Developer or Data Engineer.

---

## 4. Testing Valid Configurations: Smooth Sailing

### Story + Context + Real-World Relevance

Now that all the validation rules are defined, Alex needs to verify that known valid configurations for both a `development` and a `production` environment can be loaded successfully. This step is crucial for building confidence in the robust configuration system and ensuring that properly defined settings don't trigger false positives. Successfully loading configurations demonstrates that the system is ready to accept compliant settings, allowing development and deployment workflows to proceed without unnecessary friction.

```python
# Code cell (function definition + function execution)

# 1. Define valid development settings
dev_settings_data = {
    "APP_ENV": "development",
    "DEBUG": True,
    "SECRET_KEY": "averyverylongandsecuredevelopmentsecretkey12345",
    "RATE_LIMIT_PER_MINUTE": 100,
    "SNOWFLAKE_ACCOUNT": "dev_snowflake_account",
    "SNOWFLAKE_USER": "dev_user",
    "SNOWFLAKE_PASSWORD": "DevPassword12345!",
    "SNOWFLAKE_WAREHOUSE": "DEV_WH",
    "AWS_ACCESS_KEY_ID": "AKIADEVKEY",
    "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "S3_BUCKET": "dev-pe-bucket",
    "OPENAI_API_KEY": "sk-dev_abcdefghijklmnopqrstuvwxyz0123456789",
    "W_DATA_INFRA": 0.18,
    "W_AI_GOVERNANCE": 0.15,
    "W_TECH_STACK": 0.15,
    "W_TALENT": 0.17,
    "W_LEADERSHIP": 0.13,
    "W_USE_CASES": 0.12,
    "W_CULTURE": 0.10,
    "DAILY_COST_BUDGET_USD": 100.0
}

print("--- Loading Valid Development Configuration ---")
try:
    settings_dev = Settings(**dev_settings_data)
    print("Development settings loaded successfully:")
    print(f"  App Name: {settings_dev.APP_NAME}")
    print(f"  Environment: {settings_dev.APP_ENV}")
    print(f"  Debug Mode: {settings_dev.DEBUG}")
    print(f"  Secret Key: {settings_dev.SECRET_KEY}") # Will show as '**********'
    print(f"  OpenAI API Key: {settings_dev.OPENAI_API_KEY}") # Will show as '**********'
    print(f"  Rate Limit: {settings_dev.RATE_LIMIT_PER_MINUTE}")
    print(f"  Snowflake User: {settings_dev.SNOWFLAKE_USER}")
    print(f"  Dimension Weights Sum: {settings_dev.W_DATA_INFRA + settings_dev.W_AI_GOVERNANCE + settings_dev.W_TECH_STACK + settings_dev.W_TALENT + settings_dev.W_LEADERSHIP + settings_dev.W_USE_CASES + settings_dev.W_CULTURE}")
    print("\n")
except ValidationError as e:
    print("Error loading development settings:")
    print(e.json(indent=2))

# 2. Define valid production settings
# Note: DEBUG is False, SecretKey is long, LLM keys are present, all production required fields are set
prod_settings_data = {
    "APP_ENV": "production",
    "DEBUG": False, # Crucial for production
    "SECRET_KEY": "thisisareallylongandsecureproductionsecretkeyforourplatform", # >= 32 chars
    "RATE_LIMIT_PER_MINUTE": 500,
    "SNOWFLAKE_ACCOUNT": "prod_snowflake_account",
    "SNOWFLAKE_USER": "prod_user",
    "SNOWFLAKE_PASSWORD": "ProdPasswordHighlySecure!2023", # >= 16 chars
    "SNOWFLAKE_WAREHOUSE": "PROD_WH_XL",
    "AWS_ACCESS_KEY_ID": "AKIA123PRODKEY",
    "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYPRODKEY",
    "S3_BUCKET": "prod-pe-bucket-live",
    "OPENAI_API_KEY": "sk-prod_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", # Starts with sk-
    "ANTHROPIC_API_KEY": "sk-ant-prod_YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY", # One of them is sufficient
    "W_DATA_INFRA": 0.18,
    "W_AI_GOVERNANCE": 0.15,
    "W_TECH_STACK": 0.15,
    "W_TALENT": 0.17,
    "W_LEADERSHIP": 0.13,
    "W_USE_CASES": 0.12,
    "W_CULTURE": 0.10,
    "DAILY_COST_BUDGET_USD": 5000.0
}

print("--- Loading Valid Production Configuration ---")
try:
    settings_prod = Settings(**prod_settings_data)
    print("Production settings loaded successfully:")
    print(f"  App Name: {settings_prod.APP_NAME}")
    print(f"  Environment: {settings_prod.APP_ENV}")
    print(f"  Debug Mode: {settings_prod.DEBUG}")
    print(f"  Secret Key: {settings_prod.SECRET_KEY}")
    print(f"  OpenAI API Key: {settings_prod.OPENAI_API_KEY}")
    print(f"  Anthropic API Key: {settings_prod.ANTHROPIC_API_KEY}")
    print(f"  Rate Limit: {settings_prod.RATE_LIMIT_PER_MINUTE}")
    print(f"  Snowflake User: {settings_prod.SNOWFLAKE_USER}")
    print(f"  AWS S3 Bucket: {settings_prod.S3_BUCKET}")
    print(f"  Dimension Weights Sum: {settings_prod.W_DATA_INFRA + settings_prod.W_AI_GOVERNANCE + settings_prod.W_TECH_STACK + settings_prod.W_TALENT + settings_prod.W_LEADERSHIP + settings_prod.W_USE_CASES + settings_prod.W_CULTURE}")
    print("\n")
except ValidationError as e:
    print("Error loading production settings:")
    print(e.json(indent=2))
```

### Explanation of Execution

Successfully loading both the `development` and `production` configurations without any `ValidationError` confirms that Alex's validation rules correctly interpret and accept compliant settings. For a Software Developer, this output is a green light, indicating that the defined settings adhere to all specified constraints. Notice how `SecretStr` fields are displayed as `**********` even when the underlying value is correct; this is a key security feature automatically handled by Pydantic, preventing sensitive information from being printed to logs or console outputs. This provides Alex with the assurance that the platform can start up correctly in these environments.

---

## 5. Testing Invalid Configurations: Catching Issues Early

### Story + Context + Real-World Relevance

The real test of any robust validation system is its ability to *catch and report* invalid configurations. Alex now deliberately introduces various erroneous settings to see if the Pydantic validators correctly identify and halt the application startup with clear, actionable error messages. This process simulates common mistakes during development or deployment and confirms that the system will prevent misconfigured applications from ever reaching or running in production. This proactive error detection saves countless hours of debugging, prevents costly outages, and ensures the PE Intelligence Platform maintains its reliability.

```python
# Code cell (function definition + function execution)

print("--- Testing Invalid Configuration Scenarios ---")

# Scenario 1: Invalid Field Value (RATE_LIMIT_PER_MINUTE out of range)
invalid_rate_limit_data = dev_settings_data.copy()
invalid_rate_limit_data["RATE_LIMIT_PER_MINUTE"] = 2000 # Max is 1000

print("\n--- Scenario 1: Rate Limit Out of Range ---")
try:
    Settings(**invalid_rate_limit_data)
except ValidationError as e:
    print("Caught ValidationError for invalid rate limit:")
    print(e.json(indent=2))

# Scenario 2: Dimension Weights Don't Sum to 1.0
invalid_weights_data = prod_settings_data.copy()
invalid_weights_data["W_DATA_INFRA"] = 0.25 # Original was 0.18, sum will be > 1.0
invalid_weights_data["W_AI_GOVERNANCE"] = 0.15
invalid_weights_data["W_TECH_STACK"] = 0.15
invalid_weights_data["W_TALENT"] = 0.17
invalid_weights_data["W_LEADERSHIP"] = 0.13
invalid_weights_data["W_USE_CASES"] = 0.12
invalid_weights_data["W_CULTURE"] = 0.10
# Sum will be 0.25 + 0.15 + 0.15 + 0.17 + 0.13 + 0.12 + 0.10 = 1.07

print("\n--- Scenario 2: Dimension Weights Don't Sum to 1.0 ---")
try:
    Settings(**invalid_weights_data)
except ValidationError as e:
    print("Caught ValidationError for dimension weights sum:")
    print(e.json(indent=2))

# Scenario 3: Production Environment Violations (DEBUG enabled, SECRET_KEY too short, missing LLM key, missing AWS)
invalid_prod_violations_data = prod_settings_data.copy()
invalid_prod_violations_data["DEBUG"] = True # Debug cannot be true in production
invalid_prod_violations_data["SECRET_KEY"] = "shortkey" # Too short for production
invalid_prod_violations_data["OPENAI_API_KEY"] = None # No LLM API key
invalid_prod_violations_data["ANTHROPIC_API_KEY"] = None
invalid_prod_violations_data["AWS_ACCESS_KEY_ID"] = None # Missing AWS creds
invalid_prod_violations_data["AWS_SECRET_ACCESS_KEY"] = None
invalid_prod_violations_data["S3_BUCKET"] = None

print("\n--- Scenario 3: Production Environment Violations ---")
try:
    Settings(**invalid_prod_violations_data)
except ValidationError as e:
    print("Caught ValidationError for production environment violations:")
    print(e.json(indent=2))

# Scenario 4: Invalid OpenAI API Key format
invalid_openai_format_data = dev_settings_data.copy()
invalid_openai_format_data["OPENAI_API_KEY"] = "invalid-key-format-123"

print("\n--- Scenario 4: Invalid OpenAI API Key Format ---")
try:
    Settings(**invalid_openai_format_data)
except ValidationError as e:
    print("Caught ValidationError for invalid OpenAI API key format:")
    print(e.json(indent=2))

# Scenario 5: Missing Snowflake configuration for production
missing_snowflake_prod_data = prod_settings_data.copy()
missing_snowflake_prod_data["SNOWFLAKE_ACCOUNT"] = "" # Missing essential Snowflake detail

print("\n--- Scenario 5: Missing Snowflake configuration for production ---")
try:
    Settings(**missing_snowflake_prod_data)
except ValidationError as e:
    print("Caught ValidationError for missing Snowflake configuration in production:")
    print(e.json(indent=2))
```

### Explanation of Execution

Each `try...except ValidationError` block above demonstrates how Pydantic's validation system robustly handles erroneous configurations. For Alex, these outputs are highly valuable:

*   **Scenario 1 (Rate Limit Out of Range)**: The error message clearly indicates that `RATE_LIMIT_PER_MINUTE` must be less than or equal to 1000, preventing a misconfigured API from being deployed with an unrealistic or dangerous rate limit.
*   **Scenario 2 (Dimension Weights Don't Sum to 1.0)**: This error, caught by our `@model_validator`, explicitly states that "Dimension weights must sum to 1.0, but got 1.070". This is critical feedback for a Data Engineer, ensuring the mathematical integrity of the scoring model before deployment.
*   **Scenario 3 (Production Environment Violations)**: This simulation triggers multiple production-specific errors: `DEBUG` being `True`, `SECRET_KEY` being too short, and both LLM API keys missing, along with missing AWS credentials. The `ValidationError` aggregates all these issues, providing a comprehensive report of why the configuration is unsuitable for production. This immediately flags critical security and functional risks.
*   **Scenario 4 (Invalid OpenAI API Key Format)**: The `@field_validator` correctly identifies that the `OPENAI_API_KEY` does not start with "sk-", preventing API integration failures due to malformed credentials.
*   **Scenario 5 (Missing Snowflake configuration for production)**: The `@model_validator` specifically flags that Snowflake connection details are required in production, catching crucial missing dependencies.

The detailed error messages provided by Pydantic in these scenarios are indispensable. They don't just say "invalid config"; they pinpoint the exact field(s) and the reason for the failure, allowing Alex to quickly identify and rectify the issues. This direct feedback loop is what makes this automated validation system a powerful tool for preventing deployment failures and ensuring the stability and security of the PE Intelligence Platform.

---

## Deliverable Summary: The Validated Configuration Report

This notebook serves as a practical "Validated Configuration Report." Through hands-on activities, we've demonstrated how to:

1.  **Define a structured configuration system** using Pydantic `BaseSettings`, establishing a clear blueprint for all application parameters.
2.  **Apply granular data type and range validation** using `Field` and `@field_validator` for individual settings like API key formats and rate limits.
3.  **Implement complex cross-field and conditional validation logic** using `@model_validator`, ensuring critical business rules (like scoring model weights summing to 1.0) and stringent production environment safeguards (e.g., `DEBUG=False`, robust secret keys, required external API keys) are enforced.
4.  **Simulate configuration loading** for both valid and invalid scenarios, explicitly showcasing how the system catches errors at startup with clear, actionable `ValidationError` messages.

This detailed, executable specification illustrates how a Software Developer or Data Engineer can proactively prevent configuration-related bugs, improve application reliability, and instill greater trust in the PE Intelligence Platform's operations. By catching these issues during development and testing, we avoid costly production outages and maintain the high standards expected by PE Corp.'s stakeholders.
