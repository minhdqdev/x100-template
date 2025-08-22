<div align="right">
  <details>
    <summary >🌐 Language</summary>
    <div>
      <div align="center">
        <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=en">English</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=zh-CN">简体中文</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=zh-TW">繁體中文</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=ja">日本語</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=ko">한국어</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=hi">हिन्दी</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=th">ไทย</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=fr">Français</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=de">Deutsch</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=es">Español</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=it">Italiano</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=ru">Русский</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=pt">Português</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=nl">Nederlands</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=pl">Polski</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=ar">العربية</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=fa">فارسی</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=tr">Türkçe</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=vi">Tiếng Việt</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=id">Bahasa Indonesia</a>
        | <a href="https://openaitx.github.io/view.html?user=minhdqdev&project=x100-template&lang=as">অসমীয়া</
      </div>
    </div>
  </details>
</div>

# ⚡️ x100-template ⚡️
This repository serves as a foundational template for new and existing projects, engineered to streamline development workflows, particularly when integrating AI Agents. It leverages Git submodules to manage child repositories, ensuring a modular and organized project structure.

## Getting Started
### Prerequisites
- Claude Code

MCP Tools:
- Context7



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

#### Setting up Claude Code
TLDR: generate the `CLAUDE.md` file

Execute the `/init` command within your Claude Code environment to generate the CLAUDE.md file.



## Important Considerations
This repository is provided as a starting template. It should be modified and adapted to meet the unique requirements and specifications of your individual projects. Adjust the submodule configurations and AI Agent integration steps as necessary for compatibility with your development environment and tools.


## Author
- Minh Dang Quang (minhdq.dev)

