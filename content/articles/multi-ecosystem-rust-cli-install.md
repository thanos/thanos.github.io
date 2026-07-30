---
title: "Ship one Rust CLI everywhere: multi-ecosystem install without rewriting it"
description: "Treat GitHub Release binaries as the source of truth, then wrap them for Homebrew, Scoop, mise/asdf, pip, npm, Mix, and CI—the Ruff/esbuild pattern for tools like Oratos."
date: 2026-07-30
tags:
  - Rust
  - CLI
  - Distribution
  - Homebrew
  - PyPI
  - npm
  - Hex
  - DevEx

draft: false
---

<!-- Medium subtitle: One native binary, many installers: how to distribute a Rust CLI like Ruff without ports, NIFs, or cargo-install-as-default. -->

Your users work across macOS, Windows, Linux, Node.js, Python, and Elixir. They do not want to install a Rust toolchain just to run your CLI.


The winning pattern—used by Ruff, esbuild, and tools like [Oratos](https://github.com/latentmeta/oratos)—is simple: **build one binary**, publish it through GitHub Releases, and make every ecosystem a thin wrapper around that artifact.

## The rule

Maintain **one** Rust binary. Do not reimplement the tool in every language.

Each installation method should either:

1. download a prebuilt binary from GitHub Releases; or 
2. bundle that same binary, as with PyPI wheels or npm packages. 

Keep `cargo install` as a **fallback for contributors**, not the first installation method in your README.

## 1. Release assets are the contract

For every `v*` tag, publish consistently named assets along with their checksums:

| Platform | Asset |
| -------- | ----- |
| Linux x86_64 / aarch64 | `greet-v0.1.0-linux-*.tar.gz` |
| macOS Intel / Apple Silicon | `greet-v0.1.0-macos-*.tar.gz` |
| Windows x86_64 | `greet-v0.1.0-windows-x86_64.zip` |
| All | `SHA256SUMS` |

Here is an example CLI that can stand in for any small Rust tool:

```rust
// src/main.rs
fn main() {
    println!("hello from greet {}", env!("CARGO_PKG_VERSION"));
}
```

Your release workflow builds `--release` per target, packs the binary, uploads artifacts, then writes `SHA256SUMS`. That file is what Homebrew, Scoop, `install.sh`, and CI verify against.

Your release workflow should build the binary in `--release` mode for each target, package it, upload the assets, and generate `SHA256SUMS`. Homebrew, Scoop, `install.sh`, and your CI integrations can then use that file to verify their downloads.

## 2. Support operating-system and version managers without compilation

| Channel | Pattern |
| ------- | ------- |
| curl | `install.sh` → detect OS and architecture → download and verify → install to `~/.local/bin` |
| Homebrew | Homebrew Formula URL + `sha256` from GitHub Releases; download the prebuilt binary without requiring a bottle|
| Scoop | Manifest `url` + `hash` from the Windows zip |
| mise | `github:owner/greet` backend, or `[tool_alias] greet = "github:owner/greet"` |
| asdf | Small plugin repository with `bin/list-all` and `bin/install`, both using the same release assets |
| CI | Composite action that installs the release binary instead of running `cargo install` |

A single organization-level tap or bucket can host formulas for multiple tools—for example, `latentmeta/homebrew-tap` or `scoop-bucket`.

## 3. Use language ecosystems as wrappers around the binary

**PyPI with maturin and bindings** = "bin" — Include the CLI in the wheel, following the Ruff model:

```toml
# pyproject.toml
[tool.maturin]
bindings = "bin"
manifest-path = "Cargo.toml"
module-name = "greet"
strip = true
```

Publish through Trusted Publishing with OIDC. Include `LICENSE` in the source distribution, or PyPI may reject the upload with a 400 response.

**npm** — Publish a scoped package whose `postinstall` script downloads the matching GitHub Release:

```bash
npm install -D @org/greet
npx greet
```

Use a granular access token configured to  **bypass 2FA**. Exporting `NPM_TOKEN` alone has no effect unless your `.npmrc` is configured to use it.

**Hex / Mix** — Do not use a NIF. Instead, provide a Mix task that downloads the CLI into `priv/bin`—for example, with Req—and executes it:

```elixir
{:greet, "~> 0.1", only: [:dev, :test], runtime: false}
# mix greet.audit …
```

Make the boundary explicit in your documentation: Mix manages the **native CLI**; the audit does not run inside the BEAM.

## 4. Order the README around how people actually install the tool

1. Homebrew, Scoop, and install.sh
2. mise and asdf
3. CI action
4. pip, npm, and Mix
5. cargo install for Rust contributors 

If your README begins with `cargo install`, many non-Rust users will leave before discovering that they do not actually need Rust.

## 5. What not to do

- Build from source in Homebrew or CI by default.
- Port the tool to Python, JavaScript, or Elixir soleMake the official GitHub Action run cargo install.
- Make the official Action run `cargo install`  
- Wrap the library in a Mix NIF just to distribute an audit CLI.

## Checklist

- [ ] Multi-architecture release matrix and `SHA256SUMS`  
- [ ] `install.sh` with checksum verification
- [ ] Homebrew and Scoop hashes populated from `SHA256SUMS`
- [ ] asdf plugin repository, or a mise `github:` backend or `tool_alias` 
- [ ] Setup action that installs binaries from GitHub Releases
- [ ] maturin binary package published to PyPI through Trusted Publishing
- [ ] Scoped npm package with an appropriately configured token
- [ ] Hex/Mix wrapper that downloads the CLI 
- [ ] Documentation that presents no-Rust installation methods first

 

That is the entire playbook: **one binary, many front doors**. Everything else is packaging—and being honest in your `README` about how users should install the tool.
