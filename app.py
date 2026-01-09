import streamlit as st
import os
import io
from contextlib import redirect_stdout
from source import *

st.set_page_config(
    page_title="QuLab: Foundation and Platform Setup", layout="wide")
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
if 'show_fix_1' not in st.session_state:
    st.session_state.show_fix_1 = False
if 'show_fix_2' not in st.session_state:
    st.session_state.show_fix_2 = False
if 'show_fix_3' not in st.session_state:
    st.session_state.show_fix_3 = False
if 'show_fix_4' not in st.session_state:
    st.session_state.show_fix_4 = False

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
    "1. Project Initialization",
    "2. Configuration with Validation",
    "3. FastAPI Application Setup",
    "4. Field-Level Validation",
    "5. Cross-Field Validation (Scoring Weights)",
    "6. Environment-Specific Validation (Production)",
    "Configuration Simulation & Troubleshooting"
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

st.sidebar.divider()
st.sidebar.markdown("### 🎯 Key Objectives")
st.sidebar.markdown("""
- **Remember:** List the components of a FastAPI application and Pydantic validation
- **Understand:** Explain why configuration validation prevents runtime errors
- **Apply:** Implement a validated configuration system with weight constraints
- **Create:** Design a project structure for production PE intelligence platforms
""")

st.sidebar.divider()
st.sidebar.markdown("### 🛠️ Tools Introduced")
st.sidebar.markdown("""
- **Pydantic v2** - Data validation and settings management
- **FastAPI** - Modern Python web framework
- **Poetry** - Python dependency management
- **Structlog** - Structured logging
- **Redis** - Caching and task queues
- **OpenTelemetry** - Distributed tracing
""")


if st.session_state.current_page == "Introduction":
    st.markdown(f"## Introduction: Safeguarding the PE Intelligence Platform")
    st.markdown(f"")
    st.markdown(f"As a **Software Developer** building the Organizational AIR Scoring platform, ensuring the robustness and security of our application configurations is paramount. Every new feature or data processing service we deploy relies on correct, consistent, and validated settings across different environments – development, staging, and crucially, production. A single misconfigured parameter, such as an incorrect API key, an out-of-bounds budget, or an improperly weighted scoring dimension, can lead to critical application crashes, compromised data integrity, or skewed analytical outcomes that directly impact investment decisions.")
    st.markdown(f"")
    st.markdown(f"This notebook outlines a real-world workflow to implement a highly reliable configuration system using Pydantic v2. Our goal is to prevent these costly configuration-related bugs by enforcing strict validation rules at application startup, significantly reducing operational overhead and building trust in our platform's outputs. We will walk through defining settings, applying various validation types, and simulating different environmental scenarios to demonstrate how invalid configurations are caught *before* they can cause harm.")
    st.markdown(f"---")

elif st.session_state.current_page == "1. Project Initialization":
    st.markdown(f"### Task 1.1: Project Initialization")
    st.markdown(f"Before we dive into configuration validation, let's set up the proper project structure. This foundational step ensures we have a well-organized codebase that follows Python best practices.")

    st.markdown(f"#### Step 1: Create Project Structure")
    st.markdown(f"Run the following commands to initialize your project:")
    st.code('''# Create project structure
mkdir pe-orgair-platform && cd pe-orgair-platform
poetry init --name="pe-orgair-platform" --python="^3.12"''', language='bash')

    st.markdown(f"#### Step 2: Install Dependencies")
    st.markdown(f"Install the core dependencies for Week 1:")
    st.code('''# Install Week 1 dependencies
poetry add fastapi "uvicorn[standard]" pydantic pydantic-settings httpx
poetry add snowflake-connector-python sqlalchemy alembic boto3 redis
poetry add structlog sse-starlette websockets''', language='bash')

    st.markdown(f"#### Step 3: Install Development Dependencies")
    st.code('''# Development dependencies
poetry add --group dev pytest pytest-asyncio pytest-cov black ruff mypy hypothesis''', language='bash')

    st.markdown(f"#### Step 4: Create Source Structure")
    st.code('''# Create source structure
mkdir -p src/pe_orgair/api/routes/v1
mkdir -p src/pe_orgair/api/routes/v2
mkdir -p src/pe_orgair/config
mkdir -p src/pe_orgair/models
mkdir -p src/pe_orgair/services
mkdir -p src/pe_orgair/schemas
mkdir -p src/pe_orgair/agents
mkdir -p src/pe_orgair/mcp
mkdir -p src/pe_orgair/observability
mkdir -p src/pe_orgair/infrastructure
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/evals
mkdir -p scripts
mkdir -p migrations''', language='bash')

    st.info("💡 **Note:** This structure provides a clean separation of concerns with dedicated folders for API routes, configuration, models, services, and testing.")
    st.markdown(f"---")

elif st.session_state.current_page == "2. Configuration with Validation":
    st.markdown(f"### Task 1.2: Configuration with Validation")
    st.markdown(f"Now let's implement the core configuration system using Pydantic v2. This will be the foundation of our application's settings management.")

    st.markdown(f"#### File: `src/pe_orgair/config/settings.py`")
    st.markdown(
        f"This module defines our application settings with comprehensive validation:")

    st.code('''"""Application configuration with comprehensive validation."""
from typing import Optional, Literal, List
from functools import lru_cache
from decimal import Decimal
from pydantic import Field, field_validator, model_validator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings with production-grade validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "4.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"
    SECRET_KEY: SecretStr
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000)
    
    # Parameter Version
    PARAM_VERSION: Literal["v1.0", "v2.0"] = "v2.0"
    
    # Snowflake
    SNOWFLAKE_ACCOUNT: str
    SNOWFLAKE_USER: str
    SNOWFLAKE_PASSWORD: SecretStr
    SNOWFLAKE_DATABASE: str = "PE_ORGAIR"
    SNOWFLAKE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_WAREHOUSE: str
    SNOWFLAKE_ROLE: str = "PE_ORGAIR_ROLE"
    
    # AWS
    AWS_ACCESS_KEY_ID: SecretStr
    AWS_SECRET_ACCESS_KEY: SecretStr
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECTORS: int = 86400  # 24 hours
    CACHE_TTL_SCORES: int = 3600    # 1 hour
    
    # LLM Providers (Multi-provider via LiteLLM)
    OPENAI_API_KEY: Optional[SecretStr] = None
    ANTHROPIC_API_KEY: Optional[SecretStr] = None
    DEFAULT_LLM_MODEL: str = "gpt-4o-2024-08-06"
    FALLBACK_LLM_MODEL: str = "claude-sonnet-4-20250514"
    
    # Cost Management (NEW)
    DAILY_COST_BUDGET_USD: float = Field(default=500.0, ge=0)
    COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1)
    
    # Scoring Parameters (v2.0)
    ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.55, le=0.70)
    BETA_SYNERGY_WEIGHT: float = Field(default=0.12, ge=0.08, le=0.20)
    LAMBDA_PENALTY: float = Field(default=0.25, ge=0, le=0.50)
    DELTA_POSITION: float = Field(default=0.15, ge=0.10, le=0.20)
    
    # Dimension Weights
    W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0)
    W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0)
    W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0)
    W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0)
    W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0)
    W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0)
    
    # HITL Thresholds (NEW)
    HITL_SCORE_CHANGE_THRESHOLD: float = Field(default=15.0, ge=5, le=30)
    HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(default=10.0, ge=5, le=25)
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    OTEL_SERVICE_NAME: str = "pe-orgair"
    
    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
        if v is not None and not v.get_secret_value().startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format")
        return v
    
    @model_validator(mode="after")
    def validate_dimension_weights(self):
        """Validate dimension weights sum to 1.0."""
        weights = [
            self.W_DATA_INFRA, self.W_AI_GOVERNANCE, self.W_TECH_STACK,
            self.W_TALENT, self.W_LEADERSHIP, self.W_USE_CASES, self.W_CULTURE
        ]
        total = sum(weights)
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Dimension weights must sum to 1.0, got {total}")
        return self
    
    @model_validator(mode="after")
    def validate_production_settings(self):
        """Ensure production has required security settings."""
        if self.APP_ENV == "production":
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")
            if len(self.SECRET_KEY.get_secret_value()) < 32:
                raise ValueError("SECRET_KEY must be ≥32 characters in production")
            if not self.OPENAI_API_KEY and not self.ANTHROPIC_API_KEY:
                raise ValueError("At least one LLM API key required in production")
        return self
    
    @property
    def dimension_weights(self) -> List[float]:
        """Get dimension weights as list."""
        return [
            self.W_DATA_INFRA, self.W_AI_GOVERNANCE, self.W_TECH_STACK,
            self.W_TALENT, self.W_LEADERSHIP, self.W_USE_CASES, self.W_CULTURE
        ]

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()''', language='python')

    st.markdown(f"#### Key Features:")
    st.markdown(
        f"- **Type Safety**: All settings are strongly typed with proper validation")
    st.markdown(
        f"- **Security**: Sensitive data uses `SecretStr` to prevent accidental exposure")
    st.markdown(
        f"- **Field Validation**: Range constraints (e.g., `ge=1, le=1000`) ensure values are within bounds")
    st.markdown(
        f"- **Cross-Field Validation**: `@model_validator` ensures dimension weights sum to 1.0")
    st.markdown(
        f"- **Environment-Specific Rules**: Production environment has stricter requirements")

    if st.button("Load Default Configuration Settings"):
        _set_env_vars(GLOBAL_REQUIRED_ENV_VARS)
        get_settings.cache_clear()
        try:
            st.session_state.current_settings = get_settings()
            st.session_state.settings_initialized = True
            st.success("✅ Default settings loaded successfully!")
        except ValidationError as e:
            st.error(f"❌ Error loading default settings: {e}")
            st.session_state.settings_initialized = False
            st.session_state.current_settings = None
        finally:
            _clear_env_vars()

    if st.session_state.settings_initialized and st.session_state.current_settings:
        settings = st.session_state.current_settings
        st.markdown(f"**Loaded Configuration:**")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"- App Name: `{settings.APP_NAME}`")
            st.markdown(f"- Environment: `{settings.APP_ENV}`")
            st.markdown(f"- Debug Mode: `{settings.DEBUG}`")
            st.markdown(
                f"- API Rate Limit: `{settings.RATE_LIMIT_PER_MINUTE}` req/min")
        with col2:
            st.markdown(
                f"- Daily Cost Budget: `${settings.DAILY_COST_BUDGET_USD}`")
            st.markdown(
                f"- Cost Alert Threshold: `{settings.COST_ALERT_THRESHOLD_PCT*100}%`")
            st.markdown(
                f"- HITL Score Threshold: `{settings.HITL_SCORE_CHANGE_THRESHOLD}`")
            st.markdown(
                f"- Secret Key Set: `{'Yes' if settings.SECRET_KEY else 'No'}` (masked)")
    st.markdown(f"---")

elif st.session_state.current_page == "3. FastAPI Application Setup":
    st.markdown(f"### Task 1.3: FastAPI Application with Middleware")
    st.markdown(f"With our configuration system in place, let's build the FastAPI application with comprehensive middleware for logging, tracing, and error handling.")

    st.markdown(f"#### File: `src/pe_orgair/api/main.py`")
    st.code('''"""FastAPI application with comprehensive middleware stack."""
from contextlib import asynccontextmanager
from typing import Callable
import time
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from pe_orgair.config.settings import settings
from pe_orgair.api.routes.v1 import router as v1_router
from pe_orgair.api.routes.v2 import router as v2_router
from pe_orgair.api.routes import health
from pe_orgair.observability.setup import setup_tracing, setup_logging

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with startup/shutdown."""
    # Startup
    logger.info("starting_application",
                app_name=settings.APP_NAME,
                version=settings.APP_VERSION,
                env=settings.APP_ENV)
    
    # Initialize connections, caches, etc.
    # await initialize_redis()
    # await validate_database()
    
    yield
    
    # Shutdown
    logger.info("shutting_down_application")

def create_app() -> FastAPI:
    """Application factory."""
    setup_logging()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else [],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request correlation middleware
    @app.middleware("http")
    async def add_correlation_id(request: Request, call_next: Callable) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time
        
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        
        return response
    
    # Global error handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled_exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "type": "https://api.pe-orgair.example.com/errors/internal",
                "title": "Internal Server Error",
                "status": 500,
                "detail": str(exc) if settings.DEBUG else "An internal error occurred",
            },
        )
    
    # Tracing
    setup_tracing(app)
    
    # Routes
    app.include_router(health.router, tags=["Health"])
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)
    app.include_router(v2_router, prefix=settings.API_V2_PREFIX)
    
    return app

app = create_app()''', language='python')

    st.markdown(f"#### Key Features:")
    st.markdown(
        f"- **Lifespan Management**: Proper startup/shutdown handling for resources")
    st.markdown(
        f"- **Request Correlation**: Each request gets a unique ID for distributed tracing")
    st.markdown(
        f"- **Performance Tracking**: Request duration automatically logged")
    st.markdown(
        f"- **Error Handling**: Global exception handler with environment-aware error details")
    st.markdown(f"- **Security**: CORS properly configured based on environment")

    st.info("💡 **Best Practice:** The lifespan context manager ensures proper cleanup of database connections, cache clients, and other resources when the application shuts down.")
    st.markdown(f"---")

elif st.session_state.current_page == "1. Initial Setup: Core Configuration":
    st.markdown(f"### 1. Initial Setup: Environment and Dependencies")
    st.markdown(f"Before we dive into defining and validating our application settings, let's ensure our environment has all the necessary tools. We'll specifically need `pydantic` and `pydantic-settings` for robust configuration management.")
    st.markdown(
        f"```python\n!pip install pydantic==2.* pydantic-settings==2.*\n```")
elif st.session_state.current_page == "4. Field-Level Validation":
    st.markdown(f"### 3. Ensuring Operational Integrity: Field-Level Validation")
    st.markdown(f"Operational parameters like API rate limits, daily cost budgets, and alert thresholds are critical for the stability and cost-effectiveness of our PE intelligence platform. As a Data Engineer, I need to ensure these values are always within sensible, predefined ranges to prevent system overload, budget overruns, or ineffective alerting. Pydantic's `Field` with `ge` (greater than or equal to) and `le` (less than or equal to) arguments allows us to enforce these constraints directly within the configuration definition.")

    st.markdown(f"#### Field-Level Validation Code")
    st.markdown(
        f"Here's how we define field-level constraints using Pydantic's `Field`:")
    st.code('''# API Rate Limiting
RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=1, le=1000)

# Cost Management
DAILY_COST_BUDGET_USD: float = Field(default=500.0, ge=0)
COST_ALERT_THRESHOLD_PCT: float = Field(default=0.8, ge=0, le=1)

# HITL (Human-In-The-Loop) Thresholds
HITL_SCORE_CHANGE_THRESHOLD: float = Field(default=15.0, ge=5, le=30)
HITL_EBITDA_PROJECTION_THRESHOLD: float = Field(default=10.0, ge=5, le=25)

# Scoring Parameters
ALPHA_VR_WEIGHT: float = Field(default=0.60, ge=0.55, le=0.70)
BETA_SYNERGY_WEIGHT: float = Field(default=0.12, ge=0.08, le=0.20)
LAMBDA_PENALTY: float = Field(default=0.25, ge=0, le=0.50)
DELTA_POSITION: float = Field(default=0.15, ge=0.10, le=0.20)''', language='python')

    st.markdown(
        f"#### Workflow Task: Validate Operational Parameters with Range Constraints")
    st.markdown(f"We'll define an API rate limit (`RATE_LIMIT_PER_MINUTE`), a daily cost budget (`DAILY_COST_BUDGET_USD`), and a cost alert threshold (`COST_ALERT_THRESHOLD_PCT`). These parameters are crucial for system health and financial governance.")

    st.markdown(f"Configure the operational parameters below and click 'Validate'. Observe how Pydantic handles values outside the expected ranges:")

    col1, col2 = st.columns(2)
    with col1:
        rate_limit = st.number_input(
            "API Rate Limit (1-1000 req/min)", min_value=1, max_value=1500, value=100, step=10)
        daily_budget = st.number_input(
            "Daily Cost Budget (USD, >=0)", min_value=-50.0, max_value=2000.0, value=1000.0, step=10.0)
        hitl_score_change = st.number_input(
            "HITL Score Change Threshold (5-30)", min_value=2.0, max_value=50.0, value=20.0, step=1.0)
    with col2:
        cost_threshold = st.slider("Cost Alert Threshold (0-1, e.g., 0.75 for 75%)",
                                   min_value=0.0, max_value=1.5, value=0.75, step=0.01)
        hitl_ebitda_projection = st.number_input(
            "HITL EBITDA Projection Threshold (5-25)", min_value=5.0, max_value=50.0, value=15.0, step=1.0)

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
            st.markdown(
                f"  API Rate Limit: `{settings.RATE_LIMIT_PER_MINUTE}` req/min")
            st.markdown(
                f"  Daily Cost Budget: `${settings.DAILY_COST_BUDGET_USD}`")
            st.markdown(
                f"  Cost Alert Threshold: `{settings.COST_ALERT_THRESHOLD_PCT*100}%`")
            st.markdown(
                f"  HITL Score Change Threshold: `{settings.HITL_SCORE_CHANGE_THRESHOLD}`")
            st.markdown(
                f"  HITL EBITDA Projection Threshold: `{settings.HITL_EBITDA_PROJECTION_THRESHOLD}`")
        except ValidationError as e:
            st.session_state.operational_settings_valid = False
            st.session_state.operational_validation_error = e
            st.error(
                f"❌ Operational settings are INVALID! Details: \n```\n{e}\n```")
        finally:
            _clear_env_vars()

    if st.session_state.operational_validation_error:
        st.markdown(f"**Last Validation Result:**")
        if st.session_state.operational_settings_valid:
            st.success("✅ Valid settings were loaded last.")
        else:
            st.error(
                f"❌ Last attempt resulted in an error:\n```\n{st.session_state.operational_validation_error}\n```")

    st.markdown(f"The first scenario demonstrates successful loading when all operational parameters are within their defined bounds. In contrast, the second scenario attempts to load configurations with values exceeding or falling below the specified ranges for `RATE_LIMIT_PER_MINUTE`, `DAILY_COST_BUDGET_USD`, `COST_ALERT_THRESHOLD_PCT`, `HITL_SCORE_CHANGE_THRESHOLD`, and `HITL_EBITDA_PROJECTION_THRESHOLD`. Pydantic immediately raises a `ValidationError`, providing clear, detailed messages about which specific fields failed and why. This automatic, early detection of out-of-bounds values by `Field(ge=X, le=Y)` is crucial. It prevents the system from starting with configurations that could lead to financial losses (e.g., negative budget), operational issues (e.g., excessively high rate limits), or ineffective human-in-the-loop interventions due to inappropriate thresholds.")
    st.markdown(f"---")

elif st.session_state.current_page == "5. Cross-Field Validation (Scoring Weights)":
    st.markdown(
        f"### 4. Implementing Business Logic: Cross-Field Validation for Scoring Weights")
    st.markdown(f"A core component of the PE intelligence platform is its investment scoring model, which relies on various dimensions (e.g., data infrastructure, AI governance, talent). The relative importance of these dimensions is defined by a set of weights. A critical business rule mandates that these **dimension weights must sum up to exactly 1.0** to ensure a coherent and balanced scoring mechanism. Deviations from this sum would lead to skewed, unreliable scores and potentially poor investment recommendations.")
    st.markdown(f"As a Data Engineer, I need to implement a robust check to enforce this rule. Pydantic's `@model_validator(mode=\"after\")` is perfect for this, as it allows us to perform validation logic that involves multiple fields *after* individual field validations have passed.")

    st.markdown(f"#### Cross-Field Validation Code")
    st.markdown(
        f"Here's how we implement cross-field validation to ensure dimension weights sum to 1.0:")
    st.code('''# Dimension Weight Fields
W_DATA_INFRA: float = Field(default=0.18, ge=0.0, le=1.0)
W_AI_GOVERNANCE: float = Field(default=0.15, ge=0.0, le=1.0)
W_TECH_STACK: float = Field(default=0.15, ge=0.0, le=1.0)
W_TALENT: float = Field(default=0.17, ge=0.0, le=1.0)
W_LEADERSHIP: float = Field(default=0.13, ge=0.0, le=1.0)
W_USE_CASES: float = Field(default=0.12, ge=0.0, le=1.0)
W_CULTURE: float = Field(default=0.10, ge=0.0, le=1.0)

@model_validator(mode="after")
def validate_dimension_weights(self):
    """Validate dimension weights sum to 1.0."""
    weights = [
        self.W_DATA_INFRA, self.W_AI_GOVERNANCE, self.W_TECH_STACK,
        self.W_TALENT, self.W_LEADERSHIP, self.W_USE_CASES, self.W_CULTURE
    ]
    total = sum(weights)
    if abs(total - 1.0) > 0.001:  # Small tolerance for floating-point precision
        raise ValueError(f"Dimension weights must sum to 1.0, got {total}")
    return self''', language='python')

    st.markdown(f"#### Workflow Task: Validate Dimension Weights Sum to 1.0")
    st.markdown(f"We will define new fields for dimension weights and then add a `@model_validator` to ensure their sum is $1.0$. A small tolerance $\epsilon$ is used to account for floating-point inaccuracies. The validation check will be:")

    st.markdown(r"$$\left| \sum_{{i=1}}^{{n}} w_i - 1.0 \right| > \epsilon$$")
    st.markdown(r"where $w_i$ are the dimension weights and $\epsilon = 0.001$.")

    st.markdown(f"Adjust the dimension weights below. Ensure their sum is approximately 1.0 (within 0.001 tolerance) to pass validation. The default values sum to 1.0.")

    col1, col2 = st.columns(2)
    with col1:
        w_data_infra = st.slider(
            "W_DATA_INFRA", min_value=0.0, max_value=1.0, value=0.18, step=0.01)
        w_ai_governance = st.slider(
            "W_AI_GOVERNANCE", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
        w_tech_stack = st.slider(
            "W_TECH_STACK", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
        w_talent = st.slider("W_TALENT", min_value=0.0,
                             max_value=1.0, value=0.17, step=0.01)
    with col2:
        w_leadership = st.slider(
            "W_LEADERSHIP", min_value=0.0, max_value=1.0, value=0.13, step=0.01)
        w_use_cases = st.slider(
            "W_USE_CASES", min_value=0.0, max_value=1.0, value=0.12, step=0.01)
        w_culture = st.slider("W_CULTURE", min_value=0.0,
                              max_value=1.0, value=0.10, step=0.01)

    weights_sum = w_data_infra + w_ai_governance + w_tech_stack + \
        w_talent + w_leadership + w_use_cases + w_culture
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
            st.error(
                f"❌ Dimension weights are INVALID! Details: \n```\n{e}\n```")
        finally:
            _clear_env_vars()

    if st.session_state.weights_validation_error:
        st.markdown(f"**Last Validation Result:**")
        if st.session_state.weights_settings_valid:
            st.success("✅ Valid settings were loaded last.")
        else:
            st.error(
                f"❌ Last attempt resulted in an error:\n```\n{st.session_state.weights_validation_error}\n```")

    st.markdown(f"The first scenario successfully loads settings where the default dimension weights (or explicitly set ones that sum to 1.0) pass the `@model_validator`. This demonstrates a correct configuration. The second scenario, however, intentionally provides weights that do not sum to $1.0$. As expected, Pydantic's `@model_validator` catches this discrepancy and raises a `ValueError` wrapped within a `ValidationError`.")
    st.markdown(f"This validation is critical for the PE intelligence platform. It ensures that the investment scoring model is always configured with logically consistent weights, preventing calculation errors that could lead to flawed analytical outputs and incorrect investment decisions. It’s a direct safeguard against subtle yet significant business logic flaws that might otherwise only be detected much later in the analysis pipeline, if at all.")
    st.markdown(f"---")

elif st.session_state.current_page == "6. Environment-Specific Validation (Production)":
    st.markdown(
        f"### 5. Fortifying Production: Conditional Environment-Specific Validation")
    st.markdown(f"Deploying to a production environment demands a heightened level of rigor. As a Software Developer, I need to ensure that certain security and operational settings are strictly enforced *only* when the application is running in a `production` environment. For instance, `DEBUG` mode must be disabled, sensitive `SECRET_KEY`s must meet minimum length requirements, and all critical external service API keys (like LLM provider keys) must be present.")
    st.markdown(f"This conditional validation logic is best implemented using another `@model_validator(mode=\"after\")`, which allows us to inspect the `APP_ENV` and apply specific rules accordingly. We'll also include a `@field_validator` for `OPENAI_API_KEY` to ensure it starts with the expected \"sk-\" prefix, an example of a specific format requirement.")

    st.markdown(f"#### Validation Code Implementation")
    st.markdown(
        f"Here's the code that validates production settings and API key formats:")
    st.code('''@field_validator("OPENAI_API_KEY")
@classmethod
def validate_openai_key(cls, v: Optional[SecretStr]) -> Optional[SecretStr]:
    if v is not None and not v.get_secret_value().startswith("sk-"):
        raise ValueError("Invalid OpenAI API key format: must start with 'sk-'")
    return v

@model_validator(mode="after")
def validate_production_settings(self) -> "Settings":
    """Ensure production environment has required security settings."""
    if self.APP_ENV == "production":
        if self.DEBUG:
            raise ValueError("DEBUG must be False in production")
        if len(self.SECRET_KEY.get_secret_value()) < 32:
            raise ValueError("SECRET_KEY must be ≥32 characters in production")
        if not self.OPENAI_API_KEY and not self.ANTHROPIC_API_KEY:
            raise ValueError("At least one LLM API key (OpenAI or Anthropic) is required in production")
    return self''', language='python')

    st.markdown(
        f"#### Workflow Task: Enforce Production Security and API Key Presence")
    st.markdown(f"We will add a `@model_validator` to the `Settings` class that performs the following checks when `APP_ENV` is set to `\"production\"`:")
    st.markdown(f"1.  `DEBUG` mode must be `False`.")
    st.markdown(f"2.  `SECRET_KEY` length must be at least 32 characters.")
    st.markdown(
        f"3.  At least one of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` must be provided.")

    st.markdown(
        f"Configure the settings below, paying attention to production requirements:")

    col1, col2 = st.columns(2)
    with col1:
        app_env = st.selectbox(
            "APP_ENV", ["development", "staging", "production"], index=0)
        debug_mode = st.checkbox(
            "DEBUG Mode", value=True if app_env == "development" else False)
        secret_key = st.text_input(
            "SECRET_KEY (min 32 chars in production)", "dev_key_for_testing_12345678901234567890")
    with col2:
        openai_key = st.text_input("OPENAI_API_KEY (starts with 'sk-')", "")
        anthropic_key = st.text_input("ANTHROPIC_API_KEY", "")
        st.markdown(f"*(Note: One LLM API key is required in production)*")

    # Client-side validation feedback
    validation_messages = []

    if not openai_key and not anthropic_key and app_env == "production":
        st.warning("⚠️ At least one LLM API key is required in production")
        validation_messages.append("No LLM API key provided")

    if openai_key and not openai_key.startswith("sk-"):
        st.warning("⚠️ OpenAI API key should start with 'sk-'")
        validation_messages.append("OpenAI key format invalid")

    if anthropic_key and not anthropic_key.startswith("sk-ant-"):
        st.info("💡 Anthropic API keys typically start with 'sk-ant-'")

    if app_env == "production":
        if len(secret_key) < 32:
            st.warning(
                f"⚠️ SECRET_KEY is only {len(secret_key)} characters. Production requires ≥32 characters.")
            validation_messages.append("SECRET_KEY too short")

        if not openai_key and not anthropic_key:
            st.warning(
                "⚠️ Production environment requires at least one LLM API key")
            validation_messages.append("No LLM API key provided")

        if debug_mode:
            st.warning("⚠️ DEBUG mode should be disabled in production")
            validation_messages.append("DEBUG enabled in production")

    if st.button("Validate Settings"):
        # Explicitly clear API key environment variables first
        _clear_env_vars()

        env_vars = {
            "APP_ENV": app_env,
            "DEBUG": debug_mode,
            "SECRET_KEY": secret_key,
        }

        # Only set API keys if they're non-empty
        if openai_key and openai_key.strip():
            env_vars["OPENAI_API_KEY"] = openai_key
        if anthropic_key and anthropic_key.strip():
            env_vars["ANTHROPIC_API_KEY"] = anthropic_key

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
            st.markdown(
                f"  SECRET_KEY length: `{len(settings.SECRET_KEY.get_secret_value())}`")
            st.markdown(
                f"  OpenAI API Key provided: `{'Yes' if settings.OPENAI_API_KEY else 'No'}`")
            st.markdown(
                f"  Anthropic API Key provided: `{'Yes' if settings.ANTHROPIC_API_KEY else 'No'}`")
        except ValidationError as e:
            st.session_state.prod_settings_valid = False
            st.session_state.prod_validation_error = e
            st.error(
                f"❌ Production settings are INVALID! Details: \n```\n{e}\n```")
        finally:
            _clear_env_vars()

    if st.session_state.prod_validation_error:
        st.markdown(f"**Last Validation Result:**")
        if st.session_state.prod_settings_valid:
            st.success("✅ Valid settings were loaded last.")
        else:
            st.error(
                f"❌ Last attempt resulted in an error:\n```\n{st.session_state.prod_validation_error}\n```")

    st.markdown(f"For a Software Developer or Data Engineer, these explicit error messages at application startup are invaluable. They act as an immediate feedback mechanism, preventing the deployment of insecure or non-functional configurations to live environments. This proactive validation drastically reduces the risk of security breaches, service outages, or unexpected runtime behavior stemming from configuration errors.")
    st.markdown(f"---")

elif st.session_state.current_page == "Configuration Simulation & Troubleshooting":
    st.markdown(
        f"### 6. Catching Errors Early: Configuration Simulation and Reporting")
    st.markdown(f"The ultimate value of a robust configuration validation system is its ability to prevent failures before they impact users. As a Data Engineer preparing a deployment, I need a way to confidently verify that a given set of environment variables or configuration files will result in a valid application state. This \"Validated Configuration Report\" ensures that any potential issues are identified and resolved during development or staging, rather than during a critical production rollout.")
    st.markdown(f"We can simulate different configuration scenarios and observe Pydantic's error reporting. This acts as our \"report,\" detailing what works and what breaks, and why.")

    st.markdown(f"### Common Mistakes & Troubleshooting")

    st.markdown(f"#### ❌ Mistake 1: Dimension weights don't sum to 1.0")
    st.code('''# WRONG
W_DATA_INFRA = 0.20
W_AI_GOVERNANCE = 0.15
W_TECH_STACK = 0.15
W_TALENT = 0.20
W_LEADERSHIP = 0.15
W_USE_CASES = 0.10
W_CULTURE = 0.10
# Sum = 1.05!''', language='python')

    if st.button("Show Fix for Mistake 1", key="fix_btn_1"):
        st.session_state.show_fix_1 = not st.session_state.show_fix_1

    if st.session_state.show_fix_1:
        st.success("✅ **Fixed Code:**")
        st.code('''# CORRECT
W_DATA_INFRA = 0.18
W_AI_GOVERNANCE = 0.15
W_TECH_STACK = 0.15
W_TALENT = 0.17
W_LEADERSHIP = 0.13
W_USE_CASES = 0.12
W_CULTURE = 0.10
# Sum = 1.00 ✓

@model_validator(mode="after")
def validate_dimension_weights(self):
    """Validate dimension weights sum to 1.0."""
    weights = [
        self.W_DATA_INFRA, self.W_AI_GOVERNANCE, self.W_TECH_STACK,
        self.W_TALENT, self.W_LEADERSHIP, self.W_USE_CASES, self.W_CULTURE
    ]
    total = sum(weights)
    if abs(total - 1.0) > 0.001:
        raise ValueError(f"Dimension weights must sum to 1.0, got {total}")
    return self''', language='python')
        st.markdown(f"**Explanation:** The `@model_validator` automatically catches invalid weight sums at startup, preventing configuration errors from reaching production.")

    st.markdown(f"#### ❌ Mistake 2: Exposing secrets in logs")
    st.code('''# WRONG
logger.info("connecting", password=settings.SNOWFLAKE_PASSWORD)''', language='python')

    if st.button("Show Fix for Mistake 2", key="fix_btn_2"):
        st.session_state.show_fix_2 = not st.session_state.show_fix_2

    if st.session_state.show_fix_2:
        st.success("✅ **Fixed Code:**")
        st.code('''# CORRECT - SecretStr masks the value automatically
from pydantic import SecretStr

class Settings(BaseSettings):
    SNOWFLAKE_PASSWORD: SecretStr  # Will be masked in logs
    
# Safe logging - password is masked
logger.info("connecting", password=settings.SNOWFLAKE_PASSWORD)
# Output: password=SecretStr('**********')

# Only access the secret when actually needed
actual_password = settings.SNOWFLAKE_PASSWORD.get_secret_value()''', language='python')
        st.markdown(f"**Explanation:** `SecretStr` automatically masks sensitive values in logs and string representations, preventing accidental exposure.")

    st.markdown(f"#### ❌ Mistake 3: Missing lifespan context manager")
    st.code('''# WRONG - No cleanup on shutdown
app = FastAPI()
redis_client = Redis()  # Leaks on shutdown!''', language='python')

    if st.button("Show Fix for Mistake 3", key="fix_btn_3"):
        st.session_state.show_fix_3 = not st.session_state.show_fix_3

    if st.session_state.show_fix_3:
        st.success("✅ **Fixed Code:**")
        st.code('''# CORRECT - Proper resource management
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    redis_client = Redis()
    logger.info("redis_connected")
    
    yield  # Application runs here
    
    # Shutdown - guaranteed cleanup
    await redis_client.close()
    logger.info("redis_disconnected")

app = FastAPI(lifespan=lifespan)''', language='python')
        st.markdown(f"**Explanation:** The lifespan context manager ensures proper cleanup of connections and resources when the application shuts down, preventing resource leaks.")

    st.markdown(f"#### ❌ Mistake 4: Not validating at startup")
    st.code('''# WRONG - Fails at runtime when first used
def get_sector_baseline(sector_id):
    return db.query(...)  # Database not connected!''', language='python')

    if st.button("Show Fix for Mistake 4", key="fix_btn_4"):
        st.session_state.show_fix_4 = not st.session_state.show_fix_4

    if st.session_state.show_fix_4:
        st.success("✅ **Fixed Code:**")
        st.code('''# CORRECT - Validate at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup validation
    settings = get_settings()  # Pydantic validates here
    
    # Test database connection
    try:
        await db.execute("SELECT 1")
        logger.info("database_validated")
    except Exception as e:
        logger.error("database_validation_failed", error=str(e))
        raise  # Fail fast - don't start if DB is unreachable
    
    yield
    
    # Shutdown
    await db.close()

app = FastAPI(lifespan=lifespan)

# Now this is safe - we know DB is connected
def get_sector_baseline(sector_id):
    return db.query(...)''', language='python')
        st.markdown(f"**Explanation:** Validate all external dependencies during startup using the lifespan context manager. This ensures the application fails fast with clear errors rather than failing mysteriously at runtime.")

    st.markdown(f"---")


# License
st.caption('''
## QuantUniversity License

© QuantUniversity 2025  
This notebook was created for **educational purposes only** and is **not intended for commercial use**.  

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.  
- You **may not delete or modify this license cell** without authorization.  
- This notebook was generated using **QuCreate**, an AI-powered assistant.  
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.  

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
''')
