use proc_macro2::TokenStream;
use quote::quote;

#[proc_macro]
pub fn make_answer(_input: proc_macro::TokenStream) -> proc_macro::TokenStream {
    expand().into()
}

// All the real logic operates on `proc_macro2::TokenStream`, which (unlike
// `proc_macro::TokenStream`) can be constructed and inspected outside of a
// compiler-invoked macro context, e.g. in unit tests below.
fn expand() -> TokenStream {
    quote! {
        fn answer() -> u32 {
            42
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expands_to_expected_tokens() {
        let expected = quote! {
            fn answer() -> u32 {
                42
            }
        };
        assert_eq!(expand().to_string(), expected.to_string());
    }
}
