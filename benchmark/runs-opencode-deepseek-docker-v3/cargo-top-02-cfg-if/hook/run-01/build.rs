//! Collapses the raw `target_*` cfg keys onto a small set of semantic aliases.
//!
//! Doing the platform detection here means the library source never has to
//! juggle `target_os`, `target_family`, `target_arch` or `target_env` again.
//! It just asks whether `platform_unix`, `platform_windows`, `platform_wasm`
//! or `platform_other` is active.
//!
//! Exactly one alias is emitted for any given target.

/// Every alias this build script may emit. Used both for `check-cfg` and as
/// the single source of truth for what counts as a known platform.
const ALIASES: &[&str] = &[
    "platform_unix",
    "platform_windows",
    "platform_wasm",
    "platform_other",
];

fn main() {
    for alias in ALIASES {
        // Tell rustc these cfgs are expected, so `unexpected_cfgs` stays quiet.
        println!("cargo::rustc-check-cfg=cfg({alias})");
    }

    println!("cargo::rustc-cfg={}", select_alias(&target_families()));
}

/// Pick the single alias that matches the target's OS families.
fn select_alias(families: &[String]) -> &'static str {
    let has = |family: &str| families.iter().any(|f| f == family);

    // wasm is checked first: a few wasm targets also report another family,
    // and the wasm implementation is the more specific one.
    if has("wasm") {
        "platform_wasm"
    } else if has("unix") {
        "platform_unix"
    } else if has("windows") {
        "platform_windows"
    } else {
        "platform_other"
    }
}

/// The target's OS families, e.g. `["unix"]` or `["wasm"]`.
///
/// `CARGO_CFG_TARGET_FAMILY` is comma-separated when a target belongs to more
/// than one family.
fn target_families() -> Vec<String> {
    std::env::var("CARGO_CFG_TARGET_FAMILY")
        .unwrap_or_default()
        .split(',')
        .filter(|family| !family.is_empty())
        .map(str::to_owned)
        .collect()
}
