//! Procedural macros built on `syn`'s full Rust syntax tree.
//!
//! Each macro entry point is a thin wrapper that converts to/from
//! `proc_macro2::TokenStream` and delegates to an `expand` function, so the
//! real logic can be unit-tested outside of a compiler invocation.

use proc_macro::TokenStream;
use syn::{ItemFn, parse_macro_input};

mod checked_arith;

/// Rewrites `+`, `-` and `*` inside the annotated function into
/// `checked_add`/`checked_sub`/`checked_mul` calls that panic on overflow,
/// regardless of build profile.
///
/// ```
/// use syntax_macros::checked_arith;
///
/// #[checked_arith]
/// fn add(a: u8, b: u8) -> u8 {
///     a + b
/// }
///
/// assert_eq!(add(1, 2), 3);
/// assert!(std::panic::catch_unwind(|| add(255, 1)).is_err());
/// ```
#[proc_macro_attribute]
pub fn checked_arith(args: TokenStream, input: TokenStream) -> TokenStream {
    let item = parse_macro_input!(input as ItemFn);
    checked_arith::expand(args.into(), item)
        .unwrap_or_else(syn::Error::into_compile_error)
        .into()
}
