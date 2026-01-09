
from streamlit.testing.v1 import AppTest
import pytest
import os
import sys

# Mocking `source` module components for testing purposes.
# In a real testing environment, ensure your actual `source.py` file is accessible.

class SecretStr:
    """Mock for Pydantic's SecretStr."""
    def __init__(self, value):
        self._value = value
    def get_secret_value(self):
        return self._value
    def __str__(self):
        return "********" if self._value else ""

class ValidationError(Exception):
    """Mock for Pydantic's ValidationError."""
    pass

# Mock scenarios dictionary as it's used directly in the app
scenarios = {
    "Development": {
        "APP_ENV": "development", "DEBUG": "True", "SECRET_KEY": "a_short_dev_key",
        "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": "",
        "RATE_LIMIT_PER_MINUTE": "100", "DAILY_COST_BUDGET_USD": "500.0", "COST_ALERT_THRESHOLD_PCT": "0.8",
        "HITL_SCORE_CHANGE_THRESHOLD": "15.0", "HITL_EBITDA_PROJECTION_THRESHOLD": "10.0",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
    },
    "Production Valid": {
        "APP_ENV": "production", "DEBUG": "False", "SECRET_KEY": "a_very_long_and_secure_secret_key_for_production_env",
        "OPENAI_API_KEY": "sk-validapikey1234567890", "ANTHROPIC_API_KEY": "anthropic_valid_key",
        "RATE_LIMIT_PER_MINUTE": "100", "DAILY_COST_BUDGET_USD": "500.0", "COST_ALERT_THRESHOLD_PCT": "0.8",
        "HITL_SCORE_CHANGE_THRESHOLD": "15.0", "HITL_EBITDA_PROJECTION_THRESHOLD": "10.0",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
    },
    "Production Debug On": { # This scenario is designed to be invalid
        "APP_ENV": "production", "DEBUG": "True", # Invalid in production
        "SECRET_KEY": "a_very_long_and_secure_secret_key_for_production_env",
        "OPENAI_API_KEY": "sk-validapikey1234567890", "ANTHROPIC_API_KEY": "anthropic_valid_key",
        "RATE_LIMIT_PER_MINUTE": "100", "DAILY_COST_BUDGET_USD": "500.0", "COST_ALERT_THRESHOLD_PCT": "0.8",
        "HITL_SCORE_CHANGE_THRESHOLD": "15.0", "HITL_EBITDA_PROJECTION_THRESHOLD": "10.0",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
    },
    "Weights Sum Invalid": { # This scenario is designed to be invalid
        "APP_ENV": "development", "DEBUG": "False", "SECRET_KEY": "a_dev_key_length_ok",
        "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": "",
        "RATE_LIMIT_PER_MINUTE": "100", "DAILY_COST_BUDGET_USD": "500.0", "COST_ALERT_THRESHOLD_PCT": "0.8",
        "HITL_SCORE_CHANGE_THRESHOLD": "15.0", "HITL_EBITDA_PROJECTION_THRESHOLD": "10.0",
        "W_DATA_INFRA": "0.20", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.20", "W_LEADERSHIP": "0.15", "W_USE_CASES": "0.10", "W_CULTURE": "0.10", # Sums to 1.05
    },
    "Rate Limit Invalid": { # This scenario is designed to be invalid
        "APP_ENV": "development", "DEBUG": "False", "SECRET_KEY": "a_dev_key_length_ok",
        "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": "",
        "RATE_LIMIT_PER_MINUTE": "0", # Invalid (min_value=1)
        "DAILY_COST_BUDGET_USD": "500.0", "COST_ALERT_THRESHOLD_PCT": "0.8",
        "HITL_SCORE_CHANGE_THRESHOLD": "15.0", "HITL_EBITDA_PROJECTION_THRESHOLD": "10.0",
        "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
        "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
    }
}

class MockSettings:
    """A simple mock for the Pydantic Settings object."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.SECRET_KEY = SecretStr(kwargs.get("SECRET_KEY", "default_secret"))
        self.AWS_REGION = "us-east-1" # Default value as per app behavior, not directly set in env_vars_input

# Mock for `clear_env` function from `source.py`
def clear_env():
    """A mock function to simulate clearing environment variables."""
    # In a real test, this might clear specific env vars to ensure clean state
    # For AppTest, a fresh run often handles this.
    pass

# Mock for `get_settings_with_prod_validation` from `source.py`
def get_settings_with_prod_validation():
    """A mock function to simulate Pydantic's settings loading and validation."""
    current_env = os.environ.get("APP_ENV", "development")
    debug_mode = os.environ.get("DEBUG", "False") == "True"
    secret_key = os.environ.get("SECRET_KEY", "default_secret")
    rate_limit = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "100"))
    daily_cost_budget = float(os.environ.get("DAILY_COST_BUDGET_USD", "500.0"))
    cost_alert_threshold = float(os.environ.get("COST_ALERT_THRESHOLD_PCT", "0.75"))
    hitl_score_change = float(os.environ.get("HITL_SCORE_CHANGE_THRESHOLD", "15.0"))
    hitl_ebitda_projection = float(os.environ.get("HITL_EBITDA_PROJECTION_THRESHOLD", "10.0"))
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    # Retrieve weights, converting to float for sum calculation
    w_data_infra = float(os.environ.get("W_DATA_INFRA", "0.18"))
    w_ai_governance = float(os.environ.get("W_AI_GOVERNANCE", "0.15"))
    w_tech_stack = float(os.environ.get("W_TECH_STACK", "0.15"))
    w_talent = float(os.environ.get("W_TALENT", "0.17"))
    w_leadership = float(os.environ.get("W_LEADERSHIP", "0.13"))
    w_use_cases = float(os.environ.get("W_USE_CASES", "0.12"))
    w_culture = float(os.environ.get("W_CULTURE", "0.10"))

    errors = []

    # Field-level validations
    if not (1 <= rate_limit <= 10000):
        errors.append("RATE_LIMIT_PER_MINUTE must be between 1 and 10000.")
    if not (daily_cost_budget >= 0.0):
        errors.append("DAILY_COST_BUDGET_USD must be non-negative.")
    if not (0.0 <= cost_alert_threshold <= 1.0):
        errors.append("COST_ALERT_THRESHOLD_PCT must be between 0.0 and 1.0.")
    if not (5.0 <= hitl_score_change <= 30.0):
        errors.append("HITL_SCORE_CHANGE_THRESHOLD must be between 5.0 and 30.0.")
    if not (5.0 <= hitl_ebitda_projection <= 25.0):
        errors.append("HITL_EBITDA_PROJECTION_THRESHOLD must be between 5.0 and 25.0.")
    if openai_api_key and not openai_api_key.startswith("sk-"):
        errors.append("OPENAI_API_KEY must start with 'sk-'.")

    # Cross-field validation for dimension weights
    weights_sum = sum([w_data_infra, w_ai_governance, w_tech_stack, w_talent, w_leadership, w_use_cases, w_culture])
    if abs(weights_sum - 1.0) > 0.001:
        errors.append(f"Dimension weights must sum to approximately 1.0 (current sum: {weights_sum:.3f}).")

    # Conditional validation for production environment
    if current_env == "production":
        if debug_mode:
            errors.append("DEBUG must be False in production environment.")
        if len(secret_key) < 32:
            errors.append("SECRET_KEY must be at least 32 characters long in production environment.")
        if not (openai_api_key or anthropic_api_key):
            errors.append("At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required in production.")

    if errors:
        raise ValidationError("\n".join(errors))

    # Construct and return a MockSettings object if validation passes
    return MockSettings(
        APP_NAME=os.environ.get("APP_NAME", "PE Org-AI-R Platform"),
        APP_VERSION=os.environ.get("APP_VERSION", "4.0.0"),
        APP_ENV=current_env,
        DEBUG=debug_mode,
        LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
        SECRET_KEY=secret_key,
        SNOWFLAKE_ACCOUNT=os.environ.get("SNOWFLAKE_ACCOUNT", "test_account"),
        SNOWFLAKE_USER=os.environ.get("SNOWFLAKE_USER", "test_user"),
        SNOWFLAKE_PASSWORD=os.environ.get("SNOWFLAKE_PASSWORD", "test_snowflake_password"),
        SNOWFLAKE_WAREHOUSE=os.environ.get("SNOWFLAKE_WAREHOUSE", "test_warehouse"),
        AWS_ACCESS_KEY_ID=os.environ.get("AWS_ACCESS_KEY_ID", "test_aws_key_id"),
        AWS_SECRET_ACCESS_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY", "test_aws_secret_key"),
        S3_BUCKET=os.environ.get("S3_BUCKET", "test_s3_bucket"),
        RATE_LIMIT_PER_MINUTE=rate_limit,
        DAILY_COST_BUDGET_USD=daily_cost_budget,
        COST_ALERT_THRESHOLD_PCT=cost_alert_threshold,
        HITL_SCORE_CHANGE_THRESHOLD=hitl_score_change,
        HITL_EBITDA_PROJECTION_THRESHOLD=hitl_ebitda_projection,
        W_DATA_INFRA=w_data_infra, W_AI_GOVERNANCE=w_ai_governance, W_TECH_STACK=w_tech_stack,
        W_TALENT=w_talent, W_LEADERSHIP=w_leadership, W_USE_CASES=w_use_cases, W_CULTURE=w_culture,
        OPENAI_API_KEY=openai_api_key, ANTHROPIC_API_KEY=anthropic_api_key,
    )

# Mock cache_clear method for the mocked function
get_settings_with_prod_validation.cache_clear = lambda: None

# Inject mocks into the `source` module for the `AppTest` to import them
# This is crucial for AppTest to find the imported functions and classes.
sys.modules['source'] = sys.modules[__name__]


def test_initial_page_load():
    """Verify that the app loads correctly and the initial page content is as expected."""
    at = AppTest.from_file("app.py").run()
    assert at.title[0].value == "QuLab: Foundation and Platform Setup"
    # The subheader 'Validation Result:' is displayed even on initial load due to session state initialization
    assert at.subheader[0].value == "Validation Result:"
    assert at.sidebar.selectbox[0].value == "Introduction"
    assert "Safeguarding the PE Intelligence Platform" in at.title[1].value


def test_navigate_to_core_config_page():
    """Verify navigation to the 'Core Application Configuration' page and check initial content."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("1. Core Application Configuration").run()
    assert at.title[1].value == "1. Setting the Stage: Core Application Configuration"
    assert at.text_input[0].value == "PE Org-AI-R Platform"  # Check default APP_NAME


def test_core_config_valid_submission():
    """Test submitting the Core Application Configuration form with valid data."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("1. Core Application Configuration").run()

    # Update some values to ensure form interaction works
    at.text_input[0].set_value("My New Platform").run() # APP_NAME
    at.selectbox[0].set_value("production").run() # APP_ENV
    at.checkbox[0].set_value(False).run() # DEBUG
    # Ensure SECRET_KEY is long enough for potential production validation (even if not strictly enforced on this page)
    at.text_input[2].set_value("this_is_a_sufficiently_long_secret_key_for_testing_12345").run()

    at.form[0].submit().run()

    assert at.success[0].value == "Default Application Settings Loaded Successfully!"
    assert "App Name: My New Platform" in at.markdown[2].value
    assert "Secret Key (masked value): ********" in at.markdown[2].value


def test_operational_integrity_valid_submission():
    """Test submitting the Operational Integrity form with values within valid ranges."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("2. Operational Integrity: Field Validation").run()

    at.number_input[0].set_value(500).run()  # RATE_LIMIT_PER_MINUTE (default is 100)
    at.number_input[1].set_value(750.0).run() # DAILY_COST_BUDGET_USD (default is 500.0)
    at.number_input[2].set_value(0.9).run()  # COST_ALERT_THRESHOLD_PCT (default is 0.8)
    at.number_input[3].set_value(10.0).run() # HITL_SCORE_CHANGE_THRESHOLD (default is 15.0)
    at.number_input[4].set_value(10.0).run() # HITL_EBITDA_PROJECTION_THRESHOLD (default is 10.0)

    at.form[0].submit().run()

    assert at.success[0].value == "Operational parameters are VALID."
    assert "API Rate Limit: 500 req/min" in at.markdown[2].value


def test_operational_integrity_invalid_rate_limit():
    """Test submitting the Operational Integrity form with an invalid (out-of-range) rate limit."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("2. Operational Integrity: Field Validation").run()

    at.number_input[0].set_value(0).run()  # Invalid: less than min_value=1

    at.form[0].submit().run()

    assert at.error[0].value.startswith("Operational parameters are INVALID.")
    assert "RATE_LIMIT_PER_MINUTE must be between 1 and 10000." in at.error[0].value


def test_operational_integrity_invalid_cost_budget():
    """Test submitting the Operational Integrity form with an invalid (negative) cost budget."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("2. Operational Integrity: Field Validation").run()

    at.number_input[1].set_value(-10.0).run()  # Invalid: less than min_value=0.0

    at.form[0].submit().run()

    assert at.error[0].value.startswith("Operational parameters are INVALID.")
    assert "DAILY_COST_BUDGET_USD must be non-negative." in at.error[0].value


def test_dimension_weights_valid_sum():
    """Test submitting the Dimension Weights form with weights that sum correctly to 1.0."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("3. Business Logic: Cross-Field Validation").run()

    # Set weights to sum exactly to 1.0
    at.number_input[0].set_value(0.15).run() # W_DATA_INFRA
    at.number_input[1].set_value(0.15).run() # W_AI_GOVERNANCE
    at.number_input[2].set_value(0.15).run() # W_TECH_STACK
    at.number_input[3].set_value(0.15).run() # W_TALENT
    at.number_input[4].set_value(0.15).run() # W_LEADERSHIP
    at.number_input[5].set_value(0.15).run() # W_USE_CASES
    at.number_input[6].set_value(0.10).run() # W_CULTURE (0.15 * 6 + 0.10 = 1.00)

    at.form[0].submit().run()

    assert at.success[0].value.startswith("Dimension weights sum to 1.000, which is VALID.")


def test_dimension_weights_invalid_sum():
    """Test submitting the Dimension Weights form with weights that do not sum to 1.0."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("3. Business Logic: Cross-Field Validation").run()

    # Set weights to sum to more than 1.0 (0.20 + 0.15*5 + 0.10 = 1.05)
    at.number_input[0].set_value(0.20).run() # W_DATA_INFRA
    at.number_input[1].set_value(0.15).run() # W_AI_GOVERNANCE
    at.number_input[2].set_value(0.15).run() # W_TECH_STACK
    at.number_input[3].set_value(0.15).run() # W_TALENT
    at.number_input[4].set_value(0.15).run() # W_LEADERSHIP
    at.number_input[5].set_value(0.15).run() # W_USE_CASES
    at.number_input[6].set_value(0.10).run() # W_CULTURE

    at.form[0].submit().run()

    assert at.error[0].value.startswith("Dimension weights are INVALID.")
    assert "Dimension weights must sum to approximately 1.0" in at.error[0].value


def test_production_hardening_valid_production_config():
    """Test production validation with a correctly configured production environment."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("4. Production Hardening: Conditional Validation").run()

    at.selectbox[0].set_value("production").run() # APP_ENV
    at.checkbox[0].set_value(False).run() # DEBUG Mode
    at.text_input[0].set_value("this_is_a_very_long_and_secure_secret_key_for_production_environment_abcxyz").run() # SECRET_KEY (length >= 32)
    at.text_input[1].set_value("sk-validopenaiapikey1234567890abcdef").run() # OPENAI_API_KEY
    at.text_input[2].set_value("anthropic_key_1234567890").run() # ANTHROPIC_API_KEY

    at.form[0].submit().run()

    assert at.success[0].value == "Production settings are VALID."
    assert "APP_ENV: production" in at.markdown[2].value
    assert "DEBUG: False" in at.markdown[2].value
    assert "SECRET_KEY length: 70" in at.markdown[2].value
    assert "OpenAI API Key provided: Yes" in at.markdown[2].value


def test_production_hardening_debug_true_in_production():
    """Test production validation failing when DEBUG mode is true in production."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("4. Production Hardening: Conditional Validation").run()

    at.selectbox[0].set_value("production").run() # APP_ENV
    at.checkbox[0].set_value(True).run() # DEBUG Mode (Invalid in production)
    at.text_input[0].set_value("this_is_a_very_long_and_secure_secret_key_for_production_environment_abcxyz").run()
    at.text_input[1].set_value("sk-validopenaiapikey1234567890abcdef").run()
    at.text_input[2].set_value("anthropic_key_1234567890").run()

    at.form[0].submit().run()

    assert at.error[0].value.startswith("Production settings are INVALID.")
    assert "DEBUG must be False in production environment." in at.error[0].value


def test_production_hardening_short_secret_key_in_production():
    """Test production validation failing when SECRET_KEY is too short in production."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("4. Production Hardening: Conditional Validation").run()

    at.selectbox[0].set_value("production").run() # APP_ENV
    at.checkbox[0].set_value(False).run() # DEBUG Mode
    at.text_input[0].set_value("short_key").run() # SECRET_KEY (Invalid length)
    at.text_input[1].set_value("sk-validopenaiapikey1234567890abcdef").run()
    at.text_input[2].set_value("anthropic_key_1234567890").run()

    at.form[0].submit().run()

    assert at.error[0].value.startswith("Production settings are INVALID.")
    assert "SECRET_KEY must be at least 32 characters long in production environment." in at.error[0].value


def test_production_hardening_no_llm_keys_in_production():
    """Test production validation failing when no LLM API keys are provided in production."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("4. Production Hardening: Conditional Validation").run()

    at.selectbox[0].set_value("production").run() # APP_ENV
    at.checkbox[0].set_value(False).run() # DEBUG Mode
    at.text_input[0].set_value("this_is_a_very_long_and_secure_secret_key_for_production_environment_abcxyz").run()
    at.text_input[1].set_value("").run() # OPENAI_API_KEY (empty)
    at.text_input[2].set_value("").run() # ANTHROPIC_API_KEY (empty)

    at.form[0].submit().run()

    assert at.error[0].value.startswith("Production settings are INVALID.")
    assert "At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required in production." in at.error[0].value


def test_production_hardening_invalid_openai_key_format():
    """Test validation of OpenAI API key format (must start with 'sk-')."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("4. Production Hardening: Conditional Validation").run()

    at.selectbox[0].set_value("development").run() # Set to development to isolate this validation
    at.checkbox[0].set_value(False).run()
    at.text_input[0].set_value("a_dev_secret_key_long_enough_for_any_case").run()
    at.text_input[1].set_value("invalid-openai-key").run() # Invalid format
    at.text_input[2].set_value("anthropic_key_123").run() # Provide one valid key for production case if it was production

    at.form[0].submit().run()

    assert at.error[0].value.startswith("Production settings are INVALID.")
    assert "OPENAI_API_KEY must start with 'sk-'." in at.error[0].value


def test_simulator_select_valid_scenario():
    """Test selecting a pre-defined valid scenario in the simulator."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("5. Configuration Simulator & Troubleshooting").run()

    at.selectbox[0].set_value("Development").run() # Select a valid pre-defined scenario

    at.button[0].click().run() # Run Configuration Simulation

    assert at.success[0].value == "SUCCESS: Configuration is VALID for the selected scenario and custom inputs."
    assert "APP_ENV: development" in at.markdown[2].value
    assert "DEBUG: True" in at.markdown[2].value


def test_simulator_select_invalid_scenario():
    """Test selecting a pre-defined invalid scenario in the simulator."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("5. Configuration Simulator & Troubleshooting").run()

    at.selectbox[0].set_value("Production Debug On").run() # Select a scenario known to be invalid

    at.button[0].click().run() # Run Configuration Simulation

    assert at.error[0].value.startswith("FAILURE: Configuration is INVALID. Details:")
    assert "DEBUG must be False in production environment." in at.exception[0].value


def test_simulator_custom_env_valid():
    """Test using custom environment variables to create a valid configuration."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("5. Configuration Simulator & Troubleshooting").run()

    custom_env_vars = """
APP_ENV=staging
DEBUG=False
SECRET_KEY=another_secure_key_for_staging_123456789012345
OPENAI_API_KEY=sk-teststagingkey
RATE_LIMIT_PER_MINUTE=200
"""
    at.text_area[0].set_value(custom_env_vars).run()

    at.button[0].click().run()

    assert at.success[0].value == "SUCCESS: Configuration is VALID for the selected scenario and custom inputs."
    assert "APP_ENV: staging" in at.markdown[2].value
    assert "DEBUG: False" in at.markdown[2].value
    assert "OpenAI API Key Set: Yes" in at.markdown[2].value


def test_simulator_custom_env_invalid():
    """Test using custom environment variables to create an invalid configuration."""
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("5. Configuration Simulator & Troubleshooting").run()

    custom_env_vars = """
APP_ENV=production
DEBUG=True
SECRET_KEY=short
""" # This configuration is invalid for production
    at.text_area[0].set_value(custom_env_vars).run()

    at.button[0].click().run()

    assert at.error[0].value.startswith("FAILURE: Configuration is INVALID. Details:")
    assert "DEBUG must be False in production environment." in at.exception[0].value
    assert "SECRET_KEY must be at least 32 characters long in production environment." in at.exception[0].value
    assert "At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required in production." in at.exception[0].value
