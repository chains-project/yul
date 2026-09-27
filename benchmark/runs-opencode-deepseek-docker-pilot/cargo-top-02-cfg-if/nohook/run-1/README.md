# xplat

A small Rust library scaffold demonstrating **clean, readable
conditional-compilation blocks across multiple target platforms**.

The goal is simple: platform detection should be boring and centralised, and
the rest of the code should never spell out raw `target_os = "..."` chains.

## Layout

```
build.rs                  # 1. declares every semantic cfg alias (the only raw target_* predicates)
src/lib.rs                # crate API
src/platform/mod.rs       # 2. the only place that maps aliases -> backends
src/platform/unix.rs      #    Unix backend        (cfg(unix_family))
src/platform/windows.rs   #    Windows backend     (cfg(windows_family))
src/platform/wasm.rs      #    WebAssembly backend (cfg(wasm_family))
src/platform/fallback.rs  #    everything else
tests/platform.rs         # integration tests
```

## Rules of the road

1. **Raw target predicates live in `build.rs`.** Define a semantic alias once:

   ```rust
   cfg_aliases! {
       unix_family:    { any(target_family = "unix") },
       windows_family: { target_family = "windows" },
       has_threads:    { all(feature = "std", not(target_family = "wasm")) },
   }
   ```

2. **Use aliases, not raw cfgs, everywhere else.**

   ```rust
   // Good — reads as intent, and adding a platform is a one-line change.
   #[cfg(unix_family)]
   fn ...

   // Avoid — scattered, easy to get wrong, painful to grep.
   #[cfg(any(target_os = "linux", target_os = "macos", target_os = "freebsd"))]
   fn ...
   ```

3. **Prefer `cfg_if!` over stacked `#[cfg]` attributes.** It keeps mutually
   exclusive branches flat and readable (`src/platform/mod.rs`).

4. **Isolate each platform in its own backend module.** Callers use one stable
   API regardless of the target.

5. **Put platform-only dependencies in the manifest** under
   `[target.'cfg(...)'.dependencies]`. Cargo evaluates the manifest before
   build scripts run, so this section uses Cargo's built-in `cfg` predicates,
   not the aliases.

6. **Keep the lints on.** `build.rs` + `cfg_aliases` register every custom cfg,
   so `#![deny(unexpected_cfgs)]` stays green on Rust 1.80+.

7. **No C toolchain required** for the library itself; `libc` / `windows-sys`
   are pulled in only for the target that needs them.

## Supported targets

| Family      | Alias            | Backend            | `page_size()` |
| ----------- | ---------------- | ------------------ | ------------- |
| Unix        | `unix_family`    | `platform::unix`     | yes           |
| Windows     | `windows_family` | `platform::windows`  | yes           |
| WebAssembly | `wasm_family`    | `platform::wasm`     | no            |
| Other       | *(none)*         | `platform::fallback` | no            |

## Building

```sh
cargo test
cargo build --no-default-features          # no_std
cargo clippy --all-targets -- -D warnings
cargo build --target wasm32-unknown-unknown
```

CI (`.github/workflows/ci.yml`) runs the test suite on Linux, macOS and
Windows, cross-compiles to WebAssembly, and enforces rule 2 with a grep that
fails if raw `target_*` cfgs appear outside `build.rs` and `src/platform/`.
