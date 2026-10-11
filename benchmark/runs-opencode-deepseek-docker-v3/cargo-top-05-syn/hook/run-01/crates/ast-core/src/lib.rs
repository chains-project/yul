//! Parse Rust source code into a [`syn`] syntax tree that can be inspected
//! and transformed.
//!
//! The crate is intentionally free of `proc-macro` concerns so it can be used
//! from ordinary binaries, tests, and build scripts as well as from the
//! `ast-macros` procedural-macro facade.
//!
//! ```
//! use ast_core::{inspect, parse_source, transform};
//!
//! let mut file = parse_source("fn add(a: i32, b: i32) -> i32 { a + b }").unwrap();
//! assert_eq!(inspect::item_count(&file), 1);
//!
//! transform::rename_in_file(&mut file, "a", "x");
//! assert!(inspect::collect_identifiers(&file).contains(&"x".to_owned()));
//! ```

pub mod inspect;
pub mod transform;

use syn::File;

/// Parse a complete Rust source file into a [`syn::File`] syntax tree.
pub fn parse_source(source: &str) -> syn::Result<File> {
    syn::parse_file(source)
}

/// Parse a single Rust item (function, struct, module, ...) from source text.
pub fn parse_item(source: &str) -> syn::Result<syn::Item> {
    syn::parse_str(source)
}
