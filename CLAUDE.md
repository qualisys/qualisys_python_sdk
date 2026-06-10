# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`qtm_rt` is the Qualisys SDK for Python — a client library that implements Qualisys' RealTime (RT) protocol for talking to QTM (Qualisys Track Manager). Published to PyPI as `qtm-rt`. Targets Python 3.10+ and RT protocol version 1.8+. Little-endian only; default port 22223.

## Common commands

```bash
# Setup (from README.md)
python -m venv .venv
source ./.venv/Scripts/activate   # Windows bash; on PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# Tests
pytest test/
pytest test/qrtconnection_test.py::test_connect_no_loop   # single test

# Build sdist + wheel into dist/
python -m build

# Build Sphinx docs into docs/_build/html/
make -C docs html

# Enable debug logging at runtime
QTM_LOGGING=debug python your_script.py
```

Release flow — bump `version` in `pyproject.toml` (and `docs/conf.py`), open a PR, merge to master, then create a GitHub Release on the tag `vX.Y.Z`. Publishing the release fires `.github/workflows/release.yml`, which runs tests, builds the sdist+wheel, twine-checks, uploads to PyPI via Trusted Publishing, and attaches `examples/Demo.qtm` to the release. Docs are still a manual step: build with `make -C docs html`, copy `docs/_build/html/*` into the sibling `../qualisys_python_sdk_gh_pages` checkout **preserving the legacy `v102/`, `v103/`, `v212/` directories**, commit/push that branch.

## Architecture

Everything is `asyncio`-based and built around `qtm_rt.connect()` → returns a `QRTConnection`. The data flow:

- **`qrt.py`** — public API surface. `connect()` opens a TCP connection wrapped in `QTMProtocol`, negotiates the RT protocol version (default `"1.25"`), and returns a `QRTConnection` exposing async methods for every RT command (`stream_frames`, `get_current_frame`, `get_parameters`, `take_control`, `start`, `stop`, `load`, `save`, `calibrate`, etc.). The `@validate_response([...])` decorator asserts the server's reply starts with an expected prefix and raises `QRTCommandException` otherwise.
- **`protocol.py`** — `QTMProtocol` is an `asyncio.Protocol` subclass. Outgoing commands are framed with `RTheader` (`<II`: size + packet type) and one of the `QRTPacketType` variants. Responses are dispatched through a `_handlers` dict keyed on packet type. Single-shot command replies are delivered via a `request_queue` of futures (FIFO via `popleft`, with done-future skipping so a late response to a cancelled caller doesn't crash the transport); streaming data goes to the user-supplied `on_packet` callback instead. The first `streamframes` response is synthesized as `b"Ok"` so callers can await the command even though real data packets arrive on the streaming path.
- **`receiver.py`** — buffers raw bytes, slices them into complete packets using the header size field, converts the type byte to `QRTPacketType`, wraps data/event payloads into `QRTPacket`/`QRTEvent`, and routes to the handler.
- **`packet.py`** — all binary layouts. Uses `struct.Struct` and `namedtuple` for every RT component type (2D/3D/6D/Analog/Force/GazeVector/EyeTracker/Image/Skeleton/Timecode/etc.). `QRTPacket` exposes `get_*` accessors that lazily parse components on demand. `QRTPacketType` and `QRTEvent` are enums matching the protocol byte values.
- **`discovery.py`** — UDP broadcast discovery of QTM instances on the LAN (`Discover`).
- **`control.py`** — `TakeControl`, an async context manager wrapping `take_control`/`release_control`.
- **`reboot.py`** — utility to reboot cameras.

Key invariants when modifying:

- Component and parameter names accepted by `stream_frames` / `get_current_frame` / `get_parameters` are validated against hardcoded allow-lists in `qrt.py` (`_validate_components` and the inline list in `get_parameters`). Adding a new RT component requires updating **both** that list and `packet.py`.
- `request_queue` is FIFO (`popleft`). When a caller's `asyncio.wait_for` cancels the queued future, the next QTM response is dropped rather than delivered to it — keep this property when adding code paths that enqueue futures.
- `on_packet` callbacks are sync; they run inside the asyncio event loop, so blocking work there will stall the protocol.
- `QRTConnection` is an async context manager; prefer `async with await qtm_rt.connect(...) as c:` in new examples and tests.

## Testing notes

Tests use `pytest`, `pytest-asyncio` (markers required: `@pytest.mark.asyncio`), and `pytest-mock`. They exercise `connect()` and `QRTConnection` by mocking `loop.create_connection` — there is no live QTM in CI. New protocol commands should get analogous mocked tests in `test/qrtconnection_test.py` or `test/qtmprotocol_test.py`.

## Known gaps (from README)

`GetCaptureC3D`, `GetCaptureQTM`, and per-channel analog selection are intentionally not implemented.
