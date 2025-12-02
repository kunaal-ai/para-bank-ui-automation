#!/usr/bin/env python3
"""
Monitoring management script for Para Bank UI Automation

This script provides commands to start, stop, and check the status of
Prometheus and Grafana monitoring services.
"""

import argparse
import shlex
import subprocess  # nosec B404
import sys


def run_command(command: str | list[str], check: bool = True) -> str | None:
    """Run a command and return the output

    Args:
        command (str): Command to run
        check (bool): Whether to check the return code

    Returns:
        str: Command output or None if failed
    """
    try:
        # Split command into list of arguments
        if isinstance(command, str):
            command = shlex.split(command)

        result = subprocess.run(  # nosec B603
            command,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
        return None


def check_docker_installed() -> bool:
    """Check if Docker is installed"""
    return run_command(["docker", "--version"], check=False) is not None


def check_docker_compose_installed() -> bool:
    """Check if Docker Compose is installed"""
    # Try docker compose command (newer versions) first
    if run_command(["docker", "compose", "version"], check=False) is not None:
        return True
    # Fall back to docker-compose command (older versions)
    if run_command(["docker-compose", "--version"], check=False) is not None:
        return True
    return False


def get_docker_compose_command() -> list[str]:
    """Get the appropriate docker-compose command"""
    # Check if new style 'docker compose' works
    if run_command(["docker", "compose", "version"], check=False) is not None:
        return ["docker", "compose"]
    # Fall back to old style 'docker-compose'
    return ["docker-compose"]


def start_monitoring() -> bool:
    """Start Prometheus and Grafana using docker-compose"""
    # Check Docker dependencies
    if not check_docker_installed():
        print("Error: Docker is not installed or not in your PATH.")
        print("Please install Docker from https://docs.docker.com/get-docker/")
        return False

    if not check_docker_compose_installed():
        print("Error: Docker Compose is not installed or not in your PATH.")
        print("For Docker Desktop users: Docker Compose should be included.")
        print("For others, see: https://docs.docker.com/compose/install/")
        return False

    print("Starting Prometheus and Grafana...")
    compose_cmd = get_docker_compose_command()
    run_command(compose_cmd + ["up", "-d"])
    print("\nMonitoring services started!")
    print("Prometheus UI available at: http://localhost:9090")
    print("Grafana UI available at: http://localhost:3000")
    print("Grafana default credentials: admin/admin")
    return True


def stop_monitoring() -> bool:
    """Stop Prometheus and Grafana using docker-compose"""
    # Check Docker dependencies
    if not check_docker_installed():
        print("Error: Docker is not installed or not in your PATH.")
        return False

    if not check_docker_compose_installed():
        print("Error: Docker Compose is not installed or not in your PATH.")
        return False

    print("Stopping Prometheus and Grafana...")
    compose_cmd = get_docker_compose_command()
    run_command(compose_cmd + ["down"])
    print("Monitoring services stopped.")
    return True


def check_status() -> bool:
    """Check the status of Prometheus and Grafana containers"""
    # Check Docker dependencies
    if not check_docker_installed():
        print("Error: Docker is not installed or not in your PATH.")
        return False

    if not check_docker_compose_installed():
        print("Error: Docker Compose is not installed or not in your PATH.")
        return False

    print("Checking monitoring services status...")
    compose_cmd = get_docker_compose_command()
    output = run_command(compose_cmd + ["ps"])
    if output:
        print(output)
    else:
        print("Failed to get status or no containers are running.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage Prometheus and Grafana monitoring services"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Add command parsers
    subparsers.add_parser("start", help="Start monitoring services")
    subparsers.add_parser("stop", help="Stop monitoring services")
    subparsers.add_parser("status", help="Check status of monitoring services")
    subparsers.add_parser(
        "check-docker",
        help="Check if Docker and Docker Compose are installed",
    )

    args = parser.parse_args()

    if args.command == "start":
        success = start_monitoring()
        if not success:
            sys.exit(1)
    elif args.command == "stop":
        success = stop_monitoring()
        if not success:
            sys.exit(1)
    elif args.command == "status":
        success = check_status()
        if not success:
            sys.exit(1)
    elif args.command == "check-docker":
        docker_installed = check_docker_installed()
        compose_installed = check_docker_compose_installed()

        print("Docker installation status:")
        print(f"  Docker: {'Installed' if docker_installed else 'Not installed'}")
        print(f"  Docker Compose: " f"{'Installed' if compose_installed else 'Not installed'}")

        if not docker_installed:
            print("\nTo install Docker, visit: " "https://docs.docker.com/get-docker/")
            sys.exit(1)

        if not compose_installed:
            print("\nTo install Docker Compose, visit: " "https://docs.docker.com/compose/install/")
            sys.exit(1)

        print("\nYour system is ready to run Prometheus and Grafana!")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
