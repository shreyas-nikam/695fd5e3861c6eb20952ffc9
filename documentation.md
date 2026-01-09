id: 695fd5e3861c6eb20952ffc9_documentation
summary: Foundation and Platform Setup Documentation
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Building Robust Configurations with Pydantic v2

## Introduction: Safeguarding the PE Intelligence Platform
Duration: 0:05

As a **Software Developer** building the Organizational AIR Scoring platform, ensuring the robustness and security of our application configurations is paramount. Every new feature or data processing service we deploy relies on correct, consistent, and validated settings across different environments – development, staging, and crucially, production. A single misconfigured parameter, such as an incorrect API key, an out-of-bounds budget, or an improperly weighted scoring dimension, can lead to critical application crashes, compromised data integrity, or skewed analytical outcomes that directly impact investment decisions.

This codelab outlines a real-world workflow to implement a highly reliable configuration system using Pydantic v2. Our goal is to prevent these costly configuration-related bugs by enforcing strict validation rules at application startup, significantly reducing operational overhead and building trust in our platform's outputs. We will walk through defining settings, applying various validation types, and simulating different environmental scenarios to demonstrate how invalid configurations are caught *before* they can cause harm.

<aside class="positive">
<b>Why Pydantic v2?</b> Pydantic offers a powerful, Pythonic way to define data models and validate data. With Pydantic v2, it's even faster and more flexible, especially when combined with `pydantic-settings` for managing application configurations from environment variables, `.env` files, and more. It helps enforce type hints, provides detailed validation errors, and allows for custom validation logic, making it ideal for robust application setup.
</aside>

## 1. Initial Setup: Core Application Configuration
Duration: 0:10

Before we dive into defining and validating our application settings, let's ensure our environment has all the necessary tools. We'll specifically need `pydantic` and `pydantic-settings` for robust configuration management.

```console
pip install pydantic==2.* pydantic-settings==2.*
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

### Setting the Stage: Define Base Application Settings

As a Software Developer, my first step in configuring a new service for the PE intelligence platform is to define its fundamental settings. These include basic application metadata, environment specification, logging preferences, and crucial sensitive data like secret keys. Using Pydantic's `BaseSettings` and `SettingsConfigDict` allows us to define these in a structured, type-hinted manner, automatically loading from environment variables or `.env` files.

For sensitive information, like the `SECRET_KEY`, we employ Pydantic's `SecretStr` type. This ensures that the value is never accidentally logged or exposed, enhancing the security posture of our application.

Below is an illustrative representation of our `Settings` class, which serves as the single source of truth for our application's configuration.

```python
# Illustrative Settings class, typically found in a 'source.py' or 'config.py' file.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore", # Allow additional env vars not explicitly defined
        env_prefix="APP_", # Prefix for general app settings
        case_sensitive=True
    )

    APP_NAME: str = "PE Intelligence Platform"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    SECRET_KEY: SecretStr = Field(
        ...,
        description="Secret key for application security, e.g., session management."
    )
    RATE_LIMIT_PER_MINUTE: int = 100
    DAILY_COST_BUDGET_USD: Decimal = Decimal("1000.00")
    COST_ALERT_THRESHOLD_PCT: float = 0.75
    HITL_SCORE_CHANGE_THRESHOLD: float = 20.0
    HITL_EBITDA_PROJECTION_THRESHOLD: float = 15.0

    # Required external service credentials (example for Snowflake, AWS S3)
    SNOWFLAKE_ACCOUNT: str
    SNOWFLAKE_USER: str
    SNOWFLAKE_PASSWORD: SecretStr
    SNOWFLAKE_WAREHOUSE: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: SecretStr
    S3_BUCKET: str

# Helper functions to simulate environment variable loading and settings instantiation
# In the actual Streamlit app, these are handled by functions in 'source.py'
GLOBAL_REQUIRED_ENV_VARS = {
    "SECRET_KEY": "default_secret_for_dev_env_testing_0123456789",
    "SNOWFLAKE_ACCOUNT": "test_account",
    "SNOWFLAKE_USER": "test_user",
    "SNOWFLAKE_PASSWORD": "test_snowflake_password",
    "SNOWFLAKE_WAREHOUSE": "test_warehouse",
    "AWS_ACCESS_KEY_ID": "test_aws_key_id",
    "AWS_SECRET_ACCESS_KEY": "test_aws_secret_key",
    "S3_BUCKET": "test_s3_bucket"
}

def _set_env_vars(env_dict):
    for key, value in env_dict.items():
        if value is not None:
            os.environ[key] = str(value)
        elif key in os.environ:
            del os.environ[key]
    # Ensure global required vars are always present if not overridden
    for key, value in GLOBAL_REQUIRED_ENV_VARS.items():
        if key not in os.environ:
            os.environ[key] = value

def _clear_env_vars():
    # Clear only variables that might have been set by the app
    prefixes_to_clear = ("APP_", "SECRET_", "RATE_", "DAILY_", "COST_", "W_", "OPENAI_", "ANTHROPIC_",
                         "HITL_", "SNOWFLAKE_", "AWS_", "S3_")
    for key in list(os.environ.keys()):
        if key.startswith(prefixes_to_clear) or key in ["DEBUG"]:
            del os.environ[key]

@lru_cache
def get_settings():
    _set_env_vars(GLOBAL_REQUIRED_ENV_VARS)
    settings = Settings()
    _clear_env_vars()
    return settings
```

To see these default settings in action, imagine clicking a "Load Default Application Settings" button.

<aside class="positive">
  **Action:** In the Streamlit application, click "Load Default Application Settings" in section "1. Initial Setup: Core Configuration".
</aside>

The application would then instantiate the `Settings` class, loading values from `GLOBAL_REQUIRED_ENV_VARS` and any defaults.

```console
 Default Application Settings Loaded 
App Name: `PE Intelligence Platform`
Environment: `development`
Debug Mode: `True`
Secret Key Set: `Yes` (Value masked for security)
API Rate Limit: `100` req/min
Daily Cost Budget: `$1000.00`
Cost Alert Threshold: `75.0%`
HITL Score Change Threshold: `20.0`
HITL EBITDA Projection Threshold: `15.0`
```

#### Explanation of Execution

The code successfully loads the default configuration, demonstrating how basic settings are initialized. The `SECRET_KEY` is handled by `SecretStr`, ensuring its value is never accidentally logged or exposed. This type allows us to retrieve the actual value using `.get_secret_value()` when needed for actual application logic (e.g., connecting to external services), but keeps it masked otherwise. This direct usage of `SecretStr` helps us, as developers, prevent accidental exposure of sensitive credentials, a common source of security vulnerabilities.

## 2. Ensuring Operational Integrity: Field-Level Validation
Duration: 0:15

Operational parameters like API rate limits, daily cost budgets, and alert thresholds are critical for the stability and cost-effectiveness of our PE intelligence platform. As a Data Engineer, I need to ensure these values are always within sensible, predefined ranges to prevent system overload, budget overruns, or ineffective alerting. Pydantic's `Field` with `ge` (greater than or equal to) and `le` (less than or equal to) arguments allows us to enforce these constraints directly within the configuration definition.

### Workflow Task: Validate Operational Parameters with Range Constraints

We'll extend our `Settings` class to define an API rate limit (`RATE_LIMIT_PER_MINUTE`), a daily cost budget (`DAILY_COST_BUDGET_USD`), and a cost alert threshold (`COST_ALERT_THRESHOLD_PCT`). These parameters are crucial for system health and financial governance.

```python
# Part of the Settings class definition (illustrative)
class Settings(BaseSettings):
    # ... (previous fields) ...

    # Operational Parameters with Field-Level Validation
    RATE_LIMIT_PER_MINUTE: int = Field(
        100,
        description="API rate limit in requests per minute.",
        ge=1, # Greater than or equal to 1
        le=1000 # Less than or equal to 1000
    )
    DAILY_COST_BUDGET_USD: Decimal = Field(
        Decimal("1000.00"),
        description="Maximum daily budget for external service usage.",
        ge=Decimal("0.00") # Must be non-negative
    )
    COST_ALERT_THRESHOLD_PCT: float = Field(
        0.75,
        description="Percentage of daily budget at which to trigger an alert.",
        ge=0.0, # Must be between 0 and 1 (inclusive)
        le=1.0
    )
    HITL_SCORE_CHANGE_THRESHOLD: float = Field(
        20.0,
        description="Threshold for significant score change triggering HITL review.",
        ge=5.0,
        le=30.0
    )
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(
        15.0,
        description="Threshold for EBITDA projection change triggering HITL review.",
        ge=5.0,
        le=25.0
    )
    # ... (other fields and validators) ...
```

In the Streamlit application, you can interact with sliders and number inputs to configure these values.

<aside class="positive">
  **Action:** In the Streamlit application, navigate to "2. Field-Level Validation". Adjust the sliders and inputs, then click "Validate Operational Settings". Try setting values outside the suggested ranges (e.g., Rate Limit > 1000, Daily Budget < 0) and observe the errors.
</aside>

**Example Output (Valid Configuration):**
```console
✅ Operational settings are VALID!
Loaded Settings:
  API Rate Limit: `100` req/min
  Daily Cost Budget: `$1000.00`
  Cost Alert Threshold: `75.0%`
  HITL Score Change Threshold: `20.0`
  HITL EBITDA Projection Threshold: `15.0`
```

**Example Output (Invalid Configuration - Rate Limit too high):**
```console
❌ Operational settings are INVALID! Details:
```
1 validation error for Settings
RATE_LIMIT_PER_MINUTE
  Value must be less than or equal to 1000 [type=less_than_equal, input_value=1500, input_type=int]
```
```

#### Explanation of Execution

The interactive examples demonstrate how Pydantic's `Field(ge=X, le=Y)` automatically validates incoming configuration values.
*   **Successful loading** occurs when all operational parameters are within their defined bounds.
*   **Validation errors** immediately occur when values exceed or fall below the specified ranges for fields like `RATE_LIMIT_PER_MINUTE`, `DAILY_COST_BUDGET_USD`, `COST_ALERT_THRESHOLD_PCT`, `HITL_SCORE_CHANGE_THRESHOLD`, and `HITL_EBITDA_PROJECTION_THRESHOLD`. Pydantic raises a `ValidationError`, providing clear, detailed messages about which specific fields failed and why.

This automatic, early detection of out-of-bounds values is crucial. It prevents the system from starting with configurations that could lead to financial losses (e.g., negative budget), operational issues (e.g., excessively high rate limits), or ineffective human-in-the-loop interventions due to inappropriate thresholds.

## 3. Implementing Business Logic: Cross-Field Validation for Scoring Weights
Duration: 0:20

A core component of the PE intelligence platform is its investment scoring model, which relies on various dimensions (e.g., data infrastructure, AI governance, talent). The relative importance of these dimensions is defined by a set of weights. A critical business rule mandates that these **dimension weights must sum up to exactly 1.0** to ensure a coherent and balanced scoring mechanism. Deviations from this sum would lead to skewed, unreliable scores and potentially poor investment recommendations.

As a Data Engineer, I need to implement a robust check to enforce this rule. Pydantic's `@model_validator(mode="after")` is perfect for this, as it allows us to perform validation logic that involves multiple fields *after* individual field validations have passed.

### Workflow Task: Validate Dimension Weights Sum to 1.0

We will add new fields for dimension weights to our `Settings` class and then add a `@model_validator` to ensure their sum is $1.0$. A small tolerance $\epsilon$ is used to account for floating-point inaccuracies. The validation check will be:

$$ \left| \sum_{i=1}^{n} w_i - 1.0 \right| > \epsilon $$

where $w_i$ are the dimension weights and $\epsilon = 0.001$.

```python
# Part of the Settings class definition (illustrative)
class Settings(BaseSettings):
    # ... (previous fields) ...

    # Scoring Weights with Field-Level constraints
    W_DATA_INFRA: float = Field(0.18, ge=0.0, le=1.0, description="Weight for Data Infrastructure.")
    W_AI_GOVERNANCE: float = Field(0.15, ge=0.0, le=1.0, description="Weight for AI Governance.")
    W_TECH_STACK: float = Field(0.15, ge=0.0, le=1.0, description="Weight for Tech Stack.")
    W_TALENT: float = Field(0.17, ge=0.0, le=1.0, description="Weight for Talent.")
    W_LEADERSHIP: float = Field(0.13, ge=0.0, le=1.0, description="Weight for Leadership.")
    W_USE_CASES: float = Field(0.12, ge=0.0, le=1.0, description="Weight for Use Cases.")
    W_CULTURE: float = Field(0.10, ge=0.0, le=1.0, description="Weight for Culture.")

    # ... (other fields) ...

    # Model Validator for Cross-Field Validation (sum of weights)
    @model_validator(mode="after")
    def validate_all_weights_sum(self):
        total_weights = (
            self.W_DATA_INFRA + self.W_AI_GOVERNANCE + self.W_TECH_STACK +
            self.W_TALENT + self.W_LEADERSHIP + self.W_USE_CASES + self.W_CULTURE
        )
        if abs(total_weights - 1.0) > 0.001:  # Allow for floating point inaccuracies
            raise ValueError(
                f"Dimension weights must sum to approximately 1.0 (got {total_weights:.3f})"
            )
        return self

    # ... (other validators) ...
```

In the Streamlit application, you can interact with sliders to adjust these dimension weights. The current sum is displayed to help you.

<aside class="positive">
  **Action:** In the Streamlit application, navigate to "3. Cross-Field Validation (Scoring Weights)". Adjust the sliders. Notice how the "Current sum of weights" changes. Try to make the sum exactly 1.0 (within the small tolerance) and then deliberately make it greater or less than 1.0. Click "Validate Dimension Weights" to see the outcome.
</aside>

**Example Output (Valid Configuration):**
```console
Current sum of weights: `1.00`
✅ Dimension weights are VALID!
Loaded Weights:
  Data Infra: `0.18`
  AI Governance: `0.15`
  Tech Stack: `0.15`
  Talent: `0.17`
  Leadership: `0.13`
  Use Cases: `0.12`
  Culture: `0.10`
  Total Sum: `1.00`
```

**Example Output (Invalid Configuration - Weights sum to 1.05):**
```console
Current sum of weights: `1.05`
❌ Dimension weights are INVALID! Details:
```
1 validation error for Settings
__root__
  Dimension weights must sum to approximately 1.0 (got 1.050) [type=value_error, input_value=Settings(model_config=SettingsConfigDict(env_file='.env', env_prefix='APP_', extra='ignore', case_sensitive=True), APP_NAME='PE Intellige..., input_type=Settings]
```
```

#### Explanation of Execution

This section demonstrates the effectiveness of Pydantic's `@model_validator` for enforcing complex business rules.
*   **Successful loading** occurs when the dimension weights, either defaults or user-provided, sum up to 1.0 (within the specified tolerance).
*   **Validation errors** are triggered when the sum deviates significantly from 1.0. Pydantic catches this discrepancy and raises a `ValueError` wrapped within a `ValidationError`, providing a clear message about the rule violation.

This validation is critical for the PE intelligence platform. It ensures that the investment scoring model is always configured with logically consistent weights, preventing calculation errors that could lead to flawed analytical outputs and incorrect investment decisions. It’s a direct safeguard against subtle yet significant business logic flaws that might otherwise only be detected much later in the analysis pipeline, if at all.

## 4. Fortifying Production: Conditional Environment-Specific Validation
Duration: 0:20

Deploying to a production environment demands a heightened level of rigor. As a Software Developer, I need to ensure that certain security and operational settings are strictly enforced *only* when the application is running in a `production` environment. For instance, `DEBUG` mode must be disabled, sensitive `SECRET_KEY`s must meet minimum length requirements, and all critical external service API keys (like LLM provider keys) must be present.

This conditional validation logic is best implemented using another `@model_validator(mode="after")`, which allows us to inspect the `APP_ENV` field and apply specific rules accordingly. We'll also include a `@field_validator` for `OPENAI_API_KEY` to ensure it starts with the expected "sk-" prefix, an example of a specific format requirement.

### Workflow Task: Enforce Production Security and API Key Presence

We will add a `@model_validator` to the `Settings` class that performs the following checks when `APP_ENV` is set to `"production"`:

1.  `DEBUG` mode must be `False`.
2.  `SECRET_KEY` length must be at least 32 characters.
3.  At least one of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` must be provided.

Additionally, a `@field_validator` ensures `OPENAI_API_KEY` has the correct prefix.

```python
# Part of the Settings class definition (illustrative)
class Settings(BaseSettings):
    # ... (previous fields) ...

    # Core Settings (reiterating for context on production validation)
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    SECRET_KEY: SecretStr = Field(
        ...,
        description="Secret key for application security, e.g., session management."
    )

    # External Service API Keys
    OPENAI_API_KEY: Optional[SecretStr] = Field(None, env_prefix="OPENAI_")
    ANTHROPIC_API_KEY: Optional[SecretStr] = Field(None, env_prefix="ANTHROPIC_")

    # ... (other fields) ...

    # Field Validator for specific API Key format
    @field_validator("OPENAI_API_KEY", mode="after")
    def validate_openai_key_prefix(cls, v):
        if v and not v.get_secret_value().startswith("sk-"):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v

    # Model Validator for Environment-Specific Validation (Production)
    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.APP_ENV == "production":
            if self.DEBUG:
                raise ValueError("DEBUG mode must be False in production.")
            if len(self.SECRET_KEY.get_secret_value()) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters long in production.")
            if not (self.OPENAI_API_KEY or self.ANTHROPIC_API_KEY):
                raise ValueError(
                    "At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) "
                    "must be provided in production."
                )
        return self

    # ... (other validators) ...
```

In the Streamlit application, you can configure these settings using dropdowns, checkboxes, and text inputs.

<aside class="positive">
  **Action:** In the Streamlit application, navigate to "4. Environment-Specific Validation (Production)".
  1.  Set `APP_ENV` to "production", `DEBUG Mode` to `False`, provide a `SECRET_KEY` of at least 32 characters, and at least one LLM API key (e.g., `OPENAI_API_KEY` starting with "sk-"). Click "Validate Production Settings".
  2.  Now, try to break the rules: set `APP_ENV` to "production" and `DEBUG Mode` to `True`, or make `SECRET_KEY` too short, or leave both LLM API keys empty. Observe the validation errors.
</aside>

**Example Output (Valid Production Configuration):**
```console
✅ Production settings are VALID!
Loaded Settings:
  APP_ENV: `production`
  DEBUG: `False`
  SECRET_KEY length: `45`
  OpenAI API Key provided: `Yes`
  Anthropic API Key provided: `No`
```

**Example Output (Invalid Production Configuration - DEBUG mode enabled):**
```console
❌ Production settings are INVALID! Details:
```
1 validation error for Settings
__root__
  DEBUG mode must be False in production. [type=value_error, input_value=Settings(model_config=SettingsConfigDict(env_file='.env', env_prefix='APP_', extra='ignore', case_sensitive=True), APP_NAME='PE Intellige..., input_type=Settings]
```
```

#### Explanation of Execution

This section vividly demonstrates the power of conditional and field-specific validation.
*   **Valid scenarios** show compliant production configurations loading successfully.
*   **Invalid scenarios** purposefully introduce common production misconfigurations: `DEBUG` being `True` in production, a `SECRET_KEY` that is too short, or the absence of critical LLM API keys. In each case, our `validate_production_settings` `@model_validator` correctly identifies the issue and raises a `ValidationError` with an explicit message.
*   The `@field_validator` for `OPENAI_API_KEY` catches a malformed key (e.g., one not starting with "sk-") even outside a production environment, enforcing a specific format.

For a Software Developer or Data Engineer, these explicit error messages at application startup are invaluable. They act as an immediate feedback mechanism, preventing the deployment of insecure or non-functional configurations to live environments. This proactive validation drastically reduces the risk of security breaches, service outages, or unexpected runtime behavior stemming from configuration errors.

## 5. Configuration Simulation & Troubleshooting
Duration: 0:15

The ultimate value of a robust configuration validation system is its ability to prevent failures before they impact users. As a Data Engineer preparing a deployment, I need a way to confidently verify that a given set of environment variables or configuration files will result in a valid application state. This "Validated Configuration Report" ensures that any potential issues are identified and resolved during development or staging, rather than during a critical production rollout.

We can simulate different configuration scenarios and observe Pydantic's error reporting. This acts as our "report," detailing what works and what breaks, and why.

### Common Mistakes & Troubleshooting

Here are some common configuration mistakes and how Pydantic validation helps catch them:

*   **❌ Mistake 1: Dimension weights don't sum to 1.0**
    ```python
    W_DATA_INFRA = 0.20
    W_AI_GOVERNANCE = 0.15
    W_TECH_STACK = 0.15
    W_TALENT = 0.20
    W_LEADERSHIP = 0.15
    W_USE_CASES = 0.10
    W_CULTURE = 0.10
    # Sum = 1.05!
    ```
    **Fix:** The `@model_validator` catches this at startup with a clear error message.

*   **❌ Mistake 2: Exposing secrets in logs**
    ```python
    logger.info("connecting", password=settings.SNOWFLAKE_PASSWORD)
    ```
    **Fix:** Use `SecretStr` which masks values automatically when printing or logging directly. Access the raw value only when explicitly needed using `.get_secret_value()`.

*   **❌ Mistake 3: Not validating at startup**
    ```python
    # WRONG - Fails at runtime when first used
    def get_sector_baseline(sector_id):
        return db.query(...) # Database not connected due to misconfigured credentials!
    ```
    **Fix:** Run Pydantic validation scripts before the application starts, or instantiate your `Settings` class at the application's entry point, which triggers all validations.

### Workflow Task: Simulate Configuration Scenarios and Generate a Validation Report

We will define helper functions to load settings under different simulated environment variable sets, deliberately introducing errors to demonstrate the validation system's comprehensive nature.

```python
# Illustrative dictionary of scenarios, reflecting inputs from the Streamlit app
scenarios = {
    "Valid Development Config": {
        "APP_ENV": "development", "DEBUG": "True", "SECRET_KEY": "dev_key_for_testing_1234567890",
        "RATE_LIMIT_PER_MINUTE": "500", "DAILY_COST_BUDGET_USD": "500", "COST_ALERT_THRESHOLD_PCT": "0.8",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
        "OPENAI_API_KEY": "sk-devkey123"
    },
    "Invalid: Production DEBUG True": {
        "APP_ENV": "production", "DEBUG": "True", "SECRET_KEY": "a_very_long_secret_key_for_production_env",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
        "OPENAI_API_KEY": "sk-prodkey123"
    },
    "Invalid: Weights Sum Incorrect": {
        "APP_ENV": "development", "DEBUG": "True", "SECRET_KEY": "dev_key_for_testing_1234567890",
        "W_DATA_INFRA": "0.20", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.20", "W_LEADERSHIP": "0.15", "W_USE_CASES": "0.10", "W_CULTURE": "0.10",
        "OPENAI_API_KEY": "sk-devkey123" # Sums to 1.05
    },
    "Invalid: Production Missing LLM Key": {
        "APP_ENV": "production", "DEBUG": "False", "SECRET_KEY": "a_very_long_secret_key_for_production_env_12345",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
        "OPENAI_API_KEY": None, "ANTHROPIC_API_KEY": None
    },
     "Invalid: OpenAI Key Format": {
        "APP_ENV": "development", "DEBUG": "True", "SECRET_KEY": "dev_key_for_testing_1234567890",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
        "OPENAI_API_KEY": "pk-invalidprefix" # This should fail field_validator
    },
    "Invalid: Out-of-bounds Rate Limit": {
        "APP_ENV": "development", "DEBUG": "True", "SECRET_KEY": "dev_key_for_testing_1234567890",
        "RATE_LIMIT_PER_MINUTE": "1500", # Max is 1000
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
        "OPENAI_API_KEY": "sk-devkey123"
    }
}

# This function simulates loading settings for a given scenario
def load_scenario_settings(scenario_name, env_dict):
    _clear_env_vars()
    # Apply base required env vars, then scenario-specific ones
    _set_env_vars(GLOBAL_REQUIRED_ENV_VARS)
    _set_env_vars(env_dict)
    try:
        # Instantiate the Settings class, which triggers all Pydantic validations
        settings = Settings()
        print(f"Scenario '{scenario_name}': ✅ VALID configuration loaded.")
        # print some key settings for validation if needed
        print(f"  APP_ENV: {settings.APP_ENV}")
        print(f"  DEBUG: {settings.DEBUG}")
        if hasattr(settings, 'SECRET_KEY'):
            print(f"  SECRET_KEY length: {len(settings.SECRET_KEY.get_secret_value())}")
        if hasattr(settings, 'RATE_LIMIT_PER_MINUTE'):
            print(f"  Rate Limit: {settings.RATE_LIMIT_PER_MINUTE}")
        if hasattr(settings, 'W_DATA_INFRA'):
            # Calculate sum of weights for demonstration
            current_weights = [getattr(settings, f'W_{dim}') for dim in ['DATA_INFRA', 'AI_GOVERNANCE', 'TECH_STACK', 'TALENT', 'LEADERSHIP', 'USE_CASES', 'CULTURE']]
            print(f"  Weights Sum: {sum(current_weights):.3f}")
    except ValidationError as e:
        print(f"Scenario '{scenario_name}': ❌ INVALID configuration detected!")
        print(f"  Error details: \n{e}")
    except Exception as e:
        print(f"Scenario '{scenario_name}': ❌ An unexpected error occurred: {e}")
    finally:
        _clear_env_vars() # Clean up environment variables after each scenario
```

<aside class="positive">
  **Action:** In the Streamlit application, navigate to "5. Configuration Simulation & Troubleshooting". Click "Run All Configuration Scenarios". This will execute a series of predefined tests, simulating various valid and invalid configurations, and present a consolidated report of their outcomes.
</aside>

**Example Consolidated Scenario Report Output:**

```console
Running all predefined scenarios...

Simulating Scenario: Valid Development Config
Environment Variables Set:
{
    "APP_ENV": "development",
    "DEBUG": "True",
    "SECRET_KEY": "dev_key_for_testing_1234567890",
    "RATE_LIMIT_PER_MINUTE": "500",
    "DAILY_COST_BUDGET_USD": "500",
    "COST_ALERT_THRESHOLD_PCT": "0.8",
    "W_DATA_INFRA": "0.18",
    "W_AI_GOVERNANCE": "0.15",
    "W_TECH_STACK": "0.15",
    "W_TALENT": "0.17",
    "W_LEADERSHIP": "0.13",
    "W_USE_CASES": "0.12",
    "W_CULTURE": "0.10",
    "OPENAI_API_KEY": "sk-devkey123"
}
Scenario 'Valid Development Config': ✅ VALID configuration loaded.
  APP_ENV: development
  DEBUG: True
  SECRET_KEY length: 32
  Rate Limit: 500
  Weights Sum: 1.000

Simulating Scenario: Invalid: Production DEBUG True
Environment Variables Set:
{
    "APP_ENV": "production",
    "DEBUG": "True",
    "SECRET_KEY": "a_very_long_secret_key_for_production_env",
    "W_DATA_INFRA": "0.18",
    "W_AI_GOVERNANCE": "0.15",
    "W_TECH_STACK": "0.15",
    "W_TALENT": "0.17",
    "W_LEADERSHIP": "0.13",
    "W_USE_CASES": "0.12",
    "W_CULTURE": "0.10",
    "OPENAI_API_KEY": "sk-prodkey123"
}
Scenario 'Invalid: Production DEBUG True': ❌ INVALID configuration detected!
  Error details: 
1 validation error for Settings
__root__
  DEBUG mode must be False in production. [type=value_error, input_value=Settings(model_config=SettingsConfigDict(env_file='.env', env_prefix='APP_', extra='ignore', case_sensitive=True), APP_NAME='PE Intellige..., input_type=Settings]

... (other scenarios and their outputs) ...

All scenarios completed.


#### Consolidated Scenario Report:
**Valid Development Config:**
```
Scenario 'Valid Development Config': ✅ VALID configuration loaded.
  APP_ENV: development
  DEBUG: True
  SECRET_KEY length: 32
  Rate Limit: 500
  Weights Sum: 1.000
```
**Invalid: Production DEBUG True:**
```
Scenario 'Invalid: Production DEBUG True': ❌ INVALID configuration detected!
  Error details: 
1 validation error for Settings
__root__
  DEBUG mode must be False in production. [type=value_error, input_value=Settings(model_config=SettingsConfigDict(env_file='.env', env_prefix='APP_', extra='ignore', case_sensitive=True), APP_NAME='PE Intellige..., input_type=Settings]
```
**Invalid: Weights Sum Incorrect:**
```
Scenario 'Invalid: Weights Sum Incorrect': ❌ INVALID configuration detected!
  Error details: 
1 validation error for Settings
__root__
  Dimension weights must sum to approximately 1.0 (got 1.050) [type=value_error, input_value=Settings(model_config=SettingsConfigDict(env_file='.env', env_prefix='APP_', extra='ignore', case_sensitive=True), APP_NAME='PE Intellige..., input_type=Settings]
```
... (outputs for other scenarios) ...
```

#### Explanation of Execution

This final section serves as our "Validated Configuration Report." By simulating a range of realistic configuration scenarios – both valid and invalid – we demonstrate the comprehensive safety net provided by Pydantic's validation. Each `load_scenario_settings` call clears the environment, sets specific variables, attempts to load the `Settings` class, and reports the outcome.

The output clearly shows:
*   How valid development and production configurations pass all checks.
*   How specific, critical errors (like `DEBUG` mode in production, incorrect weight sums, or out-of-range API limits) are immediately identified.
*   The exact `ValidationError` messages provide detailed information, pointing directly to the faulty parameter and the reason for the failure.

For a Software Developer or Data Engineer, this process allows for exhaustive testing of configuration permutations. It means that before any new feature or service is deployed to the PE intelligence platform, its configuration can be "pre-validated." This drastically reduces the risk of deployment failures and runtime errors, leading to a more stable, secure, and reliable platform. The proactive identification of issues at startup prevents wasted time debugging issues in live systems and ensures that the platform's critical business logic is always operating on correctly defined parameters.
