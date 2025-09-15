import os
import shutil
import sys
from typing import Callable, List

TITLE = """
 █████ █████ ████     █████       █████   
░░███ ░░███ ░░███   ███░░░███   ███░░░███ 
 ░░███ ███   ░███  ███   ░░███ ███   ░░███
  ░░█████    ░███ ░███    ░███░███    ░███
   ███░███   ░███ ░███    ░███░███    ░███
  ███ ░░███  ░███ ░░███   ███ ░░███   ███ 
 █████ █████ █████ ░░░█████░   ░░░█████░  
░░░░░ ░░░░░ ░░░░░    ░░░░░░      ░░░░░░   """


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
    sys.stdout.write("\x1b[2J\x1b[H")  # clear + move home
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


def render_menu(items: List[str], selected: int) -> None:
    clear_screen()
    print(TITLE)
    print()
    print(f"{BOLD}Use ↑/↓ to navigate, Enter to select.{RESET}")
    print()
    for idx, label in enumerate(items):
        prefix = f" {idx+1}. "
        if idx == selected:
            print(f"{REVERSE}{prefix}{label}{RESET}")
        else:
            print(f"{prefix}{label}")
    print()
    print(f"{DIM}Press ESC or Ctrl+C to exit.{RESET}")


# --- Handlers ---
def setup_vscode() -> None:
    repo_root = os.path.abspath(os.path.dirname(__file__))
    src = os.path.join(repo_root, "vscode", "settings.example.json")
    target_dir = os.path.join(repo_root, ".vscode")
    target = os.path.join(target_dir, "settings.json")

    if not os.path.exists(src):
        print(f"{RED}Source not found:{RESET} {src}")
        input("Press Enter to return to menu…")
        return

    os.makedirs(target_dir, exist_ok=True)

    if os.path.exists(target):
        if not prompt_yes_no(".vscode/settings.json exists. Overwrite?", default=False):
            print(f"{YELLOW}Skipped.{RESET} Existing settings preserved.")
            input("Press Enter to return to menu…")
            return

    shutil.copyfile(src, target)
    print(f"{GREEN}VSCode settings installed:{RESET} {target}")
    input("Press Enter to return to menu…")


def setup_ai_agent() -> None:
    repo_root = os.path.abspath(os.path.dirname(__file__))
    example = os.path.join(repo_root, "claude", "settings.example.json")
    target = os.path.join(repo_root, "claude", "settings.json")

    if os.path.exists(target):
        print(f"{YELLOW}Already exists:{RESET} {target}")
        input("Press Enter to return to menu…")
        return

    if not os.path.exists(example):
        print(f"{RED}Example not found:{RESET} {example}")
        input("Press Enter to return to menu…")
        return

    shutil.copyfile(example, target)
    print(f"{GREEN}AI Agent settings created from example:{RESET} {target}")
    input("Press Enter to return to menu…")


def verify() -> None:
    tool_dir = os.path.abspath(os.path.dirname(__file__))
    outer_dir = os.path.dirname(tool_dir)

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
        print(
            f"{YELLOW}Some checks failed. Ensure this tool lives under '.x100' at your repo root.{RESET}"
        )
    input("Press Enter to return to menu…")


def exit_app() -> None:
    clear_screen()
    # print("Goodbye! 👋")
    sys.exit(0)


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
            elif key == "ENTER":
                clear_screen()
                actions[selected]()
            elif key in ("ESC", "q"):
                exit_app()
            # ignore other keys
        except KeyboardInterrupt:
            exit_app()


def main() -> None:
    options = [
        "Setup VSCode",
        "Setup AI Agent",
        "Verify",
        "Exit",
    ]
    actions: List[Callable[[], None]] = [
        setup_vscode,
        setup_ai_agent,
        verify,
        exit_app,
    ]
    menu_loop(options, actions)


if __name__ == "__main__":
    main()
