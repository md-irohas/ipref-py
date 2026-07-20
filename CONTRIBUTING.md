# CONTRIBUTING.md

This file describes how to contribute to this project (bug reports, feature
requests, and pull requests).

For the development environment and coding conventions, see
[README-dev.md](README-dev.md).


## Bug reports and feature requests

Bug reports and feature requests are accepted via GitHub Issues.

When you create an issue, choose the issue template (bug report, feature
request, document update, etc.) which fits your purpose.

When you report a bug, include the following information:

- Steps to reproduce
- Expected behavior and actual behavior
- Environment (OS, Python version, etc.)


## Pull requests

Create pull requests with the following policy:

- Target the `develop` branch (the `main` branch is for releases).
- Write commit messages in English in the
  [Conventional Commits](https://www.conventionalcommits.org/) format.
- Make sure that the CI (formatter / linter / type checker / tests) passes.
    - See [README-dev.md](README-dev.md) for how to run them locally.

Pull requests are merged with **Squash and merge** after the CI passes.
