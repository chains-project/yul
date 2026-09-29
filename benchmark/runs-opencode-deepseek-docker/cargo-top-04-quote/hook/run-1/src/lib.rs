//! `codegen-macro` is a procedural-macro crate that generates Rust source code
//! and hands it back to the compiler as a token stream.
//!
//! It demonstrates the two most common macro shapes:
//!
//! * [`derive@Describe`] — a derive macro that inspects a type's fields.
//! * [`define_struct!`] — a function-like macro that emits a struct plus an impl.
//!
//! Code is generated with [`quote!`], which assembles a
//! [`proc_macro2::TokenStream`] from Rust-like syntax.

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{parse_macro_input, Data, DeriveInput, Fields, ItemStruct};

/// Derive macro that adds a `field_names()` associated function listing every
/// field of the annotated struct.
///
/// ```ignore
/// #[derive(Describe)]
/// struct Point {
///     x: f64,
///     y: f64,
/// }
///
/// assert_eq!(Point::field_names(), &["x", "y"]);
/// ```
#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand_describe(&input)
        .unwrap_or_else(syn::Error::into_compile_error)
        .into()
}

/// Function-like macro that emits the struct it is given together with a
/// generated `field_names()` associated function.
///
/// ```ignore
/// define_struct! {
///     pub struct Point {
///         pub x: f64,
///         pub y: f64,
///     }
/// }
/// ```
#[proc_macro]
pub fn define_struct(input: TokenStream) -> TokenStream {
    let item = parse_macro_input!(input as ItemStruct);
    expand_define_struct(&item)
        .unwrap_or_else(syn::Error::into_compile_error)
        .into()
}

fn expand_describe(input: &DeriveInput) -> syn::Result<TokenStream2> {
    let name = &input.ident;
    let fields = match &input.data {
        Data::Struct(data) => &data.fields,
        _ => {
            return Err(syn::Error::new_spanned(
                name,
                "Describe can only be derived for structs",
            ))
        }
    };

    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();
    let names = field_names(fields);

    Ok(quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            /// Names of every field on this type.
            pub fn field_names() -> &'static [&'static str] {
                &[#(#names),*]
            }
        }
    })
}

fn expand_define_struct(item: &ItemStruct) -> syn::Result<TokenStream2> {
    let name = &item.ident;
    let (impl_generics, ty_generics, where_clause) = item.generics.split_for_impl();
    let names = field_names(&item.fields);

    Ok(quote! {
        #item

        impl #impl_generics #name #ty_generics #where_clause {
            /// Names of every field on this type.
            pub fn field_names() -> &'static [&'static str] {
                &[#(#names),*]
            }
        }
    })
}

fn field_names(fields: &Fields) -> Vec<String> {
    match fields {
        Fields::Named(fields) => fields
            .named
            .iter()
            .filter_map(|field| field.ident.as_ref().map(ToString::to_string))
            .collect(),
        Fields::Unnamed(fields) => (0..fields.unnamed.len()).map(|i| i.to_string()).collect(),
        Fields::Unit => Vec::new(),
    }
}
