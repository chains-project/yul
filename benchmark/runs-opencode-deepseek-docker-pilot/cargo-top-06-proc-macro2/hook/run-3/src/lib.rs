use proc_macro::TokenStream as TokenStream1;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{parse_macro_input, Data, DeriveInput, Fields};

/// Derives an associated `FIELD_NAMES` constant listing every field of the type.
///
/// The macro entry point only bridges the compiler's `proc_macro::TokenStream`
/// to `proc_macro2::TokenStream`. All token processing happens in
/// [`expand_field_names`], which is written entirely against `proc-macro2` and
/// therefore runs as ordinary Rust code, including in unit tests outside the
/// compiler.
#[proc_macro_derive(FieldNames)]
pub fn field_names(input: TokenStream1) -> TokenStream1 {
    let input = parse_macro_input!(input as DeriveInput);
    expand_field_names(input).into()
}

fn expand_field_names(input: DeriveInput) -> TokenStream2 {
    let ident = &input.ident;

    let fields: Vec<String> = match &input.data {
        Data::Struct(data) => match &data.fields {
            Fields::Named(named) => named
                .named
                .iter()
                .filter_map(|field| field.ident.as_ref())
                .map(ToString::to_string)
                .collect(),
            Fields::Unnamed(unnamed) => {
                (0..unnamed.unnamed.len()).map(|i| i.to_string()).collect()
            }
            Fields::Unit => Vec::new(),
        },
        Data::Enum(_) | Data::Union(_) => Vec::new(),
    };

    quote! {
        impl #ident {
            pub const FIELD_NAMES: &'static [&'static str] = &[#(#fields),*];
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use syn::parse_quote;

    #[test]
    fn derives_names_of_named_fields() {
        let input: DeriveInput = parse_quote! {
            struct Point {
                x: i32,
                y: i32,
            }
        };

        let rendered = expand_field_names(input).to_string();
        assert!(rendered.contains("\"x\""));
        assert!(rendered.contains("\"y\""));
    }

    #[test]
    fn derives_indices_of_unnamed_fields() {
        let input: DeriveInput = parse_quote! {
            struct Pair(u8, u8);
        };

        let rendered = expand_field_names(input).to_string();
        assert!(rendered.contains("\"0\""));
        assert!(rendered.contains("\"1\""));
    }
}
