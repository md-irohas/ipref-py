# Copilot Instructions for ipref-py

This document describes instructions for GitHub Copilot to generate code
effectively in the "ipref-py" repository.


## Prerequisites

- Write answers, code comments, commit messages, issues, and pull requests in
  English.
- When you make large changes, present a plan first.
- If anything is unclear, investigate the files in the repository and then ask
  the developer.
- Do not commit and push automatically even after you change files. The
  developer reviews the changes, so wait for instructions before committing.


## Overview of this repository

`ipref-py` is a simple utility to look up IP addresses in MaxMind's GeoIP
downloadable databases by command-line and web.

### Main features

- Look up IP addresses by MaxMind's GeoIP databases.
- Look up hostnames of IP addresses by DNS reverse lookups.
- A command line interface (`ipref`) and a simple web interface (`ipref-web`).
- Configuration by YAML files.
- Flexible outputs (JSON, JSON-Lines, CSV, TSV).


## Instructions for development

See [README-dev.md](README-dev.md) for the development guide, and
[CONTRIBUTING.md](CONTRIBUTING.md) for the contribution guide (pull request
policy, etc.).
