# ⚡️ x100-template ⚡️
This repository serves as a foundational template for new and existing projects, engineered to streamline development workflows, particularly when integrating AI Agents. It leverages Git submodules to manage child repositories, ensuring a modular and organized project structure.

## Getting Started
To set up your project using this template, follow these steps:

### 1. Configure Submodules
Integrate all related repositories (e.g., frontend, backend, documentation) as submodules.

**Via Command Line:**

```bash
git submodule add -b <branch_name> <repo_url> submodules/<submodule_name>
```

**Via `.gitmodules` (Manual Configuration):**
Alternatively, you can manually edit the .gitmodules file.
For example:

```bash
[submodule "submodules/frontend"]
	path = submodules/frontend
	url = git@github.com:minhdqdev/x100-frontend.git
	branch = develop
[submodule "submodules/backend"]
	path = submodules/backend
	url = git@github.com:minhdqdev/x100-backend.git
	branch = develop
```

After adding submodules, initialize and update them:

```bash
git submodule update --init --recursive
```


### 2. AI Agent Integration
For optimal integration with AI development tools, follow the specific initialization procedures for your chosen AI Agent. For example, if using Claude Code:

Execute the `/init` command within your Claude Code environment to generate the CLAUDE.md file.



## Important Considerations
This repository is provided as a starting template. It should be modified and adapted to meet the unique requirements and specifications of your individual projects. Adjust the submodule configurations and AI Agent integration steps as necessary for compatibility with your development environment and tools.


## Author
- Minh Dang Quang (minhdq.dev)

