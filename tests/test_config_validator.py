import json
from src.collector.config_validator import validate_sources_config, print_validation_report


def test_valid_config_has_no_errors():
    errors, _ = validate_sources_config("config/sources.json")
    assert errors == []


def test_print_validation_report_returns_true_for_valid_config():
    assert print_validation_report("config/sources.json") is True


def test_missing_file_is_critical_error(tmp_path):
    errors, _ = validate_sources_config(str(tmp_path / "no_existe.json"))
    assert len(errors) == 1


def test_invalid_json_is_critical_error(tmp_path):
    path = tmp_path / "sources.json"
    path.write_text("{not valid json", encoding="utf-8")
    errors, _ = validate_sources_config(str(path))
    assert len(errors) == 1


def test_empty_whitelist_is_critical_error(tmp_path):
    path = tmp_path / "sources.json"
    path.write_text(json.dumps({"whitelisted_domains": []}), encoding="utf-8")
    errors, _ = validate_sources_config(str(path))
    assert len(errors) == 1
