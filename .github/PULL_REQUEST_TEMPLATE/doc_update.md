---
# URL Example: https://github.com/md-irohas/ipref-py/compare/main...develop?template=doc_update

# NOTE: This metadata is not recognized automatically. Fill it in manually.
name: Document update
about: For pull requests of document updates.
title: 'Document updates'
labels: ['documentation']
assignees: 'md-irohas'
---

**Changes**

- #issue-number
- Other changes


**Checklist**

- [ ] No changes to the code or the version itself?
- [ ] Mergeable to the main branch?


<!--
**Update procedure**

If the checklist above is fine, merge this branch to the main or release
branch ("Create a merge commit").

After the merge, the Build and Release workflow (release.yml) runs the
following steps:

1. Check the version in pyproject.toml (`uv version --short`).
1. The version is already tagged in git, so the workflow stops there.
-->
