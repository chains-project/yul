//! `token_macros` is a procedural-macro crate built on [`proc_macro2`], the
//! stable wrapper around the compiler's token-stream API that can also be
//! used outside of macro-expansion contexts.

extern crate proc_macro;

use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

/// Derives an associated `describe()` function returning the type's name.
#[proc_macro_derive(Describe)]
pub fn describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let ident = input.ident;
    let name = ident.to_string();

    quote! {
        impl #ident {
            pub fn describe() -> &'static str {
                #name
            }
        }
    }
    .into()
}

#[cfg(test)]
mod tests {
    use proc_macro2::TokenStream;
    use quote::quote;

    #[test]
    fn renders_tokens_outside_the_compiler() {
        let tokens: TokenStream = quote! { fn answer() -> u8 { 42 } };
        assert_eq!(tokens.to_string(), "fn answer () -> u8 { 42 }");
    }
}
