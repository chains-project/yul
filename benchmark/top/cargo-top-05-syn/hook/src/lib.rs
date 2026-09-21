use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Describe)]
pub fn describe(input: TokenStream) -> TokenStream {
    let ast: DeriveInput = parse_macro_input!(input as DeriveInput);
    let name = &ast.ident;
    let description = format!("{} is a struct or enum", name);

    let expanded = quote! {
        impl #name {
            pub fn describe() -> &'static str {
                #description
            }
        }
    };

    TokenStream::from(expanded)
}
