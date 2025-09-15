import os


def check_agents_md(root_dir):
    agents_md_path = os.path.join(root_dir, "AGENTS.md")
    if not os.path.exists(agents_md_path):
        print("  ✗ AGENTS.md file is missing.")
        return

    # with open(agents_md_path, "r") as f:
    #     content = f.read()

    print("  ✓ AGENTS.md file is present.")


def check_prd(root_dir):
    prd_path = os.path.join(root_dir, "docs", "PRD.md")
    if not os.path.exists(prd_path):
        print("  ✗ PRD.md file is missing.")
        return

    # with open(prd_path, "r") as f:
    #     content = f.read()

    print("  ✓ PRD.md file is present.")


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    print("Checklist:")
    check_agents_md(root_dir)
    check_prd(root_dir)


if __name__ == "__main__":
    main()
