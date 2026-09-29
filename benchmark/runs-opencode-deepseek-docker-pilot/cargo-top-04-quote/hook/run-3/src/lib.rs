use proc_macro::TokenStream;
use quote::{format_ident, quote};
use syn::{parse_macro_input, Data, DeriveInput, Fields, LitStr};

#[proc_macro]
pub fn declare_fields(input: TokenStream) -> TokenStream {
    let name = parse_macro_input!(input as LitStr);
    let struct_ident = format_ident!("{}", name.value());

    quote! {
        pub struct #struct_ident {
            pub value: i64,
        }

        impl #struct_ident {
            pub fn new(value: i64) -> Self {
                Self { value }
            }
        }
    }
    .into()
}

#[proc_macro_derive(Describe, attributes(describe))]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;
    let field_names: Vec<String> = match &input.data {
        Data::Struct(data) => match &data.fields {
            Fields::Named(fields) => fields
                .named
                .iter()
                .filter_map(|f| f.ident.as_ref().map(|i| i.to_string()))
                .collect(),
            _ => Vec::new(),
        },
        _ => Vec::new(),
    };
    let field_literals = field_names.iter().map(|f| LitStr::new(f, name.span()));
    let field_count = field_names.len();

    quote! {
        impl #name {
            pub const FIELD_NAMES: [&'static str; #field_count] = [#(#field_literals),*];

            pub fn describe_fields() -> Vec<&'static str> {
                Self::FIELD_NAMES.to_vec()
            }
        }
    }
    .into()
}
