use proc_macro2::TokenStream;
use quote::quote;
use syn::DeriveInput;

pub fn describe(input: &DeriveInput) -> TokenStream {
    let ident = &input.ident;
    let name = ident.to_string();
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    quote! {
        impl #impl_generics #ident #ty_generics #where_clause {
            pub fn describe() -> &'static str {
                #name
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use syn::parse_quote;

    #[test]
    fn describes_a_unit_struct() {
        let input: DeriveInput = parse_quote! {
            struct Widget;
        };

        let expanded = describe(&input).to_string();

        assert!(expanded.contains("impl Widget"));
        assert!(expanded.contains("\"Widget\""));
    }

    #[test]
    fn preserves_generics() {
        let input: DeriveInput = parse_quote! {
            struct Holder<T> where T: Clone {
                value: T,
            }
        };

        let expanded = describe(&input).to_string();

        assert!(expanded.contains("impl < T > Holder < T > where T : Clone"));
        assert!(expanded.contains("\"Holder\""));
    }
}
