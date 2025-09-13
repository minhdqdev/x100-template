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

<div align="center">
    <img src=".x100/media/x100-template-logo.webp"/>
    <h1>⚡️ x100-template ⚡️</h1>
    <h3><em>Create high-grade software at speed with AI agent</em></h3>
</div>

A starter blueprint for new and existing projects, built to speed up dev workflows—especially when wiring up AI agents with spec-driven development.


## ⚡️ Get started 

### 🔧 Prerequisites

- **Linux/macOS** (or WSL2 on Windows)
- **AI coding agent**: [OpenAI Codex](https://openai.com/codex/), [Claude Code](https://www.anthropic.com/claude-code), [GitHub Copilot](https://code.visualstudio.com/), [Gemini CLI](https://github.com/google-gemini/gemini-cli), or [Cursor](https://cursor.sh/)
<!-- - [uv](https://docs.astral.sh/uv/) for package management -->
<!-- - [Python 3.11+](https://www.python.org/downloads/) -->
- [Git](https://git-scm.com/downloads)

### Option 1: Bootstrap a project from scratch

1. Clone or fork this repository:

```bash
git clone https://github.com/minhdqdev/x100-template.git your-project-name
cd your-project-name
```



### Option 2: Integrate this template to an existing project

#### 1. Configure Submodules
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



## 📚 Core philosophy
TODO

- **Context engineering is king**

- **Intent-driven development** where specifications define the "_what_" before the "_how_"
- **Heavy reliance** on advanced AI model capabilities for specification interpretation


## 🙏 Acknowledgements
This repository is provided as a starting template. It should be modified and adapted to meet the unique requirements and specifications of your individual projects. Adjust the submodule configurations and AI Agent integration steps as necessary for compatibility with your development environment and tools.

## 🔍 Troubleshooting
TODO


## 👥 Maintainers
- Minh Dang Quang ([@minhdqdev](https://github.com/minhdqdev))


## 💬 Support

For support, please open a [GitHub issue](https://github.com/minhdqdev/x100-template/issues/new). We welcome bug reports, feature requests, and questions about using the template.


## 📄 License

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./.github/LICENSE) file for the full terms.
