//! Procedural macros that generate Rust source as token streams.

use proc_macro::TokenStream;
use quote::{format_ident, quote};
use syn::{Data, DeriveInput, Fields, parse_macro_input};

/// Derives a `describe()` method returning the type name and its field names.
///
/// ```
/// use codegen_macros::Describe;
///
/// #[derive(Describe)]
/// struct Point { x: i32, y: i32 }
///
/// assert_eq!(Point::describe(), "Point { x, y }");
/// ```
#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand_describe(input)
        .unwrap_or_else(syn::Error::into_compile_error)
        .into()
}

fn expand_describe(input: DeriveInput) -> syn::Result<proc_macro2::TokenStream> {
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

/// Generates a getter method for every named field: `#[getters] struct S { a: T }`
/// produces `fn get_a(&self) -> &T`.
#[proc_macro_attribute]
pub fn getters(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as DeriveInput);
    expand_getters(input)
        .unwrap_or_else(syn::Error::into_compile_error)
        .into()
}

fn expand_getters(input: DeriveInput) -> syn::Result<proc_macro2::TokenStream> {
    let name = &input.ident;
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    let Data::Struct(data) = &input.data else {
        return Err(syn::Error::new_spanned(name, "#[getters] only supports structs"));
    };
    let Fields::Named(fields) = &data.fields else {
        return Err(syn::Error::new_spanned(name, "#[getters] requires named fields"));
    };

    let methods = fields.named.iter().map(|f| {
        let field = f.ident.as_ref().unwrap();
        let ty = &f.ty;
        let getter = format_ident!("get_{}", field);
        quote! {
            pub fn #getter(&self) -> &#ty {
                &self.#field
            }
        }
    });

    Ok(quote! {
        #input

        impl #impl_generics #name #ty_generics #where_clause {
            #(#methods)*
        }
    })
}
