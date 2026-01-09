Here's a comprehensive `README.md` file for your Streamlit application lab project, designed for developers and users.

---

# QuLab: Foundation and Platform Setup (PE Intelligence Platform Configuration)

## Safeguarding the PE Intelligence Platform: Robust Configuration with Pydantic v2

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-streamlit-app-url.streamlit.app/) <!-- Replace with your actual deployment URL -->
[![QuantUniversity Logo](https://www.quantuniversity.com/assets/img/logo5.jpg)](https://www.quantuniversity.com)

---

## 🚀 Project Overview

Welcome to the `QuLab: Foundation and Platform Setup` project, an interactive Streamlit application designed to demonstrate robust configuration management using Pydantic v2. This project simulates the real-world challenges faced by Software Developers and Data Engineers in building a complex **PE (Private Equity) Intelligence Platform**, where application configuration errors can lead to critical failures, security vulnerabilities, or flawed analytical outcomes.

The core objective is to showcase how Pydantic v2 can be leveraged to define, validate, and secure application settings effectively. Through a series of interactive steps, you will explore various validation techniques, from basic type checking and range constraints to complex cross-field business logic and environment-specific security enforcement. This ensures that the PE Intelligence Platform always starts with a valid and secure configuration, preventing costly runtime errors and ensuring data integrity and reliable investment insights.

## ✨ Features

This application highlights critical aspects of robust configuration:

*   **Core Application Configuration**: Define fundamental settings like `APP_NAME`, `APP_VERSION`, `APP_ENV`, `LOG_LEVEL`, and `SECRET_KEY` using Pydantic's `BaseSettings` and `SecretStr` for sensitive data handling.
*   **Operational Integrity: Field Validation**: Enforce range constraints on operational parameters such as `RATE_LIMIT_PER_MINUTE`, `DAILY_COST_BUDGET_USD`, and Human-In-The-Loop (HITL) thresholds using Pydantic's `Field(ge, le)`.
*   **Business Logic: Cross-Field Validation**: Implement complex business rules, such as ensuring that the sum of investment scoring dimension weights (`W_DATA_INFRA`, `W_AI_GOVERNANCE`, etc.) precisely equals `1.0` using Pydantic's `@model_validator`.
*   **Production Hardening: Conditional Validation**: Apply environment-specific security policies for `production` deployments, like disabling `DEBUG` mode, enforcing `SECRET_KEY` length, and requiring essential API keys (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).
*   **Configuration Simulator & Troubleshooting**: An interactive sandbox to simulate various configuration scenarios, troubleshoot potential issues, and generate a "Validated Configuration Report" before deployment.
*   **Clear Error Reporting**: Observe how Pydantic generates detailed `ValidationError` messages, providing immediate feedback on misconfigured parameters.

## 🏁 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

Ensure you have the following installed:

*   **Python 3.8+**
*   **pip** (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/quolab-streamlit-config.git
    cd quolab-streamlit-config
    ```
    (Replace `your-username/quolab-streamlit-config.git` with your actual repository URL)

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    Create a `requirements.txt` file in your project root with the following content:
    ```
    streamlit
    pydantic~=2.0
    pydantic-settings~=2.0
    ```
    Then, install them:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create `source.py`:**
    The provided `app.py` imports functions and Pydantic models from `source.py`. You'll need to create this file in the same directory as `app.py` and populate it with the Pydantic `Settings` model, validators, helper functions (`clear_env`, `get_settings_with_prod_validation`), and the `scenarios` dictionary. Below is a conceptual `source.py` structure (the actual implementation for validators would be defined here):

    ```python
    # source.py
    import os
    from typing import Dict, Literal, Union
    from pydantic import Field, ValidationError, model_validator, field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticSettingsError
    from functools import lru_cache
    import math

    # --- Helper Functions ---
    def clear_env():
        """Clears specific environment variables set by the app to ensure clean state."""
        keys_to_clear = [
            "APP_NAME", "APP_VERSION", "APP_ENV", "DEBUG", "LOG_LEVEL", "SECRET_KEY",
            "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_WAREHOUSE",
            "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_BUCKET",
            "RATE_LIMIT_PER_MINUTE", "DAILY_COST_BUDGET_USD", "COST_ALERT_THRESHOLD_PCT",
            "HITL_SCORE_CHANGE_THRESHOLD", "HITL_EBITDA_PROJECTION_THRESHOLD",
            "W_DATA_INFRA", "W_AI_GOVERNANCE", "W_TECH_STACK", "W_TALENT",
            "W_LEADERSHIP", "W_USE_CASES", "W_CULTURE",
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY"
        ]
        for key in keys_to_clear:
            if key in os.environ:
                del os.environ[key]

    # --- Pydantic Settings Model ---
    class Settings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file='.env', 
            env_file_encoding='utf-8', 
            extra='ignore', 
            secrets_dir='/run/secrets' # For production environments
        )

        # 1. Core Application Configuration
        APP_NAME: str = "PE Org-AI-R Platform"
        APP_VERSION: str = "4.0.0"
        APP_ENV: Literal["development", "staging", "production"] = "development"
        DEBUG: bool = False
        LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
        SECRET_KEY: SecretStr = Field("a_default_secret_key_for_dev_env_0123456789012345", min_length=16) # Minimal default
        
        # Database Credentials (example: Snowflake)
        SNOWFLAKE_ACCOUNT: str = "test_account"
        SNOWFLAKE_USER: str = "test_user"
        SNOWFLAKE_PASSWORD: SecretStr = "test_snowflake_password"
        SNOWFLAKE_WAREHOUSE: str = "test_warehouse"

        # AWS Configuration (example)
        AWS_REGION: str = "us-east-1" # Default region
        AWS_ACCESS_KEY_ID: SecretStr = "test_aws_key_id"
        AWS_SECRET_ACCESS_KEY: SecretStr = "test_aws_secret_key"
        S3_BUCKET: str = "test_s3_bucket"

        # 2. Operational Integrity: Field Validation
        RATE_LIMIT_PER_MINUTE: int = Field(100, ge=1, le=1000)
        DAILY_COST_BUDGET_USD: float = Field(500.0, ge=0.0)
        COST_ALERT_THRESHOLD_PCT: float = Field(0.8, ge=0.0, le=1.0)
        
        HITL_SCORE_CHANGE_THRESHOLD: float = Field(15.0, ge=5.0, le=30.0)
        HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(10.0, ge=5.0, le=25.0)

        # 3. Business Logic: Cross-Field Validation (Scoring Weights)
        W_DATA_INFRA: float = Field(0.18, ge=0.0, le=1.0)
        W_AI_GOVERNANCE: float = Field(0.15, ge=0.0, le=1.0)
        W_TECH_STACK: float = Field(0.15, ge=0.0, le=1.0)
        W_TALENT: float = Field(0.17, ge=0.0, le=1.0)
        W_LEADERSHIP: float = Field(0.13, ge=0.0, le=1.0)
        W_USE_CASES: float = Field(0.12, ge=0.0, le=1.0)
        W_CULTURE: float = Field(0.10, ge=0.0, le=1.0)

        # 4. Production Hardening: Conditional Validation
        OPENAI_API_KEY: SecretStr = ""
        ANTHROPIC_API_KEY: SecretStr = ""

        @field_validator('OPENAI_API_KEY', mode='after')
        @classmethod
        def validate_openai_key_prefix(cls, v: SecretStr) -> SecretStr:
            if v and v.get_secret_value() and not v.get_secret_value().startswith("sk-"):
                raise ValueError("OPENAI_API_KEY must start with 'sk-'")
            return v
            
        @model_validator(mode='after')
        def check_dimension_weights_sum(self) -> 'Settings':
            weights = [
                self.W_DATA_INFRA, self.W_AI_GOVERNANCE, self.W_TECH_STACK,
                self.W_TALENT, self.W_LEADERSHIP, self.W_USE_CASES, self.W_CULTURE
            ]
            total_sum = sum(weights)
            # Allow a small floating point tolerance
            if not math.isclose(total_sum, 1.0, rel_tol=1e-3): 
                raise ValueError(f"Dimension weights must sum to approximately 1.0 (current sum: {total_sum:.3f})")
            return self

        @model_validator(mode='after')
        def enforce_production_rules(self) -> 'Settings':
            if self.APP_ENV == "production":
                if self.DEBUG:
                    raise ValueError("DEBUG mode must be False in production.")
                if len(self.SECRET_KEY.get_secret_value()) < 32:
                    raise ValueError("SECRET_KEY must be at least 32 characters long in production.")
                if not self.OPENAI_API_KEY and not self.ANTHROPIC_API_KEY:
                    raise ValueError("At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) is required in production.")
            return self

    # --- Cached Settings Loader ---
    @lru_cache()
    def get_settings_with_prod_validation() -> Settings:
        """Loads and validates settings, with a focus on production rules."""
        # When `get_settings_with_prod_validation` is called, Pydantic automatically
        # loads from environment variables or .env file based on SettingsConfigDict.
        # The validators defined in the Settings class are then applied.
        return Settings()

    # --- Pre-defined Scenarios for Simulation ---
    scenarios: Dict[str, Dict[str, str]] = {
        "Default Valid Dev": {
            "APP_ENV": "development", "DEBUG": "True", "SECRET_KEY": "dev_key_01234567890123456789",
            "RATE_LIMIT_PER_MINUTE": "100", "DAILY_COST_BUDGET_USD": "500.0", "COST_ALERT_THRESHOLD_PCT": "0.8",
            "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
            "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
            "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""
        },
        "Valid Production": {
            "APP_ENV": "production", "DEBUG": "False", "SECRET_KEY": "a_very_long_and_secure_secret_key_for_production_01234567890",
            "RATE_LIMIT_PER_MINUTE": "50", "DAILY_COST_BUDGET_USD": "1000.0", "COST_ALERT_THRESHOLD_PCT": "0.9",
            "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
            "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
            "OPENAI_API_KEY": "sk-your-openai-key-here-1234567890", "ANTHROPIC_API_KEY": ""
        },
        "Invalid: Weights Sum Incorrect": {
            "APP_ENV": "development", "DEBUG": "True", "SECRET_KEY": "dev_key_01234567890123456789",
            "RATE_LIMIT_PER_MINUTE": "100", "DAILY_COST_BUDGET_USD": "500.0", "COST_ALERT_THRESHOLD_PCT": "0.8",
            "W_DATA_INFRA": "0.20", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
            "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10", # Sums to 1.02
            "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""
        },
        "Invalid: Production DEBUG True": {
            "APP_ENV": "production", "DEBUG": "True", "SECRET_KEY": "a_very_long_and_secure_secret_key_for_production_01234567890",
            "RATE_LIMIT_PER_MINUTE": "50", "DAILY_COST_BUDGET_USD": "1000.0", "COST_ALERT_THRESHOLD_PCT": "0.9",
            "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
            "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
            "OPENAI_API_KEY": "sk-your-openai-key-here-1234567890", "ANTHROPIC_API_KEY": ""
        },
        "Invalid: Production Short Secret Key": {
            "APP_ENV": "production", "DEBUG": "False", "SECRET_KEY": "too_short_key",
            "RATE_LIMIT_PER_MINUTE": "50", "DAILY_COST_BUDGET_USD": "1000.0", "COST_ALERT_THRESHOLD_PCT": "0.9",
            "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
            "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
            "OPENAI_API_KEY": "sk-your-openai-key-here-1234567890", "ANTHROPIC_API_KEY": ""
        },
        "Invalid: Production Missing LLM Keys": {
            "APP_ENV": "production", "DEBUG": "False", "SECRET_KEY": "a_very_long_and_secure_secret_key_for_production_01234567890",
            "RATE_LIMIT_PER_MINUTE": "50", "DAILY_COST_BUDGET_USD": "1000.0", "COST_ALERT_THRESHOLD_PCT": "0.9",
            "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
            "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
            "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": "" # Both missing
        },
        "Invalid: Out-of-Range Rate Limit": {
            "APP_ENV": "development", "DEBUG": "True", "SECRET_KEY": "dev_key_01234567890123456789",
            "RATE_LIMIT_PER_MINUTE": "1500", # Too high
            "DAILY_COST_BUDGET_USD": "500.0", "COST_ALERT_THRESHOLD_PCT": "0.8",
            "W_DATA_INFRA": "0.18", "W_AI_GOVERNANCE": "0.15", "W_TECH_STACK": "0.15",
            "W_TALENT": "0.17", "W_LEADERSHIP": "0.13", "W_USE_CASES": "0.12", "W_CULTURE": "0.10",
            "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""
        }
    }
    ```

## ▶️ Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
2.  Your browser will automatically open the Streamlit application.
3.  **Navigate through the sections** using the sidebar to explore different validation techniques.
    *   Experiment with valid and invalid inputs in each section to observe Pydantic's real-time validation and error reporting.
    *   In the "Configuration Simulator & Troubleshooting" section, try selecting pre-defined scenarios or entering custom environment variables to test the combined validation logic.

## 📁 Project Structure

```
.
├── app.py                  # Main Streamlit application file
├── source.py               # Pydantic Settings model, validators, and helper functions
├── requirements.txt        # Python dependencies
└── .env                    # Optional: Example environment file (for local development)
```

## ⚙️ Technology Stack

*   **Python 3.8+**: The core programming language.
*   **Streamlit**: For creating the interactive web application interface.
*   **Pydantic v2**: The data validation and settings management library.
*   **Pydantic-Settings v2**: Extension of Pydantic for managing application settings loaded from environment variables or files.

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or new features:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
5.  Push to the branch (`git push origin feature/AmazingFeature`).
6.  Open a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the `LICENSE` file for details. (You should create a `LICENSE` file in your repository if it doesn't exist).

## 📧 Contact

For questions or feedback, please reach out to:

*   **QuantUniversity**: [info@quantuniversity.com](mailto:info@quantuniversity.com)
*   **Project Maintainer**: [Your Name/Email] or [Your GitHub Profile](https://github.com/your-username)

---
Developed as a lab project for QuantUniversity.
---