use super::Platform;
use crate::Family;

/// WebAssembly backend, covering both `wasm32-unknown-unknown` and
/// `wasm32-wasip1`.
pub(crate) struct Imp;

impl Platform for Imp {
    const NAME: &'static str = "wasm";
    const FAMILY: Family = Family::Wasm;
    const PATH_SEPARATOR: char = '/';
    const LINE_ENDING: &'static str = "\n";
    const CASE_SENSITIVE_FS: bool = true;
}
