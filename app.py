import streamlit as st
import os
from source import *

st.set_page_config(page_title="QuLab: Foundation and Platform Setup", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Foundation and Platform Setup")
st.divider()

# Initialize session state variables with sensible defaults
if "env_vars_input" not in st.session_state:
    st.session_state.env_vars_input = {
        "APP_NAME": "PE Org-AI-R Platform",
        "APP_VERSION": "4.0.0",
        "APP_ENV": "development",
        "DEBUG": "False", 
        "LOG_LEVEL": "INFO",
        "SECRET_KEY": "a_default_secret_key_for_dev_env_0123456789012345",
        "SNOWFLAKE_ACCOUNT": "test_account",
        "SNOWFLAKE_USER": "test_user",
        "SNOWFLAKE_PASSWORD": "test_snowflake_password",
        "SNOWFLAKE_WAREHOUSE": "test_warehouse",
        "AWS_ACCESS_KEY_ID": "test_aws_key_id",
        "AWS_SECRET_ACCESS_KEY": "test_aws_secret_key",
        "S3_BUCKET": "test_s3_bucket",
        "RATE_LIMIT_PER_MINUTE": "100",
        "DAILY_COST_BUDGET_USD": "500.0",
        "COST_ALERT_THRESHOLD_PCT": "0.8",
        "HITL_SCORE_CHANGE_THRESHOLD": "15.0",
        "HITL_EBITDA_PROJECTION_THRESHOLD": "10.0",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
        "OPENAI_API_KEY": "", 
        "ANTHROPIC_API_KEY": "",
    }

if "current_page" not in st.session_state:
    st.session_state.current_page = "Introduction"
if "validation_result" not in st.session_state:
    st.session_state.validation_result = None
if "dimension_weights_input" not in st.session_state:
    st.session_state.dimension_weights_input = {
        "W_DATA_INFRA": 0.18, "W_AI_GOVERNANCE": 0.15, "W_TECH_STACK": 0.15,
        "W_TALENT": 0.17, "W_LEADERSHIP": 0.13, "W_USE_CASES": 0.12, "W_CULTURE": 0.10
    }
if "selected_scenario" not in st.session_state:
    st.session_state.selected_scenario = list(scenarios.keys())[0] if scenarios else None
if "custom_scenario_env_vars_text" not in st.session_state:
    st.session_state.custom_scenario_env_vars_text = ""

# Sidebar navigation
page_options = [
    "Introduction",
    "1. Core Application Configuration",
    "2. Operational Integrity: Field Validation",
    "3. Business Logic: Cross-Field Validation",
    "4. Production Hardening: Conditional Validation",
    "5. Configuration Simulator & Troubleshooting"
]
st.sidebar.title("PE Intelligence Platform")
selected_page = st.sidebar.selectbox("Navigate Sections", page_options, key="current_page")

if st.session_state.current_page == "Introduction":
    st.title("Safeguarding the PE Intelligence Platform: Robust Configuration with Pydantic v2")

    st.markdown(f"")
    st.markdown(f"As a **Software Developer** building the Organizational AIR Scoring platform, ensuring the robustness and security of our application configurations is paramount. Every new feature or data processing service we deploy relies on correct, consistent, and validated settings across different environments – development, staging, and crucially, production. A single misconfigured parameter, such as an incorrect API key, an out-of-bounds budget, or an improperly weighted scoring dimension, can lead to critical application crashes, compromised data integrity, or skewed analytical outcomes that directly impact investment decisions.")
    st.markdown(f"")
    st.markdown(f"This application outlines a real-world workflow to implement a highly reliable configuration system using Pydantic v2. Our goal is to prevent these costly configuration-related bugs by enforcing strict validation rules at application startup, significantly reducing operational overhead and building trust in our platform's outputs. We will walk through defining settings, applying various validation types, and simulating different environmental scenarios to demonstrate how invalid configurations are caught *before* they can cause harm.")
    st.markdown(f"---")
    st.markdown(f"")
    st.markdown(f"### 1. Initial Setup: Environment and Dependencies")
    st.markdown(f"Before we dive into defining and validating our application settings, let's ensure our environment has all the necessary tools. We'll specifically need `pydantic` and `pydantic-settings` for robust configuration management. This application assumes these are already installed in your Python environment.")
    st.markdown(f"")
    st.markdown(f"Next, we'll import the core components from Pydantic and Python's standard library that we'll use throughout this workflow. In this Streamlit application, these are imported from the `source.py` module.")
    st.markdown(f"---")

elif st.session_state.current_page == "1. Core Application Configuration":
    st.title("1. Setting the Stage: Core Application Configuration")
    st.markdown(f"")
    st.markdown(f"As a Software Developer, my first step in configuring a new service for the PE intelligence platform is to define its fundamental settings. These include basic application metadata, environment specification, logging preferences, and crucial sensitive data like secret keys. Using Pydantic's `BaseSettings` and `SettingsConfigDict` allows us to define these in a structured, type-hinted manner, automatically loading from environment variables or `.env` files.")
    st.markdown(f"")
    st.markdown(f"For sensitive information, like the `SECRET_KEY`, we employ Pydantic's `SecretStr` type. This ensures that the value is never accidentally logged or exposed, enhancing the security posture of our application.")
    st.markdown(f"")
    st.markdown(f"#### Workflow Task: Define Base Application Settings")
    st.markdown(f"We will define the `Settings` class, which will serve as the single source of truth for our application's configuration. Use the inputs below to configure the basic settings.")
    st.markdown(f"")

    with st.form("core_settings_form"):
        st.subheader("Application Metadata")
        app_name = st.text_input("APP_NAME", value=st.session_state.env_vars_input.get("APP_NAME"))
        app_version = st.text_input("APP_VERSION", value=st.session_state.env_vars_input.get("APP_VERSION"))
        
        app_env_options = ["development", "staging", "production"]
        current_app_env = st.session_state.env_vars_input.get("APP_ENV")
        app_env_index = app_env_options.index(current_app_env) if current_app_env in app_env_options else 0
        app_env = st.selectbox("APP_ENV", app_env_options, index=app_env_index)
        
        debug_mode = st.checkbox("DEBUG", value=st.session_state.env_vars_input.get("DEBUG") == "True")
        
        log_level_options = ["DEBUG", "INFO", "WARNING", "ERROR"]
        current_log_level = st.session_state.env_vars_input.get("LOG_LEVEL")
        log_level_index = log_level_options.index(current_log_level) if current_log_level in log_level_options else 1
        log_level = st.selectbox("LOG_LEVEL", log_level_options, index=log_level_index)

        st.subheader("Security & Database Credentials (Required for Settings Instantiation)")
        secret_key = st.text_input("SECRET_KEY", value=st.session_state.env_vars_input.get("SECRET_KEY"), type="password")
        
        st.markdown(f"")
        st.markdown(f"**Snowflake Configuration:**")
        snowflake_account = st.text_input("SNOWFLAKE_ACCOUNT", value=st.session_state.env_vars_input.get("SNOWFLAKE_ACCOUNT"))
        snowflake_user = st.text_input("SNOWFLAKE_USER", value=st.session_state.env_vars_input.get("SNOWFLAKE_USER"))
        snowflake_password = st.text_input("SNOWFLAKE_PASSWORD", value=st.session_state.env_vars_input.get("SNOWFLAKE_PASSWORD"), type="password")
        snowflake_warehouse = st.text_input("SNOWFLAKE_WAREHOUSE", value=st.session_state.env_vars_input.get("SNOWFLAKE_WAREHOUSE"))

        st.markdown(f"")
        st.markdown(f"**AWS Configuration:**")
        aws_access_key_id = st.text_input("AWS_ACCESS_KEY_ID", value=st.session_state.env_vars_input.get("AWS_ACCESS_KEY_ID"), type="password")
        aws_secret_access_key = st.text_input("AWS_SECRET_ACCESS_KEY", value=st.session_state.env_vars_input.get("AWS_SECRET_ACCESS_KEY"), type="password")
        s3_bucket = st.text_input("S3_BUCKET", value=st.session_state.env_vars_input.get("S3_BUCKET"))

        submitted = st.form_submit_button("Load Default Settings")
        if submitted:
            # Update session state with current form values
            st.session_state.env_vars_input.update({
                "APP_NAME": app_name,
                "APP_VERSION": app_version,
                "APP_ENV": app_env,
                "DEBUG": str(debug_mode),
                "LOG_LEVEL": log_level,
                "SECRET_KEY": secret_key,
                "SNOWFLAKE_ACCOUNT": snowflake_account,
                "SNOWFLAKE_USER": snowflake_user,
                "SNOWFLAKE_PASSWORD": snowflake_password,
                "SNOWFLAKE_WAREHOUSE": snowflake_warehouse,
                "AWS_ACCESS_KEY_ID": aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": aws_secret_access_key,
                "S3_BUCKET": s3_bucket,
            })

            clear_env() # Clear all tracked environment variables before setting new ones
            for key, value in st.session_state.env_vars_input.items():
                os.environ[key] = value

            get_settings_with_prod_validation.cache_clear() # Clear cache to force reload
            try:
                current_settings = get_settings_with_prod_validation()
                st.session_state.validation_result = {
                    "status": "SUCCESS",
                    "message": "Default Application Settings Loaded Successfully!",
                    "settings": {
                        "App Name": current_settings.APP_NAME,
                        "Environment": current_settings.APP_ENV,
                        "Debug Mode": current_settings.DEBUG,
                        "Secret Key Set": "Yes" if current_settings.SECRET_KEY.get_secret_value() else "No",
                        "Secret Key (masked value)": str(current_settings.SECRET_KEY), 
                        "Snowflake Account": current_settings.SNOWFLAKE_ACCOUNT,
                        "AWS Region": current_settings.AWS_REGION
                    }
                }
            except ValidationError as e:
                st.session_state.validation_result = {
                    "status": "FAILURE",
                    "message": f"Error loading settings: {e}"
                }
            except Exception as e:
                st.session_state.validation_result = {
                    "status": "FAILURE",
                    "message": f"An unexpected error occurred: {e}"
                }
            finally:
                clear_env() # Clean up environment variables

    if st.session_state.validation_result:
        st.markdown(f"---")
        st.subheader("Validation Result:")
        if st.session_state.validation_result["status"] == "SUCCESS":
            st.success(st.session_state.validation_result["message"])
            for key, value in st.session_state.validation_result["settings"].items():
                st.write(f"- **{key}**: {value}")
        else:
            st.error(st.session_state.validation_result["message"])

    st.markdown(f"")
    st.markdown(f"#### Explanation of Execution")
    st.markdown(f"The interaction above demonstrates how Pydantic loads configuration. When you click 'Load Default Settings', the application attempts to initialize the `Settings` class using the provided inputs as environment variables. The `SECRET_KEY` is handled by `SecretStr`, ensuring its value is masked when accessed directly (e.g., in `print()`) but can be retrieved using `.get_secret_value()` when needed for actual application logic. This direct usage of `SecretStr` helps us, as developers, prevent accidental exposure of sensitive credentials, a common source of security vulnerabilities.")
    st.markdown(f"---")

elif st.session_state.current_page == "2. Operational Integrity: Field Validation":
    st.title("2. Ensuring Operational Integrity: Field-Level Validation")
    st.markdown(f"")
    st.markdown(f"Operational parameters like API rate limits, daily cost budgets, and alert thresholds are critical for the stability and cost-effectiveness of our PE intelligence platform. As a Data Engineer, I need to ensure these values are always within sensible, predefined ranges to prevent system overload, budget overruns, or ineffective alerting. Pydantic's `Field` with `ge` (greater than or equal to) and `le` (less than or equal to) arguments allows us to enforce these constraints directly within the configuration definition.")
    st.markdown(f"")
    st.markdown(f"#### Workflow Task: Validate Operational Parameters with Range Constraints")
    st.markdown(f"Adjust the values below for API rate limits, daily cost budget, and alert thresholds. Observe how the validation system reacts to values outside the allowed ranges.")
    st.markdown(f"")

    with st.form("operational_settings_form"):
        st.subheader("API and Cost Management Settings")
        rate_limit = st.number_input("RATE_LIMIT_PER_MINUTE (Range: 1 to 1000)", min_value=1, max_value=10000, value=int(st.session_state.env_vars_input.get("RATE_LIMIT_PER_MINUTE", "100")), step=1)
        daily_cost_budget = st.number_input("DAILY_COST_BUDGET_USD (Range: >= 0)", min_value=0.0, value=float(st.session_state.env_vars_input.get("DAILY_COST_BUDGET_USD", "1000.0")), step=50.0)
        cost_alert_threshold = st.number_input("COST_ALERT_THRESHOLD_PCT (Range: 0 to 1)", min_value=0.0, max_value=1.0, value=float(st.session_state.env_vars_input.get("COST_ALERT_THRESHOLD_PCT", "0.75")), step=0.01, format="%.2f")

        st.subheader("Human-In-The-Loop (HITL) Thresholds")
        hitl_score_change = st.number_input("HITL_SCORE_CHANGE_THRESHOLD (Range: 5 to 30)", min_value=5.0, max_value=30.0, value=float(st.session_state.env_vars_input.get("HITL_SCORE_CHANGE_THRESHOLD", "20.0")), step=1.0)
        hitl_ebitda_projection = st.number_input("HITL_EBITDA_PROJECTION_THRESHOLD (Range: 5 to 25)", min_value=5.0, max_value=25.0, value=float(st.session_state.env_vars_input.get("HITL_EBITDA_PROJECTION_THRESHOLD", "15.0")), step=1.0)

        submitted = st.form_submit_button("Validate Operational Settings")
        if submitted:
            # Update session state with current form values
            st.session_state.env_vars_input.update({
                "RATE_LIMIT_PER_MINUTE": str(int(rate_limit)),
                "DAILY_COST_BUDGET_USD": str(float(daily_cost_budget)),
                "COST_ALERT_THRESHOLD_PCT": str(float(cost_alert_threshold)),
                "HITL_SCORE_CHANGE_THRESHOLD": str(float(hitl_score_change)),
                "HITL_EBITDA_PROJECTION_THRESHOLD": str(float(hitl_ebitda_projection)),
            })

            clear_env()
            for key, value in st.session_state.env_vars_input.items():
                os.environ[key] = value

            get_settings_with_prod_validation.cache_clear()
            try:
                validated_settings = get_settings_with_prod_validation()
                st.session_state.validation_result = {
                    "status": "SUCCESS",
                    "message": "Operational parameters are VALID.",
                    "settings": {
                        "API Rate Limit": f"{validated_settings.RATE_LIMIT_PER_MINUTE} req/min",
                        "Daily Cost Budget": f"${validated_settings.DAILY_COST_BUDGET_USD}",
                        "Cost Alert Threshold": f"{validated_settings.COST_ALERT_THRESHOLD_PCT*100:.0f}%",
                        "HITL Score Change Threshold": f"{validated_settings.HITL_SCORE_CHANGE_THRESHOLD}",
                        "HITL EBITDA Projection Threshold": f"{validated_settings.HITL_EBITDA_PROJECTION_THRESHOLD}"
                    }
                }
            except ValidationError as e:
                st.session_state.validation_result = {
                    "status": "FAILURE",
                    "message": f"Operational parameters are INVALID. Details: {e}"
                }
            except Exception as e:
                st.session_state.validation_result = {
                    "status": "FAILURE",
                    "message": f"An unexpected error occurred: {e}"
                }
            finally:
                clear_env()

    if st.session_state.validation_result:
        st.markdown(f"---")
        st.subheader("Validation Result:")
        if st.session_state.validation_result["status"] == "SUCCESS":
            st.success(st.session_state.validation_result["message"])
            for key, value in st.session_state.validation_result["settings"].items():
                st.write(f"- **{key}**: {value}")
        else:
            st.error(st.session_state.validation_result["message"])

    st.markdown(f"")
    st.markdown(f"#### Explanation of Execution")
    st.markdown(f"The scenarios above demonstrate successful loading when all operational parameters are within their defined bounds. When you set values exceeding or falling below the specified ranges, Pydantic immediately raises a `ValidationError`, providing clear, detailed messages about which specific fields failed and why. This automatic, early detection of out-of-bounds values by `Field(ge=X, le=Y)` is crucial. It prevents the system from starting with configurations that could lead to financial losses (e.g., negative budget), operational issues (e.g., excessively high rate limits), or ineffective human-in-the-loop interventions due to inappropriate thresholds.")
    st.markdown(f"---")

elif st.session_state.current_page == "3. Business Logic: Cross-Field Validation":
    st.title("3. Implementing Business Logic: Cross-Field Validation for Scoring Weights")
    st.markdown(f"")
    st.markdown(f"A core component of the PE intelligence platform is its investment scoring model, which relies on various dimensions (e.g., data infrastructure, AI governance, talent). The relative importance of these dimensions is defined by a set of weights. A critical business rule mandates that these **dimension weights must sum up to exactly 1.0** to ensure a coherent and balanced scoring mechanism. Deviations from this sum would lead to skewed, unreliable scores and potentially poor investment recommendations.")
    st.markdown(f"")
    st.markdown(f"As a Data Engineer, I need to implement a robust check to enforce this rule. Pydantic's `@model_validator(mode=\"after\")` is perfect for this, as it allows us to perform validation logic that involves multiple fields *after* individual field validations have passed.")
    st.markdown(f"")
    st.markdown(f"#### Workflow Task: Validate Dimension Weights Sum to 1.0")
    st.markdown(f"Adjust the dimension weights below. The validation check will be:")
    st.markdown(r"$$\left| \sum_{{i=1}}^{{n}} w_i - 1.0 \right| > \epsilon$$")
    st.markdown(r"where $w_i$ are the dimension weights and $\epsilon = 0.001$. Try to make the sum exactly 1.0, or slightly off, to see the validation in action.")
    st.markdown(f"")

    with st.form("dimension_weights_form"):
        st.subheader("Dimension Weights (Sum must be 1.0)")
        weights = {}
        col1, col2, col3 = st.columns(3)
        with col1:
            weights["W_DATA_INFRA"] = st.number_input("Data Infrastructure", min_value=0.0, max_value=1.0, value=st.session_state.dimension_weights_input.get("W_DATA_INFRA"), step=0.01, format="%.2f", key="W_DATA_INFRA_input")
            weights["W_AI_GOVERNANCE"] = st.number_input("AI Governance", min_value=0.0, max_value=1.0, value=st.session_state.dimension_weights_input.get("W_AI_GOVERNANCE"), step=0.01, format="%.2f", key="W_AI_GOVERNANCE_input")
            weights["W_TECH_STACK"] = st.number_input("Tech Stack", min_value=0.0, max_value=1.0, value=st.session_state.dimension_weights_input.get("W_TECH_STACK"), step=0.01, format="%.2f", key="W_TECH_STACK_input")
        with col2:
            weights["W_TALENT"] = st.number_input("Talent", min_value=0.0, max_value=1.0, value=st.session_state.dimension_weights_input.get("W_TALENT"), step=0.01, format="%.2f", key="W_TALENT_input")
            weights["W_LEADERSHIP"] = st.number_input("Leadership", min_value=0.0, max_value=1.0, value=st.session_state.dimension_weights_input.get("W_LEADERSHIP"), step=0.01, format="%.2f", key="W_LEADERSHIP_input")
        with col3:
            weights["W_USE_CASES"] = st.number_input("Use Cases", min_value=0.0, max_value=1.0, value=st.session_state.dimension_weights_input.get("W_USE_CASES"), step=0.01, format="%.2f", key="W_USE_CASES_input")
            weights["W_CULTURE"] = st.number_input("Culture", min_value=0.0, max_value=1.0, value=st.session_state.dimension_weights_input.get("W_CULTURE"), step=0.01, format="%.2f", key="W_CULTURE_input")
        
        current_sum = sum(weights.values())
        st.info(f"Current Sum of Weights: **{current_sum:.3f}**")

        submitted = st.form_submit_button("Validate Dimension Weights")
        if submitted:
            # Update session state with current form values
            st.session_state.dimension_weights_input.update(weights)
            st.session_state.env_vars_input.update({key: str(value) for key, value in weights.items()})
            
            clear_env()
            for key, value in st.session_state.env_vars_input.items():
                os.environ[key] = value

            get_settings_with_prod_validation.cache_clear()
            try:
                validated_settings = get_settings_with_prod_validation()
                dimension_weights_list = [
                    validated_settings.W_DATA_INFRA, validated_settings.W_AI_GOVERNANCE, validated_settings.W_TECH_STACK,
                    validated_settings.W_TALENT, validated_settings.W_LEADERSHIP, validated_settings.W_USE_CASES, validated_settings.W_CULTURE
                ]
                st.session_state.validation_result = {
                    "status": "SUCCESS",
                    "message": f"Dimension weights sum to {sum(dimension_weights_list):.3f}, which is VALID.",
                }
            except ValidationError as e:
                st.session_state.validation_result = {
                    "status": "FAILURE",
                    "message": f"Dimension weights are INVALID. Details: {e}"
                }
            except Exception as e:
                st.session_state.validation_result = {
                    "status": "FAILURE",
                    "message": f"An unexpected error occurred: {e}"
                }
            finally:
                clear_env()

    if st.session_state.validation_result:
        st.markdown(f"---")
        st.subheader("Validation Result:")
        if st.session_state.validation_result["status"] == "SUCCESS":
            st.success(st.session_state.validation_result["message"])
        else:
            st.error(st.session_state.validation_result["message"])

    st.markdown(f"")
    st.markdown(f"#### Explanation of Execution")
    st.markdown(f"The interaction above demonstrates how Pydantic's `@model_validator` enforces cross-field business logic. If the sum of the dimension weights deviates from $1.0$ by more than the small tolerance $\epsilon$, Pydantic raises a `ValidationError`. This validation is critical for the PE intelligence platform, ensuring the investment scoring model is always configured with logically consistent weights, preventing calculation errors that could lead to flawed analytical outputs and incorrect investment decisions. It’s a direct safeguard against subtle yet significant business logic flaws.")
    st.markdown(f"---")

elif st.session_state.current_page == "4. Production Hardening: Conditional Validation":
    st.title("4. Fortifying Production: Conditional Environment-Specific Validation")
    st.markdown(f"")
    st.markdown(f"Deploying to a production environment demands a heightened level of rigor. As a Software Developer, I need to ensure that certain security and operational settings are strictly enforced *only* when the application is running in a `production` environment. For instance, `DEBUG` mode must be disabled, sensitive `SECRET_KEY`s must meet minimum length requirements, and all critical external service API keys (like LLM provider keys) must be present.")
    st.markdown(f"")
    st.markdown(f"This conditional validation logic is best implemented using another `@model_validator(mode=\"after\")`, which allows us to inspect the `APP_ENV` and apply specific rules accordingly. We'll also include a `@field_validator` for `OPENAI_API_KEY` to ensure it starts with the expected \"sk-\" prefix, an example of a specific format requirement.")
    st.markdown(f"")
    st.markdown(f"#### Workflow Task: Enforce Production Security and API Key Presence")
    st.markdown(f"Configure the settings below. Pay close attention to `APP_ENV`. When set to `production`, try to intentionally break the rules (e.g., `DEBUG` True, short `SECRET_KEY`, no LLM API keys) to observe the validation failures.")
    st.markdown(f"")

    with st.form("prod_validation_form"):
        st.subheader("General Application Settings")
        app_env_options = ["development", "staging", "production"]
        current_app_env = st.session_state.env_vars_input.get("APP_ENV")
        app_env_index = app_env_options.index(current_app_env) if current_app_env in app_env_options else 0
        app_env_prod = st.selectbox("APP_ENV", app_env_options, index=app_env_index, key="app_env_prod_input")
        
        debug_mode_prod = st.checkbox("DEBUG Mode", value=st.session_state.env_vars_input.get("DEBUG") == "True", key="debug_mode_prod_input")
        secret_key_prod = st.text_input("SECRET_KEY (min 32 chars in production)", value=st.session_state.env_vars_input.get("SECRET_KEY"), type="password", key="secret_key_prod_input")

        st.subheader("LLM Provider API Keys (One required in production)")
        openai_api_key = st.text_input("OPENAI_API_KEY (e.g., sk-...) (Optional in Dev)", value=st.session_state.env_vars_input.get("OPENAI_API_KEY"), type="password", key="openai_api_key_input")
        anthropic_api_key = st.text_input("ANTHROPIC_API_KEY (Optional in Dev)", value=st.session_state.env_vars_input.get("ANTHROPIC_API_KEY"), type="password", key="anthropic_api_key_input")

        submitted = st.form_submit_button("Validate Production Settings")
        if submitted:
            # Update session state with current form values
            st.session_state.env_vars_input.update({
                "APP_ENV": app_env_prod,
                "DEBUG": str(debug_mode_prod),
                "SECRET_KEY": secret_key_prod,
                "OPENAI_API_KEY": openai_api_key,
                "ANTHROPIC_API_KEY": anthropic_api_key,
            })

            clear_env()
            for key, value in st.session_state.env_vars_input.items():
                os.environ[key] = value

            get_settings_with_prod_validation.cache_clear()
            try:
                validated_settings = get_settings_with_prod_validation()
                st.session_state.validation_result = {
                    "status": "SUCCESS",
                    "message": "Production settings are VALID.",
                    "settings": {
                        "APP_ENV": validated_settings.APP_ENV,
                        "DEBUG": validated_settings.DEBUG,
                        "SECRET_KEY length": len(validated_settings.SECRET_KEY.get_secret_value()),
                        "OpenAI API Key provided": "Yes" if validated_settings.OPENAI_API_KEY else "No",
                        "Anthropic API Key provided": "Yes" if validated_settings.ANTHROPIC_API_KEY else "No",
                    }
                }
            except ValidationError as e:
                st.session_state.validation_result = {
                    "status": "FAILURE",
                    "message": f"Production settings are INVALID. Details: {e}"
                }
            except Exception as e:
                st.session_state.validation_result = {
                    "status": "FAILURE",
                    "message": f"An unexpected error occurred: {e}"
                }
            finally:
                clear_env()

    if st.session_state.validation_result:
        st.markdown(f"---")
        st.subheader("Validation Result:")
        if st.session_state.validation_result["status"] == "SUCCESS":
            st.success(st.session_state.validation_result["message"])
            for key, value in st.session_state.validation_result["settings"].items():
                st.write(f"- **{key}**: {value}")
        else:
            st.error(st.session_state.validation_result["message"])

    st.markdown(f"")
    st.markdown(f"#### Explanation of Execution")
    st.markdown(f"This section vividly demonstrates the power of conditional and field-specific validation. When `APP_ENV` is `production`, specific rules are enforced for `DEBUG` mode, `SECRET_KEY` length, and the presence of LLM API keys. The `@field_validator` for `OPENAI_API_KEY` catches malformed keys. These explicit error messages at application startup are invaluable, preventing the deployment of insecure or non-functional configurations to live environments, drastically reducing the risk of security breaches, service outages, or unexpected runtime behavior stemming from configuration errors.")
    st.markdown(f"---")

elif st.session_state.current_page == "5. Configuration Simulator & Troubleshooting":
    st.title("5. Catching Errors Early: Configuration Simulation and Reporting")
    st.markdown(f"")
    st.markdown(f"The ultimate value of a robust configuration validation system is its ability to prevent failures before they impact users. As a Data Engineer preparing a deployment, I need a way to confidently verify that a given set of environment variables or configuration files will result in a valid application state. This \"Validated Configuration Report\" ensures that any potential issues are identified and resolved during development or staging, rather than during a critical production rollout.")
    st.markdown(f"")
    st.markdown(f"We can simulate different configuration scenarios and observe Pydantic's error reporting. This acts as our \"report,\" detailing what works and what breaks, and why.")
    st.markdown(f"")
    st.markdown(f"#### Workflow Task: Simulate Configuration Scenarios and Generate a Validation Report")
    st.markdown(f"Select a pre-defined scenario or provide your own environment variables to simulate a configuration load. The application will attempt to load the settings and report any validation issues.")
    st.markdown(f"")

    scenario_names = list(scenarios.keys())
    current_scenario = st.session_state.selected_scenario
    scenario_index = scenario_names.index(current_scenario) if current_scenario in scenario_names else 0
    selected_scenario_name = st.selectbox("Select a Pre-defined Scenario", scenario_names, key="selected_scenario", index=scenario_index)

    st.markdown(f"")
    st.subheader("Custom Environment Variables (Optional)")
    st.markdown(f"Provide key-value pairs separated by `=` on each line. These will override selected scenario settings or be used if no scenario is chosen.")
    custom_env_vars_text = st.text_area(
        "Enter custom environment variables (e.g., `APP_ENV=production\nDEBUG=True`)",
        value=st.session_state.custom_scenario_env_vars_text,
        height=200, key="custom_scenario_env_vars_text_input"
    )

    simulation_button = st.button("Run Configuration Simulation")

    if simulation_button:
        # Prepare environment variables for simulation
        env_vars_to_apply = {}
        # Apply base defaults from session_state for any unmentioned keys
        env_vars_to_apply.update(st.session_state.env_vars_input) 

        if selected_scenario_name:
            env_vars_to_apply.update(scenarios[selected_scenario_name])

        # Parse custom environment variables, overriding existing
        if custom_env_vars_text:
            for line in custom_env_vars_text.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars_to_apply[key.strip()] = value.strip()
        
        # Store custom input for persistence
        st.session_state.custom_scenario_env_vars_text = custom_env_vars_text

        st.subheader("Simulation Result:")
        clear_env() # Ensure a clean slate before setting new env vars
        for key, value in env_vars_to_apply.items():
            os.environ[key] = value

        get_settings_with_prod_validation.cache_clear() # Clear cache for new env vars
        try:
            settings_obj = get_settings_with_prod_validation()
            st.success(f"SUCCESS: Configuration is VALID for the selected scenario and custom inputs.")
            st.write(f"- **APP_ENV**: {settings_obj.APP_ENV}")
            st.write(f"- **DEBUG**: {settings_obj.DEBUG}")
            st.write(f"- **SECRET_KEY (masked)**: {settings_obj.SECRET_KEY}")
            
            dimension_weights_sum = sum([
                settings_obj.W_DATA_INFRA, settings_obj.W_AI_GOVERNANCE, settings_obj.W_TECH_STACK,
                settings_obj.W_TALENT, settings_obj.W_LEADERSHIP, settings_obj.W_USE_CASES, settings_obj.W_CULTURE
            ])
            st.write(f"- **Dimension Weights Sum**: {dimension_weights_sum:.3f}")
            st.write(f"- **OpenAI API Key Set**: {'Yes' if settings_obj.OPENAI_API_KEY else 'No'}")
            st.write(f"- **Anthropic API Key Set**: {'Yes' if settings_obj.ANTHROPIC_API_KEY else 'No'}")

        except ValidationError as e:
            st.error(f"FAILURE: Configuration is INVALID. Details:")
            st.exception(e) # Streamlit's way to show detailed exception
        except Exception as e:
            st.error(f"FAILURE: An unexpected error occurred during simulation:")
            st.exception(e)
        finally:
            clear_env() # Always clean up environment variables

    st.markdown(f"---")
    st.markdown(f"#### Explanation of Execution")
    st.markdown(f"This final section serves as our \"Validated Configuration Report.\" By simulating a range of realistic configuration scenarios – both valid and invalid – we demonstrate the comprehensive safety net provided by Pydantic's validation. Each simulation attempt clears the environment, sets specific variables, attempts to load the `Settings`, and reports the outcome.")
    st.markdown(f"")
    st.markdown(f"The output clearly shows how valid configurations pass all checks and how specific, critical errors (like `DEBUG` mode in production, incorrect weight sums, or out-of-range API limits) are immediately identified. The exact `ValidationError` messages provide detailed information, pointing directly to the faulty parameter and the reason for the failure.")
    st.markdown(f"")
    st.markdown(f"For a Software Developer or Data Engineer, this process allows for exhaustive testing of configuration permutations. It means that before any new feature or service is deployed to the PE intelligence platform, its configuration can be \"pre-validated.\" This drastically reduces the risk of deployment failures and runtime errors, leading to a more stable, secure, and reliable platform. The proactive identification of issues at startup prevents wasted time debugging issues in live systems and ensures that the platform's critical business logic is always operating on correctly defined parameters.")
    st.markdown(f"---")

    st.markdown(f"### Common Mistakes & Troubleshooting")
    st.markdown(f"Understanding common pitfalls can accelerate development and debugging:")
    st.markdown(f"\u274c **Mistake 1: Dimension weights don't sum to 1.0**")
    st.markdown(f"```python\nW_DATA_INFRA = 0.20\nW_AI_GOVERNANCE = 0.15\nW_TECH_STACK = 0.15\nW_TALENT = 0.20\nW_LEADERSHIP = 0.15\nW_USE_CASES = 0.10\nW_CULTURE = 0.10\n# Sum = 1.05!\n```")
    st.markdown(f"**Fix:** The `model_validator` catches this at startup with a clear error message. Ensure your weights sum to 1.0 within the allowed tolerance.")
    st.markdown(f"")
    st.markdown(f"\u274c **Mistake 2: Exposing secrets in logs**")
    st.markdown(f"```python\nlogger.info(\"connecting\", password=settings.SNOWFLAKE_PASSWORD)\n```")
    st.markdown(f"**Fix:** Use `SecretStr` which masks values automatically when accessed directly. Use `.get_secret_value()` only when the raw secret is absolutely necessary for connecting to an external service.")
    st.markdown(f"")
    st.markdown(f"\u274c **Mistake 3: Missing lifespan context manager**")
    st.markdown(f"```python\napp = FastAPI()\nredis_client = Redis() # Leaks on shutdown!\n```")
    st.markdown(f"**Fix:** Always use FastAPI's `lifespan` context manager (`@asynccontextmanager`) for resource management (e.g., database connections, Redis clients) to ensure proper cleanup on shutdown.")
    st.markdown(f"")
    st.markdown(f"\u274c **Mistake 4: Not validating at startup**")
    st.markdown(f"```python\ndef get_sector_baseline(sector_id):\n    return db.query(...) # Database not connected!\n```")
    st.markdown(f"**Fix:** Run validation scripts or load your Pydantic `Settings` *before* the application starts serving requests. This ensures that any critical dependencies (like database connections) are properly configured and validated, preventing runtime failures.")
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
