//! Procedural macros that generate Rust source as token streams.
//!
//! `proc_macro` is the compiler-facing API; all real work happens on
//! `proc_macro2::TokenStream` so the generation logic is unit-testable
//! outside of a macro expansion context.

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::{format_ident, quote};
use syn::{Data, DeriveInput, Fields, parse_macro_input};

/// Derives a `describe()` method returning the type name and its field names.
///
/// ```ignore
/// #[derive(Describe)]
/// struct Point { x: i32, y: i32 }
///
/// assert_eq!(Point::describe(), "Point { x, y }");
/// ```
#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand_describe(&input)
        .unwrap_or_else(syn::Error::into_compile_error)
        .into()
}

fn expand_describe(input: &DeriveInput) -> syn::Result<TokenStream2> {
    let name = &input.ident;
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    let field_names: Vec<String> = match &input.data {
        Data::Struct(data) => match &data.fields {
            Fields::Named(fields) => fields
                .named
                .iter()
                .map(|f| f.ident.as_ref().unwrap().to_string())
                .collect(),
            Fields::Unnamed(fields) => (0..fields.unnamed.len()).map(|i| i.to_string()).collect(),
            Fields::Unit => Vec::new(),
        },
        _ => {
            return Err(syn::Error::new_spanned(
                name,
                "#[derive(Describe)] only supports structs",
            ));
        }
    };

    let description = if field_names.is_empty() {
        name.to_string()
    } else {
        format!("{name} {{ {} }}", field_names.join(", "))
    };

    Ok(quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            pub fn describe() -> &'static str {
                #description
            }
        }
    })
}

/// Generates one getter function per identifier.
///
/// ```ignore
/// make_constants!(alpha = 1, beta = 2);
/// assert_eq!(alpha(), 1);
/// ```
#[proc_macro]
pub fn make_constants(input: TokenStream) -> TokenStream {
    let pairs = parse_macro_input!(input as ConstantList);
    expand_constants(&pairs).into()
}

struct ConstantList(Vec<(syn::Ident, syn::LitInt)>);

impl syn::parse::Parse for ConstantList {
    fn parse(input: syn::parse::ParseStream) -> syn::Result<Self> {
        let mut items = Vec::new();
        while !input.is_empty() {
            let ident: syn::Ident = input.parse()?;
            input.parse::<syn::Token![=]>()?;
            let value: syn::LitInt = input.parse()?;
            items.push((ident, value));
            if input.is_empty() {
                break;
            }
            input.parse::<syn::Token![,]>()?;
        }
        Ok(ConstantList(items))
    }
}

fn expand_constants(list: &ConstantList) -> TokenStream2 {
    let fns = list.0.iter().map(|(ident, value)| {
        let const_name = format_ident!("{}", ident.to_string().to_uppercase());
        quote! {
            pub const #const_name: i64 = #value;
            pub fn #ident() -> i64 { #const_name }
        }
    });
    quote! { #(#fns)* }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn describe_expansion_contains_fields() {
        let input: DeriveInput = syn::parse_quote! {
            struct Point { x: i32, y: i32 }
        };
        let out = expand_describe(&input).unwrap().to_string();
        assert!(out.contains("\"Point { x, y }\""), "{out}");
    }

    #[test]
    fn describe_rejects_enums() {
        let input: DeriveInput = syn::parse_quote! { enum E { A } };
        assert!(expand_describe(&input).is_err());
    }
}
