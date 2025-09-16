import argparse
import json
import os
import shutil
import subprocess
import sys
from typing import Callable, List

TITLE = """
/====================================================\\
||                                                  ||
||     █████ █████ ████     █████       █████       ||
||    ░░███ ░░███ ░░███   ███░░░███   ███░░░███     ||
||     ░░███ ███   ░███  ███   ░░███ ███   ░░███    ||
||      ░░█████    ░███ ░███    ░███░███    ░███    ||
||       ███░███   ░███ ░███    ░███░███    ░███    ||
||      ███ ░░███  ░███ ░░███   ███ ░░███   ███     ||
||     █████ █████ █████ ░░░█████░   ░░░█████░      ||
||    ░░░░░ ░░░░░ ░░░░░    ░░░░░░      ░░░░░░       ||
||                                                  ||
\\====================================================/"""


# Paths
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
TOOL_ROOT = os.path.dirname(CURRENT_DIR)  # points to .x100
OUTER_DIR = os.path.dirname(TOOL_ROOT)


# --- Cross-platform single-key reader with arrow key support ---
if os.name == "nt":
    import msvcrt  # type: ignore

    def read_key() -> str:
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):
            ch2 = msvcrt.getch()
            mapping = {b"H": "UP", b"P": "DOWN", b"K": "LEFT", b"M": "RIGHT"}
            return mapping.get(ch2, "")
        if ch == b"\r":
            return "ENTER"
        if ch == b"\x1b":
            return "ESC"
        return ch.decode(errors="ignore")

else:
    import termios
    import tty

    def read_key() -> str:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":  # Escape sequence
                seq = sys.stdin.read(2)
                if seq == "[A":
                    return "UP"
                if seq == "[B":
                    return "DOWN"
                if seq == "[C":
                    return "RIGHT"
                if seq == "[D":
                    return "LEFT"
                return "ESC"
            if ch in ("\r", "\n"):
                return "ENTER"
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# --- UI helpers ---
RESET = "\x1b[0m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"
REVERSE = "\x1b[7m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
RED = "\x1b[31m"


def clear_screen() -> None:
    try:
        if os.name == "nt":
            os.system("cls")
        else:
            # Clear screen + scrollback, then move cursor home (macOS/iTerm compatible)
            sys.stdout.write("\x1b[2J\x1b[3J\x1b[H")
            sys.stdout.flush()
    except Exception:
        # Fallback to shell clear
        try:
            os.system("cls" if os.name == "nt" else "clear")
        except Exception:
            # Last resort: push old content offscreen
            sys.stdout.write("\n" * 100)
            sys.stdout.flush()


def prompt_yes_no(question: str, default: bool = False) -> bool:
    hint = "Y/n" if default else "y/N"
    sys.stdout.write(f"{question} [{hint}]: ")
    sys.stdout.flush()
    try:
        choice = input("").strip().lower()
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        return False
    if not choice:
        return default
    return choice in ("y", "yes")


def prompt_text(question: str, default: str = "", validator: Callable[[str], bool] | None = None) -> str:
    while True:
        hint = f" [{default}]" if default else ""
        sys.stdout.write(f"{question}{hint}: ")
        sys.stdout.flush()
        try:
            val = input("")
        except KeyboardInterrupt:
            sys.stdout.write("\n")
            return default
        val = val.strip() or default
        if validator is None or validator(val):
            return val
        print(f"{YELLOW}Invalid value. Please try again.{RESET}")


def prompt_choice(question: str, options: List[str], default_index: int | None = None) -> int:
    # Backwards compatible wrapper over interactive_select
    idx = interactive_select(question, options, default_index or 0)
    if idx is None:
        return default_index or 0
    return idx


def render_menu(items: List[str], selected: int) -> None:
    clear_screen()
    print(TITLE)
    print()
    print(f"{BOLD}Use ↑/↓ to navigate, Enter or number to select.{RESET}")
    print()
    for idx, label in enumerate(items):
        prefix = f" {idx+1}. "
        if idx == selected:
            print(f"{REVERSE}{prefix}{label}{RESET}")
        else:
            print(f"{prefix}{label}")
    print()
    print(f"{DIM}Press ESC or Ctrl+C to exit.{RESET}")


def render_submenu(title: str, items: List[str], selected: int) -> None:
    clear_screen()
    print(TITLE)
    print()
    print(f"{BOLD}{title}{RESET}")
    print(f"{DIM}Use ↑/↓ to navigate, Enter or number to select. ESC to cancel.{RESET}")
    print()
    for idx, label in enumerate(items):
        prefix = f" {idx+1}. "
        if idx == selected:
            print(f"{REVERSE}{prefix}{label}{RESET}")
        else:
            print(f"{prefix}{label}")


def interactive_select(title: str, options: List[str], default_index: int = 0) -> int | None:
    if not options:
        return None
    selected = max(0, min(default_index, len(options) - 1))
    while True:
        render_submenu(title, options, selected)
        try:
            key = read_key()
        except KeyboardInterrupt:
            return None
        if key == "UP":
            selected = (selected - 1) % len(options)
        elif key == "DOWN":
            selected = (selected + 1) % len(options)
        elif key == "ENTER":
            return selected
        elif key in ("ESC", "q"):
            return None
        elif key.isdigit():
            idx = int(key) - 1
            if 0 <= idx < len(options):
                return idx


# --- Handlers ---
def setup_vscode() -> None:
    src = os.path.join(TOOL_ROOT, "resources", "vscode", "settings.example.json")
    target_dir = os.path.join(OUTER_DIR, ".vscode")
    target = os.path.join(target_dir, "settings.json")

    if not os.path.exists(src):
        print(f"{RED}Source not found:{RESET} {src}")
        input("Press Enter to return to menu…")
        return

    os.makedirs(target_dir, exist_ok=True)

    # Load source settings
    try:
        with open(src, "r", encoding="utf-8") as f:
            src_cfg = json.load(f)
        if not isinstance(src_cfg, dict):
            raise ValueError("Source settings must be a JSON object")
    except Exception as e:
        print(f"{RED}Error reading source settings:{RESET} {e}")
        input("Press Enter to return to menu…")
        return

    # If target doesn't exist, write source directly
    if not os.path.exists(target):
        with open(target, "w", encoding="utf-8") as f:
            json.dump(src_cfg, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"{GREEN}CREATED{RESET} {target}")
        input("Press Enter to return to menu…")
        return

    # Load existing target settings
    try:
        with open(target, "r", encoding="utf-8") as f:
            dst_cfg = json.load(f)
        if not isinstance(dst_cfg, dict):
            raise ValueError("Target settings must be a JSON object")
    except Exception as e:
        print(f"{YELLOW}Warning:{RESET} cannot parse existing settings: {e}")
        if prompt_yes_no("Replace with example settings?", default=False):
            with open(target, "w", encoding="utf-8") as f:
                json.dump(src_cfg, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"{GREEN}UPDATED{RESET} {target} (replaced)")
        else:
            print(f"{YELLOW}Skipped.{RESET} Existing settings preserved.")
        input("Press Enter to return to menu…")
        return

    # Merge with per-key prompts on conflicts
    merged = dict(dst_cfg)
    changes = 0
    for key, src_val in src_cfg.items():
        if key not in dst_cfg:
            merged[key] = src_val
            print(f"{GREEN}ADD{RESET} {key}")
            changes += 1
        else:
            dst_val = dst_cfg[key]
            if dst_val == src_val:
                # identical, no action
                continue
            else:
                # conflict: prompt per key
                print()
                print(f"{YELLOW}Conflict for key:{RESET} {BOLD}{key}{RESET}")
                print(f"  Existing: {dst_val}")
                print(f"  Example:  {src_val}")
                if prompt_yes_no("Overwrite with example value?", default=False):
                    merged[key] = src_val
                    print(f"{GREEN}SET{RESET} {key} -> example value")
                    changes += 1
                else:
                    print(f"{YELLOW}KEEP{RESET} {key} -> existing value")

    if changes:
        with open(target, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\n{GREEN}UPDATED{RESET} {target} ({changes} changes)")
    else:
        print(f"{GREEN}No changes needed.{RESET} {target} already up to date")

    input("Press Enter to return to menu…")


def setup_ai_agent() -> None:
    choices = [
        "Claude Code",
        "Gemini CLI",
        "OpenAI Codex",
        "Exit",
    ]
    idx = interactive_select("Setup AI Agent - Choose an option", choices, default_index=0)
    if idx is None:
        return
    if choices[idx] == "Claude Code":
        setup_claude_code()
    elif choices[idx] == "Gemini CLI":
        overwrite_agents_md("Gemini CLI")
    elif choices[idx] == "OpenAI Codex":
        overwrite_agents_md("OpenAI Codex")
    elif choices[idx] == "Exit":
        return
    else:
        print(f"{YELLOW}Not implemented yet:{RESET} {choices[idx]}")
        input("Press Enter to return to menu…")


def setup_claude_code() -> None:
    src_root = os.path.join(TOOL_ROOT, "resources", "claude")
    dst_root = os.path.join(OUTER_DIR, ".claude")

    # Warn about overwrite
    print(f"This will copy and overwrite contents in: {dst_root}")
    if not prompt_yes_no("Proceed?", default=False):
        print(f"{YELLOW}Cancelled by user.{RESET}")
        input("Press Enter to return to menu…")
        return

    os.makedirs(dst_root, exist_ok=True)

    # Paths to copy
    dir_items = ["agents", "commands"]
    file_items = ["settings.json", "statusline.sh"]

    # Copy directories
    for d in dir_items:
        src_d = os.path.join(src_root, d)
        dst_d = os.path.join(dst_root, d)
        if os.path.exists(dst_d):
            shutil.rmtree(dst_d, ignore_errors=True)
        if os.path.isdir(src_d):
            shutil.copytree(src_d, dst_d)
            print(f"{GREEN}COPIED{RESET} {d}/")
        else:
            print(f"{YELLOW}SKIP{RESET} Missing directory in resources: {src_d}")

    # Copy files
    for f in file_items:
        src_f = os.path.join(src_root, f)
        dst_f = os.path.join(dst_root, f)
        if os.path.exists(src_f):
            shutil.copy2(src_f, dst_f)
            # Make statusline.sh executable
            if f.endswith(".sh"):
                try:
                    mode = os.stat(dst_f).st_mode
                    os.chmod(dst_f, mode | 0o111)
                except Exception:
                    pass
            print(f"{GREEN}COPIED{RESET} {f}")
        else:
            print(f"{YELLOW}SKIP{RESET} Missing file in resources: {src_f}")

    print(f"\n{GREEN}Claude Code assets installed to{RESET} {dst_root}")
    input("Press Enter to return to menu…")


def overwrite_agents_md(provider: str) -> None:
    src = os.path.join(TOOL_ROOT, "resources", "AGENTS.example.md")
    dst = os.path.join(OUTER_DIR, "AGENTS.md")
    try:
        if not os.path.exists(src):
            print(f"{RED}Missing resource:{RESET} {src}")
        else:
            shutil.copyfile(src, dst)
            print(f"{GREEN}OVERWROTE{RESET} AGENTS.md using template for {provider}: {dst}")
    except Exception as e:
        print(f"{RED}ERROR{RESET} Overwriting AGENTS.md failed: {e}")
    input("Press Enter to return to menu…")


def verify() -> None:
    tool_dir = TOOL_ROOT
    outer_dir = OUTER_DIR

    print(f"{BOLD}Verification Results{RESET}\n")

    all_ok = True

    # 1) Check current dir name is .x100
    if os.path.basename(tool_dir) == ".x100":
        print(f"{GREEN}OK{RESET}    Current directory name is '.x100' -> {tool_dir}")
    else:
        all_ok = False
        print(
            f"{RED}FAIL{RESET}  Expected parent tool directory to be named '.x100' but got '"
            f"{os.path.basename(tool_dir)}' at {tool_dir}"
        )

    # 2) Check outer directory is a git repo (.git dir or file present)
    dotgit = os.path.join(outer_dir, ".git")
    if os.path.isdir(dotgit) or os.path.isfile(dotgit):
        print(f"{GREEN}OK{RESET}    Outer directory appears to be a git repo -> {outer_dir}")
    else:
        all_ok = False
        print(f"{RED}FAIL{RESET}  Outer directory is not a git repo -> {outer_dir}")

    # 3) Check required items in outer directory
    required_items = [
        ("dir", "submodules"),
        ("dir", "docs"),
        ("file", "README.md"),
        ("file", "AGENTS.md"),
    ]

    for kind, name in required_items:
        path = os.path.join(outer_dir, name)
        if kind == "dir":
            exists = os.path.isdir(path)
        else:
            exists = os.path.isfile(path)
        if exists:
            print(f"{GREEN}OK{RESET}    {name} -> {path}")
        else:
            all_ok = False
            print(f"{RED}MISS{RESET}  {name} (expected at {path})")

    print()
    if all_ok:
        print(f"{GREEN}All checks passed.{RESET}")
    else:
        print(f"{YELLOW}Some checks failed. Please review the output above.{RESET}")
    input("Press Enter to return to menu…")


def init_project(wait_for_key: bool = True) -> None:
    tool_dir = TOOL_ROOT
    outer_dir = OUTER_DIR
    resources_dir = os.path.join(TOOL_ROOT, "resources")

    print(f"{BOLD}Initializing Project Structure{RESET}\n")

    # Ensure directories
    for dname in ["submodules", "docs", "tests", "scripts"]:
        path = os.path.join(outer_dir, dname)
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
            print(f"{GREEN}CREATED{RESET} {path}")
        else:
            print(f"{GREEN}OK{RESET}      {path}")

    # Ensure README.md
    src_readme = os.path.join(resources_dir, "README.example.md")
    dst_readme = os.path.join(outer_dir, "README.md")
    if not os.path.exists(dst_readme):
        if os.path.exists(src_readme):
            shutil.copyfile(src_readme, dst_readme)
            print(f"{GREEN}CREATED{RESET} {dst_readme} from resources")
        else:
            print(f"{RED}MISSING{RESET} Resource not found: {src_readme}")
    else:
        print(f"{GREEN}OK{RESET}      README.md already exists -> {dst_readme}")

    # Ensure AGENTS.md
    src_agents = os.path.join(resources_dir, "AGENTS.example.md")
    dst_agents = os.path.join(outer_dir, "AGENTS.md")
    if not os.path.exists(dst_agents):
        if os.path.exists(src_agents):
            shutil.copyfile(src_agents, dst_agents)
            print(f"{GREEN}CREATED{RESET} {dst_agents} from resources")
        else:
            print(f"{RED}MISSING{RESET} Resource not found: {src_agents}")
    else:
        print(f"{GREEN}OK{RESET}      AGENTS.md already exists -> {dst_agents}")

    # Git initialization
    dotgit = os.path.join(outer_dir, ".git")
    if os.path.isdir(dotgit) or os.path.isfile(dotgit):
        print(f"{GREEN}OK{RESET}      Git repo detected -> {outer_dir}")
    else:
        print(f"{YELLOW}NO GIT{RESET}  {outer_dir} is not a git repo.")
        if prompt_yes_no("Initialize git repository here?", default=True):
            try:
                result = subprocess.run(["git", "init", outer_dir], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{GREEN}INIT{RESET}     Git repository initialized in {outer_dir}")
                else:
                    print(f"{RED}ERROR{RESET}    git init failed: {result.stderr.strip()}")
            except FileNotFoundError:
                print(f"{RED}ERROR{RESET}    'git' command not found on PATH.")

    # Collect project metadata (prompt only for missing fields)
    print()
    print(f"{BOLD}Project Metadata{RESET}")
    cfg_path = os.path.join(TOOL_ROOT, "config.json")
    config: dict = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, dict):
                config.update(existing)
        except Exception as e:
            print(f"{YELLOW}Warning:{RESET} could not read existing config: {e}")

    # project_name
    if not config.get("project_name"):
        name_default = os.path.basename(outer_dir)
        config["project_name"] = prompt_text("Project name", default=name_default)

    # project_code
    if not config.get("project_code"):

        def _code_validator(x: str) -> bool:
            return len(x) > 0 and all(c.isalnum() or c in ("-", "_") for c in x)

        base = str(config.get("project_name", os.path.basename(outer_dir)))
        code_default = base.lower().replace(" ", "-")
        config["project_code"] = prompt_text(
            "Project code (slug; letters, digits, - or _)",
            default=code_default,
            validator=_code_validator,
        )

    # backend
    if "backend" not in config:
        backend_opts = ["None", "Python - no framework", "Python - Django"]
        be_idx = prompt_choice("Backend language/framework:", backend_opts, default_index=0)
        config["backend"] = [None, "python", "django"][be_idx]

    # frontend
    if "frontend" not in config:
        frontend_opts = ["None", "NodeJS - NextJS"]
        fe_idx = prompt_choice("Frontend language/framework:", frontend_opts, default_index=0)
        config["frontend"] = [None, "nextjs"][fe_idx]

    # Persist config under .x100/config.json
    try:
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"{GREEN}SAVED{RESET} Configuration -> {cfg_path}")
    except Exception as e:
        print(f"{RED}ERROR{RESET} Saving config failed: {e}")

    # Create a symlink or wrapper at outer folder to run x100 directly
    print()
    print(f"{BOLD}Linking CLI{RESET}")
    cli_src = os.path.join(TOOL_ROOT, "x100")
    link_path = os.path.join(outer_dir, "x100")

    def create_wrapper_script(path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        # Make executable on POSIX
        try:
            mode = os.stat(path).st_mode
            os.chmod(path, mode | 0o111)
        except Exception:
            pass

    # POSIX link or wrapper
    try:
        need_link = True
        if os.path.islink(link_path):
            if os.path.realpath(link_path) == os.path.realpath(cli_src):
                print(f"{GREEN}OK{RESET}      Symlink already exists -> {link_path}")
                need_link = False
            else:
                if prompt_yes_no("A different symlink named 'x100' exists. Replace?", default=False):
                    os.remove(link_path)
                else:
                    need_link = False
        elif os.path.exists(link_path):
            if prompt_yes_no("An 'x100' file exists. Replace with symlink?", default=False):
                os.remove(link_path)
            else:
                need_link = False

        if need_link:
            try:
                os.symlink(cli_src, link_path)
                print(f"{GREEN}LINKED{RESET}   {link_path} -> {cli_src}")
            except (OSError, NotImplementedError):
                # Fallback to wrapper script
                wrapper = """#!/usr/bin/env bash
exec "$(dirname "$0")/.x100/x100" "$@"
"""
                create_wrapper_script(link_path, wrapper)
                print(f"{YELLOW}WRAPPED{RESET}  Created shell wrapper at {link_path}")
    except Exception as e:
        print(f"{YELLOW}Note:{RESET} Could not create POSIX launcher: {e}")

    # Windows CMD wrapper
    if os.name == "nt":
        cmd_path = os.path.join(outer_dir, "x100.cmd")
        if not os.path.exists(cmd_path):
            try:
                cmd_content = '@echo off\r\n"%~dp0\\.x100\\x100.cmd" %*\r\n'
                create_wrapper_script(cmd_path, cmd_content)
                print(f"{GREEN}CREATED{RESET}  {cmd_path}")
            except Exception as e:
                print(f"{YELLOW}Note:{RESET} Could not create Windows launcher: {e}")

    print()
    if wait_for_key:
        input("Press Enter to return to menu…")


def exit_app() -> None:
    clear_screen()
    sys.exit(0)


def run_contribute() -> None:
    """Run the contribute flow via the shell script."""
    script_path = os.path.join(TOOL_ROOT, "scripts", "contribute.sh")
    if not os.path.exists(script_path):
        print(f"{RED}ERROR{RESET} contribute script not found: {script_path}")
        sys.exit(1)
    try:
        # Invoke with bash to be cross-platform where bash is available
        result = subprocess.run(["bash", script_path])
        if result.returncode != 0:
            sys.exit(result.returncode)
    except FileNotFoundError:
        print(f"{RED}ERROR{RESET} 'bash' not found on PATH. Install bash to run contribute.")
        sys.exit(127)


def menu_loop(options: List[str], actions: List[Callable[[], None]]) -> None:
    assert len(options) == len(actions)
    selected = 0
    while True:
        try:
            render_menu(options, selected)
            key = read_key()
            if key == "UP":
                selected = (selected - 1) % len(options)
            elif key == "DOWN":
                selected = (selected + 1) % len(options)
            elif key.isdigit():
                idx = int(key) - 1
                if 0 <= idx < len(options):
                    clear_screen()
                    actions[idx]()
            elif key == "ENTER":
                clear_screen()
                actions[selected]()
            elif key in ("ESC", "q"):
                exit_app()
            # ignore other keys
        except KeyboardInterrupt:
            exit_app()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="x100", add_help=True)
    sub = parser.add_subparsers(dest="command")

    # init
    sub.add_parser("init", help="Initialize project structure")
    sub.add_parser("initialize", help="Alias of init")
    sub.add_parser("init-project", help="Alias of init")

    # contribute
    sub.add_parser("contribute", help="Sync and open a PR with changes")

    # verify (optional convenience)
    sub.add_parser("verify", help="Run environment checks")

    return parser


def main() -> None:
    parser = build_parser()
    args, extra = parser.parse_known_args()

    if args.command in ("init", "initialize", "init-project"):
        clear_screen()
        init_project(wait_for_key=False)
        return
    if args.command == "contribute":
        clear_screen()
        run_contribute()
        return
    if args.command == "verify":
        clear_screen()
        verify()
        return

    options = [
        "Init project",
        "Setup VSCode",
        "Setup AI Agent",
        "Verify",
        "Exit",
    ]
    actions: List[Callable[[], None]] = [
        init_project,
        setup_vscode,
        setup_ai_agent,
        verify,
        exit_app,
    ]
    menu_loop(options, actions)


if __name__ == "__main__":
    main()
