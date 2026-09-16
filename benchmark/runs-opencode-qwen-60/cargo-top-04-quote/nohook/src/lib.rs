use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

/// Derives a simple struct that programmatically generates implementation code
/// using token streams. This demonstrates:
/// - Parsing input via syn
/// - Generating code via quote
/// - Returning TokenStream output
#[proc_macro_derive(TypedInfo)]
pub fn derive_typed_info(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;

    // Programmatically generate Rust source code as a token stream
    let expanded = quote! {
        impl #name {
            /// Returns the type name of this struct at runtime
            pub fn type_name() -> &'static str {
                stringify!(#name)
            }
        }
    };

    TokenStream::from(expanded)
}