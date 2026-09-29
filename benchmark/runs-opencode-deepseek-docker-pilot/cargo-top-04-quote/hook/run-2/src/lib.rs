use proc_macro::TokenStream;
use quote::{format_ident, quote};
use syn::{
    parse_macro_input, punctuated::Punctuated, Data, DeriveInput, Fields, Ident, Token,
};

/// Derive macro that generates a `describe()` method returning the field names.
///
/// ```ignore
/// #[derive(Describe)]
/// struct Point {
///     x: f32,
///     y: f32,
/// }
/// ```
#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;

    let fields: Vec<&Ident> = match &input.data {
        Data::Struct(data) => match &data.fields {
            Fields::Named(named) => named.named.iter().filter_map(|f| f.ident.as_ref()).collect(),
            _ => Vec::new(),
        },
        _ => Vec::new(),
    };
    let field_names = fields.iter().map(|ident| ident.to_string());

    let expanded = quote! {
        impl #name {
            pub fn describe(&self) -> &'static [&'static str] {
                &[#(#field_names),*]
            }
        }
    };

    expanded.into()
}

/// Function-like macro that turns identifiers into `pub const` items.
///
/// ```ignore
/// make_consts!(alpha, beta);
/// // expands to:
/// pub const ALPHA: &str = "alpha";
/// pub const BETA: &str = "beta";
/// ```
#[proc_macro]
pub fn make_consts(input: TokenStream) -> TokenStream {
    let names = parse_macro_input!(
        input with Punctuated::<Ident, Token![,]>::parse_terminated
    );

    let consts = names.iter().map(|ident| {
        let upper = format_ident!("{}", ident.to_string().to_uppercase());
        quote! {
            pub const #upper: &str = stringify!(#ident);
        }
    });

    quote! { #(#consts)* }.into()
}
