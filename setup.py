#!/usr/bin/env python3
"""
ThunderBuddy Setup Script

This script sets up a Python virtual environment for the ThunderBuddy\nbackend.
It also configures automatic activation of the virtual environment when entering the
repository directory.

Features:
- Creates and configures a Python virtual environment
- Installs all required dependencies
- Sets up automatic virtual environment activation using direnv
- Configures IDE integration for VS Code and PyCharm
- Provides clear feedback on setup progress and next steps

Usage:
    python setup.py [--force] [--no-auto-activate]

Options:
    --force           Force recreation of virtual environment if it already exists
    --no-auto-activate  Skip setting up automatic virtual environment activation
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import venv
from pathlib import Path


class ThunderBuddySetup:
    """Handles the setup of the ThunderBuddy development environment."""

    def __init__(self, force=False, auto_activate=True):
        """Initialize the setup process.

        Args:
            force (bool): Whether to force recreation of the virtual environment
            auto_activate (bool): Whether to set up automatic activation
        """
        self.force = force
        self.auto_activate = auto_activate
        self.venv_dir = Path("venv")
        self.project_root = Path.cwd()
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_mac = self.system == "Darwin"
        self.is_linux = self.system == "Linux"
        self.python_executable = self._get_python_executable()
        self.pip_executable = self._get_pip_executable()
        self.activate_script = self._get_activate_script()

    def _get_python_executable(self):
        """Get the path to the Python executable in the virtual environment."""
        if self.is_windows:
            return self.venv_dir / "Scripts" / "python.exe"
        return self.venv_dir / "bin" / "python"

    def _get_pip_executable(self):
        """Get the path to the pip executable in the virtual environment."""
        if self.is_windows:
            return self.venv_dir / "Scripts" / "pip.exe"
        return self.venv_dir / "bin" / "pip"

    def _get_activate_script(self):
        """Get the path to the activation script for the virtual environment."""
        if self.is_windows:
            return self.venv_dir / "Scripts" / "activate"
        return self.venv_dir / "bin" / "activate"

    def run(self):
        """Run the setup process."""
        self._print_header()
        self._setup_venv()
        self._install_dependencies()
        if self.auto_activate:
            self._setup_auto_activation()
        self._setup_ide_integration()
        self._print_success()

    def _print_header(self):
        """Print the setup header."""
        print("\n" + "=" * 80)
        print("ThunderBuddy Development Environment Setup".center(80))
        print("=" * 80 + "\n")

    def _setup_venv(self):
        """Set up the virtual environment."""
        print("🔧 Setting up Python virtual environment...")
        if self.venv_dir.exists():
            if self.force:
                print("  ↪ Removing existing virtual environment...")
                shutil.rmtree(self.venv_dir)
            else:
                print("  ↪ Virtual environment already exists.")
                print("  ↪ Use --force to recreate it if needed.")
                return
        print("  ↪ Creating new virtual environment...")
        venv.create(self.venv_dir, with_pip=True)
        print("  ✅ Virtual environment created successfully!")

    def _install_dependencies(self):
        """Install project dependencies."""
        print("\n📦 Installing dependencies...")
        # Upgrade pip first
        self._run_venv_command(["-m", "pip", "install", "--upgrade", "pip"])
        # Install requirements
        if Path("requirements.txt").exists():
            print("  ↪ Installing packages from requirements.txt...")
            self._run_venv_command(["-m", "pip", "install", "-r", "requirements.txt"])
        # Install development requirements if they exist
        if Path("requirements-dev.txt").exists():
            print("  ↪ Installing development packages from requirements-dev.txt...")
            self._run_venv_command([
                "-m", "pip", "install", "-r", "requirements-dev.txt"
            ])
        print("  ✅ Dependencies installed successfully!")

    def _setup_auto_activation(self):
        """Set up automatic virtual environment activation."""
        print("\n🔄 Setting up automatic virtual environment activation...")
        # Setup direnv for auto-activation
        if self._is_command_available("direnv"):
            self._setup_direnv()
        else:
            self._install_direnv()
        print("  ✅ Automatic activation configured!")

    def _is_command_available(self, command):
        """Check if a command is available in the system."""
        try:
            subprocess.run(
                ["which" if not self.is_windows else "where", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _install_direnv(self):
        """Provide instructions for installing direnv."""
        print("  ↪ direnv is not installed. Installing or providing instructions...")
        if self.is_mac:
            if self._is_command_available("brew"):
                print("  ↪ Installing direnv via Homebrew...")
                subprocess.run(["brew", "install", "direnv"], check=False)
                self._setup_direnv()
            else:
                print("  ℹ️ Please install direnv using Homebrew:")
                print("    $ brew install direnv")
        elif self.is_linux:
            if self._is_command_available("apt-get"):
                print("  ↪ Installing direnv via apt...")
                subprocess.run(["sudo", "apt-get", "install", "direnv"], check=False)
                self._setup_direnv()
            else:
                print("  ℹ️ Please install direnv using your package manager:")
                print("    $ sudo apt-get install direnv")
                print("    or")
                print("    $ sudo yum install direnv")
        elif self.is_windows:
            print("  ℹ️ For Windows, install direnv via PowerShell:")
            print("    $ scoop install direnv")
            print("    Or you can use the manual activation method described below.")
        print("\n  ℹ️ After installing direnv, add to shell config:")
        if self.is_windows:
            print('    Add to your PowerShell profile: eval "$(direnv hook pwsh)"')
        else:
            print('    For bash: eval "$(direnv hook bash)"')
            print('    For zsh: eval "$(direnv hook zsh)"')
            print('    For fish: direnv hook fish | source')

    def _setup_direnv(self):
        """Set up direnv for automatic virtual environment activation."""
        print("  ↪ Configuring direnv...")
        # Create .envrc file
        envrc_path = self.project_root / ".envrc"
        relative_path = os.path.relpath(self.activate_script, self.project_root)
        with open(envrc_path, "w") as f:
            if self.is_windows:
                f.write(f'source_env "{relative_path}"\n')
            else:
                f.write(f'source_env "{relative_path}"\n')
        # Allow direnv in this directory
        try:
            subprocess.run(["direnv", "allow"], check=False)
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        # Add .envrc to .gitignore if it's not already there
        self._add_to_gitignore(".envrc")

    def _add_to_gitignore(self, entry):
        """Add an entry to .gitignore if it doesn't exist."""
        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, "w") as f:
                f.write(f"{entry}\n")
            return
        with open(gitignore_path, "r") as f:
            content = f.read()
        if entry not in content:
            with open(gitignore_path, "a") as f:
                f.write(f"\n{entry}\n")

    def _setup_ide_integration(self):
        """Set up IDE integration for VS Code and PyCharm."""
        print("\n🔌 Setting up IDE integration...")
        # VS Code integration
        vscode_dir = self.project_root / ".vscode"
        if not vscode_dir.exists():
            vscode_dir.mkdir()
        settings_path = vscode_dir / "settings.json"
        if not settings_path.exists():
            with open(settings_path, "w") as f:
                f.write('{\n')
                f.write('    "python.defaultInterpreterPath": "{0}",\n'.format(
                    self.python_executable))
                f.write('    "python.terminal.activateEnvironment": true,\n')
                f.write('    "python.linting.enabled": true,\n')
                f.write('    "python.linting.pylintEnabled": true,\n')
                f.write('    "python.linting.flake8Enabled": true,\n')
                f.write('    "python.formatting.provider": "black"\n')
                f.write('}\n')
        print("  ✅ IDE integration configured!")

    def _run_venv_command(self, args):
        """Run a command in the virtual environment."""
        cmd = [str(self.python_executable)] + args
        subprocess.run(cmd, check=True)

    def _print_success(self):
        """Print success message and next steps."""
        print("\n" + "=" * 80)
        print("🎉 ThunderBuddy Development Environment Setup Complete! 🎉".center(80))
        print("=" * 80 + "\n")
        print("📋 Next Steps:")
        if self.auto_activate:
            print("  1. Close and reopen your terminal, or run 'direnv allow'")
            print("     to activate the virtual environment automatically.")
        else:
            if self.is_windows:
                print("  1. Activate the virtual environment manually:")
                print(f"     > .\\{self.venv_dir}\\Scripts\\activate")
            else:
                print("  1. Activate the virtual environment manually:")
                print(f"     $ source {self.venv_dir}/bin/activate")
        print("  2. Start developing with ThunderBuddy!")
        print("     - Run 'make test' to verify your setup")
        print("     - Run 'make lint' to check code quality")
        print("     - Run 'make help' to see all available commands")
        print("\n💡 For VS Code users:")
        print("  - The Python interpreter is already configured")
        print("  - Restart VS Code or reload the window to apply changes")
        print("\n💡 For PyCharm users:")
        print("  - Go to Settings → Project → Python Interpreter")
        print("  - Click the gear icon → Add → Existing Environment")
        print(f"  - Select the interpreter at: {self.python_executable}")
        print("\n📚 For more information, refer to the README.md file.")
        print("=" * 80 + "\n")


def main():
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(
        description="Set up ThunderBuddy development environment"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recreation of virtual environment"
    )
    parser.add_argument(
        "--no-auto-activate",
        action="store_true",
        help="Skip setting up automatic activation"
    )
    args = parser.parse_args()
    setup = ThunderBuddySetup(
        force=args.force,
        auto_activate=not args.no_auto_activate
    )
    setup.run()


if __name__ == "__main__":
    main()
