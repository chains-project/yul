use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, Data, DeriveInput, Fields};

#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let ast = parse_macro_input!(input as DeriveInput);
    let name = &ast.ident;

    let field_names: Vec<String> = match &ast.data {
        Data::Struct(data) => match &data.fields {
            Fields::Named(fields) => fields
                .named
                .iter()
                .map(|f| f.ident.as_ref().unwrap().to_string())
                .collect(),
            _ => Vec::new(),
        },
        _ => Vec::new(),
    };

    let expanded = quote! {
        impl #name {
            pub fn describe() -> &'static [&'static str] {
                &[#(#field_names),*]
            }
        }
    };

    expanded.into()
}
