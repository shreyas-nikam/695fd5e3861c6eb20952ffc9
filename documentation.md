id: 695fd5e3861c6eb20952ffc9_documentation
summary: Foundation and Platform Setup Documentation
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Building Robust and Secure Configurations with Pydantic

## 1. Introduction: Safeguarding Your PE Intelligence Platform
Duration: 0:10:00

As a **Software Developer** or **Data Engineer** building the Organizational AI Scoring (PE Org-AI-R) platform, ensuring the robustness and security of our application configurations is paramount. Every new feature or data processing service we deploy relies on correct, consistent, and validated settings across different environments – development, staging, and crucially, production. A single misconfigured parameter, such as an incorrect API key, an out-of-bounds budget, or an improperly weighted scoring dimension, can lead to critical application crashes, compromised data integrity, or skewed analytical outcomes that directly impact investment decisions.

This codelab outlines a real-world workflow to implement a highly reliable configuration system using **Pydantic v2**. Our goal is to prevent these costly configuration-related bugs by enforcing strict validation rules, significantly reducing operational overhead and building trust in our platform's outputs. We will walk through defining settings, applying various validation types, and simulating different environmental scenarios to demonstrate how invalid configurations are caught *before* they can cause harm.

<aside class="positive">
This approach minimizes "configuration drift" and ensures that your application behaves predictably across all environments, from local development to production. It's a cornerstone of building reliable and maintainable systems.
</aside>

### Key Objectives:
*   **Remember**: List the components of a FastAPI application and Pydantic validation.
*   **Understand**: Explain why configuration validation prevents runtime errors.
*   **Apply**: Implement a validated configuration system with weight constraints.
*   **Create**: Design a project structure for production PE intelligence platforms.

### The Problem: Unvalidated Configurations
Consider a scenario where your application's scoring model relies on a set of weights for different dimensions. If these weights don't sum to $1.0$, your scoring logic will be fundamentally flawed, leading to incorrect investment recommendations. Without a robust validation system, this error might only be discovered during critical analysis, leading to costly recalculations and loss of trust.

### The Solution: Proactive Pydantic Validation
Pydantic allows us to define our application settings as Python classes with type hints and validation rules. These rules can range from simple type checks to complex cross-field validations and environment-specific constraints. By validating configurations at application startup, we catch errors early, preventing them from propagating into runtime issues.

### High-Level Flow of Configuration Validation

The diagram below illustrates how configuration data flows through the system and is validated at various stages:

```mermaid
graph TD
    A[Streamlit UI Inputs] --> B{Streamlit Session State};
    B --> C[Populate os.environ];
    C --> D{get_settings_with_prod_validation()};
    D -- Pydantic Model Loading --> E[Pydantic Settings Model];
    E -- Field Validation (Types, Ranges) --> F{Model Validators};
    F -- Cross-field Validation (Sum of Weights) --> G{Environment-specific Validation (e.g., Production)};
    G -- Pass --> H[Validated Settings Object];
    H -- Fail --> I[Validation Errors (PydanticValidationError)];
    I --> J[Streamlit Validation Errors Display];
    H --> K[Streamlit Configuration Report];
```

This flow ensures that all user inputs and environmental variables are parsed, typed, and validated against predefined rules before a `Settings` object is considered valid for use by the application.

## 2. Setting Up Your Environment and Understanding `source.py`
Duration: 0:08:00

Before diving into the Streamlit application, let's set up your environment and understand the core Python logic contained in `source.py`. This file is where our Pydantic `Settings` model and validation logic reside.

### 2.1. Project Structure
Create a project directory named `qu_lab_codelab`. Inside it, create two files: `streamlit_app.py` and `source.py`.

```
qu_lab_codelab/
├── streamlit_app.py
└── source.py
```

### 2.2. The `source.py` File
The `source.py` file defines our application's configuration `Settings` using Pydantic. It includes various fields with type hints, default values, and sophisticated validation rules.

<aside class="negative">
The provided `streamlit_app.py` implicitly relies on a `source.py` file with specific Pydantic `Settings` definitions and helper functions. Ensure your `source.py` matches the structure below to avoid `NameError` or `ImportError`.
</aside>

```python
# source.py
import os
from functools import lru_cache
from typing import Dict, List, Any
from pydantic import Field, SecretStr, ValidationError, model_validator, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

#  Helper Functions for Environment Management 

def clear_env():
    """Clears all specific environment variables used by Settings."""
    env_vars_to_clear = [
        "APP_NAME", "APP_VERSION", "APP_ENV", "DEBUG", "LOG_LEVEL", "LOG_FORMAT",
        "SECRET_KEY", "API_V1_PREFIX", "API_V2_PREFIX", "RATE_LIMIT_PER_MINUTE",
        "PARAM_VERSION", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEFAULT_LLM_MODEL",
        "FALLBACK_LLM_MODEL", "DAILY_COST_BUDGET_USD", "COST_ALERT_THRESHOLD_PCT",
        "HITL_SCORE_CHANGE_THRESHOLD", "HITL_EBITDA_PROJECTION_THRESHOLD",
        "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_DATABASE", "SNOWFLAKE_SCHEMA", "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_ROLE", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION", "S3_BUCKET", "REDIS_URL", "CACHE_TTL_SECTORS",
        "CACHE_TTL_SCORES", "ALPHA_VR_WEIGHT", "BETA_SYNERGY_WEIGHT",
        "LAMBDA_PENALTY", "DELTA_POSITION", "W_DATA_INFRA", "W_AI_GOVERNANCE",
        "W_TECH_STACK", "W_TALENT", "W_LEADERSHIP", "W_USE_CASES", "W_CULTURE",
        "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", "OTEL_EXPORTER_OTLP_ENDPOINT",
        "OTEL_SERVICE_NAME"
    ]
    for key in env_vars_to_clear:
        if key in os.environ:
            del os.environ[key]

#  Pydantic Settings Model 

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: str = Field("development", pattern=r"^(development|staging|production)$")
    DEBUG: bool = False
    LOG_LEVEL: str = Field("INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR)$")
    LOG_FORMAT: str = Field("json", pattern=r"^(json|console)$")
    SECRET_KEY: SecretStr = "default_secret_for_dev_env_testing_0123456789"

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    RATE_LIMIT_PER_MINUTE: int = Field(60, ge=1, le=1000)
    PARAM_VERSION: str = Field("v2.0", pattern=r"^(v1\.0|v2\.0)$")

    # LLM Providers
    OPENAI_API_KEY: SecretStr = ""
    ANTHROPIC_API_KEY: SecretStr = ""
    DEFAULT_LLM_MODEL: str = "gpt-40-2024-08-06"
    FALLBACK_LLM_MODEL: str = "claude-sonnet-4-20250514"

    # Cost Management
    DAILY_COST_BUDGET_USD: float = Field(500.0, ge=0.0)
    COST_ALERT_THRESHOLD_PCT: float = Field(0.8, ge=0.0, le=1.0) # 0.0 to 1.0 (0% to 100%)
    HITL_SCORE_CHANGE_THRESHOLD: float = Field(15.0, ge=5.0, le=30.0)
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(10.0, ge=5.0, le=25.0)

    # Database (Snowflake)
    SNOWFLAKE_ACCOUNT: SecretStr = "default_snowflake_account"
    SNOWFLAKE_USER: SecretStr = "default_snowflake_user"
    SNOWFLAKE_PASSWORD: SecretStr = "default_snowflake_password"
    SNOWFLAKE_DATABASE: str = "PE_ORGAIR"
    SNOWFLAKE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_WAREHOUSE: SecretStr = "default_snowflake_warehouse"
    SNOWFLAKE_ROLE: str = "PE_ORGAIR_ROLE"

    # AWS Settings
    AWS_ACCESS_KEY_ID: SecretStr = "default_aws_key_id"
    AWS_SECRET_ACCESS_KEY: SecretStr = "default_aws_secret_key"
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = "default_s3_bucket"

    # Redis Settings
    REDIS_URL: HttpUrl = "redis://localhost:6379/0" # Use HttpUrl for URL validation
    CACHE_TTL_SECTORS: int = Field(86400, ge=1) # 24 hours
    CACHE_TTL_SCORES: int = Field(3600, ge=1) # 1 hour

    # Scoring Parameters (v2.0)
    ALPHA_VR_WEIGHT: float = Field(0.60, ge=0.55, le=0.70)
    BETA_SYNERGY_WEIGHT: float = Field(0.12, ge=0.08, le=0.20)
    LAMBDA_PENALTY: float = Field(0.25, ge=0.0, le=0.50)
    DELTA_POSITION: float = Field(0.15, ge=0.10, le=0.20)

    # Dimension Weights (must sum to 1.0)
    W_DATA_INFRA: float = Field(0.18, ge=0.0, le=1.0)
    W_AI_GOVERNANCE: float = Field(0.15, ge=0.0, le=1.0)
    W_TECH_STACK: float = Field(0.15, ge=0.0, le=1.0)
    W_TALENT: float = Field(0.17, ge=0.0, le=1.0)
    W_LEADERSHIP: float = Field(0.13, ge=0.0, le=1.0)
    W_USE_CASES: float = Field(0.12, ge=0.0, le=1.0)
    W_CULTURE: float = Field(0.10, ge=0.0, le=1.0)

    # Celery Settings
    CELERY_BROKER_URL: HttpUrl = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: HttpUrl = "redis://localhost:6379/2"

    # Observability Settings
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    OTEL_SERVICE_NAME: str = "pe-orgair"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignore extra fields from .env or environment that are not defined in the model
    )

    @model_validator(mode="after")
    def validate_all_settings(self) -> 'Settings':
        # 1. Validate dimension weights sum to 1.0
        dimension_weights_sum = (
            self.W_DATA_INFRA + self.W_AI_GOVERNANCE + self.W_TECH_STACK +
            self.W_TALENT + self.W_LEADERSHIP + self.W_USE_CASES + self.W_CULTURE
        )
        # Using a small tolerance for floating point comparisons
        if abs(dimension_weights_sum - 1.0) > 0.001:
            raise ValueError(f"Dimension weights must sum to approximately 1.0 (current sum: {dimension_weights_sum:.2f}).")

        # 2. Production environment specific validations
        if self.APP_ENV == "production":
            if self.DEBUG:
                raise ValueError("DEBUG mode must be False in production environment.")
            if len(self.SECRET_KEY.get_secret_value()) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters long in production environment.")
            if not self.OPENAI_API_KEY.get_secret_value() and not self.ANTHROPIC_API_KEY.get_secret_value():
                raise ValueError("At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required in production environment.")
            
            # Ensure database and AWS secrets are not default placeholders in production
            if self.SNOWFLAKE_PASSWORD.get_secret_value() == "default_snowflake_password" or \
               self.SNOWFLAKE_ACCOUNT.get_secret_value() == "default_snowflake_account" or \
               self.SNOWFLAKE_USER.get_secret_value() == "default_snowflake_user":
                raise ValueError("Snowflake credentials must be properly configured (not default placeholders) in production environment.")
            
            if self.AWS_SECRET_ACCESS_KEY.get_secret_value() == "default_aws_secret_key" or \
               self.AWS_ACCESS_KEY_ID.get_secret_value() == "default_aws_key_id":
                raise ValueError("AWS credentials must be properly configured (not default placeholders) in production environment.")
            
            if not self.S3_BUCKET or self.S3_BUCKET == "default_s3_bucket":
                raise ValueError("S3_BUCKET must be specified and not a default placeholder in production environment.")

        # 3. OpenAI API Key format validation (if provided)
        if self.OPENAI_API_KEY.get_secret_value() and not self.OPENAI_API_KEY.get_secret_value().startswith("sk-"):
            raise ValueError("OpenAI API Key must start with 'sk-'.")
            
        return self

#  Scenarios for demonstration 
scenarios: Dict[str, Dict[str, Any]] = {
    "Default Development Config": {
        "APP_ENV": "development",
        "DEBUG": True,
        "SECRET_KEY": "dev_secret_0123456789", # Shorter key for dev
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "W_DATA_INFRA": 0.18, "W_AI_GOVERNANCE": 0.15, "W_TECH_STACK": 0.15,
        "W_TALENT": 0.17, "W_LEADERSHIP": 0.13, "W_USE_CASES": 0.12, "W_CULTURE": 0.10,
        "DAILY_COST_BUDGET_USD": 100.0,
    },
    "Valid Production Config": {
        "APP_ENV": "production",
        "DEBUG": False,
        "SECRET_KEY": "a_very_long_and_secure_secret_key_for_production_0123456789",
        "OPENAI_API_KEY": "sk-production_openai_key_abcdefg",
        "ANTHROPIC_API_KEY": "",
        "SNOWFLAKE_ACCOUNT": "prod_snowflake_account",
        "SNOWFLAKE_USER": "prod_user",
        "SNOWFLAKE_PASSWORD": "prod_snowflake_password",
        "AWS_ACCESS_KEY_ID": "PRODACCESSKEY",
        "AWS_SECRET_ACCESS_KEY": "PRODSECRETACCESSKEY",
        "S3_BUCKET": "prod-qu-lab-bucket",
        "W_DATA_INFRA": 0.18, "W_AI_GOVERNANCE": 0.15, "W_TECH_STACK": 0.15,
        "W_TALENT": 0.17, "W_LEADERSHIP": 0.13, "W_USE_CASES": 0.12, "W_CULTURE": 0.10,
        "DAILY_COST_BUDGET_USD": 1000.0,
    },
    "Invalid Production Config - Debug On": {
        "APP_ENV": "production",
        "DEBUG": True, # Invalid for production
        "SECRET_KEY": "a_very_long_and_secure_secret_key_for_production_0123456789",
        "OPENAI_API_KEY": "sk-production_openai_key_abcdefg",
        "ANTHROPIC_API_KEY": "",
        "SNOWFLAKE_ACCOUNT": "prod_snowflake_account",
        "SNOWFLAKE_USER": "prod_user",
        "SNOWFLAKE_PASSWORD": "prod_snowflake_password",
        "AWS_ACCESS_KEY_ID": "PRODACCESSKEY",
        "AWS_SECRET_ACCESS_KEY": "PRODSECRETACCESSKEY",
        "S3_BUCKET": "prod-qu-lab-bucket",
        "W_DATA_INFRA": 0.18, "W_AI_GOVERNANCE": 0.15, "W_TECH_STACK": 0.15,
        "W_TALENT": 0.17, "W_LEADERSHIP": 0.13, "W_USE_CASES": 0.12, "W_CULTURE": 0.10,
        "DAILY_COST_BUDGET_USD": 1000.0,
    },
    "Invalid Production Config - Short Secret": {
        "APP_ENV": "production",
        "DEBUG": False,
        "SECRET_KEY": "short_secret", # Invalid for production (<32 chars)
        "OPENAI_API_KEY": "sk-production_openai_key_abcdefg",
        "ANTHROPIC_API_KEY": "",
        "SNOWFLAKE_ACCOUNT": "prod_snowflake_account",
        "SNOWFLAKE_USER": "prod_user",
        "SNOWFLAKE_PASSWORD": "prod_snowflake_password",
        "AWS_ACCESS_KEY_ID": "PRODACCESSKEY",
        "AWS_SECRET_ACCESS_KEY": "PRODSECRETACCESSKEY",
        "S3_BUCKET": "prod-qu-lab-bucket",
        "W_DATA_INFRA": 0.18, "W_AI_GOVERNANCE": 0.15, "W_TECH_STACK": 0.15,
        "W_TALENT": 0.17, "W_LEADERSHIP": 0.13, "W_USE_CASES": 0.12, "W_CULTURE": 0.10,
        "DAILY_COST_BUDGET_USD": 1000.0,
    },
    "Invalid Production Config - Missing LLM Key": {
        "APP_ENV": "production",
        "DEBUG": False,
        "SECRET_KEY": "a_very_long_and_secure_secret_key_for_production_0123456789",
        "OPENAI_API_KEY": "", # Invalid for production (no LLM key)
        "ANTHROPIC_API_KEY": "", # Invalid for production (no LLM key)
        "SNOWFLAKE_ACCOUNT": "prod_snowflake_account",
        "SNOWFLAKE_USER": "prod_user",
        "SNOWFLAKE_PASSWORD": "prod_snowflake_password",
        "AWS_ACCESS_KEY_ID": "PRODACCESSKEY",
        "AWS_SECRET_ACCESS_KEY": "PRODSECRETACCESSKEY",
        "S3_BUCKET": "prod-qu-lab-bucket",
        "W_DATA_INFRA": 0.18, "W_AI_GOVERNANCE": 0.15, "W_TECH_STACK": 0.15,
        "W_TALENT": 0.17, "W_LEADERSHIP": 0.13, "W_USE_CASES": 0.12, "W_CULTURE": 0.10,
        "DAILY_COST_BUDGET_USD": 1000.0,
    },
    "Invalid Dimension Weights": {
        "APP_ENV": "development",
        "DEBUG": True,
        "SECRET_KEY": "dev_secret_0123456789",
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "W_DATA_INFRA": 0.20, "W_AI_GOVERNANCE": 0.15, "W_TECH_STACK": 0.15,
        "W_TALENT": 0.20, "W_LEADERSHIP": 0.15, "W_USE_CASES": 0.10, "W_CULTURE": 0.10, # Sums to 1.05
        "DAILY_COST_BUDGET_USD": 100.0,
    },
    "Invalid OpenAI Key Format": {
        "APP_ENV": "development",
        "DEBUG": True,
        "SECRET_KEY": "dev_secret_0123456789",
        "OPENAI_API_KEY": "pk-wrong_format", # Does not start with sk-
        "ANTHROPIC_API_KEY": "",
        "W_DATA_INFRA": 0.18, "W_AI_GOVERNANCE": 0.15, "W_TECH_STACK": 0.15,
        "W_TALENT": 0.17, "W_LEADERSHIP": 0.13, "W_USE_CASES": 0.12, "W_CULTURE": 0.10,
        "DAILY_COST_BUDGET_USD": 100.0,
    },
    "Invalid Cost Budget": {
        "APP_ENV": "development",
        "DEBUG": True,
        "SECRET_KEY": "dev_secret_0123456789",
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "W_DATA_INFRA": 0.18, "W_AI_GOVERNANCE": 0.15, "W_TECH_STACK": 0.15,
        "W_TALENT": 0.17, "W_LEADERSHIP": 0.13, "W_USE_CASES": 0.12, "W_CULTURE": 0.10,
        "DAILY_COST_BUDGET_USD": -10.0, # Invalid, must be >= 0
    }
}

@lru_cache()
def get_settings_with_prod_validation():
    """Caches settings object for performance and ensures production validation.
    This function simulates how a FastAPI app might load settings.
    """
    return Settings()

```

### 2.3. Installing Dependencies
Install the required Python packages using pip:

```console
pip install streamlit pydantic pydantic-settings
```

### 2.4. Running the Streamlit Application
Save the provided `streamlit_app.py` content into your `streamlit_app.py` file.
Then, run the application from your terminal:

```console
streamlit run streamlit_app.py
```

This will open the application in your web browser, allowing you to interact with the configuration settings.

## 3. Exploring General Application Settings
Duration: 0:07:00

The first page you'll see is "Introduction." Navigate to **"Configure Application Settings"** using the sidebar.

This section focuses on the fundamental settings of your application, demonstrating basic Pydantic features like type enforcement and `SecretStr` for sensitive data.

### 3.1. Initial Setup: Environment and Dependencies

As a Software Developer, your first step in configuring a new service for the PE intelligence platform is to define its fundamental settings. These include basic application metadata, environment specification, logging preferences, and crucial sensitive data like secret keys. Using Pydantic's `BaseSettings` and `SettingsConfigDict` allows us to define these in a structured, type-hinted manner, automatically loading from environment variables or `.env` files.

<aside class="positive">
Pydantic's `BaseSettings` automatically reads environment variables matching your field names (e.g., `APP_NAME` from `os.environ["APP_NAME"]`), making it easy to manage configurations across different deployment environments.
</aside>

#### Workflow Task: Define Base Application Settings

1.  **Application Name and Version**: Standard string fields.
2.  **Application Environment (`APP_ENV`)**: This field is controlled by the sidebar radio buttons (`development`, `staging`, `production`). Notice how the info box updates based on your selection. In `source.py`, this field uses `Field(pattern=...)` to ensure only specific string values are accepted.
3.  **Debug Mode (`DEBUG`)**: A boolean field. If you try to set `DEBUG` to `True` while `APP_ENV` is `production` and validate, you'll encounter a validation error.
4.  **Log Level and Format**: String fields with restricted choices (e.g., `INFO`, `json`) using `Field(pattern=...)` in `source.py`.
5.  **Secret Key (`SECRET_KEY`)**: This is a crucial field. It uses Pydantic's `SecretStr` type.

    *   When you input a value into `SECRET_KEY`, observe its behavior in the `Validated Configuration Report`. `SecretStr` automatically masks the actual value when serialized (e.g., to JSON or when `str()` is called on it), preventing accidental logging or exposure.
    *   In a `production` environment, there's an additional validation rule requiring `SECRET_KEY` to be at least 32 characters long.

<aside class="positive">
Using `SecretStr` for sensitive credentials like API keys or database passwords is a best practice. It prevents these values from being accidentally printed to logs or included in crash reports, significantly improving your application's security posture.
</aside>

#### Activity:
1.  Navigate to "Configure Application Settings".
2.  Change `APP_NAME` and `APP_VERSION`.
3.  Observe the `APP_ENV` automatically updating if you change it from the sidebar.
4.  Enter a short string (e.g., "mysecret") for `SECRET_KEY`.
5.  Click "Validate Configuration" in the sidebar. Note if any errors appear related to `SECRET_KEY` (especially if `APP_ENV` is `production`).
6.  Go to the "Validated Configuration Report" page. Observe how `SECRET_KEY` is displayed (it will be masked).

## 4. Implementing Field-Level Validation (Cost Management)
Duration: 0:08:00

This step focuses on enforcing numerical range constraints for critical operational parameters, a common requirement for preventing misconfigurations.

### 4.1. Ensuring Operational Integrity: Field-Level Validation

Operational parameters like API rate limits, daily cost budgets, and alert thresholds are critical for the stability and cost-effectiveness of our PE intelligence platform. As a Data Engineer, you need to ensure these values are always within sensible, predefined ranges to prevent system overload, budget overruns, or ineffective alerting. Pydantic's `Field` with `ge` (greater than or equal to) and `le` (less than or equal to) arguments allows us to enforce these constraints directly within the configuration definition.

#### Workflow Task: Validate Operational Parameters with Range Constraints

In the `source.py` file, the `Settings` class defines several fields with range constraints using `pydantic.Field`:

```python
# From source.py
class Settings(BaseSettings):
    # ... other fields ...
    RATE_LIMIT_PER_MINUTE: int = Field(60, ge=1, le=1000)
    DAILY_COST_BUDGET_USD: float = Field(500.0, ge=0.0)
    COST_ALERT_THRESHOLD_PCT: float = Field(0.8, ge=0.0, le=1.0) # 0.0 to 1.0 (0% to 100%)
    HITL_SCORE_CHANGE_THRESHOLD: float = Field(15.0, ge=5.0, le=30.0)
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(10.0, ge=5.0, le=25.0)
    # ... other fields ...
```

*   `RATE_LIMIT_PER_MINUTE` must be between 1 and 1000.
*   `DAILY_COST_BUDGET_USD` must be non-negative.
*   `COST_ALERT_THRESHOLD_PCT` must be a percentage between 0.0 and 1.0.
*   `HITL_SCORE_CHANGE_THRESHOLD` and `HITL_EBITDA_PROJECTION_THRESHOLD` have specific bounds to reflect business rules.

These `Field` constraints are applied during the initial parsing and validation of the `Settings` model. If an input value falls outside these ranges, Pydantic immediately raises a `ValidationError`.

#### Activity:
1.  Navigate to "Configure Application Settings" and open the "Cost Management" expander.
2.  Set the `DAILY_COST_BUDGET_USD` to a negative value, e.g., `-10.0`.
3.  Click "Validate Configuration" in the sidebar.
4.  Observe the error message that appears below the input field and in the "Validated Configuration Report".
5.  Set `COST_ALERT_THRESHOLD_PCT` to a value greater than 1.0 (e.g., 1.5) or less than 0.0 (e.g., -0.1).
6.  Click "Validate Configuration" and observe the error.
7.  Experiment with `RATE_LIMIT_PER_MINUTE` by entering values outside the 1-1000 range.
8.  Try loading the "Invalid Cost Budget" scenario using the sidebar to quickly see an example of this validation in action.

## 5. Cross-Field Validation for Scoring Weights
Duration: 0:12:00

This step demonstrates a more advanced validation technique: validating relationships *between* multiple fields using Pydantic's `@model_validator`. This is crucial for enforcing complex business logic.

### 5.1. Implementing Business Logic: Cross-Field Validation for Scoring Weights

A core component of the PE intelligence platform is its investment scoring model, which relies on various dimensions (e.g., data infrastructure, AI governance, talent). The relative importance of these dimensions is defined by a set of weights. A critical business rule mandates that these **dimension weights must sum up to exactly 1.0** to ensure a coherent and balanced scoring mechanism. Deviations from this sum would lead to skewed, unreliable scores and potentially poor investment recommendations.

As a Data Engineer, you need to implement a robust check to enforce this rule. Pydantic's `@model_validator(mode="after")` is perfect for this, as it allows us to perform validation logic that involves multiple fields *after* individual field validations have passed.

#### Workflow Task: Validate Dimension Weights Sum to 1.0

In `source.py`, within the `Settings` class, a `model_validator` is defined to perform this check:

```python
# From source.py
class Settings(BaseSettings):
    # ... other fields ...
    W_DATA_INFRA: float = Field(0.18, ge=0.0, le=1.0)
    W_AI_GOVERNANCE: float = Field(0.15, ge=0.0, le=1.0)
    # ... (other W_ fields) ...
    W_CULTURE: float = Field(0.10, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_all_settings(self) -> 'Settings':
        # 1. Validate dimension weights sum to 1.0
        dimension_weights_sum = (
            self.W_DATA_INFRA + self.W_AI_GOVERNANCE + self.W_TECH_STACK +
            self.W_TALENT + self.W_LEADERSHIP + self.W_USE_CASES + self.W_CULTURE
        )
        # Using a small tolerance for floating point comparisons
        if abs(dimension_weights_sum - 1.0) > 0.001:
            raise ValueError(f"Dimension weights must sum to approximately 1.0 (current sum: {dimension_weights_sum:.2f}).")
        # ... (other validations) ...
        return self
```

We will define new fields for dimension weights and then add a `@model_validator` to ensure their sum is $1.0$. A small tolerance $\epsilon$ is used to account for floating-point inaccuracies. The validation check will be:

$$\left| \sum_{{i=1}}^{{n}} w_i - 1.0 \right| > \epsilon$$

where $w_i$ are the dimension weights and $\epsilon = 0.001$.

#### Activity:
1.  Navigate to "Configure Application Settings" and open the "Dimension Weights" expander.
2.  Observe the "Current Dimension Weights Sum" displayed at the bottom of the expander. By default, with the initial values, it should be `1.00`.
3.  Change one or more weights so that their sum deviates significantly from `1.0`. For example, increase `W_DATA_INFRA` to `0.30` while keeping others the same. The sum will become `1.12`.
4.  Click "Validate Configuration" in the sidebar.
5.  Observe the error message related to `validate_dimension_weights` that appears below the inputs and in the "Validated Configuration Report."
6.  Adjust the weights again so they sum approximately to `1.0` (e.g., set `W_DATA_INFRA` to `0.18`, `W_AI_GOVERNANCE` to `0.15`, `W_TECH_STACK` to `0.15`, `W_TALENT` to `0.17`, `W_LEADERSHIP` to `0.13`, `W_USE_CASES` to `0.12`, `W_CULTURE` to `0.10`). You should see `1.00`.
7.  Click "Validate Configuration" and confirm that no error appears for dimension weights.
8.  Try loading the "Invalid Dimension Weights" scenario from the sidebar to quickly see an example of this validation.

## 6. Environment-Specific and Conditional Validation (Production Readiness)
Duration: 0:15:00

This is a critical step for deploying robust applications. It demonstrates how to apply different validation rules based on the `APP_ENV` setting, ensuring that production environments meet higher security and operational standards.

### 6.1. Fortifying Production: Conditional Environment-Specific Validation

Deploying to a production environment demands a heightened level of rigor. As a Software Developer, you need to ensure that certain security and operational settings are strictly enforced *only* when the application is running in a `production` environment. For instance, `DEBUG` mode must be disabled, sensitive `SECRET_KEY`s must meet minimum length requirements, and all critical external service API keys (like LLM provider keys) must be present. This conditional validation logic is implemented using Pydantic's `@model_validator(mode="after")`.

In `source.py`, the `validate_all_settings` model validator includes checks specifically for `self.APP_ENV == "production"`:

```python
# From source.py
class Settings(BaseSettings):
    # ...
    @model_validator(mode="after")
    def validate_all_settings(self) -> 'Settings':
        # ... (dimension weights validation) ...

        # 2. Production environment specific validations
        if self.APP_ENV == "production":
            if self.DEBUG:
                raise ValueError("DEBUG mode must be False in production environment.")
            if len(self.SECRET_KEY.get_secret_value()) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters long in production environment.")
            if not self.OPENAI_API_KEY.get_secret_value() and not self.ANTHROPIC_API_KEY.get_secret_value():
                raise ValueError("At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required in production environment.")
            
            # Additional checks for production secrets
            if self.SNOWFLAKE_PASSWORD.get_secret_value() == "default_snowflake_password" or \
               self.SNOWFLAKE_ACCOUNT.get_secret_value() == "default_snowflake_account" or \
               self.SNOWFLAKE_USER.get_secret_value() == "default_snowflake_user":
                raise ValueError("Snowflake credentials must be properly configured (not default placeholders) in production environment.")
            
            if self.AWS_SECRET_ACCESS_KEY.get_secret_value() == "default_aws_secret_key" or \
               self.AWS_ACCESS_KEY_ID.get_secret_value() == "default_aws_key_id":
                raise ValueError("AWS credentials must be properly configured (not default placeholders) in production environment.")
            
            if not self.S3_BUCKET or self.S3_BUCKET == "default_s3_bucket":
                raise ValueError("S3_BUCKET must be specified and not a default placeholder in production environment.")

        # 3. OpenAI API Key format validation (if provided)
        if self.OPENAI_API_KEY.get_secret_value() and not self.OPENAI_API_KEY.get_secret_value().startswith("sk-"):
            raise ValueError("OpenAI API Key must start with 'sk-'.")
            
        return self
```

### 6.2. Activity: Simulating Production Scenarios

1.  **Switch to Production Environment**: In the sidebar, select **`production`** for "Select Environment".
2.  **Debug Mode in Production**:
    *   Navigate to "Configure Application Settings" -> "General Application Settings".
    *   Ensure `DEBUG` checkbox is **checked** (`True`).
    *   Click "Validate Configuration". Observe the error: "DEBUG mode must be False in production environment."
    *   Uncheck `DEBUG` and re-validate.
3.  **Short Secret Key in Production**:
    *   With `APP_ENV` as `production`, set `SECRET_KEY` to something short like `"mysecretprod"`.
    *   Click "Validate Configuration". Observe the error: "SECRET_KEY must be at least 32 characters long in production environment."
    *   Set a longer key (e.g., "a_very_long_and_secure_secret_key_for_production_0123456789").
4.  **Missing LLM API Keys in Production**:
    *   Ensure both `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` are empty strings in the "LLM Providers" section.
    *   Click "Validate Configuration". Observe the error: "At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required in production environment."
    *   Provide a valid OpenAI API key (must start with `sk-`, e.g., "sk-example_prod_key_12345") or Anthropic key.
5.  **Invalid OpenAI Key Format**:
    *   Enter an OpenAI API key that does not start with `sk-` (e.g., "pk-invalidkey").
    *   Click "Validate Configuration". Observe the error: "OpenAI API Key must start with 'sk-'."
6.  **Using Scenario Presets**: The "Scenario Presets" in the sidebar are designed to quickly demonstrate these validations:
    *   Select "Invalid Production Config - Debug On" and click "Load Scenario". Then "Validate Configuration".
    *   Select "Invalid Production Config - Short Secret" and click "Load Scenario". Then "Validate Configuration".
    *   Select "Invalid Production Config - Missing LLM Key" and click "Load Scenario". Then "Validate Configuration".
    *   Select "Valid Production Config" and click "Load Scenario". Then "Validate Configuration". This should pass all checks.

## 7. Catching Errors Early: Configuration Simulation and Reporting
Duration: 0:10:00

This step brings together all the validation mechanisms and demonstrates the final report, emphasizing its role in a development and deployment workflow.

### 7.1. Configuration Simulation and Reporting

The ultimate value of a robust configuration validation system is its ability to prevent failures before they impact users. As a Data Engineer preparing a deployment, you need a way to confidently verify that a given set of environment variables or configuration files will result in a valid application state. This "Validated Configuration Report" ensures that any potential issues are identified and resolved during development or staging, rather than during a critical production rollout.

The Streamlit application provides a dedicated page, "Validated Configuration Report," to display the outcome of the Pydantic validation.

### 7.2. Understanding the Report

1.  **Overall Validation Status**: Clearly indicates "Valid" or "Invalid" with a prominent emoji.
2.  **Validation Errors**: If the configuration is invalid, a detailed list of errors from Pydantic is displayed. Each error points to the specific field or model validator that failed.
3.  **Current Settings**: For a valid configuration, the report displays the fully validated `Settings` object in JSON format. This is extremely useful for verifying that values were parsed correctly, defaults were applied, and secrets are masked.
4.  **Critical Validation Rules Applied**: This section summarizes the key validation rules that are active in the system, providing a quick reference for developers and reviewers.

#### The `get_settings_with_prod_validation` Function

In `source.py`, the `get_settings_with_prod_validation` function (decorated with `@lru_cache()`) simulates how an actual application (like a FastAPI app) would load its settings. The `lru_cache` ensures that the `Settings` object is initialized and validated only once, optimizing performance and guaranteeing that validation happens early in the application's lifecycle.

```python
# From source.py
@lru_cache()
def get_settings_with_prod_validation():
    """Caches settings object for performance and ensures production validation.
    This function simulates how a FastAPI app might load settings.
    """
    return Settings()
```

<aside class="positive">
Integrating configuration validation as part of your application's startup process (e.g., in a FastAPI `lifespan` event) is a powerful way to catch configuration issues before your service starts handling requests.
</aside>

### 7.3. Common Mistakes & Troubleshooting

The "Validated Configuration Report" page also includes a "Common Mistakes & Troubleshooting" section. This highlights real-world configuration pitfalls that Pydantic helps you avoid:

*   **Dimension weights don't sum to 1.0**: Caught by `@model_validator`.
*   **Exposing secrets in logs**: Prevented by `SecretStr`.
*   **Missing lifespan context manager**: While not directly Pydantic's role, `get_settings_with_prod_validation` demonstrates the concept of centralized resource/settings initialization.
*   **Not validating at startup**: The very problem Pydantic validation aims to solve by forcing checks at the `Settings()` instantiation.

#### Activity:
1.  Go to the "Validated Configuration Report" page.
2.  Use the "Load Scenario" feature in the sidebar to load various "Invalid" scenarios (e.g., "Invalid Dimension Weights", "Invalid Production Config - Short Secret").
3.  After loading each, click "Validate Configuration" and observe the detailed errors in the report. Note how the errors specifically mention the field or validator that failed.
4.  Load the "Valid Production Config" scenario and click "Validate Configuration".
5.  Observe the successful validation report and the JSON representation of the `Settings` object, noting how `SecretStr` values are masked.

## 8. Conclusion and Next Steps
Duration: 0:05:00

Congratulations! You've successfully navigated the core functionalities of the QuLab configuration system, implementing and testing robust validation mechanisms using Pydantic v2.

### 8.1. Summary of Learnings:

*   **Pydantic Fundamentals**: You've seen how `BaseSettings`, type hints, and default values create a structured configuration.
*   **Secure Handling of Secrets**: The importance and implementation of `SecretStr` for sensitive data.
*   **Field-Level Constraints**: Using `pydantic.Field` with `ge`, `le`, and `pattern` to enforce specific ranges and formats for individual parameters.
*   **Cross-Field Business Logic**: Leveraging `@model_validator(mode="after")` to validate relationships between multiple fields (e.g., dimension weights summing to 1.0).
*   **Environment-Specific Validation**: Implementing conditional checks based on the `APP_ENV` to enforce stricter rules for production environments.
*   **Early Error Detection**: Understanding how a comprehensive validation system catches errors at startup, preventing runtime failures and improving application reliability.
*   **Interactive Testing**: Utilizing a Streamlit application to interactively test and visualize configuration validation outcomes.

This codelab provides a solid foundation for building highly reliable and secure configuration systems for any Python application, especially critical platforms like the PE intelligence platform.

### 8.2. Further Exploration:

*   **Custom Validators**: For even more complex validation logic, explore Pydantic's `@field_validator` for single-field validation or custom types.
*   **Pydantic Aliases**: Learn how to use field aliases to map environment variables with different naming conventions (e.g., `MY_APP_API_KEY` to `api_key`).
*   **Dynamic Settings Loading**: Explore strategies for loading settings from multiple sources (e.g., environment variables, `.env` files, configuration management tools like HashiCorp Vault) and how Pydantic handles precedence.
*   **Integration with FastAPI**: Implement a `lifespan` event in a FastAPI application to load and validate settings at startup, ensuring your API always runs with a verified configuration.
*   **Automated Testing**: Write unit and integration tests for your `Settings` class and its validators to ensure configuration changes don't introduce regressions.

<aside class="positive">
By internalizing these practices, you transform configuration management from a potential source of bugs into a powerful tool for ensuring application quality and security.
</aside>

Thank you for completing this codelab!
