import os
import re
import time
import uuid
from collections import defaultdict, deque
from functools import wraps
from io import BytesIO
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, g, has_request_context, request, jsonify, redirect, send_file
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_migrate import Migrate
from flask_cors import CORS
import logging

from database import db, UploadedFile, User_Detail

# Load environment variables
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=True)

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///business_automation.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret-key-change-me-32-characters")
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key-change-me-32-chars")
app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER", "uploads")
app.config['FILE_STORAGE_DIR'] = os.getenv("FILE_STORAGE_DIR", app.config['UPLOAD_FOLDER'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['FORCE_HTTPS'] = os.getenv("FORCE_HTTPS", "false").lower() == "true"
app.config['TRUST_PROXY_HEADERS'] = os.getenv("TRUST_PROXY_HEADERS", "false").lower() == "true"
app.config['LOG_LEVEL'] = os.getenv("LOG_LEVEL", "INFO").upper()
app.config['LOG_FILE'] = os.getenv("LOG_FILE", str(ROOT_DIR / "logs" / "backend.log"))
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['FILE_STORAGE_DIR'], exist_ok=True)

if app.config['TRUST_PROXY_HEADERS']:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
migrate = Migrate(app, db, directory=str(ROOT_DIR / "migrations"))
allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501").split(",")
    if origin.strip()
]
CORS(app, origins=allowed_origins)


EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z\s'.-]{1,98}[A-Za-z.]$")
PASSWORD_SPECIAL_RE = re.compile(r"[^A-Za-z0-9]")
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json"}
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")
_rate_limit_buckets = defaultdict(deque)


def configure_logging():
    log_level = getattr(logging, app.config['LOG_LEVEL'], logging.INFO)
    app.logger.setLevel(log_level)
    app.logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(request_id)s] %(remote_addr)s %(method)s %(path)s - %(message)s"
    )

    class RequestContextFilter(logging.Filter):
        def filter(self, record):
            if has_request_context():
                record.request_id = getattr(g, "request_id", "-")
                record.remote_addr = _client_ip()
                record.method = request.method
                record.path = request.path
            else:
                record.request_id = "-"
                record.remote_addr = "-"
                record.method = "-"
                record.path = "-"
            return True

    context_filter = RequestContextFilter()
    log_file = Path(app.config['LOG_FILE'])
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(context_filter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)


def api_error(message, status_code=400, error_code="bad_request", details=None):
    payload = {
        "error": {
            "code": error_code,
            "message": message,
            "request_id": getattr(g, "request_id", None),
        }
    }
    if details:
        payload["error"]["details"] = details
    return jsonify(payload), status_code


def api_success(data=None, status_code=200, message=None):
    payload = {
        "data": data or {},
        "request_id": getattr(g, "request_id", None),
    }
    if message:
        payload["message"] = message
    return jsonify(payload), status_code


configure_logging()


def _client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if app.config['TRUST_PROXY_HEADERS'] and forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "unknown"


def rate_limit(max_requests, window_seconds, key_func=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            bucket_key = key_func() if key_func else f"{_client_ip()}:{request.endpoint}"
            now = time.time()
            bucket = _rate_limit_buckets[bucket_key]
            while bucket and now - bucket[0] >= window_seconds:
                bucket.popleft()
            if len(bucket) >= max_requests:
                retry_after = max(1, int(window_seconds - (now - bucket[0])))
                response, status = api_error("Too many requests. Please try again later.", 429, "rate_limited")
                return response, status, {"Retry-After": str(retry_after)}
            bucket.append(now)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def sanitize_text(value, max_length):
    if not isinstance(value, str):
        return ""
    cleaned = CONTROL_CHARS_RE.sub("", value).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace("<", "").replace(">", "")
    return cleaned[:max_length]


def sanitize_email(value):
    return sanitize_text(value, 254).lower()


def parse_pagination(default_per_page=20, max_per_page=100):
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get("per_page", default_per_page))
    except (TypeError, ValueError):
        per_page = default_per_page

    page = max(page, 1)
    per_page = min(max(per_page, 1), max_per_page)
    return page, per_page


def require_json_body(required_fields):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, api_error("Request body must be a JSON object.", 400, "invalid_json")

    missing = [field for field in required_fields if data.get(field) in (None, "")]
    if missing:
        return None, api_error(
            "Missing required fields.",
            400,
            "missing_required_fields",
            {"fields": missing},
        )
    return data, None


def validate_signup_payload():
    data, error = require_json_body(("full_name", "email", "password"))
    if error:
        return None, error

    full_name = sanitize_text(data.get("full_name"), 100)
    email = sanitize_email(data.get("email"))
    password = data.get("password")

    field_errors = {}
    if not NAME_RE.match(full_name):
        field_errors["full_name"] = "Full name must be 3-100 characters and contain only letters, spaces, apostrophes, periods, or hyphens."
    if not EMAIL_RE.match(email):
        field_errors["email"] = "Enter a valid email address."
    password_error = validate_password(password, email=email, full_name=full_name)
    if password_error:
        field_errors["password"] = password_error

    if field_errors:
        return None, api_error("Request validation failed.", 400, "validation_error", field_errors)

    return {"full_name": full_name, "email": email, "password": password}, None


def validate_login_payload():
    data, error = require_json_body(("email", "password"))
    if error:
        return None, error

    email = sanitize_email(data.get("email"))
    password = data.get("password")
    field_errors = {}
    if not EMAIL_RE.match(email):
        field_errors["email"] = "Enter a valid email address."
    if not isinstance(password, str):
        field_errors["password"] = "Password is required."

    if field_errors:
        return None, api_error("Request validation failed.", 400, "validation_error", field_errors)

    return {"email": email, "password": password}, None


def validate_filename(value):
    filename = secure_filename(sanitize_text(value or "", 255))
    if not filename:
        return None, api_error("Filename is required", 400, "missing_filename")
    return filename, None


def pagination_payload(pagination):
    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }


def _storage_root():
    return Path(app.config['FILE_STORAGE_DIR']).resolve()


def store_uploaded_bytes(user_id, filename, file_data):
    user_dir = _storage_root() / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{filename}"
    destination = user_dir / stored_name
    destination.write_bytes(file_data)
    return str(destination.relative_to(_storage_root()))


def resolve_stored_file(storage_path):
    if not storage_path:
        return None
    root = _storage_root()
    resolved = (root / storage_path).resolve()
    if root != resolved and root not in resolved.parents:
        app.logger.warning("blocked file read outside storage root: %s", storage_path)
        return None
    return resolved if resolved.exists() and resolved.is_file() else None


def send_uploaded_file(file_entry):
    stored_file = resolve_stored_file(file_entry.storage_path)
    mimetype = file_entry.content_type or "application/octet-stream"
    if stored_file:
        return send_file(
            BytesIO(stored_file.read_bytes()),
            as_attachment=True,
            download_name=file_entry.filename,
            mimetype=mimetype,
        )
    if file_entry.file_data:
        return send_file(
            BytesIO(file_entry.file_data),
            as_attachment=True,
            download_name=file_entry.filename,
            mimetype=mimetype,
        )
    return api_error("Stored file content is unavailable.", 404, "file_content_missing")


def delete_stored_file(file_entry):
    stored_file = resolve_stored_file(file_entry.storage_path)
    if not stored_file:
        return
    try:
        stored_file.unlink()
    except OSError:
        app.logger.exception("failed to delete stored file id=%s", file_entry.id)


def validate_password(password, email="", full_name=""):
    if not isinstance(password, str):
        return "Password is required."
    if len(password) < 12:
        return "Password must be at least 12 characters long."
    if len(password) > 128:
        return "Password must be 128 characters or fewer."
    if not re.search(r"[A-Z]", password):
        return "Password must include an uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must include a lowercase letter."
    if not re.search(r"\d", password):
        return "Password must include a number."
    if not PASSWORD_SPECIAL_RE.search(password):
        return "Password must include a special character."

    lowered = password.lower()
    local_part = email.split("@", 1)[0].lower() if email else ""
    name_parts = [part.lower() for part in re.split(r"\s+", full_name) if len(part) >= 3]
    if local_part and local_part in lowered:
        return "Password must not contain your email username."
    if any(part in lowered for part in name_parts):
        return "Password must not contain your name."
    return None


def _auth_rate_key():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        data = {}
    email = sanitize_email(data.get("email") or "")
    return f"{_client_ip()}:{request.endpoint}:{email}"


@app.before_request
def assign_request_id():
    g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex


@app.before_request
def enforce_https():
    if not app.config['FORCE_HTTPS'] or request.is_secure or request.host.startswith(("127.0.0.1", "localhost")):
        return None
    url = request.url.replace("http://", "https://", 1)
    return redirect(url, code=308)


@app.after_request
def add_security_headers(response):
    response.headers["X-Request-ID"] = getattr(g, "request_id", "")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'")
    if app.config['FORCE_HTTPS'] or request.is_secure:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.after_request
def log_request(response):
    app.logger.info("request completed with status %s", response.status_code)
    return response


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    app.logger.warning("http error %s: %s", error.code, error.description)
    # Normalize all Werkzeug HTTP errors to the shared API error envelope.
    return api_error(
        error.description,
        getattr(error, "code", 400),
        str(getattr(error, "name", "http_error")).lower().replace(" ", "_"),
    )



@app.errorhandler(SQLAlchemyError)
def handle_database_exception(error):
    db.session.rollback()
    app.logger.exception("database error")
    return api_error("A database error occurred. Please try again later.", 500, "database_error")


@app.errorhandler(Exception)
def handle_unexpected_exception(error):
    app.logger.exception("unexpected server error")
    return api_error("An unexpected error occurred. Please try again later.", 500, "internal_server_error")


@jwt.unauthorized_loader
def handle_missing_jwt(reason):
    app.logger.warning("missing authorization token: %s", reason)
    return api_error("Authentication is required.", 401, "authentication_required")


@jwt.invalid_token_loader
def handle_invalid_jwt(reason):
    app.logger.warning("invalid authorization token: %s", reason)
    return api_error("Invalid authentication token.", 422, "invalid_token")


@jwt.expired_token_loader
def handle_expired_jwt(jwt_header, jwt_payload):
    app.logger.info("expired authorization token for subject=%s", jwt_payload.get("sub"))
    return api_error("Session expired. Please log in again.", 401, "token_expired")


@jwt.revoked_token_loader
def handle_revoked_jwt(jwt_header, jwt_payload):
    app.logger.warning("revoked authorization token for subject=%s", jwt_payload.get("sub"))
    return api_error("Authentication token has been revoked.", 401, "token_revoked")


@jwt.needs_fresh_token_loader
def handle_stale_jwt(jwt_header, jwt_payload):
    app.logger.warning("fresh authorization token required for subject=%s", jwt_payload.get("sub"))
    return api_error("Fresh authentication is required.", 401, "fresh_token_required")


def openapi_spec():
    error_schema = {
        "type": "object",
        "required": ["error"],
        "properties": {
            "error": {
                "type": "object",
                "required": ["code", "message", "request_id"],
                "properties": {
                    "code": {"type": "string"},
                    "message": {"type": "string"},
                    "request_id": {"type": "string", "nullable": True},
                    "details": {"type": "object"},
                },
            }
        },
    }
    success_schema = {
        "type": "object",
        "required": ["data", "request_id"],
        "properties": {
            "data": {"type": "object"},
            "message": {"type": "string"},
            "request_id": {"type": "string", "nullable": True},
        },
    }
    bearer_security = [{"bearerAuth": []}]
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Business Automation Tool API",
            "version": "1.0.0",
            "description": "Authentication, upload, history, and file download API.",
        },
        "servers": [{"url": "http://127.0.0.1:5000"}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            },
            "schemas": {
                "SuccessResponse": success_schema,
                "ErrorResponse": error_schema,
                "Pagination": {
                    "type": "object",
                    "properties": {
                        "page": {"type": "integer"},
                        "per_page": {"type": "integer"},
                        "total": {"type": "integer"},
                        "pages": {"type": "integer"},
                        "has_next": {"type": "boolean"},
                        "has_prev": {"type": "boolean"},
                    },
                },
            },
        },
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "responses": {"200": {"description": "API is running", "content": {"application/json": {"schema": success_schema}}}},
                }
            },
            "/signup": {
                "post": {
                    "summary": "Create an account",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["full_name", "email", "password"],
                                    "properties": {
                                        "full_name": {"type": "string", "minLength": 3, "maxLength": 100},
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string", "minLength": 12, "maxLength": 128},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Account created", "content": {"application/json": {"schema": success_schema}}},
                        "400": {"description": "Validation error", "content": {"application/json": {"schema": error_schema}}},
                    },
                }
            },
            "/login": {
                "post": {
                    "summary": "Authenticate and receive a JWT",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["email", "password"],
                                    "properties": {
                                        "email": {"type": "string", "format": "email"},
                                        "password": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Login successful", "content": {"application/json": {"schema": success_schema}}},
                        "400": {"description": "Validation error", "content": {"application/json": {"schema": error_schema}}},
                        "401": {"description": "Invalid credentials", "content": {"application/json": {"schema": error_schema}}},
                    },
                }
            },
            "/upload": {
                "post": {
                    "summary": "Upload a CSV, XLSX, or JSON file",
                    "security": bearer_security,
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "required": ["file"],
                                    "properties": {"file": {"type": "string", "format": "binary"}},
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "File uploaded", "content": {"application/json": {"schema": success_schema}}},
                        "400": {"description": "Validation error", "content": {"application/json": {"schema": error_schema}}},
                        "401": {"description": "Authentication required", "content": {"application/json": {"schema": error_schema}}},
                    },
                }
            },
            "/history": {
                "get": {
                    "summary": "List uploaded files for the current user",
                    "security": bearer_security,
                    "parameters": [
                        {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                        {"name": "per_page", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 100}},
                    ],
                    "responses": {"200": {"description": "Paginated history", "content": {"application/json": {"schema": success_schema}}}},
                }
            },
            "/files/{email}": {
                "get": {
                    "summary": "List filenames for a user",
                    "security": bearer_security,
                    "parameters": [
                        {"name": "email", "in": "path", "required": True, "schema": {"type": "string", "format": "email"}},
                        {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                        {"name": "per_page", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 200}},
                    ],
                    "responses": {"200": {"description": "Paginated filenames", "content": {"application/json": {"schema": success_schema}}}},
                }
            },
            "/files/{file_id}": {
                "delete": {
                    "summary": "Delete an uploaded file",
                    "security": bearer_security,
                    "parameters": [{"name": "file_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                    "responses": {"200": {"description": "File deleted", "content": {"application/json": {"schema": success_schema}}}},
                }
            },
            "/download/{filename}": {
                "get": {
                    "summary": "Download a file by name",
                    "security": bearer_security,
                    "parameters": [{"name": "filename", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "File bytes"}, "404": {"description": "File not found", "content": {"application/json": {"schema": error_schema}}}},
                }
            },
            "/get_file_data": {
                "get": {
                    "summary": "Download a file by query parameter",
                    "security": bearer_security,
                    "parameters": [{"name": "filename", "in": "query", "required": True, "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "File bytes"}, "404": {"description": "File not found", "content": {"application/json": {"schema": error_schema}}}},
                }
            },
            "/openapi.json": {
                "get": {
                    "summary": "OpenAPI specification",
                    "responses": {"200": {"description": "OpenAPI JSON"}},
                }
            },
        },
    }


@app.route("/health", methods=["GET"])
def health():
    return api_success({"status": "ok"})


@app.route("/openapi.json", methods=["GET"])
def get_openapi_spec():
    return jsonify(openapi_spec()), 200

# ------------------ USER AUTHENTICATION ------------------

@app.route('/signup', methods=['POST'])
@csrf.exempt
@rate_limit(5, 15 * 60, _auth_rate_key)
def signup():
    payload, error = validate_signup_payload()
    if error:
        return error
    full_name = payload["full_name"]
    email = payload["email"]
    password = payload["password"]

    if User_Detail.query.filter_by(email=email).first():
        return api_error("Email already registered", 400, "email_already_registered")

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User_Detail(full_name=full_name, email=email, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return api_success({"user": {"id": new_user.id, "full_name": full_name, "email": email}}, 201, "User registered successfully.")
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("failed to create user account")
        return api_error("Could not create account. Please try again later.", 500, "database_error")

@app.route('/login', methods=['POST'])
@csrf.exempt
@rate_limit(10, 15 * 60, _auth_rate_key)
def login():
    payload, error = validate_login_payload()
    if error:
        return error
    email = payload["email"]
    password = payload["password"]

    user = User_Detail.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        app.logger.warning("failed login attempt for email=%s", email)
        return api_error("Invalid credentials", 401, "invalid_credentials")

    access_token = create_access_token(identity=email)

    return api_success({
        "token": access_token,
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email}
    }, 200, "Login successful.")

# ------------------ FILE UPLOAD & HISTORY ------------------

@app.route('/upload', methods=['POST'])
@csrf.exempt
@jwt_required()
@rate_limit(30, 60)
def upload_file():
    if 'file' not in request.files:
        return api_error("No file uploaded", 400, "missing_file")

    file = request.files['file']
    if file.filename == '':
        return api_error("No selected file", 400, "missing_filename")

    current_user = get_jwt_identity()
    user = User_Detail.query.filter_by(email=current_user).first()
    if not user:
        return api_error("User not found", 404, "user_not_found")

    file_data = file.read()
    if not file_data:
        return api_error("File upload failed, no data read.", 400, "empty_file")

    safe_filename = secure_filename(sanitize_text(file.filename, 255))
    if not safe_filename:
        return api_error("Invalid filename", 400, "invalid_filename")
    if Path(safe_filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        return api_error("Unsupported file type", 400, "unsupported_file_type")

    storage_path = None
    try:
        storage_path = store_uploaded_bytes(user.id, safe_filename, file_data)
        new_file = UploadedFile(
            user_id=user.id,
            filename=safe_filename,
            storage_path=storage_path,
            file_size=len(file_data),
            content_type=file.mimetype or "application/octet-stream",
        )
        db.session.add(new_file)
        db.session.commit()
        return api_success({
            "filename": safe_filename,
            "file_size": len(file_data),
        }, 201, "File uploaded successfully.")
    except SQLAlchemyError:
        db.session.rollback()
        if storage_path:
            stored_file = resolve_stored_file(storage_path)
            if stored_file:
                try:
                    stored_file.unlink(missing_ok=True)
                except OSError:
                    app.logger.exception("failed to clean up orphaned upload after database error")
        app.logger.exception("failed to store uploaded file")
        return api_error("Could not save file. Please try again later.", 500, "database_error")
    except OSError:
        app.logger.exception("failed to write uploaded file to storage")
        return api_error("Could not store file. Please try again later.", 500, "file_storage_error")

@app.route("/history", methods=["GET"])
@jwt_required()
@csrf.exempt
def get_user_history():
    current_user = get_jwt_identity()
    user = User_Detail.query.filter_by(email=current_user).first()

    if not user:
        return api_error("User not found", 404, "user_not_found")

    page, per_page = parse_pagination(default_per_page=20, max_per_page=100)
    pagination = (
        UploadedFile.query.filter_by(user_id=user.id)
        .order_by(UploadedFile.upload_time.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    files_data = [
        {
            "id": file.id,
            "filename": file.filename,
            "file_size": file.file_size,
            "content_type": file.content_type,
            "upload_time": file.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for file in pagination.items
    ]

    return api_success({"uploaded_files": files_data, "pagination": pagination_payload(pagination)})


@app.route('/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
@csrf.exempt
def delete_uploaded_file(file_id):
    current_user = get_jwt_identity()
    user = User_Detail.query.filter_by(email=current_user).first()

    if not user:
        return api_error("User not found", 404, "user_not_found")

    file_entry = UploadedFile.query.filter_by(id=file_id, user_id=user.id).first()
    if not file_entry:
        return api_error("File not found", 404, "file_not_found")

    try:
        deleted_filename = file_entry.filename
        db.session.delete(file_entry)
        db.session.commit()
        delete_stored_file(file_entry)
        return api_success({"filename": deleted_filename}, 200, "File deleted successfully.")
    except SQLAlchemyError:
        db.session.rollback()
        app.logger.exception("failed to delete uploaded file id=%s", file_id)
        return api_error("Could not delete file. Please try again later.", 500, "database_error")

# ------------------ GET USER FILES LIST ------------------

@app.route('/files/<email>', methods=['GET'])
@jwt_required()
@csrf.exempt
def get_user_files(email):
    current_user = get_jwt_identity()
    email = sanitize_email(email)

    if current_user != email:
        return api_error("Unauthorized access", 403, "forbidden")

    user = User_Detail.query.filter_by(email=email).first()
    if not user:
        return api_error("User not found", 404, "user_not_found")

    page, per_page = parse_pagination(default_per_page=100, max_per_page=200)
    pagination = (
        UploadedFile.query.filter_by(user_id=user.id)
        .order_by(UploadedFile.upload_time.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    filenames = [file.filename for file in pagination.items]

    return api_success({"files": filenames, "pagination": pagination_payload(pagination)})

# ------------------ DOWNLOAD FILE BY NAME ------------------

@app.route('/download/<filename>', methods=['GET'])
@jwt_required()
@csrf.exempt
def download_file(filename):
    current_user = get_jwt_identity()
    user = User_Detail.query.filter_by(email=current_user).first()

    if not user:
        return api_error("User not found", 404, "user_not_found")

    safe_filename, error = validate_filename(filename)
    if error:
        return error

    file_entry = UploadedFile.query.filter_by(user_id=user.id, filename=safe_filename).first()

    if not file_entry:
        return api_error("File not found", 404, "file_not_found")

    return send_uploaded_file(file_entry)

# ------------------ GET FILE DATA (For Visualization Page) ------------------

@app.route('/get_file_data', methods=['GET'])
@jwt_required()
@csrf.exempt
def get_file_data():
    email = get_jwt_identity()
    filename, error = validate_filename(request.args.get("filename", ""))
    if error:
        return error

    user = User_Detail.query.filter_by(email=email).first()
    if not user:
        return api_error("User not found", 404, "user_not_found")

    file_entry = UploadedFile.query.filter_by(user_id=user.id, filename=filename).first()

    if not file_entry:
        return api_error("File not found", 404, "file_not_found")

    return send_uploaded_file(file_entry)

# ------------------ RUN FLASK APP ------------------

if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
