//! `codegen-macros` — procedural macros that emit Rust source code.
//!
//! This crate is a `proc-macro` crate: the macros run at compile time and their
//! return value, a [`proc_macro::TokenStream`], is spliced into the call site as
//! source code.
//!
//! Token streams are built with [`quote!`] (which interpolates values prefixed
//! by `#`) and, when needed, constructed by hand via `proc_macro2`. Always
//! return `proc_macro2::TokenStream::into()` to convert back to the compiler's
//! `proc_macro::TokenStream`.

use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, Data, DeriveInput, Fields};

/// Generates a public record struct plus an impl, from a struct definition.
///
/// Every field is made public and a `field_names()` associated function is
/// added that returns the field names as string literals.
///
/// ```
/// codegen_macros::make_record! {
///     struct User {
///         id: u64,
///         name: String,
///     }
/// }
///
/// assert_eq!(User::field_names(), &["id", "name"]);
/// ```
///
/// The macro accepts a single named-field struct definition. Tuple structs,
/// unit structs, enums and unions produce a compile error.
#[proc_macro]
pub fn make_record(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;

    let fields = match &input.data {
        Data::Struct(data) => match &data.fields {
            Fields::Named(named) => &named.named,
            _ => {
                return syn::Error::new_spanned(
                    &input,
                    "make_record! only supports structs with named fields",
                )
                .to_compile_error()
                .into();
            }
        },
        _ => {
            return syn::Error::new_spanned(&input, "make_record! expects a struct definition")
                .to_compile_error()
                .into();
        }
    };

    let field_defs = fields.iter().map(|field| {
        let ident = field.ident.as_ref();
        let ty = &field.ty;
        quote! { pub #ident: #ty }
    });

    let field_names = fields.iter().map(|field| {
        field
            .ident
            .as_ref()
            .expect("named field")
            .to_string()
    });

    let expanded = quote! {
        #[derive(Clone, Debug, Default, PartialEq, Eq)]
        pub struct #name {
            #(#field_defs,)*
        }

        impl #name {
            /// Names of the struct's fields, in declaration order.
            pub fn field_names() -> &'static [&'static str] {
                &[#(#field_names),*]
            }
        }
    };

    expanded.into()
}
