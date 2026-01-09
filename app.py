import streamlit as st
from source import *
from pydantic import ValidationError, SecretStr
import os
from typing import Dict, List, Any
import json

st.set_page_config(page_title="QuLab: Foundation and Platform Setup", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Foundation and Platform Setup")
st.divider()

# --- Session State Initialization ---

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Introduction"

if 'app_env' not in st.session_state:
    st.session_state.app_env = "development" # Default environment

if 'config_inputs' not in st.session_state:
    # Initialize config_inputs with default values matching the Settings class in source.py
    st.session_state.config_inputs = {
        "APP_NAME": "PE Org-AI-R Platform",
        "APP_VERSION": "4.0.0",
        "APP_ENV": "development",
        "DEBUG": False,
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "json",
        "SECRET_KEY": "default_secret_for_dev_env_testing_0123456789",
        "API_V1_PREFIX": "/api/v1",
        "API_V2_PREFIX": "/api/v2",
        "RATE_LIMIT_PER_MINUTE": 60,
        "PARAM_VERSION": "v2.0",
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "DEFAULT_LLM_MODEL": "gpt-40-2024-08-06",
        "FALLBACK_LLM_MODEL": "claude-sonnet-4-20250514",
        "DAILY_COST_BUDGET_USD": 500.0,
        "COST_ALERT_THRESHOLD_PCT": 0.8,
        "HITL_SCORE_CHANGE_THRESHOLD": 15.0,
        "HITL_EBITDA_PROJECTION_THRESHOLD": 10.0,
        "SNOWFLAKE_ACCOUNT": "default_snowflake_account",
        "SNOWFLAKE_USER": "default_snowflake_user",
        "SNOWFLAKE_PASSWORD": "default_snowflake_password",
        "SNOWFLAKE_DATABASE": "PE_ORGAIR",
        "SNOWFLAKE_SCHEMA": "PUBLIC",
        "SNOWFLAKE_WAREHOUSE": "default_snowflake_warehouse",
        "SNOWFLAKE_ROLE": "PE_ORGAIR_ROLE",
        "AWS_ACCESS_KEY_ID": "default_aws_key_id",
        "AWS_SECRET_ACCESS_KEY": "default_aws_secret_key",
        "AWS_REGION": "us-east-1",
        "S3_BUCKET": "default_s3_bucket",
        "REDIS_URL": "redis://localhost:6379/0",
        "CACHE_TTL_SECTORS": 86400,
        "CACHE_TTL_SCORES": 3600,
        "ALPHA_VR_WEIGHT": 0.60,
        "BETA_SYNERGY_WEIGHT": 0.12,
        "LAMBDA_PENALTY": 0.25,
        "DELTA_POSITION": 0.15,
        "W_DATA_INFRA": 0.18,
        "W_AI_GOVERNANCE": 0.15,
        "W_TECH_STACK": 0.15,
        "W_TALENT": 0.17,
        "W_LEADERSHIP": 0.13,
        "W_USE_CASES": 0.12,
        "W_CULTURE": 0.10,
        "CELERY_BROKER_URL": "redis://localhost:6379/1",
        "CELERY_RESULT_BACKEND": "redis://localhost:6379/2",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "",
        "OTEL_SERVICE_NAME": "pe-orgair",
    }
    st.session_state.config_inputs["APP_ENV"] = st.session_state.app_env

if 'validation_errors' not in st.session_state:
    st.session_state.validation_errors = {}

if 'overall_validation_status' not in st.session_state:
    st.session_state.overall_validation_status = "Not Validated"

if 'validated_config_report' not in st.session_state:
    st.session_state.validated_config_report = ""

if 'selected_scenario_name' not in st.session_state:
    # Accessing scenarios from source.py
    st.session_state.selected_scenario_name = list(scenarios.keys())[0] if scenarios else "No Scenario"

if 'current_settings_object' not in st.session_state:
    st.session_state.current_settings_object = None

# --- Helper Functions ---

def parse_pydantic_errors(e: ValidationError) -> Dict[str, str]:
    errors = {}
    for error in e.errors():
        field = error['loc'][0] if error['loc'] else 'general'
        errors[field] = error['msg']
    return errors

def generate_valid_report(settings_obj) -> str:
    report = "### Overall Validation Status: 🎉 VALID Configuration! 🎉\n\n"
    report += "All configuration parameters have passed validation checks.\n\n"
    report += "#### Current Settings:\n"
    settings_dict = {}
    for field_name, field_value in settings_obj.model_dump().items():
        if isinstance(field_value, SecretStr):
            settings_dict[field_name] = str(field_value) # Masked value
        else:
            settings_dict[field_name] = field_value
    report += f"```json\n{json.dumps(settings_dict, indent=2)}\n```\n"
    return report

def generate_invalid_report(e: ValidationError) -> str:
    report = "### Overall Validation Status: ❌ INVALID Configuration ❌\n\n"
    report += "The following validation errors were found:\n"
    for error in e.errors():
        field = error['loc'][0] if error['loc'] else 'General Configuration'
        report += f"- **{field}**: {error['msg']}\n"
    report += "\n#### Raw Pydantic Validation Errors:\n"
    report += f"```json\n{json.dumps(e.errors(), indent=2)}\n```\n"
    return report

def load_scenario():
    if st.session_state.selected_scenario_name in scenarios:
        selected_scenario_data = scenarios[st.session_state.selected_scenario_name]
        st.session_state.config_inputs.update(selected_scenario_data)
        if "APP_ENV" in selected_scenario_data:
            st.session_state.app_env = selected_scenario_data["APP_ENV"]
            st.session_state.config_inputs["APP_ENV"] = selected_scenario_data["APP_ENV"]
        st.session_state.validation_errors = {}
        st.session_state.overall_validation_status = "Not Validated"
        st.session_state.validated_config_report = ""
        st.session_state.current_settings_object = None
        st.success(f"Scenario '{st.session_state.selected_scenario_name}' loaded successfully!")
    else:
        st.error("Invalid scenario selected.")

def validate_configuration():
    # 1. Clear existing environment variables
    clear_env()

    # 2. Populate os.environ
    default_required_env_vars = {
        "SECRET_KEY": "default_secret_for_dev_env_testing_01234567890123456789",
        "SNOWFLAKE_ACCOUNT": "test_account",
        "SNOWFLAKE_USER": "test_user",
        "SNOWFLAKE_PASSWORD": "test_snowflake_password",
        "SNOWFLAKE_WAREHOUSE": "test_warehouse",
        "AWS_ACCESS_KEY_ID": "test_aws_key_id",
        "AWS_SECRET_ACCESS_KEY": "test_aws_secret_key",
        "S3_BUCKET": "test_s3_bucket"
    }
    
    for key, value in st.session_state.config_inputs.items():
        if isinstance(value, bool):
            os.environ[key] = str(value)
        elif value is not None and value != "":
            os.environ[key] = str(value)

    for key, value in default_required_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

    os.environ["APP_ENV"] = st.session_state.app_env

    # 3. Clear lru_cache
    get_settings_with_prod_validation.cache_clear()

    # 4. Attempt to load and validate
    try:
        settings_obj = get_settings_with_prod_validation()
        st.session_state.overall_validation_status = "Valid"
        st.session_state.validated_config_report = generate_valid_report(settings_obj)
        st.session_state.validation_errors = {}
        st.session_state.current_settings_object = settings_obj
    except ValidationError as e:
        st.session_state.overall_validation_status = "Invalid"
        st.session_state.validation_errors = parse_pydantic_errors(e)
        st.session_state.validated_config_report = generate_invalid_report(e)
        st.session_state.current_settings_object = None
    finally:
        # 5. Clean up
        clear_env()

# --- Sidebar ---
with st.sidebar:
    st.header("Navigation")
    st.session_state.current_page = st.selectbox(
        "Go to",
        ["Introduction", "Configure Application Settings", "Validated Configuration Report"],
        index=["Introduction", "Configure Application Settings", "Validated Configuration Report"].index(st.session_state.current_page)
    )

    st.markdown("---")
    st.header("Global Controls")
    
    env_options = ["development", "staging", "production"]
    current_env_index = env_options.index(st.session_state.app_env) if st.session_state.app_env in env_options else 0
    
    st.session_state.app_env = st.radio(
        "Select Environment",
        env_options,
        index=current_env_index,
        key="sidebar_app_env",
        on_change=lambda: st.session_state.config_inputs.update({"APP_ENV": st.session_state.app_env})
    )

    st.markdown("---")
    st.header("Scenario Presets")
    scenario_options = list(scenarios.keys()) if scenarios else ["No Scenarios"]
    current_scenario_index = scenario_options.index(st.session_state.selected_scenario_name) if st.session_state.selected_scenario_name in scenario_options else 0
    
    st.session_state.selected_scenario_name = st.selectbox(
        "Load Example Configuration",
        scenario_options,
        index=current_scenario_index,
        key="scenario_selector"
    )
    st.button("Load Scenario", on_click=load_scenario, help="Load a pre-defined configuration scenario into the inputs.")

    st.markdown("---")
    st.button("Validate Configuration", on_click=validate_configuration, type="primary", help="Trigger Pydantic validation for the current settings.")

# --- Main Content ---

if st.session_state.current_page == "Introduction":
    st.markdown(f"## Introduction: Safeguarding the PE Intelligence Platform")
    st.markdown(f"As a **Software Developer** or **Data Engineer** building the Organizational AIR Scoring platform, ensuring the robustness and security of our application configurations is paramount. Every new feature or data processing service we deploy relies on correct, consistent, and validated settings across different environments – development, staging, and crucially, production. A single misconfigured parameter, such as an incorrect API key, an out-of-bounds budget, or an improperly weighted scoring dimension, can lead to critical application crashes, compromised data integrity, or skewed analytical outcomes that directly impact investment decisions.")
    st.markdown(f"This application outlines a real-world workflow to implement a highly reliable configuration system using Pydantic v2. Our goal is to prevent these costly configuration-related bugs by enforcing strict validation rules, significantly reducing operational overhead and building trust in our platform's outputs. We will walk through defining settings, applying various validation types, and simulating different environmental scenarios to demonstrate how invalid configurations are caught *before* they can cause harm.")
    st.markdown(f"---")
    st.markdown(f"### Key Objectives:")
    st.markdown(f"- **Remember**: List the components of a FastAPI application and Pydantic validation")
    st.markdown(f"- **Understand**: Explain why configuration validation prevents runtime errors")
    st.markdown(f"- **Apply**: Implement a validated configuration system with weight constraints")
    st.markdown(f"- **Create**: Design a project structure for production PE intelligence platforms")

elif st.session_state.current_page == "Configure Application Settings":
    st.markdown(f"## Configure Application Settings")
    st.markdown(f"Modify the parameters below to define your application's configuration. Use the 'Validate Configuration' button in the sidebar to check for issues.")

    current_env = st.session_state.app_env
    st.info(f"Currently configuring for: **`{current_env.upper()}`** environment.")

    # --- Application Settings ---
    with st.expander("General Application Settings", expanded=True):
        st.markdown(f"### 1. Initial Setup: Environment and Dependencies")
        st.markdown(f"As a Software Developer, my first step in configuring a new service for the PE intelligence platform is to define its fundamental settings. These include basic application metadata, environment specification, logging preferences, and crucial sensitive data like secret keys. Using Pydantic's `BaseSettings` and `SettingsConfigDict` allows us to define these in a structured, type-hinted manner, automatically loading from environment variables or `.env` files.")
        st.markdown(f"For sensitive information, like the `SECRET_KEY`, we employ Pydantic's `SecretStr` type. This ensures that the value is never accidentally logged or exposed, enhancing the security posture of our application.")
        st.markdown(f"#### Workflow Task: Define Base Application Settings")

        st.session_state.config_inputs["APP_NAME"] = st.text_input("Application Name", value=st.session_state.config_inputs["APP_NAME"], key="APP_NAME")
        st.session_state.config_inputs["APP_VERSION"] = st.text_input("Application Version", value=st.session_state.config_inputs["APP_VERSION"], key="APP_VERSION")
        
        st.text_input("Application Environment (controlled by sidebar)", value=st.session_state.config_inputs["APP_ENV"], disabled=True)
        
        st.session_state.config_inputs["DEBUG"] = st.checkbox("Debug Mode", value=st.session_state.config_inputs["DEBUG"], key="DEBUG")
        if "DEBUG" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["DEBUG"])
        
        log_level_opts = ["DEBUG", "INFO", "WARNING", "ERROR"]
        log_level_idx = log_level_opts.index(st.session_state.config_inputs["LOG_LEVEL"]) if st.session_state.config_inputs["LOG_LEVEL"] in log_level_opts else 1
        st.session_state.config_inputs["LOG_LEVEL"] = st.selectbox("Log Level", options=log_level_opts, index=log_level_idx, key="LOG_LEVEL")
        
        log_fmt_opts = ["json", "console"]
        log_fmt_idx = log_fmt_opts.index(st.session_state.config_inputs["LOG_FORMAT"]) if st.session_state.config_inputs["LOG_FORMAT"] in log_fmt_opts else 0
        st.session_state.config_inputs["LOG_FORMAT"] = st.radio("Log Format", options=log_fmt_opts, index=log_fmt_idx, key="LOG_FORMAT")
        
        st.session_state.config_inputs["SECRET_KEY"] = st.text_input("Secret Key", value=st.session_state.config_inputs["SECRET_KEY"], type="password", help="Minimum 32 characters in Production", key="SECRET_KEY")
        if "SECRET_KEY" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["SECRET_KEY"])

    # --- API Settings ---
    with st.expander("API Settings"):
        st.session_state.config_inputs["API_V1_PREFIX"] = st.text_input("API v1 Prefix", value=st.session_state.config_inputs["API_V1_PREFIX"], key="API_V1_PREFIX")
        st.session_state.config_inputs["API_V2_PREFIX"] = st.text_input("API v2 Prefix", value=st.session_state.config_inputs["API_V2_PREFIX"], key="API_V2_PREFIX")
        st.session_state.config_inputs["RATE_LIMIT_PER_MINUTE"] = st.slider("API Rate Limit (per minute)", min_value=1, max_value=1000, value=st.session_state.config_inputs["RATE_LIMIT_PER_MINUTE"], key="RATE_LIMIT_PER_MINUTE")
        if "RATE_LIMIT_PER_MINUTE" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["RATE_LIMIT_PER_MINUTE"])
        
        param_opts = ["v1.0", "v2.0"]
        param_idx = param_opts.index(st.session_state.config_inputs["PARAM_VERSION"]) if st.session_state.config_inputs["PARAM_VERSION"] in param_opts else 1
        st.session_state.config_inputs["PARAM_VERSION"] = st.radio("Parameter Version", options=param_opts, index=param_idx, key="PARAM_VERSION")

    # --- LLM Providers ---
    with st.expander("LLM Providers"):
        st.markdown(f"At least one LLM API key (OpenAI or Anthropic) is required in **production environment**.")
        st.session_state.config_inputs["OPENAI_API_KEY"] = st.text_input("OpenAI API Key (starts with 'sk-')", value=st.session_state.config_inputs["OPENAI_API_KEY"], type="password", key="OPENAI_API_KEY")
        if "OPENAI_API_KEY" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["OPENAI_API_KEY"])
        st.session_state.config_inputs["ANTHROPIC_API_KEY"] = st.text_input("Anthropic API Key", value=st.session_state.config_inputs["ANTHROPIC_API_KEY"], type="password", key="ANTHROPIC_API_KEY")
        if "ANTHROPIC_API_KEY" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["ANTHROPIC_API_KEY"])
        # Global model key error
        if "general" in st.session_state.validation_errors and "LLM API key" in st.session_state.validation_errors["general"]:
             st.error(st.session_state.validation_errors["general"])
        
        st.session_state.config_inputs["DEFAULT_LLM_MODEL"] = st.text_input("Default LLM Model", value=st.session_state.config_inputs["DEFAULT_LLM_MODEL"], key="DEFAULT_LLM_MODEL")
        st.session_state.config_inputs["FALLBACK_LLM_MODEL"] = st.text_input("Fallback LLM Model", value=st.session_state.config_inputs["FALLBACK_LLM_MODEL"], key="FALLBACK_LLM_MODEL")

    # --- Cost Management ---
    with st.expander("Cost Management"):
        st.markdown(f"### 3. Ensuring Operational Integrity: Field-Level Validation")
        st.markdown(f"Operational parameters like API rate limits, daily cost budgets, and alert thresholds are critical for the stability and cost-effectiveness of our PE intelligence platform. As a Data Engineer, I need to ensure these values are always within sensible, predefined ranges to prevent system overload, budget overruns, or ineffective alerting. Pydantic's `Field` with `ge` (greater than or equal to) and `le` (less than or equal to) arguments allows us to enforce these constraints directly within the configuration definition.")
        st.markdown(f"#### Workflow Task: Validate Operational Parameters with Range Constraints")

        st.session_state.config_inputs["DAILY_COST_BUDGET_USD"] = st.number_input("Daily Cost Budget (USD)", min_value=0.0, value=float(st.session_state.config_inputs["DAILY_COST_BUDGET_USD"]), format="%.2f", key="DAILY_COST_BUDGET_USD")
        if "DAILY_COST_BUDGET_USD" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["DAILY_COST_BUDGET_USD"])
        st.session_state.config_inputs["COST_ALERT_THRESHOLD_PCT"] = st.slider("Cost Alert Threshold (%)", min_value=0.0, max_value=1.0, value=float(st.session_state.config_inputs["COST_ALERT_THRESHOLD_PCT"]), step=0.01, format="%.2f", help="Percentage of daily budget to trigger an alert (0.0 to 1.0)", key="COST_ALERT_THRESHOLD_PCT")
        if "COST_ALERT_THRESHOLD_PCT" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["COST_ALERT_THRESHOLD_PCT"])
        st.session_state.config_inputs["HITL_SCORE_CHANGE_THRESHOLD"] = st.slider("HITL Score Change Threshold", min_value=5.0, max_value=30.0, value=float(st.session_state.config_inputs["HITL_SCORE_CHANGE_THRESHOLD"]), step=0.1, format="%.1f", key="HITL_SCORE_CHANGE_THRESHOLD")
        if "HITL_SCORE_CHANGE_THRESHOLD" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["HITL_SCORE_CHANGE_THRESHOLD"])
        st.session_state.config_inputs["HITL_EBITDA_PROJECTION_THRESHOLD"] = st.slider("HITL EBITDA Projection Threshold", min_value=5.0, max_value=25.0, value=float(st.session_state.config_inputs["HITL_EBITDA_PROJECTION_THRESHOLD"]), step=0.1, format="%.1f", key="HITL_EBITDA_PROJECTION_THRESHOLD")
        if "HITL_EBITDA_PROJECTION_THRESHOLD" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["HITL_EBITDA_PROJECTION_THRESHOLD"])

    # --- Database (Snowflake) ---
    with st.expander("Snowflake Settings"):
        st.session_state.config_inputs["SNOWFLAKE_ACCOUNT"] = st.text_input("Snowflake Account", value=st.session_state.config_inputs["SNOWFLAKE_ACCOUNT"], key="SNOWFLAKE_ACCOUNT")
        st.session_state.config_inputs["SNOWFLAKE_USER"] = st.text_input("Snowflake User", value=st.session_state.config_inputs["SNOWFLAKE_USER"], key="SNOWFLAKE_USER")
        st.session_state.config_inputs["SNOWFLAKE_PASSWORD"] = st.text_input("Snowflake Password", value=st.session_state.config_inputs["SNOWFLAKE_PASSWORD"], type="password", key="SNOWFLAKE_PASSWORD")
        st.session_state.config_inputs["SNOWFLAKE_DATABASE"] = st.text_input("Snowflake Database", value=st.session_state.config_inputs["SNOWFLAKE_DATABASE"], key="SNOWFLAKE_DATABASE")
        st.session_state.config_inputs["SNOWFLAKE_SCHEMA"] = st.text_input("Snowflake Schema", value=st.session_state.config_inputs["SNOWFLAKE_SCHEMA"], key="SNOWFLAKE_SCHEMA")
        st.session_state.config_inputs["SNOWFLAKE_WAREHOUSE"] = st.text_input("Snowflake Warehouse", value=st.session_state.config_inputs["SNOWFLAKE_WAREHOUSE"], key="SNOWFLAKE_WAREHOUSE")
        st.session_state.config_inputs["SNOWFLAKE_ROLE"] = st.text_input("Snowflake Role", value=st.session_state.config_inputs["SNOWFLAKE_ROLE"], key="SNOWFLAKE_ROLE")

    # --- AWS Settings ---
    with st.expander("AWS Settings"):
        st.session_state.config_inputs["AWS_ACCESS_KEY_ID"] = st.text_input("AWS Access Key ID", value=st.session_state.config_inputs["AWS_ACCESS_KEY_ID"], type="password", key="AWS_ACCESS_KEY_ID")
        st.session_state.config_inputs["AWS_SECRET_ACCESS_KEY"] = st.text_input("AWS Secret Access Key", value=st.session_state.config_inputs["AWS_SECRET_ACCESS_KEY"], type="password", key="AWS_SECRET_ACCESS_KEY")
        st.session_state.config_inputs["AWS_REGION"] = st.text_input("AWS Region", value=st.session_state.config_inputs["AWS_REGION"], key="AWS_REGION")
        st.session_state.config_inputs["S3_BUCKET"] = st.text_input("S3 Bucket Name", value=st.session_state.config_inputs["S3_BUCKET"], key="S3_BUCKET")

    # --- Redis Settings ---
    with st.expander("Redis Settings"):
        st.session_state.config_inputs["REDIS_URL"] = st.text_input("Redis URL", value=st.session_state.config_inputs["REDIS_URL"], key="REDIS_URL")
        st.session_state.config_inputs["CACHE_TTL_SECTORS"] = st.number_input("Cache TTL Sectors (seconds)", min_value=1, value=int(st.session_state.config_inputs["CACHE_TTL_SECTORS"]), key="CACHE_TTL_SECTORS")
        st.session_state.config_inputs["CACHE_TTL_SCORES"] = st.number_input("Cache TTL Scores (seconds)", min_value=1, value=int(st.session_state.config_inputs["CACHE_TTL_SCORES"]), key="CACHE_TTL_SCORES")

    # --- Scoring Parameters (v2.0) ---
    with st.expander("Scoring Parameters (v2.0)"):
        st.session_state.config_inputs["ALPHA_VR_WEIGHT"] = st.slider("ALPHA VR Weight", min_value=0.55, max_value=0.70, value=float(st.session_state.config_inputs["ALPHA_VR_WEIGHT"]), step=0.01, format="%.2f", key="ALPHA_VR_WEIGHT")
        if "ALPHA_VR_WEIGHT" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["ALPHA_VR_WEIGHT"])
        st.session_state.config_inputs["BETA_SYNERGY_WEIGHT"] = st.slider("BETA Synergy Weight", min_value=0.08, max_value=0.20, value=float(st.session_state.config_inputs["BETA_SYNERGY_WEIGHT"]), step=0.01, format="%.2f", key="BETA_SYNERGY_WEIGHT")
        if "BETA_SYNERGY_WEIGHT" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["BETA_SYNERGY_WEIGHT"])
        st.session_state.config_inputs["LAMBDA_PENALTY"] = st.slider("LAMBDA Penalty", min_value=0.0, max_value=0.50, value=float(st.session_state.config_inputs["LAMBDA_PENALTY"]), step=0.01, format="%.2f", key="LAMBDA_PENALTY")
        if "LAMBDA_PENALTY" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["LAMBDA_PENALTY"])
        st.session_state.config_inputs["DELTA_POSITION"] = st.slider("DELTA Position", min_value=0.10, max_value=0.20, value=float(st.session_state.config_inputs["DELTA_POSITION"]), step=0.01, format="%.2f", key="DELTA_POSITION")
        if "DELTA_POSITION" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["DELTA_POSITION"])

    # --- Dimension Weights ---
    with st.expander("Dimension Weights", expanded=True):
        st.markdown(f"### 4. Implementing Business Logic: Cross-Field Validation for Scoring Weights")
        st.markdown(f"A core component of the PE intelligence platform is its investment scoring model, which relies on various dimensions (e.g., data infrastructure, AI governance, talent). The relative importance of these dimensions is defined by a set of weights. A critical business rule mandates that these **dimension weights must sum up to exactly 1.0** to ensure a coherent and balanced scoring mechanism. Deviations from this sum would lead to skewed, unreliable scores and potentially poor investment recommendations.")
        st.markdown(f"As a Data Engineer, I need to implement a robust check to enforce this rule. Pydantic's `@model_validator(mode=\"after\")` is perfect for this, as it allows us to perform validation logic that involves multiple fields *after* individual field validations have passed.")
        st.markdown(f"#### Workflow Task: Validate Dimension Weights Sum to 1.0")
        st.markdown(r"We will define new fields for dimension weights and then add a `@model_validator` to ensure their sum is $1.0$. A small tolerance $\epsilon$ is used to account for floating-point inaccuracies. The validation check will be:")
        st.markdown(r"$$\left| \sum_{{i=1}}^{{n}} w_i - 1.0 \right| > \epsilon$$")
        st.markdown(r"where $w_i$ are the dimension weights and $\epsilon = 0.001$.")
        
        st.session_state.config_inputs["W_DATA_INFRA"] = st.slider("Data Infrastructure Weight (W_DATA_INFRA)", min_value=0.0, max_value=1.0, value=float(st.session_state.config_inputs["W_DATA_INFRA"]), step=0.01, format="%.2f", key="W_DATA_INFRA")
        st.session_state.config_inputs["W_AI_GOVERNANCE"] = st.slider("AI Governance Weight (W_AI_GOVERNANCE)", min_value=0.0, max_value=1.0, value=float(st.session_state.config_inputs["W_AI_GOVERNANCE"]), step=0.01, format="%.2f", key="W_AI_GOVERNANCE")
        st.session_state.config_inputs["W_TECH_STACK"] = st.slider("Tech Stack Weight (W_TECH_STACK)", min_value=0.0, max_value=1.0, value=float(st.session_state.config_inputs["W_TECH_STACK"]), step=0.01, format="%.2f", key="W_TECH_STACK")
        st.session_state.config_inputs["W_TALENT"] = st.slider("Talent Weight (W_TALENT)", min_value=0.0, max_value=1.0, value=float(st.session_state.config_inputs["W_TALENT"]), step=0.01, format="%.2f", key="W_TALENT")
        st.session_state.config_inputs["W_LEADERSHIP"] = st.slider("Leadership Weight (W_LEADERSHIP)", min_value=0.0, max_value=1.0, value=float(st.session_state.config_inputs["W_LEADERSHIP"]), step=0.01, format="%.2f", key="W_LEADERSHIP")
        st.session_state.config_inputs["W_USE_CASES"] = st.slider("Use Cases Weight (W_USE_CASES)", min_value=0.0, max_value=1.0, value=float(st.session_state.config_inputs["W_USE_CASES"]), step=0.01, format="%.2f", key="W_USE_CASES")
        st.session_state.config_inputs["W_CULTURE"] = st.slider("Culture Weight (W_CULTURE)", min_value=0.0, max_value=1.0, value=float(st.session_state.config_inputs["W_CULTURE"]), step=0.01, format="%.2f", key="W_CULTURE")
        
        if "validate_dimension_weights" in st.session_state.validation_errors:
            st.error(st.session_state.validation_errors["validate_dimension_weights"])
        # Display current sum for user feedback
        current_weights_sum = sum([
            st.session_state.config_inputs["W_DATA_INFRA"],
            st.session_state.config_inputs["W_AI_GOVERNANCE"],
            st.session_state.config_inputs["W_TECH_STACK"],
            st.session_state.config_inputs["W_TALENT"],
            st.session_state.config_inputs["W_LEADERSHIP"],
            st.session_state.config_inputs["W_USE_CASES"],
            st.session_state.config_inputs["W_CULTURE"]
        ])
        st.info(f"Current Dimension Weights Sum: **{current_weights_sum:.2f}**")

    # --- Celery Settings ---
    with st.expander("Celery Settings"):
        st.session_state.config_inputs["CELERY_BROKER_URL"] = st.text_input("Celery Broker URL", value=st.session_state.config_inputs["CELERY_BROKER_URL"], key="CELERY_BROKER_URL")
        st.session_state.config_inputs["CELERY_RESULT_BACKEND"] = st.text_input("Celery Result Backend", value=st.session_state.config_inputs["CELERY_RESULT_BACKEND"], key="CELERY_RESULT_BACKEND")

    # --- Observability Settings ---
    with st.expander("Observability Settings"):
        st.session_state.config_inputs["OTEL_EXPORTER_OTLP_ENDPOINT"] = st.text_input("OTEL Exporter OTLP Endpoint", value=st.session_state.config_inputs["OTEL_EXPORTER_OTLP_ENDPOINT"], key="OTEL_EXPORTER_OTLP_ENDPOINT")
        st.session_state.config_inputs["OTEL_SERVICE_NAME"] = st.text_input("OTEL Service Name", value=st.session_state.config_inputs["OTEL_SERVICE_NAME"], key="OTEL_SERVICE_NAME")

elif st.session_state.current_page == "Validated Configuration Report":
    st.markdown(f"## Validated Configuration Report")
    st.markdown(f"### 5. Fortifying Production: Conditional Environment-Specific Validation & 6. Catching Errors Early: Configuration Simulation and Reporting")
    st.markdown(f"Deploying to a production environment demands a heightened level of rigor. As a Software Developer, I need to ensure that certain security and operational settings are strictly enforced *only* when the application is running in a `production` environment. For instance, `DEBUG` mode must be disabled, sensitive `SECRET_KEY`s must meet minimum length requirements, and all critical external service API keys (like LLM provider keys) must be present. This conditional validation logic is implemented using Pydantic's `@model_validator(mode=\"after\")`.")
    st.markdown(f"The ultimate value of a robust configuration validation system is its ability to prevent failures before they impact users. As a Data Engineer preparing a deployment, I need a way to confidently verify that a given set of environment variables or configuration files will result in a valid application state. This 'Validated Configuration Report' ensures that any potential issues are identified and resolved during development or staging, rather than during a critical production rollout.")
    st.markdown(f"---")

    if st.session_state.overall_validation_status == "Valid":
        st.success("✅ All configurations are valid!")
    elif st.session_state.overall_validation_status == "Invalid":
        st.error("❌ Errors found in configuration. Please review the report below.")
    else:
        st.warning("Configuration not yet validated. Please configure settings and click 'Validate Configuration'.")

    # Display Critical Validation Rules Applied in an expander
    with st.expander("Critical Validation Rules Applied", expanded=True):
        st.markdown(f"**Field-Level Range Constraints:**")
        st.markdown(f"- `RATE_LIMIT_PER_MINUTE`: Must be between 1 and 1000 requests per minute.")
        st.markdown(f"- `DAILY_COST_BUDGET_USD`: Must be greater than or equal to 0.")
        st.markdown(f"- `COST_ALERT_THRESHOLD_PCT`: Must be between 0 and 1 (0% to 100%).")
        st.markdown(f"- `HITL_SCORE_CHANGE_THRESHOLD`: Must be between 5.0 and 30.0.")
        st.markdown(f"- `HITL_EBITDA_PROJECTION_THRESHOLD`: Must be between 5.0 and 25.0.")
        st.markdown(f"- `ALPHA_VR_WEIGHT`, `BETA_SYNERGY_WEIGHT`, `LAMBDA_PENALTY`, `DELTA_POSITION`: Specific ranges defined for scoring model stability.")
        st.markdown(f"- `W_DATA_INFRA` to `W_CULTURE`: Each dimension weight must be between 0.0 and 1.0.")
        st.markdown(f"**Cross-Field Business Logic Validation:**")
        st.markdown(f"- **Dimension Weights Summation:** The sum of all `W_` dimension weights must be $1.0 \pm 0.001$. This ensures the scoring model is balanced.")
        st.markdown(f"**Conditional Environment-Specific Validation (Production):**")
        st.markdown(f"- If `APP_ENV` is `production`:")
        st.markdown(f"  - `DEBUG` must be `False`.")
        st.markdown(f"  - `SECRET_KEY` must be at least 32 characters long.")
        st.markdown(f"  - At least one of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` must be provided.")
        st.markdown(f"**API Key Format Validation:**")
        st.markdown(f"- `OPENAI_API_KEY`: If provided, must start with 'sk-'.")
    
    st.markdown("---")
    st.markdown("### Configuration Validation Outcome:")
    if st.session_state.validated_config_report:
        st.markdown(st.session_state.validated_config_report)
    else:
        st.info("No validation report available. Please configure settings and click 'Validate Configuration'.")

    st.markdown("---")
    st.markdown("### Common Mistakes & Troubleshooting")
    st.markdown(f"Below are some common configuration mistakes that Pydantic validation helps catch, ensuring our PE intelligence platform remains robust and secure.")

    st.markdown(f"#### ❌ Mistake 1: Dimension weights don't sum to 1.0")
    st.markdown(f"**WRONG**")
    st.code(
        """
W_DATA_INFRA = 0.20
W_AI_GOVERNANCE = 0.15
W_TECH_STACK = 0.15
W_TALENT = 0.20
W_LEADERSHIP = 0.15
W_USE_CASES = 0.10
W_CULTURE = 0.10
# Sum = 1.05!
"""
    )
    st.markdown(f"**Fix**: The `model_validator` catches this at startup with a clear error message. Adjust weights to sum to 1.0.")

    st.markdown(f"#### ❌ Mistake 2: Exposing secrets in logs")
    st.markdown(f"**WRONG**")
    st.code(
        """
logger.info("connecting", password=settings.SNOWFLAKE_PASSWORD)
"""
    )
    st.markdown(f"**Fix**: Use `SecretStr` which masks values automatically when accessed directly, preventing accidental exposure.")

    st.markdown(f"#### ❌ Mistake 3: Missing lifespan context manager")
    st.markdown(f"**WRONG - No cleanup on shutdown**")
    st.code(
        """
app = FastAPI()
redis_client = Redis() # Leaks on shutdown!
"""
    )
    st.markdown(f"**Fix**: Always use lifespan for resource management in FastAPI, ensuring proper initialization and cleanup.")

    st.markdown(f"#### ❌ Mistake 4: Not validating at startup")
    st.markdown(f"**WRONG - Fails at runtime when first used**")
    st.code(
        """
def get_sector_baseline(sector_id):
    return db.query(...) # Database not connected!
"""
    )
    st.markdown(f"**Fix**: Run validation scripts and checks before the application starts or serves requests to catch issues early.")