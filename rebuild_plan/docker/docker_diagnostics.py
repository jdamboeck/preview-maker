#!/usr/bin/env python3
"""
Docker Environment Diagnostic Tool for Preview Maker

This script performs comprehensive diagnostic checks for the Preview Maker
Docker environment, verifying GTK 4.0 installation, GPU acceleration,
and overall system health.
"""
import os
import sys
import platform
import json
import shutil
import subprocess
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("docker-diagnostics")


@dataclass
class DiagnosticResult:
    """Class for storing diagnostic results."""

    component: str
    status: str  # "pass", "warn", "fail"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "component": self.component,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class DockerDiagnostics:
    """Diagnostic tool for the Docker environment."""

    def __init__(self):
        """Initialize the diagnostic tool."""
        self.results: List[DiagnosticResult] = []
        self.temp_dir = Path(tempfile.mkdtemp())

    def run_all_checks(self) -> None:
        """Run all diagnostic checks."""
        try:
            self.check_system_info()
            self.check_gtk_installation()
            self.check_python_packages()
            self.check_cairo_installation()
            self.check_pillow_installation()
            self.check_x11_forwarding()
            self.check_opengl_support()
            self.check_docker_environment()
            self.check_network_access()
            self.check_filesystem_access()
        finally:
            # Clean up temporary files
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)

    def check_system_info(self) -> None:
        """Check basic system information."""
        try:
            details = {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "hostname": platform.node(),
                "username": os.getenv("USER", "unknown"),
                "container_id": self._get_container_id(),
                "environment_vars": {
                    k: v
                    for k, v in os.environ.items()
                    if k.startswith("PREVIEW_")
                    or k in ["DISPLAY", "PYTHONPATH", "LANG", "PATH"]
                },
            }

            self.results.append(
                DiagnosticResult(
                    component="system_info",
                    status="pass",
                    message="Successfully gathered system information",
                    details=details,
                )
            )
        except Exception as e:
            self.results.append(
                DiagnosticResult(
                    component="system_info",
                    status="fail",
                    message=f"Failed to gather system information: {str(e)}",
                    details={"error": str(e)},
                )
            )

    def check_gtk_installation(self) -> None:
        """Check if GTK 4.0 is properly installed."""
        try:
            # Try to import GTK
            output = subprocess.check_output(
                [
                    sys.executable,
                    "-c",
                    "import gi; gi.require_version('Gtk', '4.0'); "
                    "from gi.repository import Gtk; "
                    "print(f'GTK version: {Gtk._version}')",
                ],
                stderr=subprocess.STDOUT,
                text=True,
            )

            self.results.append(
                DiagnosticResult(
                    component="gtk_installation",
                    status="pass",
                    message="GTK 4.0 is properly installed",
                    details={"output": output.strip()},
                )
            )
        except subprocess.CalledProcessError as e:
            self.results.append(
                DiagnosticResult(
                    component="gtk_installation",
                    status="fail",
                    message="GTK 4.0 installation check failed",
                    details={"error": e.output.strip()},
                )
            )

    def check_python_packages(self) -> None:
        """Check installed Python packages."""
        try:
            # Get list of installed packages
            output = subprocess.check_output(
                [sys.executable, "-m", "pip", "list"], text=True
            )

            # Parse the package list
            packages = {}
            for line in output.strip().split("\n")[2:]:  # Skip header rows
                parts = line.split()
                if len(parts) >= 2:
                    packages[parts[0]] = parts[1]

            # Check for required packages
            required_packages = [
                "PyGObject",
                "pycairo",
                "Pillow",
                "google-generativeai",
                "pytest",
                "debugpy",
                "psutil",
            ]

            missing_packages = [
                pkg
                for pkg in required_packages
                if pkg.lower() not in [p.lower() for p in packages.keys()]
            ]

            if missing_packages:
                status = "warn"
                message = f"Missing required packages: {', '.join(missing_packages)}"
            else:
                status = "pass"
                message = "All required Python packages are installed"

            self.results.append(
                DiagnosticResult(
                    component="python_packages",
                    status=status,
                    message=message,
                    details={"installed_packages": packages},
                )
            )
        except Exception as e:
            self.results.append(
                DiagnosticResult(
                    component="python_packages",
                    status="fail",
                    message=f"Failed to check Python packages: {str(e)}",
                    details={"error": str(e)},
                )
            )

    def check_cairo_installation(self) -> None:
        """Check if Cairo is properly installed."""
        try:
            # Create a temporary file
            test_file = self.temp_dir / "cairo_test.png"

            # Try to create a Cairo surface
            output = subprocess.check_output(
                [
                    sys.executable,
                    "-c",
                    f"import cairo; surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100); "
                    f"ctx = cairo.Context(surface); "
                    f"ctx.set_source_rgb(0.3, 0.6, 0.8); "
                    f"ctx.rectangle(10, 10, 80, 80); "
                    f"ctx.fill(); "
                    f"surface.write_to_png('{test_file}'); "
                    f"print('Successfully created Cairo surface and wrote to PNG file')",
                ],
                stderr=subprocess.STDOUT,
                text=True,
            )

            if test_file.exists():
                status = "pass"
                message = "Cairo is properly installed and can create images"
                details = {"output": output.strip(), "test_file": str(test_file)}
            else:
                status = "warn"
                message = "Cairo seems to be installed but couldn't create a test image"
                details = {"output": output.strip()}

            self.results.append(
                DiagnosticResult(
                    component="cairo_installation",
                    status=status,
                    message=message,
                    details=details,
                )
            )
        except subprocess.CalledProcessError as e:
            self.results.append(
                DiagnosticResult(
                    component="cairo_installation",
                    status="fail",
                    message="Cairo installation check failed",
                    details={"error": e.output.strip()},
                )
            )

    def check_pillow_installation(self) -> None:
        """Check if Pillow is properly installed."""
        try:
            # Create a temporary file
            test_file = self.temp_dir / "pillow_test.png"

            # Try to create a Pillow image
            output = subprocess.check_output(
                [
                    sys.executable,
                    "-c",
                    f"from PIL import Image, ImageDraw; "
                    f"img = Image.new('RGB', (100, 100), color='white'); "
                    f"draw = ImageDraw.Draw(img); "
                    f"draw.rectangle((10, 10, 90, 90), fill='blue'); "
                    f"img.save('{test_file}'); "
                    f"print('Successfully created Pillow image and saved to file')",
                ],
                stderr=subprocess.STDOUT,
                text=True,
            )

            if test_file.exists():
                status = "pass"
                message = "Pillow is properly installed and can create images"
                details = {"output": output.strip(), "test_file": str(test_file)}
            else:
                status = "warn"
                message = (
                    "Pillow seems to be installed but couldn't create a test image"
                )
                details = {"output": output.strip()}

            self.results.append(
                DiagnosticResult(
                    component="pillow_installation",
                    status=status,
                    message=message,
                    details=details,
                )
            )
        except subprocess.CalledProcessError as e:
            self.results.append(
                DiagnosticResult(
                    component="pillow_installation",
                    status="fail",
                    message="Pillow installation check failed",
                    details={"error": e.output.strip()},
                )
            )

    def check_x11_forwarding(self) -> None:
        """Check if X11 forwarding is working."""
        display = os.environ.get("DISPLAY")

        if not display:
            self.results.append(
                DiagnosticResult(
                    component="x11_forwarding",
                    status="fail",
                    message="DISPLAY environment variable is not set",
                    details={"error": "DISPLAY environment variable is not set"},
                )
            )
            return

        try:
            # Try to connect to the X server
            subprocess.check_output(["xdpyinfo"], stderr=subprocess.STDOUT, text=True)

            self.results.append(
                DiagnosticResult(
                    component="x11_forwarding",
                    status="pass",
                    message="X11 forwarding is working",
                    details={"display": display},
                )
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error_msg = getattr(e, "output", str(e)).strip()
            self.results.append(
                DiagnosticResult(
                    component="x11_forwarding",
                    status="fail",
                    message="X11 forwarding is not working",
                    details={"error": error_msg, "display": display},
                )
            )

    def check_opengl_support(self) -> None:
        """Check for OpenGL support (important for GTK rendering)."""
        try:
            # Try to get OpenGL info
            output = subprocess.check_output(
                ["glxinfo | grep 'OpenGL version'"],
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
            )

            self.results.append(
                DiagnosticResult(
                    component="opengl_support",
                    status="pass",
                    message="OpenGL support detected",
                    details={"output": output.strip()},
                )
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error_msg = getattr(e, "output", str(e)).strip()
            self.results.append(
                DiagnosticResult(
                    component="opengl_support",
                    status="warn",
                    message="OpenGL support check failed (not critical for headless operation)",
                    details={"error": error_msg},
                )
            )

    def check_docker_environment(self) -> None:
        """Check if we're running in a Docker container."""
        in_docker = os.path.exists("/.dockerenv") or os.path.exists(
            "/run/.containerenv"
        )
        cgroup_content = ""

        try:
            with open("/proc/1/cgroup", "r") as f:
                cgroup_content = f.read()
        except:
            pass

        docker_indicators = in_docker or "docker" in cgroup_content

        if docker_indicators:
            # We're in Docker, check container resources
            try:
                # CPU info
                cpu_count = os.cpu_count() or 0

                # Memory info
                with open("/proc/meminfo", "r") as f:
                    mem_info = f.read()

                memory_lines = {
                    line.split(":")[0]: line.split(":")[1].strip()
                    for line in mem_info.split("\n")
                    if ":" in line
                }

                self.results.append(
                    DiagnosticResult(
                        component="docker_environment",
                        status="pass",
                        message="Running in Docker container",
                        details={
                            "cpu_count": cpu_count,
                            "memory_info": memory_lines,
                            "container_id": self._get_container_id(),
                        },
                    )
                )
            except Exception as e:
                self.results.append(
                    DiagnosticResult(
                        component="docker_environment",
                        status="warn",
                        message="Running in Docker but couldn't get resource info",
                        details={"error": str(e)},
                    )
                )
        else:
            self.results.append(
                DiagnosticResult(
                    component="docker_environment",
                    status="warn",
                    message="Not running in a Docker container",
                    details={},
                )
            )

    def check_network_access(self) -> None:
        """Check network connectivity (important for API access)."""
        try:
            # Try to fetch a URL with curl (more likely to be available than ping)
            subprocess.check_output(
                [
                    "curl",
                    "-s",
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    "https://www.google.com",
                ],
                stderr=subprocess.STDOUT,
            )

            self.results.append(
                DiagnosticResult(
                    component="network_access",
                    status="pass",
                    message="Network connectivity is working",
                    details={},
                )
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error_msg = getattr(e, "output", str(e)).strip()
            self.results.append(
                DiagnosticResult(
                    component="network_access",
                    status="warn",
                    message="Network connectivity check failed",
                    details={"error": error_msg},
                )
            )

    def check_filesystem_access(self) -> None:
        """Check filesystem access permissions."""
        dirs_to_check = ["/app", "/home/developer", "/tmp"]

        results = {}
        overall_status = "pass"

        for directory in dirs_to_check:
            dir_path = Path(directory)
            if not dir_path.exists():
                results[directory] = {
                    "exists": False,
                    "readable": False,
                    "writable": False,
                }
                overall_status = "warn"
                continue

            readable = os.access(directory, os.R_OK)
            writable = os.access(directory, os.W_OK)

            if not readable or not writable:
                overall_status = "warn"

            results[directory] = {
                "exists": True,
                "readable": readable,
                "writable": writable,
            }

        self.results.append(
            DiagnosticResult(
                component="filesystem_access",
                status=overall_status,
                message="Checked filesystem access permissions",
                details={"directories": results},
            )
        )

    def _get_container_id(self) -> str:
        """Get the Docker container ID."""
        try:
            with open("/proc/self/cgroup", "r") as f:
                for line in f:
                    if "docker" in line:
                        parts = line.split("/")
                        for part in parts:
                            if part.startswith("docker-"):
                                return part.replace("docker-", "").strip()
            return "unknown"
        except:
            return "unknown"

    def generate_report(self) -> Dict[str, Any]:
        """Generate a report from the diagnostic results."""
        # Count results by status
        status_counts = {"pass": 0, "warn": 0, "fail": 0}
        for result in self.results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1

        # Determine overall status
        if status_counts["fail"] > 0:
            overall_status = "fail"
        elif status_counts["warn"] > 0:
            overall_status = "warn"
        else:
            overall_status = "pass"

        # Format results
        results_dict = [result.to_dict() for result in self.results]

        return {
            "timestamp": time.time(),
            "overall_status": overall_status,
            "summary": {
                "total_checks": len(self.results),
                "passed": status_counts["pass"],
                "warnings": status_counts["warn"],
                "failures": status_counts["fail"],
            },
            "results": results_dict,
        }

    def print_report(self) -> None:
        """Print the diagnostic report to stdout."""
        report = self.generate_report()

        print("\n" + "=" * 80)
        print(f"Preview Maker Docker Environment Diagnostics")
        print("=" * 80)

        print(f"\nOverall Status: {report['overall_status'].upper()}")
        print(f"Total Checks:   {report['summary']['total_checks']}")
        print(f"Passed:         {report['summary']['passed']}")
        print(f"Warnings:       {report['summary']['warnings']}")
        print(f"Failures:       {report['summary']['failures']}")

        print("\nDetailed Results:")
        print("-" * 80)

        for result in self.results:
            status_display = {"pass": "✓ PASS", "warn": "⚠ WARN", "fail": "✗ FAIL"}.get(
                result.status, result.status.upper()
            )

            print(
                f"{status_display.ljust(8)} | {result.component.ljust(20)} | {result.message}"
            )

        print("\nSee the JSON output for detailed information.")

    def save_report(self, file_path: str) -> None:
        """Save the diagnostic report to a file."""
        report = self.generate_report()
        with open(file_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Diagnostic report saved to {file_path}")


def main():
    """Main function to run the diagnostic tool."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Docker environment diagnostics for Preview Maker"
    )
    parser.add_argument("--output", "-o", type=str, help="Output file for JSON report")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress terminal output"
    )

    args = parser.parse_args()

    diagnostics = DockerDiagnostics()
    diagnostics.run_all_checks()

    if not args.quiet:
        diagnostics.print_report()

    if args.output:
        diagnostics.save_report(args.output)

    # Determine exit code based on overall status
    report = diagnostics.generate_report()
    if report["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
