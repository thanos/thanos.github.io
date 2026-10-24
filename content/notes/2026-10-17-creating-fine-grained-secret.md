---
title: "Creating a fine-grained GitHub secret"
description: "Create a fine-grained GitHub token on your user, then store it as the Actions secret INSTALL_REPOS_TOKEN so a release job can push to selected install repos."
date: 2026-10-17
tags:
  - GitHub
  - Actions
  - Gnosis
  - tokens
draft: false
authors:
  - Thanos Vassilakis
---

Create the token on your GitHub user, then store that `github_pat_…` string as the Actions secret `INSTALL_REPOS_TOKEN` on `some_org/some_repo`.

1. Open [Fine-grained tokens](https://github.com/settings/personal-access-tokens) and choose **Generate new token**.
2. Name it something  and set an expiration.
3. Set **Resource owner**.
4. Under **Repository access**, choose **Only select repositories** and add `homebrew-tap`, `scoop-bucket`, and `asdf-gnosis`.
5. Under **Repository permissions**, set **Contents** to **Read and write**. Leave the other permissions alone.
6. Generate the token and copy the `github_pat_…` value. GitHub shows it once.
7. On [SinAnima/gnosis Actions secrets](https://github.com/SinAnima/gnosis/settings/secrets/actions), add a repository secret named `INSTALL_REPOS_TOKEN` and paste that value.

If SinAnima requires approval for fine-grained tokens, the token stays pending until an org owner approves it under the organization’s personal-access-token requests. The release job can push with it only after that approval, and only after the workflow that reads `INSTALL_REPOS_TOKEN` is on `main`.
