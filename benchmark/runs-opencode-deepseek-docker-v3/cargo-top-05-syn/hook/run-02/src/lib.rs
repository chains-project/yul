//! `ast_transform` — a procedural-macro crate that parses Rust source into a
//! [`syn`] syntax tree, inspects it, and rewrites it back into source tokens.
//!
//! The crate demonstrates the canonical proc-macro pipeline:
//!
//! 1. Parse the incoming [`proc_macro::TokenStream`] into typed `syn` AST nodes
//!    (here via [`syn::parse_macro_input!`]).
//! 2. Walk/inspect those nodes (see [`timed`]).
//! 3. Emit transformed tokens with the [`quote`] crate.
//!
//! For non-entrypoint parsing (e.g. reading Rust files or `TokenStream`s at
//! runtime) use [`syn::parse2`] / [`syn::parse_str`] instead.

use proc_macro::TokenStream;
use quote::quote;
use syn::{ItemFn, parse_macro_input, parse_quote};

/// Attribute macro that measures and reports the wall-clock time a function
/// takes to run.
///
/// It parses the annotated item into a [`syn::ItemFn`], reads the function's
/// name for the report, then transforms the body by wrapping it in timing
/// statements before re-emitting the whole function.
///
/// ```ignore
/// #[ast_transform::timed]
/// fn add(a: i32, b: i32) -> i32 {
///     a + b
/// }
/// ```
#[proc_macro_attribute]
pub fn timed(_attr: TokenStream, item: TokenStream) -> TokenStream {
    // 1. Parse into a typed AST. `parse_macro_input!` emits a helpful
    //    compile_error! if the input isn't a function.
    let mut func = parse_macro_input!(item as ItemFn);

    // 2. Inspect the tree: grab the identifier and the original body block.
    let name = func.sig.ident.clone();
    let original: syn::Block = (*func.block).clone();

    // 3. Transform: run the original body as a block expression so its tail
    //    value is preserved, then report the elapsed time.
    let new_block: syn::Block = parse_quote!({
        let __start = ::std::time::Instant::now();
        let __result = #original;
        ::std::eprintln!(
            "[timed] {} took {:?}",
            ::std::stringify!(#name),
            __start.elapsed()
        );
        __result
    });
    *func.block = new_block;

    // 4. Emit the rewritten function.
    quote!(#func).into()
}
