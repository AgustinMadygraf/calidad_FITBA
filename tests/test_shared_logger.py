import logging

import src.shared.logger as app_logger


def test_level_prefix_formatter_formats_prefix():
    formatter = app_logger.LevelPrefixFormatter("%(levelprefix)s %(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hola",
        args=(),
        exc_info=None,
    )

    rendered = formatter.format(record)

    assert rendered.startswith("INFO:")
    assert rendered.endswith("hola")


def test_build_logging_config_shape():
    config = app_logger._build_logging_config("WARNING")
    assert config["version"] == 1
    assert "default" in config["handlers"]
    assert config["loggers"][""]["level"] == "WARNING"


def test_configure_logging_when_handlers_exist(monkeypatch):
    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(logging.StreamHandler())

    called = {"dict_config": False}
    monkeypatch.setattr(
        app_logger.logging.config,
        "dictConfig",
        lambda *_args, **_kwargs: called.update(dict_config=True),
    )

    app_logger.configure_logging(level=logging.DEBUG)

    assert root.level == logging.DEBUG
    assert called["dict_config"] is False


def test_configure_logging_when_handlers_are_missing(monkeypatch):
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    root.handlers.clear()

    called = {}

    def fake_dict_config(payload):
        called["payload"] = payload

    monkeypatch.setattr(app_logger.logging.config, "dictConfig", fake_dict_config)

    try:
        app_logger.configure_logging(level="ERROR")
        assert called["payload"]["loggers"][""]["level"] == "ERROR"
        assert root.level == logging.ERROR
    finally:
        root.handlers[:] = original_handlers


def test_get_logger_calls_configure(monkeypatch):
    called = {}

    def fake_configure(level):
        called["level"] = level

    monkeypatch.setattr(app_logger, "configure_logging", fake_configure)
    logger = app_logger.get_logger("my-app", level="INFO")

    assert logger.name == "my-app"
    assert called["level"] == "INFO"
