
import pytest
from streamlit.testing.v1 import AppTest
import os

# Assume app.py and source.py are in the same directory for AppTest.from_file

# Helper to ensure environment variables are reset for each test
@pytest.fixture(autouse=True)
def run_around_tests():
    # Set up by ensuring a clean environment before each test
    _clear_all_env_vars()
    yield
    # Clean up by clearing environment variables after each test
    _clear_all_env_vars()

def _clear_all_env_vars():
    # Helper to clear environment variables that the app might set or rely on
    prefixes_to_clear = ("APP_", "SECRET_", "RATE_", "DAILY_", "COST_", "W_", "OPENAI_", "ANTHROPIC_",
                         "HITL_", "SNOWFLAKE_", "AWS_", "S3_", "REDIS_", "CACHE_", "CELERY_", "OTEL_",
                         "ALPHA_", "BETA_", "LAMBDA_", "DELTA_", "API_", "PARAM_", "DEFAULT_",
                         "FALLBACK_", "LOG_", "DEBUG")
    for key in list(os.environ.keys()):
        if key.startswith(prefixes_to_clear):
            del os.environ[key]

def test_initial_load_and_introduction_page():
    at = AppTest.from_file("app.py").run()
    assert at.title[0].value == "QuLab: Foundation and Platform Setup"
    assert at.markdown[0].value.startswith("## PE Intelligence Platform: Robust Configuration with Pydantic v2")
    assert at.session_state["current_page"] == "Introduction"
    assert at.markdown[1].value.startswith("## Introduction: Safeguarding the PE Intelligence Platform")
    assert "software developer" in at.markdown[2].value.lower()


def test_sidebar_navigation():
    at = AppTest.from_file("app.py").run()

    # Navigate to "1. Initial Setup: Core Configuration"
    at.sidebar.selectbox[0].set_value("1. Initial Setup: Core Configuration").run()
    assert at.session_state["current_page"] == "1. Initial Setup: Core Configuration"
    assert at.markdown[1].value.startswith("### 1. Initial Setup: Environment and Dependencies")

    # Navigate to "2. Field-Level Validation"
    at.sidebar.selectbox[0].set_value("2. Field-Level Validation").run()
    assert at.session_state["current_page"] == "2. Field-Level Validation"
    assert at.markdown[1].value.startswith("### 3. Ensuring Operational Integrity: Field-Level Validation")

    # Navigate to "3. Cross-Field Validation (Scoring Weights)"
    at.sidebar.selectbox[0].set_value("3. Cross-Field Validation (Scoring Weights)").run()
    assert at.session_state["current_page"] == "3. Cross-Field Validation (Scoring Weights)"
    assert at.markdown[1].value.startswith("### 4. Implementing Business Logic: Cross-Field Validation for Scoring Weights")

    # Navigate to "4. Environment-Specific Validation (Production)"
    at.sidebar.selectbox[0].set_value("4. Environment-Specific Validation (Production)").run()
    assert at.session_state["current_page"] == "4. Environment-Specific Validation (Production)"
    assert at.markdown[1].value.startswith("### 5. Fortifying Production: Conditional Environment-Specific Validation")

    # Navigate to "5. Configuration Simulation & Troubleshooting"
    at.sidebar.selectbox[0].set_value("5. Configuration Simulation & Troubleshooting").run()
    assert at.session_state["current_page"] == "5. Configuration Simulation & Troubleshooting"
    assert at.markdown[1].value.startswith("### 6. Catching Errors Early: Configuration Simulation and Reporting")


def test_initial_setup_core_configuration():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("1. Initial Setup: Core Configuration").run()

    # Before clicking the button
    assert at.session_state["settings_initialized"] is False
    assert at.session_state["current_settings"] is None
    assert at.warning[0].value == "Click 'Load Default Application Settings' to see the initial configuration."

    # Click the "Load Default Application Settings" button
    at.button[0].click().run()

    # Assert session state and success message
    assert at.session_state["settings_initialized"] is True
    assert at.session_state["current_settings"] is not None
    assert at.success[0].value == "Default settings loaded successfully!"
    assert "App Name: `QuLab`" in at.markdown[6].value
    assert "Environment: `development`" in at.markdown[7].value
    assert "Debug Mode: `True`" in at.markdown[8].value
    assert "Secret Key Set: `Yes`" in at.markdown[9].value


def test_field_level_validation_valid_settings():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("2. Field-Level Validation").run()

    # Set valid values
    at.number_input[0].set_value(500).run()  # API Rate Limit (1-1000)
    at.number_input[1].set_value(500.0).run()  # Daily Cost Budget (>=0)
    at.number_input[2].set_value(25.0).run()  # HITL Score Change Threshold (5-30)
    at.slider[0].set_value(0.5).run()       # Cost Alert Threshold (0-1)
    at.number_input[3].set_value(10.0).run()  # HITL EBITDA Projection Threshold (5-25)

    # Click "Validate Operational Settings"
    at.button[0].click().run()

    # Assert session state and success message
    assert at.session_state["operational_settings_valid"] is True
    assert at.session_state["operational_validation_error"] is None
    assert at.success[0].value == "✅ Operational settings are VALID!"
    assert "API Rate Limit: `500` req/min" in at.markdown[6].value
    assert "Daily Cost Budget: `500.0`" in at.markdown[7].value
    assert "Cost Alert Threshold: `50.0%`" in at.markdown[8].value


def test_field_level_validation_invalid_settings():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("2. Field-Level Validation").run()

    # Set invalid values
    at.number_input[0].set_value(1200).run()  # API Rate Limit (should be <= 1000)
    at.number_input[1].set_value(-100.0).run() # Daily Cost Budget (should be >= 0)
    at.slider[0].set_value(2.0).run()       # Cost Alert Threshold (should be <= 1)

    # Click "Validate Operational Settings"
    at.button[0].click().run()

    # Assert session state and error message
    assert at.session_state["operational_settings_valid"] is False
    assert at.session_state["operational_validation_error"] is not None
    assert at.error[0].value.startswith("❌ Operational settings are INVALID!")
    assert "field 'RATE_LIMIT_PER_MINUTE' validation failed" in at.error[0].value
    assert "field 'DAILY_COST_BUDGET_USD' validation failed" in at.error[0].value
    assert "field 'COST_ALERT_THRESHOLD_PCT' validation failed" in at.error[0].value


def test_cross_field_validation_valid_weights():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("3. Cross-Field Validation (Scoring Weights)").run()

    # Default weights sum to 1.0, so just click validate
    # w_data_infra = 0.18, w_ai_governance = 0.15, w_tech_stack = 0.15, w_talent = 0.17
    # w_leadership = 0.13, w_use_cases = 0.12, w_culture = 0.10
    # Sum = 0.18 + 0.15 + 0.15 + 0.17 + 0.13 + 0.12 + 0.10 = 1.00

    # Click "Validate Dimension Weights"
    at.button[0].click().run()

    # Assert session state and success message
    assert at.session_state["weights_settings_valid"] is True
    assert at.session_state["weights_validation_error"] is None
    assert at.success[0].value == "✅ Dimension weights are VALID!"
    assert "Total Sum: `1.00`" in at.markdown[11].value


def test_cross_field_validation_invalid_weights():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("3. Cross-Field Validation (Scoring Weights)").run()

    # Change one weight so they don't sum to 1.0
    at.slider[0].set_value(0.20).run()  # W_DATA_INFRA = 0.20 (originally 0.18)
    # New sum will be 1.02

    # Click "Validate Dimension Weights"
    at.button[0].click().run()

    # Assert session state and error message
    assert at.session_state["weights_settings_valid"] is False
    assert at.session_state["weights_validation_error"] is not None
    assert at.error[0].value.startswith("❌ Dimension weights are INVALID!")
    assert "Dimension weights must sum to approximately 1.0" in at.error[0].value


def test_production_validation_valid_production_settings():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("4. Environment-Specific Validation (Production)").run()

    # Set valid production settings
    at.selectbox[0].set_value("production").run()  # APP_ENV
    at.checkbox[0].set_value(False).run()          # DEBUG Mode
    at.text_input[0].set_value("a_very_long_secret_key_for_production_env_0123456789").run() # SECRET_KEY (>=32 chars)
    at.text_input[1].set_value("sk-openai_test_key").run() # OPENAI_API_KEY (one LLM key is sufficient)
    at.text_input[2].set_value("").run() # ANTHROPIC_API_KEY (not needed if openai is present)

    # Click "Validate Production Settings"
    at.button[0].click().run()

    # Assert session state and success message
    assert at.session_state["prod_settings_valid"] is True
    assert at.session_state["prod_validation_error"] is None
    assert at.success[0].value == "✅ Production settings are VALID!"
    assert "APP_ENV: `production`" in at.markdown[9].value
    assert "DEBUG: `False`" in at.markdown[10].value
    assert "SECRET_KEY length: `45`" in at.markdown[11].value
    assert "OpenAI API Key provided: `Yes`" in at.markdown[12].value


def test_production_validation_debug_true_in_production():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("4. Environment-Specific Validation (Production)").run()

    # Set APP_ENV to production but DEBUG to True
    at.selectbox[0].set_value("production").run()
    at.checkbox[0].set_value(True).run() # DEBUG is True in production (invalid)
    at.text_input[0].set_value("a_very_long_secret_key_for_production_env_0123456789").run()
    at.text_input[1].set_value("sk-openai_test_key").run()

    # Click "Validate Production Settings"
    at.button[0].click().run()

    # Assert session state and error message
    assert at.session_state["prod_settings_valid"] is False
    assert at.session_state["prod_validation_error"] is not None
    assert at.error[0].value.startswith("❌ Production settings are INVALID!")
    assert "In production environment, DEBUG must be False" in at.error[0].value


def test_production_validation_short_secret_key_in_production():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("4. Environment-Specific Validation (Production)").run()

    # Set APP_ENV to production but short SECRET_KEY
    at.selectbox[0].set_value("production").run()
    at.checkbox[0].set_value(False).run()
    at.text_input[0].set_value("short_key").run() # SECRET_KEY < 32 chars (invalid)
    at.text_input[1].set_value("sk-openai_test_key").run()

    # Click "Validate Production Settings"
    at.button[0].click().run()

    # Assert session state and error message
    assert at.session_state["prod_settings_valid"] is False
    assert at.session_state["prod_validation_error"] is not None
    assert at.error[0].value.startswith("❌ Production settings are INVALID!")
    assert "In production environment, SECRET_KEY must be at least 32 characters long" in at.error[0].value


def test_production_validation_no_llm_key_in_production():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("4. Environment-Specific Validation (Production)").run()

    # Set APP_ENV to production but no LLM keys
    at.selectbox[0].set_value("production").run()
    at.checkbox[0].set_value(False).run()
    at.text_input[0].set_value("a_very_long_secret_key_for_production_env_0123456789").run()
    at.text_input[1].set_value("").run() # No OpenAI key
    at.text_input[2].set_value("").run() # No Anthropic key (invalid)

    # Click "Validate Production Settings"
    at.button[0].click().run()

    # Assert session state and error message
    assert at.session_state["prod_settings_valid"] is False
    assert at.session_state["prod_validation_error"] is not None
    assert at.error[0].value.startswith("❌ Production settings are INVALID!")
    assert "In production environment, either OPENAI_API_KEY or ANTHROPIC_API_KEY must be provided" in at.error[0].value


def test_production_validation_openai_key_format_invalid():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("4. Environment-Specific Validation (Production)").run()

    # Set an invalid OpenAI key format (not starting with 'sk-')
    at.selectbox[0].set_value("development").run() # Can be non-prod to test field_validator
    at.checkbox[0].set_value(True).run()
    at.text_input[0].set_value("dev_key_for_testing_12345678901234567890").run()
    at.text_input[1].set_value("invalid_openai_key").run() # Invalid format

    # Click "Validate Production Settings" (even though it's dev env, field validation runs)
    at.button[0].click().run()

    # Assert session state and error message
    assert at.session_state["prod_settings_valid"] is False
    assert at.session_state["prod_validation_error"] is not None
    assert at.error[0].value.startswith("❌ Production settings are INVALID!")
    assert "OPENAI_API_KEY must start with 'sk-'" in at.error[0].value


def test_configuration_simulation_and_troubleshooting_page():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("5. Configuration Simulation & Troubleshooting").run()

    assert at.session_state["sim_scenario_results"] == []

    # Click "Run All Configuration Scenarios"
    at.button[0].click().run()

    # Assert that scenarios were run and results are populated
    assert len(at.session_state["sim_scenario_results"]) > 0
    assert at.success[0].value == "All scenarios completed."

    # Verify some output content, for example, checking if a specific scenario ran
    # This requires knowledge of what `scenarios` dict and `load_scenario_settings` output
    # Since source.py is not provided, we can only check for general presence of output
    assert "Simulating Scenario:" in at.subheader[0].value
    assert "Environment Variables Set:" in at.markdown[2].value
    assert "Consolidated Scenario Report:" in at.markdown[6].value
    assert "output" in at.session_state["sim_scenario_results"][0]
    assert "Valid Development Settings" in at.session_state["sim_scenario_results"][0]["name"]
