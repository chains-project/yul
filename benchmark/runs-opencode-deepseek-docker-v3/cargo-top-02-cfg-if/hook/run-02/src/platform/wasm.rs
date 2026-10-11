use super::Platform;

/// The `wasm32` family, typically running inside a host engine.
pub struct Wasm;

impl Platform for Wasm {
    const NAME: &'static str = "wasm32";

    fn page_size() -> usize {
        // WebAssembly linear-memory pages are fixed at 64 KiB by the spec.
        64 * 1024
    }

    fn max_threads() -> usize {
        // Threads require the shared-memory and atomics proposals.
        1
    }
}
