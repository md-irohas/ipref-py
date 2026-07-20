---
# URL Example: https://github.com/md-irohas/ipref-py/compare/main...develop?template=version_update

# NOTE: This metadata is not recognized automatically. Fill it in manually.
name: Package release
about: For pull requests of package releases.
title: 'Release vX.Y.Z'
labels: ['build']
assignees: 'md-irohas'
---

**Version**

vX.Y.Z


**Changes**

- #issue-number
- Other changes


**Checklist**

- [ ] GitHub Actions checks
    - [ ] Lint passed? (`make lint`)
    - [ ] Tests passed? (`make test`)
    - [ ] Mergeable to the main branch?
- [ ] Reviewed by Copilot?
- [ ] Is CHANGELOG.md updated?
- [ ] Is the version in pyproject.toml updated by `uv version --bump ...`?
- [ ] Are requirements.txt and requirements-dev.txt updated by `make freeze`?
  (Optional for minor updates.)


<!--
**Notes**

- requirements.txt and requirements-dev.txt are not used in the development
  environment, but they are kept for compatibility.
- Update the version with the following commands.
    - Do not use rc versions. The version strings of rc differ between PEP
      (`0.2.0rc1`) and SemVer (`0.2.0-rc1`).

```sh
# You can check the result with --dry-run.
$ uv version --bump major
$ uv version --bump minor
$ uv version --bump patch
```
-->

<!--
**Update procedure**

If the checklist above is fine, merge this branch to the main or release
branch ("Create a merge commit").

After the merge, the Build and Release workflow (release.yml) runs the
following steps:

1. Check the version in pyproject.toml (`uv version --short`).
1. If the version is not tagged in git yet, create a tag (`git tag vX.Y.Z`)
   and push it to the repository. If it is already tagged, the workflow stops
   there.
1. GoReleaser runs the release process.
-->
