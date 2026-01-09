# QuLab: Foundation and Platform Setup

![QuantUniversity Logo](https://www.quantuniversity.com/assets/img/logo5.jpg)

## 🚀 Project Overview: Safeguarding the PE Intelligence Platform

This project, "QuLab: Foundation and Platform Setup," serves as a hands-on lab demonstrating how to build a robust and secure configuration system for a Private Equity (PE) Organizational AI Rating (AIR) platform. It focuses on using Pydantic v2 within a Streamlit interface to enforce strict validation rules across various application settings – from general metadata and API parameters to sensitive credentials, cost management, and complex scoring model weights.

As a **Software Developer** or **Data Engineer**, ensuring the reliability of application configurations is critical. Misconfigurations can lead to system failures, data integrity issues, or inaccurate analytical outcomes. This application simulates a real-world workflow to proactively catch such errors during development and staging, preventing costly incidents in production.

**Key Educational Objectives:**

*   **Remember**: List the components of a FastAPI application and Pydantic validation.
*   **Understand**: Explain why configuration validation prevents runtime errors.
*   **Apply**: Implement a validated configuration system with weight constraints.
*   **Create**: Design a project structure for production PE intelligence platforms.

## ✨ Features

This Streamlit application provides an interactive environment to explore and validate application configurations:

*   **Interactive Configuration UI**: Dynamically adjust various application parameters using Streamlit widgets.
*   **Environment Selection**: Toggle between `development`, `staging`, and `production` environments to observe how validation rules change conditionally.
*   **Scenario Presets**: Load pre-defined configuration scenarios (e.g., "Development Defaults", "Production Valid", "Production Invalid") to quickly test different states.
*   **On-Demand Validation**: Trigger Pydantic v2 validation for the current settings with a dedicated button.
*   **Detailed Validation Report**: Receive immediate feedback on configuration status (Valid/Invalid) and a comprehensive report outlining all errors or a summary of the validated settings.
*   **Field-Level Validation**: Demonstrates basic Pydantic validation for data types, min/max values, and string formats (e.g., API key prefixes, character lengths).
*   **Cross-Field Business Logic Validation**: Features an advanced Pydantic `@model_validator` to ensure that a set of dimension weights for the PE scoring model sum up to exactly 1.0 (with tolerance).
*   **Conditional Environment-Specific Validation**: Shows how Pydantic validators can enforce different rules based on the `APP_ENV`, such as requiring `DEBUG=False` and minimum `SECRET_KEY` length in `production`.
*   **Sensitive Data Handling**: Uses Pydantic's `SecretStr` to demonstrate how sensitive information like API keys and database passwords are handled securely, preventing accidental logging.
*   **Educational Insights**: Includes detailed explanations within the UI about Pydantic features, workflow tasks, and common configuration mistakes with suggested fixes.

## 🚀 Getting Started

Follow these instructions to set up and run the application locally.

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/quolab-foundation-platform-setup.git
    cd quolab-foundation-platform-setup
    ```
    *(Replace `https://github.com/your-username/quolab-foundation-platform-setup.git` with your actual repository URL)*

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    *   **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    Create a `requirements.txt` file in the project root with the following content:
    ```
    streamlit
    pydantic~=2.0
    ```
    Then, install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## 🏃‍♀️ Usage

1.  **Run the Streamlit Application:**
    Ensure your virtual environment is active, then run:
    ```bash
    streamlit run app.py
    ```
    This will open the application in your default web browser (usually at `http://localhost:8501`).

2.  **Interact with the Application:**
    *   **Navigation:** Use the "Navigation" selectbox in the sidebar to switch between "Introduction", "Configure Application Settings", and "Validated Configuration Report".
    *   **Environment Selection:** Select the desired `development`, `staging`, or `production` environment using the radio buttons in the sidebar. Observe how different validation rules (especially for `production`) come into play.
    *   **Configuration Inputs:** On the "Configure Application Settings" page, modify the various parameters using text inputs, sliders, and checkboxes.
    *   **Load Scenarios:** Use the "Scenario Presets" dropdown in the sidebar to load pre-defined configurations (e.g., "Development Valid", "Production Invalid") and see how they affect validation. Click "Load Scenario" after selecting.
    *   **Validate Configuration:** Click the "Validate Configuration" button in the sidebar (it's a primary button) to trigger the Pydantic validation process for the current inputs.
    *   **Review Report:** Navigate to the "Validated Configuration Report" page to see a summary of the validation outcome, including specific error messages if the configuration is invalid.
    *   **Explore Code:** Refer to `source.py` to understand how the Pydantic `Settings` class is defined, including `Field` validators, `@model_validator` methods, and `SecretStr` types.

## 📁 Project Structure

```
├── app.py                     # Main Streamlit application entry point
├── source.py                  # Defines Pydantic Settings model, validation logic, and scenario presets
├── requirements.txt           # Python dependencies for the project
└── README.md                  # This README file
```

## 🛠️ Technology Stack

*   **Python**: The core programming language.
*   **Streamlit**: For creating the interactive web application interface.
*   **Pydantic v2**: For defining and validating application settings, including data parsing, type hints, field-level validation, and custom model validators.
*   **Core Concepts**: `BaseSettings`, `SettingsConfigDict`, `Field`, `@model_validator(mode="after")`, `SecretStr`.

*Mentioned in configuration parameters (technologies for the *target* PE platform, not direct dependencies of this Streamlit app):*
*   **OpenAI / Anthropic**: Large Language Model (LLM) providers.
*   **Snowflake**: Cloud data warehouse.
*   **AWS S3**: Cloud storage service.
*   **Redis**: In-memory data store for caching and message brokering.
*   **Celery**: Distributed task queue for asynchronous processing.
*   **OpenTelemetry**: Observability framework for tracing and metrics.
*   **FastAPI**: The intended framework for the backend services that would consume these validated settings.

## 🤝 Contributing

This is a lab project intended for learning and demonstration. While direct contributions might not be formally managed, you are welcome to:

1.  **Fork** the repository.
2.  **Experiment** with the code.
3.  **Propose improvements** or additional validation examples via issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details (or add one if it doesn't exist).

## ✉️ Contact

For questions or feedback regarding this lab project, please reach out to:

*   **QuantUniversity**
*   **Website**: [Link to QuantUniversity website, e.g., https://www.quantuniversity.com/](https://www.quantuniversity.com/)
*   **Email**: [your-email@example.com] (Optional, replace with a relevant contact email)
