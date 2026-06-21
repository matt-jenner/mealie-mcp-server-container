# Feature 01: Project Bootstrap

## Goal

Create a standalone private wrapper repository for packaging `rldiao/mealie-mcp-server` as a remote Docker-hosted MCP service.

## Status

State: Complete

Stories:

- [x] Story 01.1: Local Repository Exists
- [x] Story 01.2: Private GitHub Repository Exists
- [x] Story 01.3: Repository Hygiene Is Defined

Review:

- [x] Implementation reviewed against acceptance criteria
- [x] Tests verified

Notes:

- Local repository and GitHub remote are created.
- No commit or push has been performed.
- Feature-level review completed with risks; all acceptance criteria passed and required checks/reviews were completed.
- GitHub metadata may report default branch `master` until first push; verify default branch is `main` after first push.
- README does not exist yet; review README for secret safety when Documentation feature adds it.

## Context

The upstream project lives outside this repository at `../../3rdParty/mealie-mcp-server`. This wrapper repository should not vendor or rewrite upstream MCP logic unless there is a concrete reason. Its job is to package and expose the upstream MCP server over internal HTTP for use behind an HTTPS reverse proxy.

## Stories

### Story 01.1: Local Repository Exists

As the maintainer, I want a dedicated local project directory so wrapper code and deployment docs are isolated from upstream source.

Acceptance criteria:

- Project exists at `./personal/mealie-mcp-server-container` relative to `/home/jennerm/repos`.
- Project is initialized as a git repository on branch `main`.
- No upstream source is committed into this wrapper repository.

### Story 01.2: Private GitHub Repository Exists

As the maintainer, I want the wrapper connected to a private GitHub repository so work can be backed up and shared intentionally.

Acceptance criteria:

- GitHub repository exists at `matt-jenner/mealie-mcp-server-container`.
- Repository visibility is private.
- Local `origin` remote points to the GitHub repository.

### Story 01.3: Repository Hygiene Is Defined

As the maintainer, I want basic repository hygiene so secrets and generated files do not get committed.

Acceptance criteria:

- `.gitignore` excludes `.env`, Python caches, test caches, local build output, and editor noise.
- Secret-bearing files are documented as local-only.
- README and specs remain safe to commit.

## Implementation Notes

- This feature is partially complete once the directory, git repo, and private GitHub remote are created.
- Do not commit or push until explicitly requested.

## Test Strategy

- Run `git status --short` to confirm only intended files are untracked or modified.
- Run `git remote -v` to confirm `origin`.
- Verify private repo creation through GitHub API/tooling.
