//! Procedural macros that generate Rust source as token streams.

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
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

fn expand_describe(input: DeriveInput) -> syn::Result<TokenStream2> {
    let name = &input.ident;
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    let fields: Vec<String> = match &input.data {
        Data::Struct(data) => match &data.fields {
            Fields::Named(named) => named
                .named
                .iter()
                .map(|f| f.ident.as_ref().unwrap().to_string())
                .collect(),
            Fields::Unnamed(unnamed) => (0..unnamed.unnamed.len()).map(|i| i.to_string()).collect(),
            Fields::Unit => Vec::new(),
        },
        _ => {
            return Err(syn::Error::new_spanned(
                name,
                "`Describe` can only be derived for structs",
            ));
        }
    };

    let description = if fields.is_empty() {
        name.to_string()
    } else {
        format!("{name} {{ {} }}", fields.join(", "))
    };

    Ok(quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            pub fn describe() -> &'static str {
                #description
            }
        }
    })
}

/// Generates a `const fn` named `<name>_value` returning the given integer.
///
/// ```
/// codegen_macros::make_const!(answer = 42);
/// assert_eq!(answer_value(), 42);
/// ```
#[proc_macro]
pub fn make_const(input: TokenStream) -> TokenStream {
    let MakeConst { name, value } = parse_macro_input!(input as MakeConst);
    let fn_name = format_ident!("{}_value", name);
    quote! {
        pub const fn #fn_name() -> i64 {
            #value
        }
    }
    .into()
}

struct MakeConst {
    name: syn::Ident,
    value: syn::LitInt,
}

impl syn::parse::Parse for MakeConst {
    fn parse(input: syn::parse::ParseStream) -> syn::Result<Self> {
        let name = input.parse()?;
        input.parse::<syn::Token![=]>()?;
        let value = input.parse()?;
        Ok(Self { name, value })
    }
}
