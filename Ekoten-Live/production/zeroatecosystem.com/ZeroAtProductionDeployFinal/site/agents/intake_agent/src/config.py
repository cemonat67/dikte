from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INCOMING_DIR = BASE_DIR / "incoming"
STAGING_DIR = BASE_DIR / "staging"
NORMALIZED_DIR = BASE_DIR / "normalized"
REVIEW_DIR = BASE_DIR / "review"
APPROVED_DIR = BASE_DIR / "approved"
REJECTED_DIR = BASE_DIR / "rejected"
ARCHIVE_DIR = BASE_DIR / "archive"
SCHEMA_PATH = BASE_DIR / "schemas" / "canonical_intake_schema_v1.json"

SUPPORTED_TABULAR_EXTENSIONS = {".csv", ".xlsx"}
SUPPORTED_TEXT_EXTENSIONS = {".txt"}

DEFAULT_CONFIDENCE = 0.65
DEFAULT_FACILITY = "Ekoten"
DEFAULT_SOURCE_LANGUAGE = "en"
PARSER_VERSION = "intake-mvp-v0.1"
