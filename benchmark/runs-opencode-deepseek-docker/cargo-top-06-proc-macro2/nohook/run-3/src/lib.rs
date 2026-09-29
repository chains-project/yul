//! A minimal procedural-macro crate demonstrating the recommended pattern:
//!
//! The actual expansion logic is written against [`proc_macro2::TokenStream`],
//! the stable wrapper around the compiler's `proc_macro` API. Only a thin
//! `#[proc_macro_derive]` entry point bridges into the compiler-owned
//! `proc_macro::TokenStream`. This keeps the logic usable (and unit-testable)
//! outside of the compiler.

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

/// Expands the `Example` derive into an inherent method returning the type name.
///
/// This is the part that lives outside the compiler: it takes and returns
/// `proc_macro2` tokens, so it can be called directly from tests, build
/// scripts, or other code-generation tools.
fn expand_example(input: DeriveInput) -> TokenStream2 {
    let ident = &input.ident;
    let name = ident.to_string();

    quote! {
        impl #ident {
            pub fn type_name() -> &'static str {
                #name
            }
        }
    }
}

/// Derives an inherent `type_name` method for the annotated type.
#[proc_macro_derive(Example)]
pub fn derive_example(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand_example(input).into()
}

#[cfg(test)]
mod tests {
    use super::*;
    use quote::quote;

    #[test]
    fn expands_outside_the_compiler() {
        let input: DeriveInput = syn::parse2(quote! {
            struct Widget;
        })
        .unwrap();

        let output = expand_example(input).to_string();

        assert!(output.contains("impl Widget"));
        assert!(output.contains("fn type_name"));
        assert!(output.contains("\"Widget\""));
    }
}
