import streamlit as st
from source import *
import os
import io
from contextlib import redirect_stdout

st.set_page_config(page_title="QuLab: Foundation and Platform Setup", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Foundation and Platform Setup")
st.divider()

# Initialize session state variables if not already present
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Introduction"
if 'settings_initialized' not in st.session_state:
    st.session_state.settings_initialized = False
if 'current_settings' not in st.session_state:
    st.session_state.current_settings = None
if 'operational_settings_valid' not in st.session_state:
    st.session_state.operational_settings_valid = None
if 'operational_validation_error' not in st.session_state:
    st.session_state.operational_validation_error = None
if 'weights_settings_valid' not in st.session_state:
    st.session_state.weights_settings_valid = None
if 'weights_validation_error' not in st.session_state:
    st.session_state.weights_validation_error = None
if 'prod_settings_valid' not in st.session_state:
    st.session_state.prod_settings_valid = None
if 'prod_validation_error' not in st.session_state:
    st.session_state.prod_validation_error = None
if 'sim_scenario_results' not in st.session_state:
    st.session_state.sim_scenario_results = []

# Global environment variables required by source.py's Settings class
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
    # Only clear variables starting with a prefix to avoid clearing system vars
    prefixes_to_clear = ("APP_", "SECRET_", "RATE_", "DAILY_", "COST_", "W_", "OPENAI_", "ANTHROPIC_", 
                         "HITL_", "SNOWFLAKE_", "AWS_", "S3_", "REDIS_", "CACHE_", "CELERY_", "OTEL_", 
                         "ALPHA_", "BETA_", "LAMBDA_", "DELTA_", "API_", "PARAM_", "DEFAULT_", 
                         "FALLBACK_", "LOG_", "DEBUG", "S3_")
    for key in list(os.environ.keys()):
        if key.startswith(prefixes_to_clear):
            del os.environ[key]

st.sidebar.title("Navigation")
page_options = [
    "Introduction",
    "1. Initial Setup: Core Configuration",
    "2. Field-Level Validation",
    "3. Cross-Field Validation (Scoring Weights)",
    "4. Environment-Specific Validation (Production)",
    "5. Configuration Simulation & Troubleshooting"
]

# Use index to set default selection based on state
if st.session_state.current_page not in page_options:
     st.session_state.current_page = page_options[0]

selection = st.sidebar.selectbox(
    "Go to section:",
    page_options,
    index=page_options.index(st.session_state.current_page)
)
st.session_state.current_page = selection

st.markdown(f"## PE Intelligence Platform: Robust Configuration with Pydantic v2")

if st.session_state.current_page == "Introduction":
    st.markdown(f"## Introduction: Safeguarding the PE Intelligence Platform")
    st.markdown(f"") 
    st.markdown(f"As a **Software Developer** building the Organizational AIR Scoring platform, ensuring the robustness and security of our application configurations is paramount. Every new feature or data processing service we deploy relies on correct, consistent, and validated settings across different environments – development, staging, and crucially, production. A single misconfigured parameter, such as an incorrect API key, an out-of-bounds budget, or an improperly weighted scoring dimension, can lead to critical application crashes, compromised data integrity, or skewed analytical outcomes that directly impact investment decisions.")
    st.markdown(f"")
    st.markdown(f"This notebook outlines a real-world workflow to implement a highly reliable configuration system using Pydantic v2. Our goal is to prevent these costly configuration-related bugs by enforcing strict validation rules at application startup, significantly reducing operational overhead and building trust in our platform's outputs. We will walk through defining settings, applying various validation types, and simulating different environmental scenarios to demonstrate how invalid configurations are caught *before* they can cause harm.")
    st.markdown(f"---")

elif st.session_state.current_page == "1. Initial Setup: Core Configuration":
    st.markdown(f"### 1. Initial Setup: Environment and Dependencies")
    st.markdown(f"Before we dive into defining and validating our application settings, let's ensure our environment has all the necessary tools. We'll specifically need `pydantic` and `pydantic-settings` for robust configuration management.")
    st.markdown(f"```python\n!pip install pydantic==2.* pydantic-settings==2.*\n```")
    st.markdown(f"Next, we'll import the core components from Pydantic and Python's standard library that we'll use throughout this workflow.")
    st.markdown(f"```python\nfrom typing import Optional, Literal, List, Dict\nfrom functools import lru_cache\nfrom decimal import Decimal\nimport os\nimport sys\n\nfrom pydantic import Field, ValidationError, field_validator, model_validator, SecretStr\nfrom pydantic_settings import BaseSettings, SettingsConfigDict\n```")
    st.markdown(f"---")
    st.markdown(f"### 2. Setting the Stage: Core Application Configuration")
    st.markdown(f"As a Software Developer, my first step in configuring a new service for the PE intelligence platform is to define its fundamental settings. These include basic application metadata, environment specification, logging preferences, and crucial sensitive data like secret keys. Using Pydantic's `BaseSettings` and `SettingsConfigDict` allows us to define these in a structured, type-hinted manner, automatically loading from environment variables or `.env` files.")
    st.markdown(f"For sensitive information, like the `SECRET_KEY`, we employ Pydantic's `SecretStr` type. This ensures that the value is never accidentally logged or exposed, enhancing the security posture of our application.")
    st.markdown(f"#### Workflow Task: Define Base Application Settings")
    st.markdown(f"We will define the `Settings` class, which will serve as the single source of truth for our application's configuration.")

    if st.button("Load Default Application Settings"):
        _set_env_vars(GLOBAL_REQUIRED_ENV_VARS)
        get_settings.cache_clear() 
        try:
            st.session_state.current_settings = get_settings()
            st.session_state.settings_initialized = True
            st.success("Default settings loaded successfully!")
        except ValidationError as e:
            st.error(f"Error loading default settings: {e}")
            st.session_state.settings_initialized = False
            st.session_state.current_settings = None
        finally:
            _clear_env_vars()

    if st.session_state.settings_initialized and st.session_state.current_settings:
        settings = st.session_state.current_settings
        st.markdown(f"--- Default Application Settings Loaded ---")
        st.markdown(f"App Name: `{settings.APP_NAME}`")
        st.markdown(f"Environment: `{settings.APP_ENV}`")
        st.markdown(f"Debug Mode: `{settings.DEBUG}`")
        st.markdown(f"Secret Key Set: `{'Yes' if settings.SECRET_KEY else 'No'}` (Value masked for security)")
        st.markdown(f"API Rate Limit: `{settings.RATE_LIMIT_PER_MINUTE}` req/min")
        st.markdown(f"Daily Cost Budget: `${settings.DAILY_COST_BUDGET_USD}`")
        st.markdown(f"Cost Alert Threshold: `{settings.COST_ALERT_THRESHOLD_PCT*100}%`")
        st.markdown(f"HITL Score Change Threshold: `{settings.HITL_SCORE_CHANGE_THRESHOLD}`")
        st.markdown(f"HITL EBITDA Projection Threshold: `{settings.HITL_EBITDA_PROJECTION_THRESHOLD}`")
    elif st.session_state.settings_initialized is False and st.session_state.current_settings is None:
         st.warning("Click 'Load Default Application Settings' to see the initial configuration.")

    st.markdown(f"#### Explanation of Execution")
    st.markdown(f"The code successfully loads the default configuration, demonstrating how basic settings are initialized. The `SECRET_KEY` is handled by `SecretStr`, ensuring its value is masked when accessed directly (e.g., in `print()`) but can be retrieved using `.get_secret_value()` when needed for actual application logic (e.g., connecting to external services). This direct usage of `SecretStr` helps us, as developers, prevent accidental exposure of sensitive credentials, a common source of security vulnerabilities.")
    st.markdown(f"---")

elif st.session_state.current_page == "2. Field-Level Validation":
    st.markdown(f"### 3. Ensuring Operational Integrity: Field-Level Validation")
    st.markdown(f"Operational parameters like API rate limits, daily cost budgets, and alert thresholds are critical for the stability and cost-effectiveness of our PE intelligence platform. As a Data Engineer, I need to ensure these values are always within sensible, predefined ranges to prevent system overload, budget overruns, or ineffective alerting. Pydantic's `Field` with `ge` (greater than or equal to) and `le` (less than or equal to) arguments allows us to enforce these constraints directly within the configuration definition.")
    st.markdown(f"#### Workflow Task: Validate Operational Parameters with Range Constraints")
    st.markdown(f"We'll define an API rate limit (`RATE_LIMIT_PER_MINUTE`), a daily cost budget (`DAILY_COST_BUDGET_USD`), and a cost alert threshold (`COST_ALERT_THRESHOLD_PCT`). These parameters are crucial for system health and financial governance.")

    st.markdown(f"Configure the operational parameters below and click 'Validate'. Observe how Pydantic handles values outside the expected ranges:")

    col1, col2 = st.columns(2)
    with col1:
        rate_limit = st.number_input("API Rate Limit (1-1000 req/min)", min_value=1, max_value=1500, value=100, step=10)
        daily_budget = st.number_input("Daily Cost Budget (USD, >=0)", min_value=-50.0, max_value=2000.0, value=1000.0, step=10.0)
        hitl_score_change = st.number_input("HITL Score Change Threshold (5-30)", min_value=2.0, max_value=50.0, value=20.0, step=1.0)
    with col2:
        cost_threshold = st.slider("Cost Alert Threshold (0-1, e.g., 0.75 for 75%)", min_value=0.0, max_value=1.5, value=0.75, step=0.01)
        hitl_ebitda_projection = st.number_input("HITL EBITDA Projection Threshold (5-25)", min_value=5.0, max_value=50.0, value=15.0, step=1.0)

    if st.button("Validate Operational Settings"):
        env_vars = {
            "RATE_LIMIT_PER_MINUTE": rate_limit,
            "DAILY_COST_BUDGET_USD": daily_budget,
            "COST_ALERT_THRESHOLD_PCT": cost_threshold,
            "HITL_SCORE_CHANGE_THRESHOLD": hitl_score_change,
            "HITL_EBITDA_PROJECTION_THRESHOLD": hitl_ebitda_projection
        }
        _set_env_vars(env_vars)
        get_settings_operational_validation.cache_clear()
        try:
            settings = get_settings_operational_validation()
            st.session_state.operational_settings_valid = True
            st.session_state.operational_validation_error = None
            st.success("✅ Operational settings are VALID!")
            st.markdown(f"**Loaded Settings:**")
            st.markdown(f"  API Rate Limit: `{settings.RATE_LIMIT_PER_MINUTE}` req/min")
            st.markdown(f"  Daily Cost Budget: `${settings.DAILY_COST_BUDGET_USD}`")
            st.markdown(f"  Cost Alert Threshold: `{settings.COST_ALERT_THRESHOLD_PCT*100}%`")
            st.markdown(f"  HITL Score Change Threshold: `{settings.HITL_SCORE_CHANGE_THRESHOLD}`")
            st.markdown(f"  HITL EBITDA Projection Threshold: `{settings.HITL_EBITDA_PROJECTION_THRESHOLD}`")
        except ValidationError as e:
            st.session_state.operational_settings_valid = False
            st.session_state.operational_validation_error = e
            st.error(f"❌ Operational settings are INVALID! Details: \n```\n{e}\n```")
        finally:
            _clear_env_vars()

    if st.session_state.operational_validation_error:
        st.markdown(f"**Last Validation Result:**")
        if st.session_state.operational_settings_valid:
            st.success("✅ Valid settings were loaded last.")
        else:
            st.error(f"❌ Last attempt resulted in an error:\n```\n{st.session_state.operational_validation_error}\n```")

    st.markdown(f"#### Explanation of Execution")
    st.markdown(f"The first scenario demonstrates successful loading when all operational parameters are within their defined bounds. In contrast, the second scenario attempts to load configurations with values exceeding or falling below the specified ranges for `RATE_LIMIT_PER_MINUTE`, `DAILY_COST_BUDGET_USD`, `COST_ALERT_THRESHOLD_PCT`, `HITL_SCORE_CHANGE_THRESHOLD`, and `HITL_EBITDA_PROJECTION_THRESHOLD`. Pydantic immediately raises a `ValidationError`, providing clear, detailed messages about which specific fields failed and why. This automatic, early detection of out-of-bounds values by `Field(ge=X, le=Y)` is crucial. It prevents the system from starting with configurations that could lead to financial losses (e.g., negative budget), operational issues (e.g., excessively high rate limits), or ineffective human-in-the-loop interventions due to inappropriate thresholds.")
    st.markdown(f"---")

elif st.session_state.current_page == "3. Cross-Field Validation (Scoring Weights)":
    st.markdown(f"### 4. Implementing Business Logic: Cross-Field Validation for Scoring Weights")
    st.markdown(f"A core component of the PE intelligence platform is its investment scoring model, which relies on various dimensions (e.g., data infrastructure, AI governance, talent). The relative importance of these dimensions is defined by a set of weights. A critical business rule mandates that these **dimension weights must sum up to exactly 1.0** to ensure a coherent and balanced scoring mechanism. Deviations from this sum would lead to skewed, unreliable scores and potentially poor investment recommendations.")
    st.markdown(f"As a Data Engineer, I need to implement a robust check to enforce this rule. Pydantic's `@model_validator(mode=\"after\")` is perfect for this, as it allows us to perform validation logic that involves multiple fields *after* individual field validations have passed.")
    st.markdown(f"#### Workflow Task: Validate Dimension Weights Sum to 1.0")
    st.markdown(f"We will define new fields for dimension weights and then add a `@model_validator` to ensure their sum is $1.0$. A small tolerance $\epsilon$ is used to account for floating-point inaccuracies. The validation check will be:")

    st.markdown(r"$$\left| \sum_{{i=1}}^{{n}} w_i - 1.0 \right| > \epsilon$$")
    st.markdown(r"where $w_i$ are the dimension weights and $\epsilon = 0.001$.")

    st.markdown(f"Adjust the dimension weights below. Ensure their sum is approximately 1.0 (within 0.001 tolerance) to pass validation. The default values sum to 1.0.")

    col1, col2 = st.columns(2)
    with col1:
        w_data_infra = st.slider("W_DATA_INFRA", min_value=0.0, max_value=1.0, value=0.18, step=0.01)
        w_ai_governance = st.slider("W_AI_GOVERNANCE", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
        w_tech_stack = st.slider("W_TECH_STACK", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
        w_talent = st.slider("W_TALENT", min_value=0.0, max_value=1.0, value=0.17, step=0.01)
    with col2:
        w_leadership = st.slider("W_LEADERSHIP", min_value=0.0, max_value=1.0, value=0.13, step=0.01)
        w_use_cases = st.slider("W_USE_CASES", min_value=0.0, max_value=1.0, value=0.12, step=0.01)
        w_culture = st.slider("W_CULTURE", min_value=0.0, max_value=1.0, value=0.10, step=0.01)

    weights_sum = w_data_infra + w_ai_governance + w_tech_stack + w_talent + w_leadership + w_use_cases + w_culture
    st.info(f"Current sum of weights: `{weights_sum:.2f}`")

    if st.button("Validate Dimension Weights"):
        env_vars = {
            "W_DATA_INFRA": w_data_infra,
            "W_AI_GOVERNANCE": w_ai_governance,
            "W_TECH_STACK": w_tech_stack,
            "W_TALENT": w_talent,
            "W_LEADERSHIP": w_leadership,
            "W_USE_CASES": w_use_cases,
            "W_CULTURE": w_culture
        }
        _set_env_vars(env_vars)
        get_settings_with_weights.cache_clear()
        try:
            settings = get_settings_with_weights()
            st.session_state.weights_settings_valid = True
            st.session_state.weights_validation_error = None
            st.success("✅ Dimension weights are VALID!")
            st.markdown(f"**Loaded Weights:**")
            st.markdown(f"  Data Infra: `{settings.W_DATA_INFRA}`")
            st.markdown(f"  AI Governance: `{settings.W_AI_GOVERNANCE}`")
            st.markdown(f"  Tech Stack: `{settings.W_TECH_STACK}`")
            st.markdown(f"  Talent: `{settings.W_TALENT}`")
            st.markdown(f"  Leadership: `{settings.W_LEADERSHIP}`")
            st.markdown(f"  Use Cases: `{settings.W_USE_CASES}`")
            st.markdown(f"  Culture: `{settings.W_CULTURE}`")
            st.markdown(f"  **Total Sum: `{weights_sum:.2f}`**")
        except ValidationError as e:
            st.session_state.weights_settings_valid = False
            st.session_state.weights_validation_error = e
            st.error(f"❌ Dimension weights are INVALID! Details: \n```\n{e}\n```")
        finally:
            _clear_env_vars()

    if st.session_state.weights_validation_error:
        st.markdown(f"**Last Validation Result:**")
        if st.session_state.weights_settings_valid:
            st.success("✅ Valid settings were loaded last.")
        else:
            st.error(f"❌ Last attempt resulted in an error:\n```\n{st.session_state.weights_validation_error}\n```")

    st.markdown(f"#### Explanation of Execution")
    st.markdown(f"The first scenario successfully loads settings where the default dimension weights (or explicitly set ones that sum to 1.0) pass the `@model_validator`. This demonstrates a correct configuration. The second scenario, however, intentionally provides weights that do not sum to $1.0$. As expected, Pydantic's `@model_validator` catches this discrepancy and raises a `ValueError` wrapped within a `ValidationError`.")
    st.markdown(f"This validation is critical for the PE intelligence platform. It ensures that the investment scoring model is always configured with logically consistent weights, preventing calculation errors that could lead to flawed analytical outputs and incorrect investment decisions. It’s a direct safeguard against subtle yet significant business logic flaws that might otherwise only be detected much later in the analysis pipeline, if at all.")
    st.markdown(f"---")

elif st.session_state.current_page == "4. Environment-Specific Validation (Production)":
    st.markdown(f"### 5. Fortifying Production: Conditional Environment-Specific Validation")
    st.markdown(f"Deploying to a production environment demands a heightened level of rigor. As a Software Developer, I need to ensure that certain security and operational settings are strictly enforced *only* when the application is running in a `production` environment. For instance, `DEBUG` mode must be disabled, sensitive `SECRET_KEY`s must meet minimum length requirements, and all critical external service API keys (like LLM provider keys) must be present.")
    st.markdown(f"This conditional validation logic is best implemented using another `@model_validator(mode=\"after\")`, which allows us to inspect the `APP_ENV` and apply specific rules accordingly. We'll also include a `@field_validator` for `OPENAI_API_KEY` to ensure it starts with the expected \"sk-\" prefix, an example of a specific format requirement.")
    st.markdown(f"#### Workflow Task: Enforce Production Security and API Key Presence")
    st.markdown(f"We will add a `@model_validator` to the `Settings` class that performs the following checks when `APP_ENV` is set to `\"production\"`:")
    st.markdown(f"1.  `DEBUG` mode must be `False`.")
    st.markdown(f"2.  `SECRET_KEY` length must be at least 32 characters.")
    st.markdown(f"3.  At least one of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` must be provided.")

    st.markdown(f"Configure the settings below, paying attention to production requirements:")

    col1, col2 = st.columns(2)
    with col1:
        app_env = st.selectbox("APP_ENV", ["development", "staging", "production"], index=0)
        debug_mode = st.checkbox("DEBUG Mode", value=True if app_env == "development" else False)
        secret_key = st.text_input("SECRET_KEY (min 32 chars in production)", "dev_key_for_testing_12345678901234567890")
    with col2:
        openai_key = st.text_input("OPENAI_API_KEY (starts with 'sk-')", "")
        anthropic_key = st.text_input("ANTHROPIC_API_KEY", "")
        st.markdown(f"*(Note: One LLM API key is required in production)*")

    if st.button("Validate Production Settings"):
        env_vars = {
            "APP_ENV": app_env,
            "DEBUG": debug_mode,
            "SECRET_KEY": secret_key,
            "OPENAI_API_KEY": openai_key if openai_key else None,
            "ANTHROPIC_API_KEY": anthropic_key if anthropic_key else None
        }
        _set_env_vars(env_vars)
        get_settings_with_prod_validation.cache_clear()
        try:
            settings = get_settings_with_prod_validation()
            st.session_state.prod_settings_valid = True
            st.session_state.prod_validation_error = None
            st.success("✅ Production settings are VALID!")
            st.markdown(f"**Loaded Settings:**")
            st.markdown(f"  APP_ENV: `{settings.APP_ENV}`")
            st.markdown(f"  DEBUG: `{settings.DEBUG}`")
            st.markdown(f"  SECRET_KEY length: `{len(settings.SECRET_KEY.get_secret_value())}`")
            st.markdown(f"  OpenAI API Key provided: `{'Yes' if settings.OPENAI_API_KEY else 'No'}`")
            st.markdown(f"  Anthropic API Key provided: `{'Yes' if settings.ANTHROPIC_API_KEY else 'No'}`")
        except ValidationError as e:
            st.session_state.prod_settings_valid = False
            st.session_state.prod_validation_error = e
            st.error(f"❌ Production settings are INVALID! Details: \n```\n{e}\n```")
        finally:
            _clear_env_vars()

    if st.session_state.prod_validation_error:
        st.markdown(f"**Last Validation Result:**")
        if st.session_state.prod_settings_valid:
            st.success("✅ Valid settings were loaded last.")
        else:
            st.error(f"❌ Last attempt resulted in an error:\n```\n{st.session_state.prod_validation_error}\n```")

    st.markdown(f"#### Explanation of Execution")
    st.markdown(f"This section vividly demonstrates the power of conditional and field-specific validation.")
    st.markdown(f"*   **Scenario 1** shows a compliant production configuration loading successfully.")
    st.markdown(f"*   **Scenarios 2, 3, and 4** purposefully introduce common production misconfigurations: `DEBUG` being `True`, a `SECRET_KEY` that is too short, and the absence of critical LLM API keys. In each case, our `validate_production_settings` `@model_validator` correctly identifies the issue and raises a `ValidationError` with an explicit message.")
    st.markdown(f"*   **Scenario 5** targets the `OPENAI_API_KEY`'s format using the `@field_validator`, catching a malformed key even outside a production environment.")
    st.markdown(f"For a Software Developer or Data Engineer, these explicit error messages at application startup are invaluable. They act as an immediate feedback mechanism, preventing the deployment of insecure or non-functional configurations to live environments. This proactive validation drastically reduces the risk of security breaches, service outages, or unexpected runtime behavior stemming from configuration errors.")
    st.markdown(f"---")

elif st.session_state.current_page == "5. Configuration Simulation & Troubleshooting":
    st.markdown(f"### 6. Catching Errors Early: Configuration Simulation and Reporting")
    st.markdown(f"The ultimate value of a robust configuration validation system is its ability to prevent failures before they impact users. As a Data Engineer preparing a deployment, I need a way to confidently verify that a given set of environment variables or configuration files will result in a valid application state. This \"Validated Configuration Report\" ensures that any potential issues are identified and resolved during development or staging, rather than during a critical production rollout.")
    st.markdown(f"We can simulate different configuration scenarios and observe Pydantic's error reporting. This acts as our \"report,\" detailing what works and what breaks, and why.")
    st.markdown(f"#### 1.3 Common Mistakes & Troubleshooting")
    st.markdown(f"❌ Mistake 1: Dimension weights don't sum to 1.0")
    st.markdown(f"```python\nW_DATA_INFRA = 0.20\nW_AI_GOVERNANCE = 0.15\nW_TECH_STACK = 0.15\nW_TALENT = 0.20\nW_LEADERSHIP = 0.15\nW_USE_CASES = 0.10\nW_CULTURE = 0.10\n# Sum = 1.05!\n```")
    st.markdown(f"Fix: The `model_validator` catches this at startup with a clear error message.")
    st.markdown(f"❌ Mistake 2: Exposing secrets in logs")
    st.markdown(f"```python\nlogger.info(\"connecting\", password=settings.SNOWFLAKE_PASSWORD)\n```")
    st.markdown(f"Fix: Use SecretStr which masks values automatically.")
    st.markdown(f"❌ Mistake 3: Missing lifespan context manager")
    st.markdown(f"```python\n# WRONG - No cleanup on shutdown\napp = FastAPI()\nredis_client = Redis() # Leaks on shutdown!\n```")
    st.markdown(f"Fix: Always use lifespan for resource management.")
    st.markdown(f"❌ Mistake 4: Not validating at startup")
    st.markdown(f"```python\n# WRONG - Fails at runtime when first used\ndef get_sector_baseline(sector_id):\n    return db.query(...) # Database not connected!\n```")
    st.markdown(f"Fix: Run validation scripts before application starts")

    st.markdown(f"#### Workflow Task: Simulate Configuration Scenarios and Generate a Validation Report")
    st.markdown(f"We will define helper functions to load settings under different simulated environment variable sets, deliberately introducing errors to demonstrate the validation system's comprehensive nature.")

    if st.button("Run All Configuration Scenarios"):
        st.session_state.sim_scenario_results = []
        st.write("Running all predefined scenarios...")

        for name, env_vars_dict in scenarios.items():
            st.subheader(f"Simulating Scenario: {name}")
            st.markdown(f"**Environment Variables Set:**")
            st.json(env_vars_dict)

            f = io.StringIO()
            with redirect_stdout(f):
                load_scenario_settings(name, env_vars_dict)
            
            output_string = f.getvalue()
            st.code(output_string, language='text')
            st.session_state.sim_scenario_results.append({"name": name, "output": output_string})
        
        st.success("All scenarios completed.")
    
    if st.session_state.sim_scenario_results:
        st.markdown(f"---")
        st.markdown(f"#### Consolidated Scenario Report:")
        for result in st.session_state.sim_scenario_results:
            st.markdown(f"**{result['name']}:**")
            st.code(result['output'], language='text')

    st.markdown(f"#### Explanation of Execution")
    st.markdown(f"This final section serves as our \"Validated Configuration Report.\" By simulating a range of realistic configuration scenarios – both valid and invalid – we demonstrate the comprehensive safety net provided by Pydantic's validation. Each `load_scenario_settings` call clears the environment, sets specific variables, attempts to load the `Settings`, and reports the outcome.")
    st.markdown(f"The output clearly shows:")
    st.markdown(f"*   How valid development and production configurations pass all checks.")
    st.markdown(f"*   How specific, critical errors (like `DEBUG` mode in production, incorrect weight sums, or out-of-range API limits) are immediately identified.")
    st.markdown(f"*   The exact `ValidationError` messages provide detailed information, pointing directly to the faulty parameter and the reason for the failure.")
    st.markdown(f"For a Software Developer or Data Engineer, this process allows for exhaustive testing of configuration permutations. It means that before any new feature or service is deployed to the PE intelligence platform, its configuration can be \"pre-validated.\" This drastically reduces the risk of deployment failures and runtime errors, leading to a more stable, secure, and reliable platform. The proactive identification of issues at startup prevents wasted time debugging issues in live systems and ensures that the platform's critical business logic is always operating on correctly defined parameters.")
    st.markdown(f"---")

# License
st.caption('''
---
## QuantUniversity License

© QuantUniversity 2025  
This notebook was created for **educational purposes only** and is **not intended for commercial use**.  

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.  
- You **may not delete or modify this license cell** without authorization.  
- This notebook was generated using **QuCreate**, an AI-powered assistant.  
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.  

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
''')
