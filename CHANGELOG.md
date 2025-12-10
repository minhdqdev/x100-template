# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to the Specify CLI and templates are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **`x100 convert issue` Detailed Logging**: Comprehensive logging with rotation for conversion operations
  - Logs stored in `.x100/logs/convert.log` with automatic rotation
  - Rotating file handler with 10MB max per file, keeps 5 backup files
  - Logs all conversion steps: AI requests, responses, JSON parsing, validation, GitHub API calls
  - DEBUG level logging includes: file lists, AI response previews (first 500-1000 chars), command execution details
  - ERROR level logging includes: full error messages, JSON parsing failures with context, GitHub CLI output
  - Log location displayed in command output for easy access
  - Helps diagnose conversion failures with detailed audit trail

## [0.1.2] - 2024-12-10

### Added

- **GitHub Issue Templates**: The `x100 init` command now automatically populates `.github/ISSUE_TEMPLATE/` with bug report and feature request templates
  - Templates are copied from the package's bundled templates
  - Includes `bug_report.md` and `feature_request.md` with comprehensive sections
  - Step tracked in initialization progress: "Copy GitHub issue templates"
  - Templates are included in package data for distribution

### Changed

- **Package Structure**: Moved `templates/` directory into `src/x100_cli/` for proper package inclusion
- **Template Distribution**: Added `templates/**/*` and `templates/**/*.md` to package data in `pyproject.toml`

## [0.1.1] - Previous

### Added

- **`x100 convert issue` Command**: AI-powered user story to GitHub issue conversion
  - Automatically converts user story markdown files to GitHub issues
  - Supports single file or batch directory processing
  - Only processes files matching pattern: `US-[number]-[slug].md`
  - Uses default AI agent (CLI-based) to extract structured data from markdown
  - Creates issues via GitHub CLI (`gh`) with proper metadata
  - Supports labels, assignees, milestones extracted by AI
  - Automatically links issues to GitHub projects if configured
  - Displays success/failure summary table
  - Optionally deletes successfully converted files
  - Supports multiple AI agents: claude, gemini, qwen, opencode, codex, auggie, codebuddy, amp, shai, q
  - JSON schema contract for issue data structure
  - Comprehensive error handling and reporting
  - Documentation: `docs/CONVERT_ISSUE.md`
  - Example user story: `examples/US-001-news-ingestion-pipeline.md`

- **GitHub Project Integration**: New project management commands
  - `x100 project set-url`: Configure GitHub project URL for issue linking
  - `x100 project info`: View current project configuration
  - Stores configuration in `.x100/config.json` with type, url, and id
  - Automatic linking of issues to projects during conversion

### Changed

- **Core Module**: Added `load_config()` to public exports for use in convert module
- **Documentation**: Extensive updates to README.md with convert command usage
- **Architecture**: New `convert` submodule with modular design
  - `schemas.py`: JSON schema and dataclass definitions
  - `issue_converter.py`: Main conversion logic
  - `github_issue_schema.json`: OpenAPI-compliant schema contract

## [0.1.1] - 2024-12-04

### Fixed

- **User Story Status Detection**: Fixed incorrect "done" status detection
  - Previously: Stories marked as "done" if the word "implemented" appeared anywhere (even in unchecked checkboxes)
  - Now: Properly checks acceptance criteria checkbox states `[x]` vs `[ ]`
  - Status logic: All checkboxes checked = done, some checked = in-progress, none checked = todo
  - Prevents false positives where stories with `- [ ] Code implemented` were incorrectly marked as done
  - More accurate project health reporting

### Added

- **Default AI Agent Persistence**: `x100 init` now saves the selected AI agent to `.x100/config.json`
  - Default agent is persisted during project initialization
  - Configuration file stores the chosen agent for future reference
- **`x100 agent switch-default` Command**: New command to change the default AI agent
  - Interactive selection of new default agent using arrow keys
  - Shows current default agent before switching
  - Updates `.x100/config.json` with new selection
  - Provides feedback on agent folder location
- **`x100 nextstep` uses default agent**: The nextstep command now uses the project's default agent
  - Reads from `.x100/config.json` instead of hardcoded "claude"
  - Displays which agent is performing the analysis
  - Falls back to "claude" if no default agent is configured
  - **NEW**: Actually invokes the AI CLI (Claude, Copilot, Gemini) for analysis
  - Copilot command: `copilot -p "<prompt>" --allow-all-tools`
  - Claude command: `claude chat -m "<prompt>"`
  - Gemini command: `gemini chat "<prompt>"`
  - `--use-ai/--no-ai` flag to enable/disable AI CLI usage (default: enabled)
  - `--show-ai-insights` flag to display raw AI analysis output
  - Falls back to rule-based analysis if AI CLI is not available
  - AI performs comprehensive analysis: reads files, runs git commands, analyzes code structure

### Added

- **`x100 nextstep` Command**: AI-powered project analysis and recommendations
  - Analyzes codebase health (file count, TODOs, FIXMEs)
  - Analyzes git activity and velocity
  - Analyzes test coverage
  - Calculates project health score (0-100)
  - Identifies blockers and gaps
  - Generates prioritized next step recommendations
  - Multiple output formats: rich console, JSON, Markdown
  - Report saving (--save option)
  - Configuration system (.x100/nextstep.json)
  - Optional GitHub integration (requires `--github-repo` and token)
  - Verbose mode for detailed statistics
- **`x100 nextstep-setup` Command**: Interactive configuration wizard
  - Sets up GitHub integration
  - Configures coverage thresholds
  - Creates .x100/nextstep.json configuration file
- **Enhanced Analysis (Phase 3)**:
  - User story tracking and implementation status
  - Documentation coverage analysis
  - Story-code mismatch detection
  - Missing documentation identification
  - Comprehensive gap analysis
- **AI Steering Files**: New steering system that provides AI assistants with persistent project knowledge
  - Foundation files: `product.md`, `tech.md`, `structure.md` (always included)
  - Strategy files with conditional inclusion based on file patterns:
    - `api-standards.md` - REST conventions, error handling, authentication
    - `testing-standards.md` - Test patterns, coverage requirements, best practices
    - `code-conventions.md` - Naming conventions, function design, documentation
    - `security-policies.md` - Authentication, encryption, input validation
    - `deployment-workflow.md` - Environment setup, deployment strategies, rollback
  - Steering files are located in `.x100/steering/` directory
  - Inspired by [Kiro's steering feature](https://kiro.dev/docs/steering/)
  - Eliminates need to repeatedly explain project conventions to AI assistants
  - Comprehensive README with usage examples and best practices
- **AGENTS.md Template**: Added `AGENTS.md` file that's automatically created during `x100 init`
  - Provides AI agents with project-specific guidance and workflows
  - References steering files for persistent knowledge
  - Includes workflow automation commands and best practices
  - Compatible with the [AGENTS.md standard](https://agents.md/)

## [0.0.22] - 2025-11-07

- Support for VS Code/Copilot agents, and moving away from prompts to proper agents with hand-offs.
- Move to use `AGENTS.md` for Copilot workloads, since it's already supported out-of-the-box.
- Adds support for the version command. ([#486](https://github.com/github/spec-kit/issues/486))
- Fixes potential bug with the `create-new-feature.ps1` script that ignores existing feature branches when determining next feature number ([#975](https://github.com/github/spec-kit/issues/975))
- Add graceful fallback and logging for GitHub API rate-limiting during template fetch ([#970](https://github.com/github/spec-kit/issues/970))

## [0.0.21] - 2025-10-21

- Fixes [#975](https://github.com/github/spec-kit/issues/975) (thank you [@fgalarraga](https://github.com/fgalarraga)).
- Adds support for Amp CLI.
- Adds support for VS Code hand-offs and moves prompts to be full-fledged chat modes.
- Adds support for `version` command (addresses [#811](https://github.com/github/spec-kit/issues/811) and [#486](https://github.com/github/spec-kit/issues/486), thank you [@mcasalaina](https://github.com/mcasalaina) and [@dentity007](https://github.com/dentity007)).
- Adds support for rendering the rate limit errors from the CLI when encountered ([#970](https://github.com/github/spec-kit/issues/970), thank you [@psmman](https://github.com/psmman)).

## [0.0.20] - 2025-10-14

### Added

- **Intelligent Branch Naming**: `create-new-feature` scripts now support `--short-name` parameter for custom branch names
  - When `--short-name` provided: Uses the custom name directly (cleaned and formatted)
  - When omitted: Automatically generates meaningful names using stop word filtering and length-based filtering
  - Filters out common stop words (I, want, to, the, for, etc.)
  - Removes words shorter than 3 characters (unless they're uppercase acronyms)
  - Takes 3-4 most meaningful words from the description
  - **Enforces GitHub's 244-byte branch name limit** with automatic truncation and warnings
  - Examples:
    - "I want to create user authentication" → `001-create-user-authentication`
    - "Implement OAuth2 integration for API" → `001-implement-oauth2-integration-api`
    - "Fix payment processing bug" → `001-fix-payment-processing`
    - Very long descriptions are automatically truncated at word boundaries to stay within limits
  - Designed for AI agents to provide semantic short names while maintaining standalone usability

### Changed

- Enhanced help documentation for `create-new-feature.sh` and `create-new-feature.ps1` scripts with examples
- Branch names now validated against GitHub's 244-byte limit with automatic truncation if needed

## [0.0.19] - 2025-10-10

### Added

- Support for CodeBuddy (thank you to [@lispking](https://github.com/lispking) for the contribution).
- You can now see Git-sourced errors in the Specify CLI.

### Changed

- Fixed the path to the constitution in `plan.md` (thank you to [@lyzno1](https://github.com/lyzno1) for spotting).
- Fixed backslash escapes in generated TOML files for Gemini (thank you to [@hsin19](https://github.com/hsin19) for the contribution).
- Implementation command now ensures that the correct ignore files are added (thank you to [@sigent-amazon](https://github.com/sigent-amazon) for the contribution).

## [0.0.18] - 2025-10-06

### Added

- Support for using `.` as a shorthand for current directory in `specify init .` command, equivalent to `--here` flag but more intuitive for users.
- Use the `/speckit.` command prefix to easily discover Spec Kit-related commands.
- Refactor the prompts and templates to simplify their capabilities and how they are tracked. No more polluting things with tests when they are not needed.
- Ensure that tasks are created per user story (simplifies testing and validation).
- Add support for Visual Studio Code prompt shortcuts and automatic script execution.

### Changed

- All command files now prefixed with `speckit.` (e.g., `speckit.specify.md`, `speckit.plan.md`) for better discoverability and differentiation in IDE/CLI command palettes and file explorers

## [0.0.17] - 2025-09-22

### Added

- New `/clarify` command template to surface up to 5 targeted clarification questions for an existing spec and persist answers into a Clarifications section in the spec.
- New `/analyze` command template providing a non-destructive cross-artifact discrepancy and alignment report (spec, clarifications, plan, tasks, constitution) inserted after `/tasks` and before `/implement`.
  - Note: Constitution rules are explicitly treated as non-negotiable; any conflict is a CRITICAL finding requiring artifact remediation, not weakening of principles.

## [0.0.16] - 2025-09-22

### Added

- `--force` flag for `init` command to bypass confirmation when using `--here` in a non-empty directory and proceed with merging/overwriting files.

## [0.0.15] - 2025-09-21

### Added

- Support for Roo Code.

## [0.0.14] - 2025-09-21

### Changed

- Error messages are now shown consistently.

## [0.0.13] - 2025-09-21

### Added

- Support for Kilo Code. Thank you [@shahrukhkhan489](https://github.com/shahrukhkhan489) with [#394](https://github.com/github/spec-kit/pull/394).
- Support for Auggie CLI. Thank you [@hungthai1401](https://github.com/hungthai1401) with [#137](https://github.com/github/spec-kit/pull/137).
- Agent folder security notice displayed after project provisioning completion, warning users that some agents may store credentials or auth tokens in their agent folders and recommending adding relevant folders to `.gitignore` to prevent accidental credential leakage.

### Changed

- Warning displayed to ensure that folks are aware that they might need to add their agent folder to `.gitignore`.
- Cleaned up the `check` command output.

## [0.0.12] - 2025-09-21

### Changed

- Added additional context for OpenAI Codex users - they need to set an additional environment variable, as described in [#417](https://github.com/github/spec-kit/issues/417).

## [0.0.11] - 2025-09-20

### Added

- Codex CLI support (thank you [@honjo-hiroaki-gtt](https://github.com/honjo-hiroaki-gtt) for the contribution in [#14](https://github.com/github/spec-kit/pull/14))
- Codex-aware context update tooling (Bash and PowerShell) so feature plans refresh `AGENTS.md` alongside existing assistants without manual edits.

## [0.0.10] - 2025-09-20

### Fixed

- Addressed [#378](https://github.com/github/spec-kit/issues/378) where a GitHub token may be attached to the request when it was empty.

## [0.0.9] - 2025-09-19

### Changed

- Improved agent selector UI with cyan highlighting for agent keys and gray parentheses for full names

## [0.0.8] - 2025-09-19

### Added

- Windsurf IDE support as additional AI assistant option (thank you [@raedkit](https://github.com/raedkit) for the work in [#151](https://github.com/github/spec-kit/pull/151))
- GitHub token support for API requests to handle corporate environments and rate limiting (contributed by [@zryfish](https://github.com/@zryfish) in [#243](https://github.com/github/spec-kit/pull/243))

### Changed

- Updated README with Windsurf examples and GitHub token usage
- Enhanced release workflow to include Windsurf templates

## [0.0.7] - 2025-09-18

### Changed

- Updated command instructions in the CLI.
- Cleaned up the code to not render agent-specific information when it's generic.

## [0.0.6] - 2025-09-17

### Added

- opencode support as additional AI assistant option

## [0.0.5] - 2025-09-17

### Added

- Qwen Code support as additional AI assistant option

## [0.0.4] - 2025-09-14

### Added

- SOCKS proxy support for corporate environments via `httpx[socks]` dependency

### Fixed

N/A

### Changed

N/A
