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
- Basic knowledge of Git and version control
- Basic knowledge of using AI chatbots (ChatGPT, Gemini, Claude,...)
- Claude Code (other AI agents still can work with a few tweaks)


To set up your project using this template, follow these steps:

### 1. Configure Submodules
Integrate all related repositories (e.g., frontend, backend, documentation) as submodules.

**Via Command Line:**

```shell
git submodule add -b <branch_name> <repo_url> submodules/<submodule_name>
```

**Via `.gitmodules` (Manual Configuration):**
Alternatively, you can manually edit the .gitmodules file.
For example:

```shell
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

```shell
git submodule update --init --recursive
```


### 2. AI Agent Integration

#### Setting up Claude Code

Use this prompt to generate `CLAUDE.md` file:
```
Execute `/init` command with `CLAUDE.example.md` as a template.
```



TLDR: generate the `CLAUDE.md` file

Execute the `/init` command within your Claude Code environment to generate the CLAUDE.md file.





## How to use this template?
This template will help you in every stage of SDLC, specifically, requirements gathering, design, implementation, testing, deployment, and maintenance.

The output artifacts are usually generated in Markdown format. Feel free to edit them.

Context is KING. So in every stages, you should maintain and update the context resources in `/references` and `CLAUDE.md`.


### 1. Requirements gathering
> From idea to requirements

This template also provides a quick way to refine your ideas. Just run `/refine-idea` in Claude Code
- Input: `docs/IDEA.md`
- Output: `docs/REFINED_IDEA.md`
- Human in the loop:
  - Review and provide feedback on the refined idea document.
  - Use 3rd party AI tools (ChatGPT, Claude, Grok, etc.) for additional insights and improvements.

#### Write Product Requirements Document
Run `/gen-prd` in Claude Code
- Input:  `docs/REFINED_IDEA.md`
- Output: `docs/PRD.md`
- Human in the loop:
  - Review and provide feedback on the generated PRD.
  - Use 3rd party AI tools for additional insights and improvements.

### 2.Design
> From requirements to design

#### Write Design Documents

Run `/design` in Claude Code
- Input: `docs/PRD.md`
- Output: design documents from Solutions Architect
- Human in the loop:
  - Review and provide feedback on the generated design documents.

To know more about the design documents will be generated, you can refer to the `references/DESIGN_CHECKLIST.md`.





Bước 3: Mở 1 tab mới yêu cầu AI mô tả lại cách nó hiểu về dự án, vẽ giả định 3–5 user flow để xem dự án có đúng như mình hình dung hay không.

Mình sẽ bắt AI mô tả đi mô tả lại về cách nó hiểu dự án, để xem nếu nó trả lời đúng ý mình nhất thì có nghĩa là tài liệu đã đầy đủ.

### 3. Implementation

#### Build project backlogs

Run `/build-backlogs` in Claude Code
- Input: `docs/PRD.md`
- Output: `docs/BACKLOG.md`
- Human in the loop:
  - Review and provide feedback on the generated backlog.
  - Use 3rd party AI tools for additional insights and improvements.
  - Break down large tasks into smaller, manageable subtasks.
  - Prioritize tasks based on business value and complexity.
  - Estimate effort and time required for each task.


### 4. Testing

#### Write unit tests
Coming soon...

#### Write performance tests
Coming soon...

### 5. Deployment
Coming soon...

### 6. Maintainance
Coming soon...


## Important Considerations
This repository is provided as a starting template. It should be modified and adapted to meet the unique requirements and specifications of your individual projects. Adjust the submodule configurations and AI Agent integration steps as necessary for compatibility with your development environment and tools.


## Author
- Minh Dang Quang (minhdq.dev)

