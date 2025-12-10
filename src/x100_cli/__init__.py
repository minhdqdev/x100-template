"""
X100 CLI - Setup tool for projects

Usage:
    uvx x100-cli.py init <project-name>
    uvx x100-cli.py init .
    uvx x100-cli.py init --here

Or install globally:
    uv tool install --from x100-cli.py x100-cli
    x100 init <project-name>
    x100 init .
    x100 init --here
"""

import os
import subprocess
import sys
import argparse
import zipfile
import tempfile
import shutil
import shlex
import json
import ssl
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
import readchar

import typer
import httpx

from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.tree import Tree
from typer.core import TyperGroup
import truststore


from .ui import (
    show_banner,
    StepTracker,
    console,
    check_tool,
    check_file,
)

from .core import (
    is_x100_project,
    X100_CONFIG_PATH,
    X100_CONFIG,
    AGENT_CONFIG,
    save_config,
    load_config,
)


ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client = httpx.Client(verify=ssl_context)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="x100", description="x100 project automation CLI"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser(
        "init",
        aliases=["initialize", "init-project"],
        help="Initialize project structure",
    )
    sub.add_parser("contribute", help="Sync and open a PR with changes")
    sub.add_parser("verify", help="Run environment checks")

    cmd_parser = sub.add_parser("command", help="Manage Claude Code commands")
    cmd_sub = cmd_parser.add_subparsers(dest="subcommand")
    cmd_sub.add_parser("list", help="List all available commands")
    enable_cmd = cmd_sub.add_parser("enable", help="Enable a command")
    enable_cmd.add_argument("name", nargs="?", help="Command name to enable")
    disable_cmd = cmd_sub.add_parser("disable", help="Disable a command")
    disable_cmd.add_argument("name", nargs="?", help="Command name to disable")

    agent_parser = sub.add_parser("agent", help="Manage Claude Code agents")
    agent_sub = agent_parser.add_subparsers(dest="subcommand")
    agent_sub.add_parser("list", help="List all available agents")
    enable_agent_cmd = agent_sub.add_parser("enable", help="Enable an agent")
    enable_agent_cmd.add_argument("name", nargs="?", help="Agent name to enable")
    disable_agent_cmd = agent_sub.add_parser("disable", help="Disable an agent")
    disable_agent_cmd.add_argument("name", nargs="?", help="Agent name to disable")

    sub.add_parser("workflow-enable", help="Enable all workflow commands and agents")

    return parser


# def old_main(argv: Sequence[str] | None = None) -> None:
#     parser = build_parser()
#     args = parser.parse_args(argv)
#     paths = detect_tool_paths()

#     command = args.command

#     if command in ("init", "initialize", "init-project"):
#         ui.clear_screen()
#         init_project(paths, wait_for_key=False)
#         return
#     if command == "contribute":
#         ui.clear_screen()
#         run_contribute(paths)
#         return
#     if command == "verify":
#         ui.clear_screen()
#         verify(paths)
#         return
#     if command == "workflow-enable":
#         ui.clear_screen()
#         enable_workflow(paths)
#         return

#     if command == "command":
#         ui.clear_screen()
#         subcommand = getattr(args, "subcommand", None)
#         if subcommand == "list":
#             list_available_commands(paths)
#         elif subcommand == "enable":
#             enable_command(paths, getattr(args, "name", None))
#         elif subcommand == "disable":
#             disable_command(paths, getattr(args, "name", None))
#         else:
#             manage_commands(paths)
#         return

#     if command == "agent":
#         ui.clear_screen()
#         subcommand = getattr(args, "subcommand", None)
#         if subcommand == "list":
#             list_available_agents(paths)
#         elif subcommand == "enable":
#             enable_agent(paths, getattr(args, "name", None))
#         elif subcommand == "disable":
#             disable_agent(paths, getattr(args, "name", None))
#         else:
#             manage_agents(paths)
#         return

#     ui.clear_screen()
#     run_menu(paths)


def _github_token(cli_token: str | None = None) -> str | None:
    """Return sanitized GitHub token (cli arg takes precedence) or None."""
    return (
        (cli_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or "").strip()
    ) or None


def _github_auth_headers(cli_token: str | None = None) -> dict:
    """Return Authorization header dict only when a non-empty token exists."""
    token = _github_token(cli_token)
    return {"Authorization": f"Bearer {token}"} if token else {}


def _parse_rate_limit_headers(headers: httpx.Headers) -> dict:
    """Extract and parse GitHub rate-limit headers."""
    info = {}

    # Standard GitHub rate-limit headers
    if "X-RateLimit-Limit" in headers:
        info["limit"] = headers.get("X-RateLimit-Limit")
    if "X-RateLimit-Remaining" in headers:
        info["remaining"] = headers.get("X-RateLimit-Remaining")
    if "X-RateLimit-Reset" in headers:
        reset_epoch = int(headers.get("X-RateLimit-Reset", "0"))
        if reset_epoch:
            reset_time = datetime.fromtimestamp(reset_epoch, tz=timezone.utc)
            info["reset_epoch"] = reset_epoch
            info["reset_time"] = reset_time
            info["reset_local"] = reset_time.astimezone()

    # Retry-After header (seconds or HTTP-date)
    if "Retry-After" in headers:
        retry_after = headers.get("Retry-After")
        try:
            info["retry_after_seconds"] = int(retry_after)
        except ValueError:
            # HTTP-date format - not implemented, just store as string
            info["retry_after"] = retry_after

    return info


def _format_rate_limit_error(status_code: int, headers: httpx.Headers, url: str) -> str:
    """Format a user-friendly error message with rate-limit information."""
    rate_info = _parse_rate_limit_headers(headers)

    lines = [f"GitHub API returned status {status_code} for {url}"]
    lines.append("")

    if rate_info:
        lines.append("[bold]Rate Limit Information:[/bold]")
        if "limit" in rate_info:
            lines.append(f"  • Rate Limit: {rate_info['limit']} requests/hour")
        if "remaining" in rate_info:
            lines.append(f"  • Remaining: {rate_info['remaining']}")
        if "reset_local" in rate_info:
            reset_str = rate_info["reset_local"].strftime("%Y-%m-%d %H:%M:%S %Z")
            lines.append(f"  • Resets at: {reset_str}")
        if "retry_after_seconds" in rate_info:
            lines.append(f"  • Retry after: {rate_info['retry_after_seconds']} seconds")
        lines.append("")

    # Add troubleshooting guidance
    lines.append("[bold]Troubleshooting Tips:[/bold]")
    lines.append(
        "  • If you're on a shared CI or corporate environment, you may be rate-limited."
    )
    lines.append(
        "  • Consider using a GitHub token via --github-token or the GH_TOKEN/GITHUB_TOKEN"
    )
    lines.append("    environment variable to increase rate limits.")
    lines.append(
        "  • Authenticated requests have a limit of 5,000/hour vs 60/hour for unauthenticated."
    )

    return "\n".join(lines)


SCRIPT_TYPE_CHOICES = {"sh": "POSIX Shell (bash/zsh)", "ps": "PowerShell"}


def get_key():
    """Get a single keypress in a cross-platform way using readchar."""
    key = readchar.readkey()

    if key == readchar.key.UP or key == readchar.key.CTRL_P:
        return "up"
    if key == readchar.key.DOWN or key == readchar.key.CTRL_N:
        return "down"

    if key == readchar.key.ENTER:
        return "enter"

    if key == readchar.key.ESC:
        return "escape"

    if key == readchar.key.CTRL_C:
        raise KeyboardInterrupt

    return key


def select_with_arrows(
    options: dict, prompt_text: str = "Select an option", default_key: str = None
) -> str:
    """
    Interactive selection using arrow keys with Rich Live display.

    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_key: Default option key to start with

    Returns:
        Selected option key
    """
    option_keys = list(options.keys())
    if default_key and default_key in option_keys:
        selected_index = option_keys.index(default_key)
    else:
        selected_index = 0

    selected_key = None

    def create_selection_panel():
        """Create the selection panel with current selection highlighted."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")

        for i, key in enumerate(option_keys):
            if i == selected_index:
                table.add_row("▶", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")
            else:
                table.add_row(" ", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")

        table.add_row("", "")
        table.add_row(
            "", "[dim]Use ↑/↓ to navigate, Enter to select, Esc to cancel[/dim]"
        )

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_key, selected_index
        with Live(
            create_selection_panel(),
            console=console,
            transient=True,
            auto_refresh=False,
        ) as live:
            while True:
                try:
                    key = get_key()
                    if key == "up":
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == "down":
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == "enter":
                        selected_key = option_keys[selected_index]
                        break
                    elif key == "escape":
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_key is None:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return selected_key


class BannerGroup(TyperGroup):
    """Custom group that shows banner before help."""

    def format_help(self, ctx, formatter):
        # Show banner before help
        show_banner()
        super().format_help(ctx, formatter)


app = typer.Typer(
    name="x100",
    help="Setup tool for Spec-Driven Development projects",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)


@app.callback()
def callback(ctx: typer.Context):
    """Show banner when no subcommand is provided."""
    if (
        ctx.invoked_subcommand is None
        and "--help" not in sys.argv
        and "-h" not in sys.argv
    ):
        show_banner()
        console.print(
            Align.center("[dim]Run 'x100 --help' for usage information[/dim]")
        )
        console.print()


def run_command(
    cmd: list[str],
    check_return: bool = True,
    capture: bool = False,
    shell: bool = False,
) -> Optional[str]:
    """Run a shell command and optionally capture output."""
    try:
        if capture:
            result = subprocess.run(
                cmd, check=check_return, capture_output=True, text=True, shell=shell
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=check_return, shell=shell)
            return None
    except subprocess.CalledProcessError as e:
        if check_return:
            console.print(f"[red]Error running command:[/red] {' '.join(cmd)}")
            console.print(f"[red]Exit code:[/red] {e.returncode}")
            if hasattr(e, "stderr") and e.stderr:
                console.print(f"[red]Error output:[/red] {e.stderr}")
            raise
        return None


def is_git_repo(path: Path = None) -> bool:
    """Check if the specified path is inside a git repository."""
    if path is None:
        path = Path.cwd()

    if not path.is_dir():
        return False

    try:
        # Use git command to check if inside a work tree
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            cwd=path,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def init_git_repo(
    project_path: Path, quiet: bool = False
) -> Tuple[bool, Optional[str]]:
    """Initialize a git repository in the specified path.

    Args:
        project_path: Path to initialize git repository in
        quiet: if True suppress console output (tracker handles status)

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        original_cwd = Path.cwd()
        os.chdir(project_path)
        if not quiet:
            console.print("[cyan]Initializing git repository...[/cyan]")
        subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from x100 template"],
            check=True,
            capture_output=True,
            text=True,
        )
        if not quiet:
            console.print("[green]✓[/green] Git repository initialized")
        return True, None

    except subprocess.CalledProcessError as e:
        error_msg = f"Command: {' '.join(e.cmd)}\nExit code: {e.returncode}"
        if e.stderr:
            error_msg += f"\nError: {e.stderr.strip()}"
        elif e.stdout:
            error_msg += f"\nOutput: {e.stdout.strip()}"

        if not quiet:
            console.print(f"[red]Error initializing git repository:[/red] {e}")
        return False, error_msg
    finally:
        os.chdir(original_cwd)


def handle_vscode_settings(
    sub_item, dest_file, rel_path, verbose=False, tracker=None
) -> None:
    """Handle merging or copying of .vscode/settings.json files."""

    def log(message, color="green"):
        if verbose and not tracker:
            console.print(f"[{color}]{message}[/] {rel_path}")

    try:
        with open(sub_item, "r", encoding="utf-8") as f:
            new_settings = json.load(f)

        if dest_file.exists():
            merged = merge_json_files(
                dest_file, new_settings, verbose=verbose and not tracker
            )
            with open(dest_file, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=4)
                f.write("\n")
            log("Merged:", "green")
        else:
            shutil.copy2(sub_item, dest_file)
            log("Copied (no existing settings.json):", "blue")

    except Exception as e:
        log(f"Warning: Could not merge, copying instead: {e}", "yellow")
        shutil.copy2(sub_item, dest_file)


def merge_json_files(
    existing_path: Path, new_content: dict, verbose: bool = False
) -> dict:
    """Merge new JSON content into existing JSON file.

    Performs a deep merge where:
    - New keys are added
    - Existing keys are preserved unless overwritten by new content
    - Nested dictionaries are merged recursively
    - Lists and other values are replaced (not merged)

    Args:
        existing_path: Path to existing JSON file
        new_content: New JSON content to merge in
        verbose: Whether to print merge details

    Returns:
        Merged JSON content as dict
    """
    try:
        with open(existing_path, "r", encoding="utf-8") as f:
            existing_content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, just use new content
        return new_content

    def deep_merge(base: dict, update: dict) -> dict:
        """Recursively merge update dict into base dict."""
        result = base.copy()
        for key, value in update.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge nested dictionaries
                result[key] = deep_merge(result[key], value)
            else:
                # Add new key or replace existing value
                result[key] = value
        return result

    merged = deep_merge(existing_content, new_content)

    if verbose:
        console.print(f"[cyan]Merged JSON file:[/cyan] {existing_path.name}")

    return merged


def download_template_from_github(
    ai_assistant: str,
    download_dir: Path,
    *,
    script_type: str = "sh",
    verbose: bool = True,
    show_progress: bool = True,
    client: httpx.Client = None,
    debug: bool = False,
    github_token: str = None,
) -> Tuple[Path, dict]:
    repo_owner = "minhdqdev"
    repo_name = "x100-cli"
    if client is None:
        client = httpx.Client(verify=ssl_context)

    if verbose:
        console.print("[cyan]Fetching latest release information...[/cyan]")
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    try:
        response = client.get(
            api_url,
            timeout=30,
            follow_redirects=True,
            headers=_github_auth_headers(github_token),
        )
        status = response.status_code
        if status != 200:
            # Format detailed error message with rate-limit info
            error_msg = _format_rate_limit_error(status, response.headers, api_url)
            if debug:
                error_msg += f"\n\n[dim]Response body (truncated 500):[/dim]\n{response.text[:500]}"
            raise RuntimeError(error_msg)
        try:
            release_data = response.json()
        except ValueError as je:
            raise RuntimeError(
                f"Failed to parse release JSON: {je}\nRaw (truncated 400): {response.text[:400]}"
            )
    except Exception as e:
        console.print(f"[red]Error fetching release information[/red]")
        console.print(Panel(str(e), title="Fetch Error", border_style="red"))
        raise typer.Exit(1)

    assets = release_data.get("assets", [])
    pattern = f"x100-template-{ai_assistant}-{script_type}"
    matching_assets = [
        asset
        for asset in assets
        if pattern in asset["name"] and asset["name"].endswith(".zip")
    ]

    asset = matching_assets[0] if matching_assets else None

    if asset is None:
        console.print(
            f"[red]No matching release asset found[/red] for [bold]{ai_assistant}[/bold] (expected pattern: [bold]{pattern}[/bold])"
        )
        asset_names = [a.get("name", "?") for a in assets]
        console.print(
            Panel(
                "\n".join(asset_names) or "(no assets)",
                title="Available Assets",
                border_style="yellow",
            )
        )
        raise typer.Exit(1)

    download_url = asset["browser_download_url"]
    filename = asset["name"]
    file_size = asset["size"]

    if verbose:
        console.print(f"[cyan]Found template:[/cyan] {filename}")
        console.print(f"[cyan]Size:[/cyan] {file_size:,} bytes")
        console.print(f"[cyan]Release:[/cyan] {release_data['tag_name']}")

    zip_path = download_dir / filename
    if verbose:
        console.print(f"[cyan]Downloading template...[/cyan]")

    try:
        with client.stream(
            "GET",
            download_url,
            timeout=60,
            follow_redirects=True,
            headers=_github_auth_headers(github_token),
        ) as response:
            if response.status_code != 200:
                # Handle rate-limiting on download as well
                error_msg = _format_rate_limit_error(
                    response.status_code, response.headers, download_url
                )
                if debug:
                    error_msg += f"\n\n[dim]Response body (truncated 400):[/dim]\n{response.text[:400]}"
                raise RuntimeError(error_msg)
            total_size = int(response.headers.get("content-length", 0))
            with open(zip_path, "wb") as f:
                if total_size == 0:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
                else:
                    if show_progress:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                            console=console,
                        ) as progress:
                            task = progress.add_task("Downloading...", total=total_size)
                            downloaded = 0
                            for chunk in response.iter_bytes(chunk_size=8192):
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task, completed=downloaded)
                    else:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
    except Exception as e:
        console.print(f"[red]Error downloading template[/red]")
        detail = str(e)
        if zip_path.exists():
            zip_path.unlink()
        console.print(Panel(detail, title="Download Error", border_style="red"))
        raise typer.Exit(1)
    if verbose:
        console.print(f"Downloaded: {filename}")
    metadata = {
        "filename": filename,
        "size": file_size,
        "release": release_data["tag_name"],
        "asset_url": download_url,
    }
    return zip_path, metadata


def download_and_extract_template(
    project_path: Path,
    ai_assistant: str,
    script_type: str,
    is_current_dir: bool = False,
    *,
    verbose: bool = True,
    tracker: StepTracker | None = None,
    client: httpx.Client = None,
    debug: bool = False,
    github_token: str = None,
) -> Path:
    """Download the latest release and extract it to create a new project.
    Returns project_path. Uses tracker if provided (with keys: fetch, download, extract, cleanup)
    """
    current_dir = Path.cwd()

    if tracker:
        tracker.start("fetch", "contacting GitHub API")
    try:
        zip_path, meta = download_template_from_github(
            ai_assistant,
            current_dir,
            script_type=script_type,
            verbose=verbose and tracker is None,
            show_progress=(tracker is None),
            client=client,
            debug=debug,
            github_token=github_token,
        )
        if tracker:
            tracker.complete(
                "fetch", f"release {meta['release']} ({meta['size']:,} bytes)"
            )
            tracker.add("download", "Download template")
            tracker.complete("download", meta["filename"])
    except Exception as e:
        if tracker:
            tracker.error("fetch", str(e))
        else:
            if verbose:
                console.print(f"[red]Error downloading template:[/red] {e}")
        raise

    if tracker:
        tracker.add("extract", "Extract template")
        tracker.start("extract")
    elif verbose:
        console.print("Extracting template...")

    try:
        if not is_current_dir:
            project_path.mkdir(parents=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_contents = zip_ref.namelist()
            if tracker:
                tracker.start("zip-list")
                tracker.complete("zip-list", f"{len(zip_contents)} entries")
            elif verbose:
                console.print(f"[cyan]ZIP contains {len(zip_contents)} items[/cyan]")

            if is_current_dir:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    zip_ref.extractall(temp_path)

                    extracted_items = list(temp_path.iterdir())
                    if tracker:
                        tracker.start("extracted-summary")
                        tracker.complete(
                            "extracted-summary", f"temp {len(extracted_items)} items"
                        )
                    elif verbose:
                        console.print(
                            f"[cyan]Extracted {len(extracted_items)} items to temp location[/cyan]"
                        )

                    source_dir = temp_path
                    if len(extracted_items) == 1 and extracted_items[0].is_dir():
                        source_dir = extracted_items[0]
                        if tracker:
                            tracker.add("flatten", "Flatten nested directory")
                            tracker.complete("flatten")
                        elif verbose:
                            console.print(
                                "[cyan]Found nested directory structure[/cyan]"
                            )

                    for item in source_dir.iterdir():
                        dest_path = project_path / item.name
                        if item.is_dir():
                            if dest_path.exists():
                                if verbose and not tracker:
                                    console.print(
                                        f"[yellow]Merging directory:[/yellow] {item.name}"
                                    )
                                for sub_item in item.rglob("*"):
                                    if sub_item.is_file():
                                        rel_path = sub_item.relative_to(item)
                                        dest_file = dest_path / rel_path
                                        dest_file.parent.mkdir(
                                            parents=True, exist_ok=True
                                        )
                                        # Special handling for .vscode/settings.json - merge instead of overwrite
                                        if (
                                            dest_file.name == "settings.json"
                                            and dest_file.parent.name == ".vscode"
                                        ):
                                            handle_vscode_settings(
                                                sub_item,
                                                dest_file,
                                                rel_path,
                                                verbose,
                                                tracker,
                                            )
                                        else:
                                            shutil.copy2(sub_item, dest_file)
                            else:
                                shutil.copytree(item, dest_path)
                        else:
                            if dest_path.exists() and verbose and not tracker:
                                console.print(
                                    f"[yellow]Overwriting file:[/yellow] {item.name}"
                                )
                            shutil.copy2(item, dest_path)
                    if verbose and not tracker:
                        console.print(
                            "[cyan]Template files merged into current directory[/cyan]"
                        )
            else:
                zip_ref.extractall(project_path)

                extracted_items = list(project_path.iterdir())
                if tracker:
                    tracker.start("extracted-summary")
                    tracker.complete(
                        "extracted-summary", f"{len(extracted_items)} top-level items"
                    )
                elif verbose:
                    console.print(
                        f"[cyan]Extracted {len(extracted_items)} items to {project_path}:[/cyan]"
                    )
                    for item in extracted_items:
                        console.print(
                            f"  - {item.name} ({'dir' if item.is_dir() else 'file'})"
                        )

                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    nested_dir = extracted_items[0]
                    temp_move_dir = project_path.parent / f"{project_path.name}_temp"

                    shutil.move(str(nested_dir), str(temp_move_dir))

                    project_path.rmdir()

                    shutil.move(str(temp_move_dir), str(project_path))
                    if tracker:
                        tracker.add("flatten", "Flatten nested directory")
                        tracker.complete("flatten")
                    elif verbose:
                        console.print(
                            "[cyan]Flattened nested directory structure[/cyan]"
                        )

    except Exception as e:
        if tracker:
            tracker.error("extract", str(e))
        else:
            if verbose:
                console.print(f"[red]Error extracting template:[/red] {e}")
                if debug:
                    console.print(
                        Panel(str(e), title="Extraction Error", border_style="red")
                    )

        if not is_current_dir and project_path.exists():
            shutil.rmtree(project_path)
        raise typer.Exit(1)
    else:
        if tracker:
            tracker.complete("extract")
    finally:
        if tracker:
            tracker.add("cleanup", "Remove temporary archive")

        if zip_path.exists():
            zip_path.unlink()
            if tracker:
                tracker.complete("cleanup")
            elif verbose:
                console.print(f"Cleaned up: {zip_path.name}")

    return project_path


def copy_issue_templates(
    project_path: Path, tracker: StepTracker | None = None
) -> None:
    """Copy GitHub issue templates from templates/ISSUE_TEMPLATE to .github/ISSUE_TEMPLATE."""
    # Get the templates directory from the package
    package_dir = Path(__file__).parent
    templates_source = package_dir / "templates" / "ISSUE_TEMPLATE"
    templates_dest = project_path / ".github" / "ISSUE_TEMPLATE"

    if not templates_source.exists():
        if tracker:
            tracker.skip("issue-templates", "source not found")
        else:
            console.print("[yellow]Warning: Issue template source not found[/yellow]")
        return

    try:
        if tracker:
            tracker.start("issue-templates")

        # Create destination directory
        templates_dest.mkdir(parents=True, exist_ok=True)

        # Copy all template files
        copied = 0
        for template_file in templates_source.glob("*.md"):
            dest_file = templates_dest / template_file.name
            shutil.copy2(template_file, dest_file)
            copied += 1

        if tracker:
            if copied > 0:
                tracker.complete("issue-templates", f"{copied} template(s)")
            else:
                tracker.skip("issue-templates", "no templates found")
        else:
            if copied > 0:
                console.print(
                    f"[cyan]Copied {copied} issue template(s) to .github/ISSUE_TEMPLATE/[/cyan]"
                )
    except Exception as e:
        if tracker:
            tracker.error("issue-templates", str(e))
        else:
            console.print(
                f"[yellow]Warning: Could not copy issue templates: {e}[/yellow]"
            )


def ensure_executable_scripts(
    project_path: Path, tracker: StepTracker | None = None
) -> None:
    """Ensure POSIX .sh scripts under .x100/scripts (recursively) have execute bits (no-op on Windows)."""
    if os.name == "nt":
        return  # Windows: skip silently
    scripts_root = project_path / ".x100" / "scripts"
    if not scripts_root.is_dir():
        return
    failures: list[str] = []
    updated = 0
    for script in scripts_root.rglob("*.sh"):
        try:
            if script.is_symlink() or not script.is_file():
                continue
            try:
                with script.open("rb") as f:
                    if f.read(2) != b"#!":
                        continue
            except Exception:
                continue
            st = script.stat()
            mode = st.st_mode
            if mode & 0o111:
                continue
            new_mode = mode
            if mode & 0o400:
                new_mode |= 0o100
            if mode & 0o040:
                new_mode |= 0o010
            if mode & 0o004:
                new_mode |= 0o001
            if not (new_mode & 0o100):
                new_mode |= 0o100
            os.chmod(script, new_mode)
            updated += 1
        except Exception as e:
            failures.append(f"{script.relative_to(scripts_root)}: {e}")
    if tracker:
        detail = f"{updated} updated" + (
            f", {len(failures)} failed" if failures else ""
        )
        (tracker.error if failures else tracker.complete)("chmod", detail)
    else:
        if updated:
            console.print(
                f"[cyan]Updated execute permissions on {updated} script(s) recursively[/cyan]"
            )
        if failures:
            console.print("[yellow]Some scripts could not be updated:[/yellow]")
            for f in failures:
                console.print(f"  - {f}")


def list_registered_agents():
    agents = X100_CONFIG.get("agents", {})

    if not agents:
        console.print("[yellow]No agents registered.[/yellow]")
        return

    table = Table(title="Registered AI Agents")
    table.add_column("Agent Name", style="cyan", no_wrap=True)
    table.add_column("Enabled", style="magenta")

    for agent_name, agent_info in agents.items():
        enabled = (
            "[green]Yes[/green]"
            if agent_info.get("enabled", False)
            else "[red]No[/red]"
        )
        table.add_row(agent_name, enabled)

    console.print(table)


def switch_default_agent():
    """Switch the default AI agent for the current x100 project."""
    if not X100_CONFIG_PATH.exists():
        console.print(
            "[red]Error:[/red] Not in an x100 project directory. Run this command from a project initialized with 'x100 init'."
        )
        raise typer.Exit(1)

    # Load current config
    config = {}
    try:
        config = json.loads(X100_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]Error reading config:[/red] {e}")
        raise typer.Exit(1)

    current_agent = config.get("default_agent", "unknown")

    console.print(f"\n[cyan]Current default agent:[/cyan] {current_agent}")
    console.print()

    # Show available agents and let user select
    ai_choices = {key: cfg["name"] for key, cfg in AGENT_CONFIG.items()}

    selected_ai = select_with_arrows(
        ai_choices,
        "Choose new default AI assistant:",
        current_agent if current_agent in ai_choices else "copilot",
    )

    if selected_ai == current_agent:
        console.print(f"\n[yellow]Default agent unchanged:[/yellow] {current_agent}")
        return

    # Update config
    config["default_agent"] = selected_ai
    save_config(config, X100_CONFIG_PATH)

    console.print(
        f"\n[green]✓[/green] Default agent changed from [cyan]{current_agent}[/cyan] to [cyan]{selected_ai}[/cyan]"
    )

    agent_config = AGENT_CONFIG.get(selected_ai)
    if agent_config:
        agent_folder = agent_config["folder"]
        console.print(f"\n[dim]Agent files location:[/dim] [cyan]{agent_folder}[/cyan]")

        project_root = X100_CONFIG_PATH.parent.parent
        agent_path = project_root / agent_folder.strip("./")

        if not agent_path.exists():
            console.print(
                f"\n[yellow]Note:[/yellow] Agent folder does not exist yet. "
                f"You may need to set up the agent configuration manually or re-initialize the project."
            )


@app.command()
def agent(
    subcommand: str = typer.Argument(None, help="Subcommand: list, switch-default")
):
    """
    Manage AI agents for your x100 project.

    Subcommands:
        list            List all available agents
        switch-default  Change the default AI agent
    """
    if subcommand == "list":
        list_registered_agents()
    elif subcommand == "switch-default":
        switch_default_agent()
    else:
        console.print("[yellow]Unknown subcommand.[/yellow]")
        console.print("Available subcommands: list, switch-default")
        raise typer.Exit(1)


def set_github_repo_url(url):
    """Set the GitHub repository URL in the x100 project configuration."""
    if not X100_CONFIG_PATH.exists():
        console.print(
            "[red]Error:[/red] No x100 project configuration found in the current directory."
        )
        raise typer.Exit(1)

    X100_CONFIG.setdefault("project", {})
    X100_CONFIG["project"]["url"] = url

    # Extract project id from url if possible
    if "github.com/" in url:
        parts = url.split("/projects/")[-1].split("/")
        if parts:
            project_id = parts[0]
            X100_CONFIG["project"]["id"] = project_id

    else:
        console.print("[red]Error: Unable to extract project ID from URL.[/red]")
        raise typer.Exit(1)

    try:
        with open(X100_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(X100_CONFIG, f, indent=4)
            f.write("\n")
        console.print(f"[green]✓[/green] Set GitHub repository URL to: {url}")
    except Exception as e:
        console.print(f"[red]Error writing configuration:[/red] {e}")
        raise typer.Exit(1)


@app.command(name="project")
def project(
    subcommand: str = typer.Argument(None, help="Subcommand: set-url, info"),
    args: List[str] = typer.Argument(None, help="Additional arguments for subcommands"),
):
    """
    Manage project settings for your x100 project.

    Subcommands:
        set-url    Set the URL for the project
    """

    if subcommand == "set-url":
        url = args[0] if args else None
        if not url:
            console.print("[red]Error:[/red] Project URL is required.")
            raise typer.Exit(1)
        set_github_repo_url(url)
    elif subcommand == "info":
        if not X100_CONFIG_PATH.exists():
            console.print(
                "[red]Error:[/red] No x100 project configuration found in the current directory."
            )
            raise typer.Exit(1)

        project_info = X100_CONFIG.get("project", {})
        project_type = project_info.get("type", "N/A")

        if project_type == "github_project":
            table = Table(title="GitHub Project Information")
            table.add_column("Field", style="cyan", no_wrap=True)
            table.add_column("Value", style="white")

            for key, value in project_info.items():
                table.add_row(key, str(value))

        console.print(table)
    else:
        console.print("[red]Error:[/red] Unknown subcommand.")
        raise typer.Exit(1)


@app.command()
def init(
    project_name: str = typer.Argument(
        None,
        help="Name for your new project directory (optional if using --here, or use '.' for current directory)",
    ),
    ai_assistant: str = typer.Option(
        None,
        "--ai",
        help="AI assistant to use: claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, codebuddy, amp, shai, q, or bob",
    ),
    script_type: str = typer.Option(
        None, "--script", help="Script type to use: sh or ps"
    ),
    ignore_agent_tools: bool = typer.Option(
        False,
        "--ignore-agent-tools",
        help="Skip checks for AI agent tools like Claude Code",
    ),
    no_git: bool = typer.Option(
        False, "--no-git", help="Skip git repository initialization"
    ),
    here: bool = typer.Option(
        False,
        "--here",
        help="Initialize project in the current directory instead of creating a new one",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force merge/overwrite when using --here (skip confirmation)",
    ),
    skip_tls: bool = typer.Option(
        False, "--skip-tls", help="Skip SSL/TLS verification (not recommended)"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Show verbose diagnostic output for network and extraction failures",
    ),
    github_token: str = typer.Option(
        None,
        "--github-token",
        help="GitHub token to use for API requests (or set GH_TOKEN or GITHUB_TOKEN environment variable)",
    ),
):
    """
    Initialize a new x100 project from the latest template.

    This command will:
    1. Check that required tools are installed (git is optional)
    2. Let you choose your AI assistant
    3. Download the appropriate template from GitHub
    4. Extract the template to a new project directory or current directory
    5. Initialize a fresh git repository (if not --no-git and no existing repo)
    6. Optionally set up AI assistant commands

    Examples:
        x100 init my-project
        x100 init my-project --ai claude
        x100 init my-project --ai copilot --no-git
        x100 init --ignore-agent-tools my-project
        x100 init . --ai claude         # Initialize in current directory
        x100 init .                     # Initialize in current directory (interactive AI selection)
        x100 init --here --ai claude    # Alternative syntax for current directory
        x100 init --here --ai codex
        x100 init --here --ai codebuddy
        x100 init --here
        x100 init --here --force  # Skip confirmation when current directory not empty
    """

    show_banner()

    if project_name == ".":
        here = True
        project_name = None  # Clear project_name to use existing validation logic

    if here and project_name:
        console.print(
            "[red]Error:[/red] Cannot specify both project name and --here flag"
        )
        raise typer.Exit(1)

    if not here and not project_name:
        console.print(
            "[red]Error:[/red] Must specify either a project name, use '.' for current directory, or use --here flag"
        )
        raise typer.Exit(1)

    if here:
        project_name = Path.cwd().name
        project_path = Path.cwd()

        existing_items = list(project_path.iterdir())
        if existing_items:
            console.print(
                f"[yellow]Warning:[/yellow] Current directory is not empty ({len(existing_items)} items)"
            )
            console.print(
                "[yellow]Template files will be merged with existing content and may overwrite existing files[/yellow]"
            )
            if force:
                console.print(
                    "[cyan]--force supplied: skipping confirmation and proceeding with merge[/cyan]"
                )
            else:
                response = typer.confirm("Do you want to continue?")
                if not response:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    raise typer.Exit(0)
    else:
        project_path = Path(project_name).resolve()
        if project_path.exists():
            error_panel = Panel(
                f"Directory '[cyan]{project_name}[/cyan]' already exists\n"
                "Please choose a different project name or remove the existing directory.",
                title="[red]Directory Conflict[/red]",
                border_style="red",
                padding=(1, 2),
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

    current_dir = Path.cwd()

    setup_lines = [
        "[cyan]x100 Project Setup[/cyan]",
        "",
        f"{'Project':<15} [green]{project_path.name}[/green]",
        f"{'Working Path':<15} [dim]{current_dir}[/dim]",
    ]

    if not here:
        setup_lines.append(f"{'Target Path':<15} [dim]{project_path}[/dim]")

    console.print(Panel("\n".join(setup_lines), border_style="cyan", padding=(1, 2)))

    should_init_git = False
    if not no_git:
        should_init_git = check_tool("git")
        if not should_init_git:
            console.print(
                "[yellow]Git not found - will skip repository initialization[/yellow]"
            )

    if ai_assistant:
        if ai_assistant not in AGENT_CONFIG:
            console.print(
                f"[red]Error:[/red] Invalid AI assistant '{ai_assistant}'. Choose from: {', '.join(AGENT_CONFIG.keys())}"
            )
            raise typer.Exit(1)
        selected_ai = ai_assistant
    else:
        # Create options dict for selection (agent_key: display_name)
        ai_choices = {key: config["name"] for key, config in AGENT_CONFIG.items()}
        selected_ai = select_with_arrows(
            ai_choices, "Choose your AI assistant:", "copilot"
        )

    if not ignore_agent_tools:
        agent_config = AGENT_CONFIG.get(selected_ai)
        if agent_config and agent_config["requires_cli"]:
            install_url = agent_config["install_url"]
            if not check_tool(selected_ai):
                error_panel = Panel(
                    f"[cyan]{selected_ai}[/cyan] not found\n"
                    f"Install from: [cyan]{install_url}[/cyan]\n"
                    f"{agent_config['name']} is required to continue with this project type.\n\n"
                    "Tip: Use [cyan]--ignore-agent-tools[/cyan] to skip this check",
                    title="[red]Agent Detection Error[/red]",
                    border_style="red",
                    padding=(1, 2),
                )
                console.print()
                console.print(error_panel)
                raise typer.Exit(1)

    if script_type:
        if script_type not in SCRIPT_TYPE_CHOICES:
            console.print(
                f"[red]Error:[/red] Invalid script type '{script_type}'. Choose from: {', '.join(SCRIPT_TYPE_CHOICES.keys())}"
            )
            raise typer.Exit(1)
        selected_script = script_type
    else:
        default_script = "ps" if os.name == "nt" else "sh"

        if sys.stdin.isatty():
            selected_script = select_with_arrows(
                SCRIPT_TYPE_CHOICES,
                "Choose script type (or press Enter)",
                default_script,
            )
        else:
            selected_script = default_script

    console.print(f"[cyan]Selected AI assistant:[/cyan] {selected_ai}")
    console.print(f"[cyan]Selected script type:[/cyan] {selected_script}")

    tracker = StepTracker("Initialize x100 Project")

    sys._x100_tracker_active = True

    tracker.add("precheck", "Check required tools")
    tracker.complete("precheck", "ok")
    tracker.add("ai-select", "Select AI assistant")
    tracker.complete("ai-select", f"{selected_ai}")
    tracker.add("script-select", "Select script type")
    tracker.complete("script-select", selected_script)
    for key, label in [
        ("fetch", "Fetch latest release"),
        ("download", "Download template"),
        ("extract", "Extract template"),
        ("zip-list", "Archive contents"),
        ("extracted-summary", "Extraction summary"),
        ("issue-templates", "Copy GitHub issue templates"),
        ("chmod", "Ensure scripts executable"),
        ("cleanup", "Cleanup"),
        ("git", "Initialize git repository"),
        ("final", "Finalize"),
    ]:
        tracker.add(key, label)

    # Track git error message outside Live context so it persists
    git_error_message = None

    with Live(
        tracker.render(), console=console, refresh_per_second=8, transient=True
    ) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))
        try:
            verify = not skip_tls
            local_ssl_context = ssl_context if verify else False
            local_client = httpx.Client(verify=local_ssl_context)

            download_and_extract_template(
                project_path,
                selected_ai,
                selected_script,
                here,
                verbose=False,
                tracker=tracker,
                client=local_client,
                debug=debug,
                github_token=github_token,
            )

            copy_issue_templates(project_path, tracker=tracker)
            ensure_executable_scripts(project_path, tracker=tracker)

            if not no_git:
                tracker.start("git")
                if is_git_repo(project_path):
                    tracker.complete("git", "existing repo detected")
                elif should_init_git:
                    success, error_msg = init_git_repo(project_path, quiet=True)
                    if success:
                        tracker.complete("git", "initialized")
                    else:
                        tracker.error("git", "init failed")
                        git_error_message = error_msg
                else:
                    tracker.skip("git", "git not available")
            else:
                tracker.skip("git", "--no-git flag")

            # Save default AI agent to config
            config_path = project_path / ".x100" / "config.json"
            config = {}
            if config_path.exists():
                try:
                    config = json.loads(config_path.read_text(encoding="utf-8"))
                except Exception:
                    pass

            config["default_agent"] = selected_ai
            save_config(config, config_path)

            tracker.complete("final", "project ready")
        except Exception as e:
            tracker.error("final", str(e))
            console.print(
                Panel(
                    f"Initialization failed: {e}", title="Failure", border_style="red"
                )
            )
            if debug:
                _env_pairs = [
                    ("Python", sys.version.split()[0]),
                    ("Platform", sys.platform),
                    ("CWD", str(Path.cwd())),
                ]
                _label_width = max(len(k) for k, _ in _env_pairs)
                env_lines = [
                    f"{k.ljust(_label_width)} → [bright_black]{v}[/bright_black]"
                    for k, v in _env_pairs
                ]
                console.print(
                    Panel(
                        "\n".join(env_lines),
                        title="Debug Environment",
                        border_style="magenta",
                    )
                )
            if not here and project_path.exists():
                shutil.rmtree(project_path)
            raise typer.Exit(1)
        finally:
            pass

    console.print(tracker.render())
    console.print("\n[bold green]Project ready.[/bold green]")

    # Show git error details if initialization failed
    if git_error_message:
        console.print()
        git_error_panel = Panel(
            f"[yellow]Warning:[/yellow] Git repository initialization failed\n\n"
            f"{git_error_message}\n\n"
            f"[dim]You can initialize git manually later with:[/dim]\n"
            f"[cyan]cd {project_path if not here else '.'}[/cyan]\n"
            f"[cyan]git init[/cyan]\n"
            f"[cyan]git add .[/cyan]\n"
            f'[cyan]git commit -m "Initial commit"[/cyan]',
            title="[red]Git Initialization Failed[/red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(git_error_panel)

    # Agent folder security notice
    agent_config = AGENT_CONFIG.get(selected_ai)
    if agent_config:
        agent_folder = agent_config["folder"]
        security_notice = Panel(
            f"Some agents may store credentials, auth tokens, or other identifying and private artifacts in the agent folder within your project.\n"
            f"Consider adding [cyan]{agent_folder}[/cyan] (or parts of it) to [cyan].gitignore[/cyan] to prevent accidental credential leakage.",
            title="[yellow]Agent Folder Security[/yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
        console.print()
        console.print(security_notice)

    steps_lines = []
    if not here:
        steps_lines.append(
            f"1. Go to the project folder: [cyan]cd {project_name}[/cyan]"
        )
        step_num = 2
    else:
        steps_lines.append("1. You're already in the project directory!")
        step_num = 2

    # Add Codex-specific setup step if needed
    if selected_ai == "codex":
        codex_path = project_path / ".codex"
        quoted_path = shlex.quote(str(codex_path))
        if os.name == "nt":  # Windows
            cmd = f"setx CODEX_HOME {quoted_path}"
        else:  # Unix-like systems
            cmd = f"export CODEX_HOME={quoted_path}"

        steps_lines.append(
            f"{step_num}. Set [cyan]CODEX_HOME[/cyan] environment variable before running Codex: [cyan]{cmd}[/cyan]"
        )
        step_num += 1

    steps_lines.append(f"{step_num}. Start using slash commands with your AI agent:")

    steps_lines.append(
        "   2.1 [cyan]/x100.constitution[/] - Establish project principles"
    )
    steps_lines.append("   2.2 [cyan]/x100.specify[/] - Create baseline specification")
    steps_lines.append("   2.3 [cyan]/x100.plan[/] - Create implementation plan")
    steps_lines.append("   2.4 [cyan]/x100.tasks[/] - Generate actionable tasks")
    steps_lines.append("   2.5 [cyan]/x100.implement[/] - Execute implementation")

    steps_panel = Panel(
        "\n".join(steps_lines), title="Next Steps", border_style="cyan", padding=(1, 2)
    )
    console.print()
    console.print(steps_panel)

    enhancement_lines = [
        "Optional commands that you can use for your specs [bright_black](improve quality & confidence)[/bright_black]",
        "",
        "○ [cyan]/x100.clarify[/] [bright_black](optional)[/bright_black] - Ask structured questions to de-risk ambiguous areas before planning (run before [cyan]/x100.plan[/] if used)",
        "○ [cyan]/x100.analyze[/] [bright_black](optional)[/bright_black] - Cross-artifact consistency & alignment report (after [cyan]/x100.tasks[/], before [cyan]/x100.implement[/])",
        "○ [cyan]/x100.checklist[/] [bright_black](optional)[/bright_black] - Generate quality checklists to validate requirements completeness, clarity, and consistency (after [cyan]/x100.plan[/])",
    ]
    enhancements_panel = Panel(
        "\n".join(enhancement_lines),
        title="Enhancement Commands",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print()
    console.print(enhancements_panel)


def check_gh_scopes(*, tracker: StepTracker | None = None) -> bool:
    """Check that gh CLI has required scopes."""
    required_scopes = {"repo", "read:org", "workflow"}
    try:
        result = subprocess.run(
            ["gh", "auth", "status", "--show-token"],
            capture_output=True,
            text=True,
            check=True,
        )
        token_line = next(
            (line for line in result.stdout.splitlines() if "- Token:" in line),
            None,
        )
        if token_line is None:
            raise RuntimeError("Could not find token line in gh auth status output")

        token = token_line.split(":", 1)[1].strip()

        # Check scopes via GitHub API
        api_url = "https://api.github.com/"
        headers = {"Authorization": f"token {token}"}
        response = httpx.head(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        scopes_header = response.headers.get("X-OAuth-Scopes", "")
        granted_scopes = {scope.strip() for scope in scopes_header.split(",") if scope}

        missing_scopes = required_scopes - granted_scopes
        if missing_scopes:
            if tracker:
                tracker.error(
                    "gh",
                    f"missing scopes: {', '.join(sorted(missing_scopes))} - run `gh auth refresh -s <missing_scopes>` to add",
                )
            return False
        else:
            if tracker:
                tracker.complete("gh", "all required scopes present")
            return True
    except Exception as e:
        if tracker:
            tracker.error("gh", str(e))
        return False


@app.command()
def check():
    """Check that all required tools are installed."""

    tracker = StepTracker("Checklist")

    # Check if is a x100 project
    tracker.add("x100", "Is x100 project initialized?")
    if is_x100_project(Path.cwd()):
        tracker.complete("x100", "yes")
    else:
        tracker.error("x100", "no - run `x100 init` to initialize the project")

    # Check git availability
    tracker.add("git", "Git version control")
    git_ok = check_tool("git", tracker=tracker)

    # Check gh availability
    tracker.add("gh", "GitHub CLI")
    gh_ok = check_tool("gh", tracker=tracker)

    if gh_ok:
        check_gh_scopes(tracker=tracker)

    agent_results = {}
    for agent_key, agent_config in X100_CONFIG.get("agents", {}).items():
        agent_name = agent_config["name"]
        requires_cli = agent_config["requires_cli"]

        tracker.add(agent_key, agent_name)

        if requires_cli:
            agent_results[agent_key] = check_tool(agent_key, tracker=tracker)
        else:
            # IDE-based agent - skip CLI check and mark as optional
            tracker.skip(agent_key, "IDE-based, no CLI check")
            agent_results[agent_key] = False  # Don't count IDE agents as "found"

    # Check VS Code variants (not in agent config)
    tracker.add("code", "Visual Studio Code")
    check_tool("code", tracker=tracker)

    # Check README.md presence
    tracker.add("readme", "Presence of README.md")
    check_file("readme", Path.cwd() / "README.md", tracker=tracker)

    # Check AGENTS.md presence
    tracker.add("agents_md", "Presence of AGENTS.md")
    check_file("agents_md", Path.cwd() / "AGENTS.md", tracker=tracker)

    # Check LICENSE presence
    tracker.add("license", "Presence of LICENSE")
    if not check_file("license", Path.cwd() / "LICENSE", tracker=tracker):
        check_file("license", Path.cwd() / ".github" / "LICENSE", tracker=tracker)

    # Check CONTRIBUTING.md presence
    tracker.add("contributing", "Presence of CONTRIBUTING.md")
    if not check_file("contributing", Path.cwd() / "CONTRIBUTING.md", tracker=tracker):
        check_file(
            "contributing", Path.cwd() / ".github" / "CONTRIBUTING.md", tracker=tracker
        )

    # Check CODE_OF_CONDUCT.md presence
    tracker.add("code_of_conduct", "Presence of CODE_OF_CONDUCT.md")
    if not check_file(
        "code_of_conduct", Path.cwd() / "CODE_OF_CONDUCT.md", tracker=tracker
    ):
        check_file(
            "code_of_conduct",
            Path.cwd() / ".github" / "CODE_OF_CONDUCT.md",
            tracker=tracker,
        )

    console.print(tracker.render())

    # Show tips
    if not git_ok:
        console.print("[dim]Tip: Install git for repository management[/dim]")

    if not any(agent_results.values()):
        console.print("[dim]Tip: Install an AI assistant for the best experience[/dim]")


# @app.command(hidden=True)
# def legacy_check():
#     """Check that all required tools are installed."""
#     # console.print("[bold]Checking for installed tools...[/bold]\n")

#     tracker = StepTracker("Check Available Tools")

#     tracker.add("git", "Git version control")
#     git_ok = check_tool("git", tracker=tracker)

#     agent_results = {}
#     for agent_key, agent_config in AGENT_CONFIG.items():
#         agent_name = agent_config["name"]
#         requires_cli = agent_config["requires_cli"]

#         tracker.add(agent_key, agent_name)

#         if requires_cli:
#             agent_results[agent_key] = check_tool(agent_key, tracker=tracker)
#         else:
#             # IDE-based agent - skip CLI check and mark as optional
#             tracker.skip(agent_key, "IDE-based, no CLI check")
#             agent_results[agent_key] = False  # Don't count IDE agents as "found"

#     # Check VS Code variants (not in agent config)
#     tracker.add("code", "Visual Studio Code")
#     code_ok = check_tool("code", tracker=tracker)

#     tracker.add("code-insiders", "Visual Studio Code Insiders")
#     code_insiders_ok = check_tool("code-insiders", tracker=tracker)

#     console.print(tracker.render())

#     console.print("\n[bold green]x100 CLI is ready to use![/bold green]")

#     if not git_ok:
#         console.print("[dim]Tip: Install git for repository management[/dim]")

#     if not any(agent_results.values()):
#         console.print("[dim]Tip: Install an AI assistant for the best experience[/dim]")


@app.command()
def status():
    """Display the status of the current x100 project."""
    show_banner()
    project_path = Path.cwd()
    if not is_x100_project(project_path):
        console.print(
            f"[red]Error:[/red] Current directory is not recognized as a x100 project ({project_path})"
        )
        raise typer.Exit(1)

    console.print(f"[bold]x100 Project Status:[/bold] {project_path}\n")

    status_tree = Tree("Project Status", guide_style="cyan")

    git_node = status_tree.add("Git Repository")
    if is_git_repo(project_path):
        git_node.add("[green]Initialized[/green]")
    else:
        git_node.add("[red]Not initialized[/red]")

    # agent_node = status_tree.add("AI Assistant Tools")
    # for agent_key, agent_config in AGENT_CONFIG.items():
    #     agent_name = agent_config["name"]
    #     requires_cli = agent_config["requires_cli"]
    #     if requires_cli:
    #         if check_tool(agent_key):
    #             agent_node.add(f"[green]{agent_name} detected[/green]")
    #         else:
    #             agent_node.add(f"[red]{agent_name} not found[/red]")
    #     else:
    #         agent_node.add(f"[dim]{agent_name} (IDE-based, no CLI check)[/dim]")

    console.print(status_tree)
    console.print("\n[bold green]Status check complete.[/bold green]")


@app.command()
def update():
    show_banner()

    return


@app.command()
def convert(
    ctx: typer.Context,
    subcommand: str = typer.Argument(..., help="Conversion type: issue"),
    path: str = typer.Argument(..., help="Path to user story file or directory"),
    agent: str = typer.Option(
        None,
        "--agent",
        "-a",
        help="AI agent to use for conversion (default: project's default agent)",
    ),
):
    """
    Convert user stories to GitHub issues.

    This command converts user story markdown files to GitHub issues using AI.
    Only files matching the pattern US-[number]-[slug].md will be converted.

    Examples:
        x100 convert issue docs/user_stories/US-001-news-ingestion.md
        x100 convert issue docs/user_stories
        x100 convert issue docs/user_stories --agent claude
    """
    from .convert import IssueConverter

    if subcommand != "issue":
        console.print(
            f"[red]Error:[/red] Unknown conversion type '{subcommand}'. Use 'issue'."
        )
        raise typer.Exit(1)

    # Check if in x100 project
    if not is_x100_project(Path.cwd()):
        console.print(
            "[red]Error:[/red] Not in an x100 project directory. "
            "Run this command from a project initialized with 'x100 init'."
        )
        raise typer.Exit(1)

    # Check if gh CLI is available
    if not check_tool("gh"):
        console.print(
            "[red]Error:[/red] GitHub CLI (gh) is required but not found.\n"
            "Install from: https://cli.github.com/"
        )
        raise typer.Exit(1)

    # Load project config
    config = load_config()
    project_config = config.get("project", {})

    # Check if it's a GitHub project
    repo = None
    project_id = None

    if project_config.get("type") == "github_project":
        project_url = project_config.get("url")
        project_id = project_config.get("id")

        if project_url:
            # Extract repo from project URL (format: https://github.com/orgs/ORG/projects/NUM or https://github.com/users/USER/projects/NUM)
            # For now, we'll need the repo to be configured separately or detected from git
            pass

    # Try to detect repo from git remote
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_data = json.loads(result.stdout)
        repo = repo_data.get("nameWithOwner")
    except Exception:
        console.print(
            "[yellow]Warning:[/yellow] Could not detect GitHub repository from current directory.\n"
            "Issues will be created in the current repository context."
        )

    # Validate path
    target_path = Path(path).resolve()
    if not target_path.exists():
        console.print(f"[red]Error:[/red] Path not found: {path}")
        raise typer.Exit(1)

    # Create .x100/logs directory if it doesn't exist
    log_dir = Path.cwd() / ".x100" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create converter and run conversion
    try:
        converter = IssueConverter(agent_name=agent, log_dir=log_dir)

        console.print(f"[cyan]Using AI agent:[/cyan] {converter.agent_config['name']}")
        if repo:
            console.print(f"[cyan]Target repository:[/cyan] {repo}")
        if project_id:
            console.print(f"[cyan]Linking to project:[/cyan] #{project_id}")
        console.print(f"[cyan]Logs:[/cyan] {log_dir / 'convert.log'}")
        console.print()

        results = converter.convert_and_create(
            target_path, repo=repo, project_id=project_id
        )

        # Display results
        IssueConverter.display_results(results)

        # Prompt for cleanup
        IssueConverter.prompt_cleanup(results)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def version():
    """Display version and system information."""
    import platform
    import importlib.metadata

    # Get CLI version from package metadata
    cli_version = "unknown"
    try:
        cli_version = importlib.metadata.version("x100-cli")
    except Exception:
        # Fallback: try reading from pyproject.toml if running from source
        try:
            import tomllib

            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    cli_version = data.get("project", {}).get("version", "unknown")
        except Exception:
            pass

    # Fetch latest template release version
    repo_owner = "minhdqdev"
    repo_name = "x100-cli"
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    template_version = "unknown"
    release_date = "unknown"

    try:
        response = client.get(
            api_url,
            timeout=10,
            follow_redirects=True,
            headers=_github_auth_headers(),
        )
        if response.status_code == 200:
            release_data = response.json()
            template_version = release_data.get("tag_name", "unknown")
            # Remove 'v' prefix if present
            if template_version.startswith("v"):
                template_version = template_version[1:]
            release_date = release_data.get("published_at", "unknown")
            if release_date != "unknown":
                # Format the date nicely
                try:
                    dt = datetime.fromisoformat(release_date.replace("Z", "+00:00"))
                    release_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    pass
    except Exception:
        pass

    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="orange3", justify="right")
    info_table.add_column("Value", style="white")

    info_table.add_row("CLI Version", cli_version)
    info_table.add_row("Template Version", template_version)
    info_table.add_row("Released", release_date)
    info_table.add_row("", "")
    info_table.add_row("Python", platform.python_version())
    info_table.add_row("Platform", platform.system())
    info_table.add_row("Architecture", platform.machine())
    info_table.add_row("OS Version", platform.version())

    panel = Panel(
        info_table,
        title="[bold orange3]x100 CLI Information[/bold orange3]",
        border_style="orange3",
        padding=(1, 2),
    )

    console.print(panel)
    console.print()


@app.command(hidden=True)
def initialize(ctx: typer.Context):
    """Alias for 'init' command."""
    raise typer.Exit(ctx.invoke(init))


@app.command(name="initialize-project", hidden=True)
def initialize_project(ctx: typer.Context):
    """Alias for 'init' command."""
    raise typer.Exit(ctx.invoke(init))


@app.command(name="nextstep-setup")
def nextstep_setup(
    ctx: typer.Context,
    github_repo: str = typer.Option(
        None,
        "--github-repo",
        help="GitHub repository (owner/repo)",
        prompt="GitHub repository (owner/repo, or press Enter to skip)",
    ),
    coverage_threshold: int = typer.Option(
        80,
        "--coverage-threshold",
        help="Target test coverage percentage",
        prompt="Target test coverage (%)",
    ),
):
    """
    Configure nextstep settings.

    Creates a configuration file at .x100/nextstep.json with your preferences.
    """
    from .nextstep.config import (
        NextStepConfig,
        AnalysisConfig,
        GitHubConfig,
        save_config,
    )

    show_banner()

    console.print("[cyan]Setting up nextstep configuration...[/cyan]\n")

    # Create configuration
    config = NextStepConfig()
    config.analysis.coverage_threshold = coverage_threshold

    if github_repo and github_repo.strip():
        config.github.enabled = True
        config.github.repo = github_repo.strip()
        console.print(f"[green]✓[/green] GitHub integration enabled for {github_repo}")
    else:
        console.print(
            "[yellow]○[/yellow] GitHub integration disabled (can enable later)"
        )

    # Save configuration
    config_path = Path.cwd() / ".x100" / "nextstep.json"
    save_config(config, config_path)

    console.print(f"\n[green]✓ Configuration saved to:[/green] {config_path}")
    console.print(
        "\n[dim]You can now run 'x100 nextstep' to analyze your project.[/dim]"
    )

    # Show configuration
    console.print("\n[cyan]Configuration:[/cyan]")
    console.print(f"  • Coverage threshold: {config.analysis.coverage_threshold}%")
    console.print(f"  • GitHub repo: {config.github.repo or 'Not configured'}")
    console.print(f"  • GitHub enabled: {config.github.enabled}")


@app.command()
def nextstep(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed analysis",
    ),
    format: str = typer.Option(
        "rich",
        "--format",
        "-f",
        help="Output format: rich, json, markdown",
    ),
    save: bool = typer.Option(
        False,
        "--save",
        "-s",
        help="Save report to file",
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: nextstep_report_TIMESTAMP.ext)",
    ),
    github_token: str = typer.Option(
        None,
        "--github-token",
        help="GitHub token (or set GITHUB_TOKEN env var)",
    ),
    github_repo: str = typer.Option(
        None,
        "--github-repo",
        help="GitHub repository (owner/repo)",
    ),
    config_file: str = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file path (default: .x100/nextstep.json)",
    ),
    use_ai: bool = typer.Option(
        True,
        "--use-ai/--no-ai",
        help="Use AI CLI for enhanced analysis (default: true)",
    ),
    show_ai_insights: bool = typer.Option(
        False,
        "--show-ai-insights",
        help="Show raw AI analysis output",
    ),
):
    """
    Analyze project health and suggest next steps.

    This command acts as an AI Project Manager/Tech Lead to:
    - Analyze codebase health and progress
    - Check git activity and velocity
    - Identify blockers, gaps, and risks
    - Recommend prioritized next steps

    Examples:
        x100 nextstep
        x100 nextstep --verbose
        x100 nextstep --format json
        x100 nextstep --github-repo owner/repo --github-token $GITHUB_TOKEN
        x100 nextstep --show-ai-insights  # Show AI's analysis
        x100 nextstep --no-ai  # Use only rule-based analysis
    """
    from .nextstep import (
        CodeAnalyzer,
        GitAnalyzer,
        TestAnalyzer,
        NextStepAgent,
    )
    from .nextstep.integrations import GitHubIntegration
    from .nextstep.config import load_config
    from .nextstep.formatters import MarkdownFormatter, JSONFormatter, save_report

    show_banner()

    # Load project default agent from main config
    project_config_path = Path.cwd() / ".x100" / "config.json"
    default_agent = "claude"  # fallback
    if project_config_path.exists():
        try:
            project_config = json.loads(project_config_path.read_text(encoding="utf-8"))
            default_agent = project_config.get("default_agent", "claude")
        except Exception:
            pass

    # Load nextstep configuration
    config_path = Path(config_file) if config_file else None
    config = load_config(config_path)

    # Use project's default agent if not explicitly set in nextstep config
    if config.default_ai_agent == "claude":  # if still using hardcoded default
        config.default_ai_agent = default_agent

    # Override config with command-line options
    if github_repo:
        config.github.enabled = True
        config.github.repo = github_repo

    project_path = Path.cwd()

    console.print("[cyan]Analyzing project...[/cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # 1. Code analysis
        task = progress.add_task("📊 Analyzing codebase...", total=None)
        code_analyzer = CodeAnalyzer(project_path)
        code_analysis = code_analyzer.analyze()
        progress.remove_task(task)

        # 2. Git analysis
        task = progress.add_task("📝 Analyzing git history...", total=None)
        git_analyzer = GitAnalyzer(project_path)
        git_analysis = git_analyzer.analyze()
        progress.remove_task(task)

        # 3. Test analysis
        task = progress.add_task("🧪 Analyzing tests...", total=None)
        test_analyzer = TestAnalyzer(project_path)
        test_analysis = test_analyzer.analyze()
        progress.remove_task(task)

        # 3a. Story analysis
        task = progress.add_task("📖 Analyzing user stories...", total=None)
        from .nextstep.analyzers.stories import StoryAnalyzer

        story_analyzer = StoryAnalyzer(project_path)
        story_statuses = story_analyzer.analyze()
        progress.remove_task(task)

        # 3b. Documentation analysis
        task = progress.add_task("📚 Analyzing documentation...", total=None)
        from .nextstep.analyzers.docs import DocsAnalyzer

        docs_analyzer = DocsAnalyzer(project_path)
        doc_status = docs_analyzer.analyze()
        progress.remove_task(task)

        # 4. GitHub integration (optional)
        project_status = None
        if config.github.enabled and config.github.repo:
            task = progress.add_task("📋 Fetching GitHub status...", total=None)
            token = github_token or os.getenv(config.github.token_env)
            if token:
                try:
                    github_integration = GitHubIntegration(token, config.github.repo)
                    project_status = github_integration.get_project_status()
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: GitHub integration failed: {e}[/yellow]"
                    )
            else:
                console.print(
                    f"[yellow]Warning: GitHub token not found (set {config.github.token_env})[/yellow]"
                )
            progress.remove_task(task)

        # 5. AI analysis
        task_label = (
            "🤖 Generating recommendations..."
            if use_ai
            else "📊 Analyzing (rule-based)..."
        )
        task = progress.add_task(task_label, total=None)
        agent = NextStepAgent(agent_name=config.default_ai_agent, use_ai=use_ai)
        recommendations = agent.analyze_and_recommend(
            code_analysis,
            git_analysis,
            test_analysis,
            project_status,
            story_statuses,
            doc_status,
        )
        progress.remove_task(task)

    console.print()

    # Display results based on format
    report_content = None

    if format == "json":
        formatter = JSONFormatter()
        report_content = formatter.format(
            recommendations,
            code_analysis,
            git_analysis,
            test_analysis,
            verbose,
        )
        if not save:
            console.print_json(data=report_content)

    elif format == "markdown":
        formatter = MarkdownFormatter()
        report_content = formatter.format(
            recommendations,
            code_analysis,
            git_analysis,
            test_analysis,
            verbose,
        )
        if not save:
            from rich.markdown import Markdown

            console.print(Markdown(report_content))

    else:  # rich
        _display_nextstep_report(
            recommendations,
            code_analysis,
            git_analysis,
            test_analysis,
            verbose,
            github_repo or (config.github.repo if config.github.enabled else None),
            config.default_ai_agent,
            agent.ai_response if show_ai_insights else None,
        )

    # Save report if requested
    if save:
        output_path = Path(output) if output else None
        saved_path = save_report(report_content or "", format, output_path)
        console.print(f"\n[green]✓ Report saved to:[/green] {saved_path}")


def _display_nextstep_report(
    recommendations,
    code_analysis,
    git_analysis,
    test_analysis,
    verbose,
    github_repo=None,
    agent_name=None,
    ai_response=None,
):
    """Display formatted nextstep report."""
    from rich.text import Text

    # Show which agent is being used
    if agent_name:
        agent_display = AGENT_CONFIG.get(agent_name, {}).get("name", agent_name)
        console.print(f"[dim]Analysis by:[/dim] [cyan]{agent_display}[/cyan]\n")

    # Show AI insights if available and requested
    if ai_response:
        from rich.markdown import Markdown

        console.print()
        console.print(
            Panel(
                (
                    Markdown(ai_response)
                    if not ai_response.startswith("Error:")
                    else ai_response
                ),
                title="🤖 AI Insights",
                border_style=(
                    "cyan" if not ai_response.startswith("Error:") else "yellow"
                ),
            )
        )
        console.print()

    # Health Score
    health = recommendations.health_score

    if health.overall >= 80:
        score_color = "green"
        emoji = "🎉"
    elif health.overall >= 70:
        score_color = "cyan"
        emoji = "✅"
    elif health.overall >= 60:
        score_color = "yellow"
        emoji = "⚠️"
    else:
        score_color = "red"
        emoji = "🔴"

    health_panel = Panel(
        f"[bold {score_color}]{health.overall}/100[/bold {score_color}] - {health.summary}\n\n"
        f"  • Velocity: {health.velocity_score}/100\n"
        f"  • Quality: {health.quality_score}/100\n"
        f"  • Blockers: {health.blocker_score}/100\n"
        f"  • Activity: {health.activity_score}/100",
        title=f"{emoji} Project Health",
        border_style=score_color,
    )
    console.print(health_panel)
    console.print()

    # Detailed stats if verbose
    if verbose:
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")

        stats_table.add_row("Files", str(code_analysis.file_count))
        stats_table.add_row("Lines of Code", f"{code_analysis.line_count:,}")
        stats_table.add_row("Python Files", str(code_analysis.python_files))
        stats_table.add_row("JavaScript Files", str(code_analysis.javascript_files))
        stats_table.add_row("TODO Markers", str(len(code_analysis.todos)))
        stats_table.add_row("FIXME Markers", str(len(code_analysis.fixmes)))

        if test_analysis.coverage_percentage:
            stats_table.add_row(
                "Test Coverage", f"{test_analysis.coverage_percentage}%"
            )
        stats_table.add_row("Test Files", str(test_analysis.test_count))

        if git_analysis.is_git_repo:
            stats_table.add_row("Commits (7d)", str(git_analysis.commit_count_7d))
            stats_table.add_row("Commits (30d)", str(git_analysis.commit_count_30d))
            stats_table.add_row("Commits/Day", str(git_analysis.commits_per_day))

        stats_panel = Panel(
            stats_table, title="📊 Detailed Statistics", border_style="cyan"
        )
        console.print(stats_panel)
        console.print()

    # Blockers
    if recommendations.blockers:
        console.print("[bold red]🔴 Blockers & Risks[/bold red]\n")
        for blocker in recommendations.blockers:
            console.print(f"  • [red]{blocker.title}[/red]")
            console.print(f"    [dim]Impact: {blocker.impact}[/dim]")
            if verbose and blocker.details:
                console.print(f"    [dim]{blocker.details}[/dim]")
        console.print()

    # Gaps
    if recommendations.gaps:
        console.print("[bold yellow]🔍 Gaps Detected[/bold yellow]\n")
        for gap in recommendations.gaps:
            severity_color = "red" if gap.severity == "high" else "yellow"
            console.print(
                f"  ⚠  [{severity_color}]{gap.category}:[/{severity_color}] {gap.description}"
            )
        console.print()

    # Next Steps
    if recommendations.next_steps:
        console.print("[bold cyan]💡 Recommended Next Steps[/bold cyan]\n")

        # Group by priority
        priorities = ["NOW", "This Week", "Next Sprint"]
        for priority in priorities:
            steps = [s for s in recommendations.next_steps if s.priority == priority]
            if steps:
                if priority == "NOW":
                    priority_emoji = "🎯"
                    priority_color = "red"
                elif priority == "This Week":
                    priority_emoji = "🔄"
                    priority_color = "yellow"
                else:
                    priority_emoji = "📅"
                    priority_color = "cyan"

                console.print(
                    f"[bold {priority_color}]{priority_emoji} {priority}:[/bold {priority_color}]"
                )
                for step in steps:
                    console.print(f"\n  {step.order}. [cyan]{step.action}[/cyan]")
                    console.print(f"     • Rationale: {step.rationale}")
                    console.print(f"     • Impact: {step.impact}")
                    console.print(f"     • Effort: {step.effort}")
                console.print()

    # Footer
    if not github_repo and not verbose:
        console.print("[dim]Tip: Run with --verbose for detailed statistics[/dim]")
        console.print(
            "[dim]Tip: Add --github-repo owner/repo --github-token $GITHUB_TOKEN for GitHub integration[/dim]"
        )


def main():
    """Entry point for the x100 CLI application."""
    app()


if __name__ == "__main__":
    main()
