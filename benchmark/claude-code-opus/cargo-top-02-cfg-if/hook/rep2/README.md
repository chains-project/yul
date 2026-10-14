# platkit

A `no_std` cross-platform Rust library. MSRV: 1.95.

## Layout

```
src/
├── lib.rs            platform-agnostic public API
└── sys/
    ├── mod.rs        selects exactly one backend via cfg_select!
    ├── unix.rs       Linux, macOS, BSDs, Android, iOS
    ├── windows.rs    Windows
    ├── wasm.rs       wasm32 (browser and WASI)
    └── fallback.rs   everything else (e.g. bare-metal)
```

## Conditional compilation

Use the standard library's `cfg_select!` (stable since Rust 1.95) instead of
pairs of `#[cfg(x)]` / `#[cfg(not(x))]` attributes:

```rust
cfg_select! {
    unix => { mod unix; pub use unix::*; }
    windows => { mod windows; pub use windows::*; }
    _ => { mod fallback; pub use fallback::*; }
}
```

The first matching arm wins and `_` catches everything else, so exactly one
branch compiles. It also works in expression position for one-off differences:

```rust
let sep = cfg_select! { windows => ';', _ => ':' };
```

Rules:

1. Platform-specific code lives only in `src/sys/`. Each backend defines the
   same items with identical signatures.
2. Always end a `cfg_select!` with a `_` arm. Leave it out only if you want
   unsupported targets to fail to compile.
3. `unexpected_cfgs` is set to `deny`, so misspelled cfg names or values fail
   the build.

## Adding a platform

1. Create `src/sys/<name>.rs` that implements every item listed in `src/sys/mod.rs`.
2. Add an arm before `_` in the `cfg_select!` in `src/sys/mod.rs`.
3. Add a target for it to the `cross-check` matrix in `.github/workflows/ci.yml`.

## Checking all backends locally

```sh
for t in x86_64-pc-windows-gnu aarch64-apple-darwin wasm32-unknown-unknown thumbv7em-none-eabihf; do
  rustup target add "$t" && cargo check --target "$t"
done
```
