# Agronia — AI Coding Agent Instructions

## 1. Project Identity

Project name: Agronia

Purpose: Develop an AI-powered agriculture support platform for farmers throughout Timor-Leste.

Primary use case: Preliminary crop disease identification using uploaded images.

Expected technology stack:
- Frontend: Flutter and Dart.
- Backend: Python, Django, and Django REST Framework.
- Database: SQLite for early development.
- AI: A suitable pretrained or fine-tuned computer vision model.
- Version control: Git and GitHub.

These technologies describe the intended architecture. Always inspect the existing repository before assuming a component has already been implemented.

## 2. Primary Responsibilities

The coding agent should:
- Understand the existing project before modifying it.
- Follow the documentation in `design.md` and `skill.md`.
- Preserve the existing architecture unless a change is justified.
- Implement small, verifiable changes.
- Explain technical decisions in beginner-friendly language.
- Write maintainable, readable, and testable code.
- Report limitations honestly.
- Avoid claiming that tests or commands succeeded unless they were actually executed.

## 3. Mandatory Workflow

Before implementing a task:

1. Inspect the repository structure.
2. Read the relevant documentation.
3. Identify the files and components affected.
4. Check existing dependencies and conventions.
5. Describe the intended change briefly.
6. Implement only the required scope.
7. Run relevant tests or validation commands.
8. Summarize changed files, test results, and remaining work.

If the user explicitly requests planning or documentation only, do not start implementing application code.

## 4. Repository Safety

- Do not delete or overwrite existing files without a clear requirement.
- Do not replace working implementations merely to match personal preferences.
- Do not run destructive Git commands without explicit authorization.
- Do not discard uncommitted user changes.
- Do not reset branches, rewrite Git history, or force-push without explicit authorization.
- Check the current Git branch and working tree before risky operations.
- Do not commit or push changes unless requested.

## 5. Code Quality

All code should:
- Have clear names and responsibilities.
- Follow the conventions of its programming language.
- Avoid unnecessary duplication.
- Handle errors explicitly.
- Separate business logic from presentation.
- Include tests for important behavior.
- Avoid unnecessary dependencies.

Prefer simple, maintainable solutions over premature complexity.

## 6. Flutter Guidelines

- Use Dart null safety.
- Keep UI widgets focused on presentation.
- Separate API communication from screen components.
- Use a consistent approach to application state.
- Provide loading, empty, success, and error states.
- Validate image selections before upload.
- Handle connection failures and API timeouts.
- Keep authentication tokens out of source code.
- Avoid introducing a large state-management framework without a concrete need.

Do not assume that a particular state-management library is installed.

## 7. Django Guidelines

- Use Django applications to separate major areas of responsibility.
- Use Django REST Framework for API endpoints when appropriate.
- Validate incoming data with serializers or equivalent validation layers.
- Apply authentication and object-level permissions where required.
- Keep secrets in environment variables.
- Use Django migrations for schema changes.
- Avoid unnecessary database queries.
- Use SQLite for development unless the existing configuration specifies otherwise.
- Keep production settings separate from development settings.

Do not expose uploaded images or private user records without appropriate authorization.

## 8. AI and Dataset Guidelines

- Prefer evaluating existing datasets and pretrained models before training from scratch.
- Verify dataset source, license, class labels, and known limitations.
- Separate training, validation, and test data appropriately.
- Avoid data leakage between evaluation splits.
- Do not invent model metrics or dataset statistics.
- Do not claim local accuracy without local evaluation.
- Handle unsupported classes and uncertain predictions.
- Record the model version used for each analysis when feasible.
- Keep model inference independent from API view logic.

The AI component should be replaceable without requiring a complete backend redesign.

## 9. API and Integration Guidelines

- Use consistent JSON response formats.
- Validate image files and enforce configured size limits.
- Return appropriate HTTP status codes.
- Avoid exposing stack traces or secret configuration.
- Document endpoint behavior and expected payloads.
- Keep frontend and backend contracts consistent.
- Test integration using representative requests.

Do not invent endpoints or response fields without checking the current implementation.

## 10. Security Requirements

Never:
- Hardcode credentials or private API keys.
- Commit `.env` files containing secrets.
- Disable authentication merely to make a test pass.
- Trust client-provided filenames or content types without validation.
- expose sensitive internal error details in production responses.

Always:
- Check permissions.
- Validate external input.
- Protect private uploaded files.
- Keep secrets out of logs.
- Use safe configuration for deployment.

## 11. Testing Rules

Before reporting a task as complete:
- Run relevant automated tests when possible.
- Check formatting and static analysis when configured.
- Test API behavior for invalid inputs.
- Test important permission boundaries.
- Verify frontend integration when feasible.
- Report commands that failed and explain why.

If tests cannot be run, state that clearly.

## 12. Dependency Management

- Inspect existing dependency files first.
- Respect the installed Python and Flutter/Dart versions.
- Avoid unnecessary package upgrades.
- Pin or constrain dependencies appropriately for reproducible environments.
- Explain any dependency changes.
- Do not introduce incompatible versions without checking compatibility.

## 13. Communication Rules

When responding to the project owner:
- Use Indonesian by default.
- Explain technical terminology simply.
- Distinguish implemented functionality from planned functionality.
- Give exact file paths for changes.
- Provide commands that match the actual project structure.
- Explain errors and their likely causes.
- Do not dump large amounts of code when the user asks only for planning.
- Ask one focused question when a critical requirement is unclear.

## 14. Definition of Done

A task is complete only when:
- The requested scope has been addressed.
- The changes follow project conventions.
- Relevant tests have been run or their absence disclosed.
- Security and error handling have been considered.
- Documentation is updated when necessary.
- Remaining limitations are stated honestly.

## 15. Priority Order

When requirements conflict, follow this order:

1. Explicit instructions from the project owner.
2. Security, data integrity, and repository safety.
3. Existing architecture and documented project decisions.
4. `design.md` and `skill.md`.
5. Maintainability and simplicity.
6. Optional enhancements.

Do not silently expand the requested scope.
