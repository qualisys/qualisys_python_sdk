"""Logging hygiene tests for qtm_rt (issue #44)."""

import importlib
import logging

import pytest


@pytest.fixture
def reloaded_qtm_rt(monkeypatch):
    """Reload qtm_rt with a controlled environment and isolated logger state.

    Snapshots the qtm_rt logger's handlers and level, clears them so the
    fresh import in the test starts from a known state, and restores the
    original state after the test so module-level side effects do not leak
    between tests.
    """
    import qtm_rt as qtm_rt_module

    qtm_rt_logger = logging.getLogger("qtm_rt")
    saved_handlers = list(qtm_rt_logger.handlers)
    saved_level = qtm_rt_logger.level

    qtm_rt_logger.handlers.clear()
    qtm_rt_logger.setLevel(logging.NOTSET)
    monkeypatch.delenv("QTM_LOGGING", raising=False)

    yield qtm_rt_module, monkeypatch

    qtm_rt_logger.handlers.clear()
    qtm_rt_logger.handlers.extend(saved_handlers)
    qtm_rt_logger.setLevel(saved_level)


def test_reloading_qtm_rt_does_not_touch_the_root_logger(reloaded_qtm_rt):
    """qtm_rt must not configure the root logger at import time (issue #44).

    Pytest itself attaches a capture handler to the root logger during test
    runs, so we verify the invariant by checking that re-importing qtm_rt
    does not change the root logger's handler list.
    """
    qtm_rt_module, _ = reloaded_qtm_rt
    root_handlers_before = list(logging.getLogger().handlers)

    importlib.reload(qtm_rt_module)

    assert logging.getLogger().handlers == root_handlers_before


def test_qtm_rt_logger_has_exactly_one_null_handler(reloaded_qtm_rt):
    """After import, the qtm_rt logger has a single NullHandler.

    The NullHandler prevents "No handlers could be found" warnings on
    unconfigured applications without producing any output.
    """
    qtm_rt_module, _ = reloaded_qtm_rt

    importlib.reload(qtm_rt_module)

    handlers = logging.getLogger("qtm_rt").handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.NullHandler)


def test_qtm_logging_debug_env_var_sets_qtm_rt_logger_to_debug(reloaded_qtm_rt):
    qtm_rt_module, monkeypatch = reloaded_qtm_rt
    monkeypatch.setenv("QTM_LOGGING", "debug")

    importlib.reload(qtm_rt_module)

    assert logging.getLogger("qtm_rt").level == logging.DEBUG


def test_qtm_logging_unset_leaves_qtm_rt_logger_level_unchanged(reloaded_qtm_rt):
    qtm_rt_module, _ = reloaded_qtm_rt

    importlib.reload(qtm_rt_module)

    assert logging.getLogger("qtm_rt").level == logging.NOTSET
