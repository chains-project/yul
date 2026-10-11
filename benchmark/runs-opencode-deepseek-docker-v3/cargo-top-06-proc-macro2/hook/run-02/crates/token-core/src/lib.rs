//! Compiler-independent implementation for the `token-macros` proc-macro crate.
//!
//! This crate depends on [`proc_macro2`], which is the stable wrapper around the
//! compiler's `proc_macro` token-stream API. Because `proc_macro2` works both
//! inside and outside the compiler, all of the real macro logic lives here and
//! can be unit tested on a normal target without invoking `rustc`.

use proc_macro2::TokenStream;
use quote::quote;
use syn::{parse2, DeriveInput};

/// Expands `#[derive(Hello)]` for the item described by `input`.
///
/// Any parse error is turned into a `compile_error!` invocation rather than a
/// panic, so diagnostics point at the offending tokens.
pub fn expand_hello(input: TokenStream) -> TokenStream {
    match expand_hello_impl(input) {
        Ok(tokens) => tokens,
        Err(err) => err.to_compile_error(),
    }
}

fn expand_hello_impl(input: TokenStream) -> syn::Result<TokenStream> {
    let input: DeriveInput = parse2(input)?;
    let ident = &input.ident;

    Ok(quote! {
        impl #ident {
            pub fn hello() -> &'static str {
                stringify!(#ident)
            }
        }
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use quote::quote;

    #[test]
    fn generates_impl_with_type_name() {
        let expanded = expand_hello(quote! {
            struct Widget;
        });

        let text = expanded.to_string();
        assert!(text.contains("impl Widget"));
        assert!(text.contains("stringify ! (Widget)"));
    }

    #[test]
    fn rejects_non_item_input() {
        let error = expand_hello(quote! { fn not_an_item() {} });

        assert!(error.to_string().contains("expected"));
    }
}
