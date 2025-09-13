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
- Basic familiarity with [Git](https://git-scm.com/downloads) and Git submodules
- Basic familiarity with Markdown, and shell scripting

Now you may want to set up your project using one of the following options:

### Option 1: Bootstrap a project from scratch

1. Clone or fork this repository

```bash
git clone https://github.com/minhdqdev/x100-template.git your-project-name
cd your-project-name
```

2. Setup VSCode (optional but recommended)

```bash
mkdir -p .vscode
cp .vscode/settings.example.json .vscode/settings.json
```

That's it! You can now start defining your project idea in `docs/IDEA.md` and use the AI agent commands to generate refined ideas, PRDs, implementation plans, code, and tests.

Read more in the [Use the template](#use-the-template) section below.

### Option 2: Integrate this template to an existing project

1. Setup a Git repository for your existing project if you haven't done so:

```bash
cd your-existing-project && git init
```

2. Move your existing source code to subdirectory (e.g., `submodules/frontend`, `submodules/backend`, etc.) to keep things organized.

```bash
mkdir -p submodules/frontend submodules/backend
mv your-existing-frontend-code submodules/frontend/
mv your-existing-backend-code submodules/backend/
```

1. Add submodules for your existing code if applicable (skip if not using Git):

```bash
git submodule add -b <branch_name> <repo_url> submodules/<submodule_name>
```

4. Copy the `.x100` directory from this repository to your existing project.

```bash
git clone https://github.com/minhdqdev/x100-template.git

cp -r x100-template/.x100 ./your-existing-project
rm -rf x100-template
```

5. Create `docs/` directory if it doesn't exist

```bash
mkdir -p docs
```

6. Setup AI agent
   1. For GitHub Copilot, copy `.x100/.copilot` to your project root
   2. For Claude Code, copy `.x100/.claude` to your project root
   3. For Gemini CLI, copy `.x100/.gemini` to your project root
   4. For Cursor, copy `.x100/.cursor` to your project root

TODO: Add setup script for AI agents

7. Setup VSCode (optional but recommended)

```bash
mkdir -p .vscode
cp .x100/.vscode/settings.json .vscode/settings.json
```

**Checkpoint**: You should now have a project structure similar to this:

```bash
your-project-name/
├── .git/
├── .vscode/
│   ├── settings.json
├── .copilot/  (if using GitHub Copilot)
├── .claude/   (if using Claude Code)
├── .gemini/   (if using Gemini CLI)
├── .cursor/   (if using Cursor)
├── .x100/
│   ├── agents/
│   ├── specs/
│   ├── tools/
│   ├── .env.example
│   ├── config.yaml
│   └── ...
├── submodules/
│   ├── frontend/
│   └── backend/
│   └── ...
├── docs/
└── ...
```



## Use the template

For AI agent commands, refer to the command files in `.x100/.claude/commands/` (for Claude Code), `.x100/.copilot/commands/` (for GitHub Copilot), `.x100/.gemini/commands/` (for Gemini CLI), or `.x100/.cursor/commands/` (for Cursor).

For OpenAI Codex, you can use the prompts in `.x100/.claude/commands/` as reference.

### From raw idea to refined idea
1. Define your project idea in `docs/IDEA.md`.
2. Use AI agent command: `/refine-idea`


### From refined idea to PRD
1. Use AI agent command: `/generate-prd`
2. Review and edit the generated PRD in `docs/PRD.md`

### From PRD to implementation plan
1. Use AI agent command: `/generate-implementation-plan`
2. Review and edit the generated implementation plan in `docs/IMPLEMENTATION_PLAN.md`

### From implementation plan to code
1. Use AI agent command: `/implement`
2. Review and edit the generated code in `submodules/` directories

### From code to tests
1. Use AI agent command: `/generate-tests`
2. Review and edit the generated tests in `submodules/` directories



## 📚 Core philosophy
TODO

- **Context engineering is king**

- **Intent-driven development** where specifications define the "_what_" before the "_how_"
- **Heavy reliance** on advanced AI model capabilities for specification interpretation

- **Human-in-the-loop** for critical thinking, creativity, and oversight

- Use `AGENTS.md` for all agents used in the project
  - Read more in [here](https://agents.md)

## 👥 Maintainers
- Minh Dang Quang ([@minhdqdev](https://github.com/minhdqdev))


## 💬 Support

For support, please open a [GitHub issue](https://github.com/minhdqdev/x100-template/issues/new). We welcome bug reports, feature requests, and questions about using the template.


## 📄 License

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./.github/LICENSE) file for the full terms.
