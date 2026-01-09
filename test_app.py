
import pytest
from streamlit.testing.v1 import AppTest
import os
from unittest.mock import patch

# Note: This test file assumes that a 'source.py' file exists in the same directory
# or is accessible in the Python path, containing the Settings class, scenarios dictionary,
# get_settings_with_prod_validation, and clear_env functions as described in the problem.

# Helper to reset environment variables that might be set by the app during tests
def _clear_test_env_vars():
    keys_to_clear = [
        "APP_NAME", "APP_VERSION", "APP_ENV", "DEBUG", "LOG_LEVEL", "LOG_FORMAT",
        "SECRET_KEY", "API_V1_PREFIX", "API_V2_PREFIX", "RATE_LIMIT_PER_MINUTE",
        "PARAM_VERSION", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEFAULT_LLM_MODEL",
        "FALLBACK_LLM_MODEL", "DAILY_COST_BUDGET_USD", "COST_ALERT_THRESHOLD_PCT",
        "HITL_SCORE_CHANGE_THRESHOLD", "HITL_EBITDA_PROJECTION_THRESHOLD",
        "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA", "SNOWFLAKE_WAREHOUSE", "SNOWFLAKE_ROLE",
        "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION", "S3_BUCKET",
        "REDIS_URL", "CACHE_TTL_SECTORS", "CACHE_TTL_SCORES",
        "ALPHA_VR_WEIGHT", "BETA_SYNERGY_WEIGHT", "LAMBDA_PENALTY", "DELTA_POSITION",
        "W_DATA_INFRA", "W_AI_GOVERNANCE", "W_TECH_STACK", "W_TALENT",
        "W_LEADERSHIP", "W_USE_CASES", "W_CULTURE",
        "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND",
        "OTEL_EXPORTER_OTLP_ENDPOINT", "OTEL_SERVICE_NAME"
    ]
    for key in keys_to_clear:
        if key in os.environ:
            del os.environ[key]

@pytest.fixture(autouse=True)
def run_around_tests():
    _clear_test_env_vars()
    yield
    _clear_test_env_vars()


def test_initial_app_load():
    """Verify the app loads correctly and displays the introduction page."""
    at = AppTest.from_file("app.py").run()
    assert at.session_state["current_page"] == "Introduction"
    assert "Introduction: Safeguarding the PE Intelligence Platform" in at.markdown[0].value
    assert at.sidebar_app_env.value == "development"
    assert at.session_state["app_env"] == "development"
    assert "APP_NAME" in at.session_state["config_inputs"]
    assert at.selectbox[0].value == "Introduction" # Sidebar navigation


def test_navigation_to_config_page():
    """Test navigation to the 'Configure Application Settings' page."""
    at = AppTest.from_file("app.py").run()
    at.selectbox[0].set_value("Configure Application Settings").run()
    assert at.session_state["current_page"] == "Configure Application Settings"
    assert "Configure Application Settings" in at.markdown[0].value
    assert "Currently configuring for: **`DEVELOPMENT`** environment." in at.info[0].value


def test_navigation_to_report_page():
    """Test navigation to the 'Validated Configuration Report' page."""
    at = AppTest.from_file("app.py").run()
    at.selectbox[0].set_value("Validated Configuration Report").run()
    assert at.session_state["current_page"] == "Validated Configuration Report"
    assert "Validated Configuration Report" in at.markdown[0].value
    assert at.warning[0].value == "Configuration not yet validated. Please configure settings and click 'Validate Configuration'."


def test_environment_selection():
    """Verify changing the environment updates session state and config inputs."""
    at = AppTest.from_file("app.py").run()
    assert at.sidebar_app_env.value == "development"
    assert at.session_state["app_env"] == "development"
    assert at.session_state["config_inputs"]["APP_ENV"] == "development"

    at.sidebar_app_env.set_value("production").run()
    assert at.sidebar_app_env.value == "production"
    assert at.session_state["app_env"] == "production"
    assert at.session_state["config_inputs"]["APP_ENV"] == "production"

    # Go to config page to see the updated environment info
    at.selectbox[0].set_value("Configure Application Settings").run()
    assert "Currently configuring for: **`PRODUCTION`** environment." in at.info[0].value


def test_load_default_development_scenario():
    """Test loading the 'Default Development' scenario."""
    at = AppTest.from_file("app.py").run()

    # Ensure we are on the config page to see input changes
    at.selectbox[0].set_value("Configure Application Settings").run()

    # Load "Default Development" scenario
    at.scenario_selector.set_value("Default Development").run()
    at.button[0].click().run() # Click "Load Scenario" button

    assert at.success[0].value == "Scenario 'Default Development' loaded successfully!"
    assert at.session_state["app_env"] == "development"
    assert at.session_state["config_inputs"]["APP_ENV"] == "development"
    assert at.APP_NAME.value == "PE Org-AI-R Platform"
    assert at.DEBUG.value is True # Default Development sets DEBUG to True
    assert at.SECRET_KEY.value == "default_secret_for_dev_env_testing_0123456789" # This is from app.py default not scenario


def test_load_production_valid_scenario():
    """Test loading a valid production scenario."""
    at = AppTest.from_file("app.py").run()

    # Ensure we are on the config page to see input changes
    at.selectbox[0].set_value("Configure Application Settings").run()

    # Load "Production Valid" scenario
    at.scenario_selector.set_value("Production Valid").run()
    at.button[0].click().run() # Click "Load Scenario" button

    assert at.success[0].value == "Scenario 'Production Valid' loaded successfully!"
    assert at.session_state["app_env"] == "production"
    assert at.session_state["config_inputs"]["APP_ENV"] == "production"
    assert at.DEBUG.value is False
    assert at.SECRET_KEY.value == "a_very_long_and_secure_secret_key_for_prod_0123456789"
    assert at.OPENAI_API_KEY.value == "sk-testapikeyvalidprod00000000000000000000"


def test_validate_default_development_config_success():
    """Test validation with default development settings (should be valid)."""
    at = AppTest.from_file("app.py").run()

    # Ensure we are on the config page and then validate
    at.selectbox[0].set_value("Configure Application Settings").run()

    # Load default development scenario to ensure consistent state
    at.scenario_selector.set_value("Default Development").run()
    at.button[0].click().run() # Click "Load Scenario"
    assert at.success[0].value == "Scenario 'Default Development' loaded successfully!"

    # Click Validate Configuration button
    at.button[1].click().run() # Assuming "Validate Configuration" is the second button in sidebar

    assert at.session_state["overall_validation_status"] == "Valid"
    assert "🎉 VALID Configuration! 🎉" in at.session_state["validated_config_report"]
    assert at.session_state["validation_errors"] == {}

    # Verify report page shows success
    at.selectbox[0].set_value("Validated Configuration Report").run()
    assert at.success[0].value == "✅ All configurations are valid!"
    assert "🎉 VALID Configuration! 🎉" in at.markdown[4].value


def test_validate_production_valid_scenario_success():
    """Test validation with a scenario designed to be valid in production."""
    at = AppTest.from_file("app.py").run()

    # Load "Production Valid" scenario
    at.scenario_selector.set_value("Production Valid").run()
    at.button[0].click().run() # Click "Load Scenario"
    assert at.success[0].value == "Scenario 'Production Valid' loaded successfully!"

    # Click Validate Configuration button
    at.button[1].click().run()

    assert at.session_state["overall_validation_status"] == "Valid"
    assert "🎉 VALID Configuration! 🎉" in at.session_state["validated_config_report"]
    assert at.session_state["validation_errors"] == {}

    # Verify report page shows success
    at.selectbox[0].set_value("Validated Configuration Report").run()
    assert at.success[0].value == "✅ All configurations are valid!"
    assert "🎉 VALID Configuration! 🎉" in at.markdown[4].value


def test_validate_production_invalid_debug_true():
    """Test validation failure: DEBUG is True in production."""
    at = AppTest.from_file("app.py").run()

    # Load "Production Invalid - Debug True" scenario
    at.scenario_selector.set_value("Production Invalid - Debug True").run()
    at.button[0].click().run() # Click "Load Scenario"
    assert at.success[0].value == "Scenario 'Production Invalid - Debug True' loaded successfully!"

    # Click Validate Configuration button
    at.button[1].click().run()

    assert at.session_state["overall_validation_status"] == "Invalid"
    assert "❌ INVALID Configuration ❌" in at.session_state["validated_config_report"]
    assert "DEBUG" in at.session_state["validation_errors"]
    assert at.session_state["validation_errors"]["DEBUG"] == "DEBUG must be False in production environment."

    # Verify report page shows error
    at.selectbox[0].set_value("Validated Configuration Report").run()
    assert at.error[0].value == "❌ Errors found in configuration. Please review the report below."
    assert "DEBUG must be False in production environment." in at.markdown[4].value


def test_validate_production_invalid_short_secret_key():
    """Test validation failure: SECRET_KEY too short in production."""
    at = AppTest.from_file("app.py").run()

    # Load "Production Invalid - Short Secret" scenario
    at.scenario_selector.set_value("Production Invalid - Short Secret").run()
    at.button[0].click().run() # Click "Load Scenario"
    assert at.success[0].value == "Scenario 'Production Invalid - Short Secret' loaded successfully!"

    # Click Validate Configuration button
    at.button[1].click().run()

    assert at.session_state["overall_validation_status"] == "Invalid"
    assert "SECRET_KEY" in at.session_state["validation_errors"]
    assert at.session_state["validation_errors"]["SECRET_KEY"] == "SECRET_KEY must be at least 32 characters long in production."


def test_validate_production_invalid_no_llm_key():
    """Test validation failure: No LLM API key in production."""
    at = AppTest.from_file("app.py").run()

    # Load "Production Invalid - No LLM Key" scenario
    at.scenario_selector.set_value("Production Invalid - No LLM Key").run()
    at.button[0].click().run() # Click "Load Scenario"
    assert at.success[0].value == "Scenario 'Production Invalid - No LLM Key' loaded successfully!"

    # Click Validate Configuration button
    at.button[1].click().run()

    assert at.session_state["overall_validation_status"] == "Invalid"
    assert "general" in at.session_state["validation_errors"] # The error is reported under 'general' for cross-field
    assert "At least one LLM API key (OpenAI or Anthropic) is required in production environment." in at.session_state["validation_errors"]["general"]


def test_validate_invalid_openai_api_key_format():
    """Test validation failure: OpenAI API key has an invalid format."""
    at = AppTest.from_file("app.py").run()

    # Load "Invalid OpenAI Key Format" scenario
    at.scenario_selector.set_value("Invalid OpenAI Key Format").run()
    at.button[0].click().run() # Click "Load Scenario"
    assert at.success[0].value == "Scenario 'Invalid OpenAI Key Format' loaded successfully!"

    # Click Validate Configuration button
    at.button[1].click().run()

    assert at.session_state["overall_validation_status"] == "Invalid"
    assert "OPENAI_API_KEY" in at.session_state["validation_errors"]
    assert at.session_state["validation_errors"]["OPENAI_API_KEY"] == "OPENAI_API_KEY must start with 'sk-'."


def test_validate_invalid_weights_sum():
    """Test validation failure: Dimension weights do not sum to 1.0."""
    at = AppTest.from_file("app.py").run()

    # Load "Invalid Weights Sum" scenario
    at.scenario_selector.set_value("Invalid Weights Sum").run()
    at.button[0].click().run() # Click "Load Scenario"
    assert at.success[0].value == "Scenario 'Invalid Weights Sum' loaded successfully!"

    # Click Validate Configuration button
    at.button[1].click().run()

    assert at.session_state["overall_validation_status"] == "Invalid"
    assert "validate_dimension_weights" in at.session_state["validation_errors"]
    assert "Dimension weights must sum to 1.0" in at.session_state["validation_errors"]["validate_dimension_weights"]


def test_configure_app_settings_input_widgets():
    """Verify various input widgets update session state correctly."""
    at = AppTest.from_file("app.py").run()
    at.selectbox[0].set_value("Configure Application Settings").run()

    # Text input
    at.APP_NAME.set_value("My Test App").run()
    assert at.session_state.config_inputs["APP_NAME"] == "My Test App"

    # Checkbox
    at.DEBUG.set_value(True).run()
    assert at.session_state.config_inputs["DEBUG"] is True

    # Selectbox
    at.LOG_LEVEL.set_value("DEBUG").run()
    assert at.session_state.config_inputs["LOG_LEVEL"] == "DEBUG"

    # Radio button
    at.LOG_FORMAT.set_value("console").run()
    assert at.session_state.config_inputs["LOG_FORMAT"] == "console"

    # Slider
    at.RATE_LIMIT_PER_MINUTE.set_value(500).run()
    assert at.session_state.config_inputs["RATE_LIMIT_PER_MINUTE"] == 500
    at.COST_ALERT_THRESHOLD_PCT.set_value(0.95).run()
    assert abs(at.session_state.config_inputs["COST_ALERT_THRESHOLD_PCT"] - 0.95) < 0.001

    # Number input
    at.DAILY_COST_BUDGET_USD.set_value(100.50).run()
    assert at.session_state.config_inputs["DAILY_COST_BUDGET_USD"] == 100.50


def test_field_level_validation_error_rate_limit():
    """Test `RATE_LIMIT_PER_MINUTE` validation (value outside range)."""
    at = AppTest.from_file("app.py").run()
    at.selectbox[0].set_value("Configure Application Settings").run()

    at.RATE_LIMIT_PER_MINUTE.set_value(1001).run() # Set an invalid value
    at.button[1].click().run() # Click Validate

    assert at.session_state["overall_validation_status"] == "Invalid"
    assert "RATE_LIMIT_PER_MINUTE" in at.session_state["validation_errors"]
    assert "Value must be less than or equal to 1000" in at.session_state["validation_errors"]["RATE_LIMIT_PER_MINUTE"]


def test_field_level_validation_error_daily_cost_budget():
    """Test `DAILY_COST_BUDGET_USD` validation (negative value)."""
    at = AppTest.from_file("app.py").run()
    at.selectbox[0].set_value("Configure Application Settings").run()

    at.DAILY_COST_BUDGET_USD.set_value(-10.0).run() # Set an invalid value
    at.button[1].click().run() # Click Validate

    assert at.session_state["overall_validation_status"] == "Invalid"
    assert "DAILY_COST_BUDGET_USD" in at.session_state["validation_errors"]
    assert "Value must be greater than or equal to 0.0" in at.session_state["validation_errors"]["DAILY_COST_BUDGET_USD"]


def test_current_dimension_weights_sum_display():
    """Verify the displayed sum of dimension weights updates correctly."""
    at = AppTest.from_file("app.py").run()
    at.selectbox[0].set_value("Configure Application Settings").run()

    # Change a weight and check the info box
    initial_sum_markdown = at.info[1].value
    assert "Current Dimension Weights Sum: **1.00**" in initial_sum_markdown

    at.W_DATA_INFRA.set_value(0.20).run() # Change from 0.18 to 0.20
    at.W_AI_GOVERNANCE.set_value(0.15).run()
    at.W_TECH_STACK.set_value(0.15).run()
    at.W_TALENT.set_value(0.17).run()
    at.W_LEADERSHIP.set_value(0.13).run()
    at.W_USE_CASES.set_value(0.12).run()
    at.W_CULTURE.set_value(0.10).run()
    # sum should be 1.02 now (0.20 + 0.15 + 0.15 + 0.17 + 0.13 + 0.12 + 0.10)

    updated_sum_markdown = at.info[1].value
    assert "Current Dimension Weights Sum: **1.02**" in updated_sum_markdown
