//! Procedural macros that programmatically generate Rust source code.
//!
//! Each entry point parses its input into a syntax tree with [`syn`], builds
//! new Rust items by composing token streams with [`quote!`], and hands the
//! resulting [`proc_macro::TokenStream`] back to the compiler as source code.
//!
//! * [`make_struct!`] — a function-like macro that emits a struct definition
//!   plus an inherent `new` constructor.
//! * [`Describe`] — a derive macro that emits a `describe` associated function
//!   summarizing the annotated type.

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::{format_ident, quote};
use syn::{parse_macro_input, Data, DeriveInput, Fields, Ident, ItemStruct};

/// Emits the given struct together with a generated `new` constructor.
///
/// Any struct form is accepted: named, tuple, or unit. Generic parameters,
/// bounds, and visibility are carried through unchanged.
///
/// ```ignore
/// make_struct! {
///     pub struct Point {
///         pub x: f64,
///         pub y: f64,
///     }
/// }
///
/// let point = Point::new(1.0, 2.0);
/// ```
#[proc_macro]
pub fn make_struct(input: TokenStream) -> TokenStream {
    let item = parse_macro_input!(input as ItemStruct);
    expand_struct(&item)
        .unwrap_or_else(syn::Error::into_compile_error)
        .into()
}

fn expand_struct(item: &ItemStruct) -> syn::Result<TokenStream2> {
    let name = &item.ident;
    let (impl_generics, ty_generics, where_clause) = item.generics.split_for_impl();

    let mut params = Vec::new();
    let constructor = match &item.fields {
        Fields::Named(named) => {
            let idents: Vec<&Ident> = named
                .named
                .iter()
                .map(|field| field.ident.as_ref().expect("named field"))
                .collect();
            for field in &named.named {
                let ident = field.ident.as_ref().expect("named field");
                let ty = &field.ty;
                params.push(quote!(#ident: #ty));
            }
            quote!(Self { #(#idents),* })
        }
        Fields::Unnamed(unnamed) => {
            let mut idents = Vec::new();
            for (index, field) in unnamed.unnamed.iter().enumerate() {
                let ident = format_ident!("field{}", index);
                let ty = &field.ty;
                params.push(quote!(#ident: #ty));
                idents.push(ident);
            }
            quote!(Self(#(#idents),*))
        }
        Fields::Unit => quote!(Self),
    };

    Ok(quote! {
        #item

        impl #impl_generics #name #ty_generics #where_clause {
            /// Constructs a value from its fields.
            pub fn new(#(#params),*) -> Self {
                #constructor
            }
        }
    })
}

/// Derives a `describe` associated function that summarizes the type.
///
/// ```ignore
/// #[derive(Describe)]
/// struct Config {
///     retries: u32,
///     timeout: u64,
/// }
///
/// assert_eq!(Config::describe(), "Config with 2 fields");
/// ```
#[proc_macro_derive(Describe)]
pub fn describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand_describe(&input)
        .unwrap_or_else(syn::Error::into_compile_error)
        .into()
}

fn expand_describe(input: &DeriveInput) -> syn::Result<TokenStream2> {
    let name = &input.ident;
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();
    let name_literal = name.to_string();
    let (count, noun) = match &input.data {
        Data::Struct(data) => (data.fields.len(), "fields"),
        Data::Enum(data) => (data.variants.len(), "variants"),
        Data::Union(_) => (0, "fields"),
    };

    Ok(quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            /// Returns a short, human-readable description of this type.
            pub fn describe() -> ::std::string::String {
                ::std::format!("{} with {} {}", #name_literal, #count, #noun)
            }
        }
    })
}
