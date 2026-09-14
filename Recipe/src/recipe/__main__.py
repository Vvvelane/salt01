"""Idempotent local launcher; never terminate an unrelated port owner."""

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen

import uvicorn


def existing_recipe(host: str, port: int) -> bool:
    try:
        with urlopen(f"http://{host}:{port}/api/health", timeout=2) as response:
            return json.load(response).get("service") == "recipe"
    except (URLError, OSError, ValueError):
        return False


def port_is_available(host: str, port: int) -> bool:
    probe = socket.socket()
    try:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        probe.close()


def listener_pids(port: int) -> list[int] | None:
    """Return local listener PIDs on macOS without relying on shell interpolation."""
    try:
        completed = subprocess.run(
            ["lsof", "-nP", "-t", f"-iTCP:{port}", "-sTCP:LISTEN"],
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError:
        return None
    return sorted({int(line) for line in completed.stdout.splitlines() if line.isdigit()})


def recipe_pids(host: str, port: int) -> list[int] | None:
    """Never identify or stop a listener until Recipe itself answered its health check."""
    if not existing_recipe(host, port):
        return None
    return listener_pids(port)


def stop_recipe(host: str, port: int) -> int:
    pids = recipe_pids(host, port)
    if pids is None:
        if port_is_available(host, port):
            print(f"Recipe is not running on http://{host}:{port}")
            return 0
        print(f"Port {port} is not owned by a responding Recipe service. No process was stopped.")
        return 1
    if not pids:
        print("Recipe responded, but its listener PID could not be identified. No process was stopped.")
        return 1

    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            continue
        except PermissionError:
            print(f"Recipe PID {pid} cannot be stopped by this user.")
            return 1

    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        if port_is_available(host, port):
            print(f"Stopped Recipe PID{'s' if len(pids) > 1 else ''}: {', '.join(map(str, pids))}")
            return 0
        time.sleep(0.1)
    print(f"Recipe PID{'s' if len(pids) > 1 else ''} {', '.join(map(str, pids))} did not release port {port} after SIGTERM.")
    return 1


def status_recipe(host: str, port: int) -> int:
    pids = recipe_pids(host, port)
    url = f"http://{host}:{port}"
    if pids:
        print(f"Recipe is running: {url} (PID{'s' if len(pids) > 1 else ''} {', '.join(map(str, pids))})")
        return 0
    if pids == []:
        print(f"Recipe is running at {url}, but its listener PID could not be identified.")
        return 0
    if port_is_available(host, port):
        print(f"Recipe is not running: {url}")
        return 1
    print(f"Port {port} is occupied by a non-Recipe service.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local SALT Recipe terminal")
    parser.add_argument("--port", type=int, default=8765)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--status", action="store_true", help="show the local Recipe process")
    action.add_argument("--stop", action="store_true", help="gracefully stop the local Recipe process")
    action.add_argument("--restart", action="store_true", help="gracefully replace the local Recipe process")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    host, port = "127.0.0.1", args.port
    url = f"http://{host}:{port}"
    if args.status:
        return status_recipe(host, port)
    if args.stop:
        return stop_recipe(host, port)
    if args.restart:
        stopped = stop_recipe(host, port)
        if stopped:
            return stopped
    probe = socket.socket()
    try:
        # Reserve the socket through uvicorn startup: no check-then-bind race.
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind((host, port))
    except OSError:
        probe.close()
        if existing_recipe(host, port):
            pids = listener_pids(port)
            pid_note = f" (PID{'s' if len(pids) > 1 else ''} {', '.join(map(str, pids))})" if pids else ""
            print(
                f"Recipe is already running: {url}{pid_note}. Use --restart to replace it or --stop to close it."
            )
            return 0
        print(
            f"Port {port} is unavailable or owned by another service. No process was stopped. Try: python -m recipe --port {port + 1 if port < 65535 else 8766}"
        )
        return 1
    print(f"Recipe: {url}", flush=True)
    try:
        server = uvicorn.Server(uvicorn.Config("recipe.app:app", host=host, port=port))
        server.run(sockets=[probe])
    finally:
        probe.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
