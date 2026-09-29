use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Describe)]
pub fn describe(input: TokenStream) -> TokenStream {
    let ast = parse_macro_input!(input as DeriveInput);
    let name = &ast.ident;
    let name_str = name.to_string();

    let expanded = quote! {
        impl #name {
            pub fn describe() -> &'static str {
                #name_str
            }
        }
    };

    expanded.into()
}
