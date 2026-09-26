use proc_macro::TokenStream;
use quote::quote;

/// Does the actual work using `proc_macro2::TokenStream`, which — unlike
/// `proc_macro::TokenStream` — isn't tied to the compiler's macro context,
/// so this function can be called directly from unit tests below.
fn answer_impl(input: proc_macro2::TokenStream) -> proc_macro2::TokenStream {
    if !input.is_empty() {
        panic!("answer! takes no arguments");
    }
    quote! { 42 }
}

#[proc_macro]
pub fn answer(input: TokenStream) -> TokenStream {
    answer_impl(input.into()).into()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expands_to_42() {
        let expanded = answer_impl(proc_macro2::TokenStream::new());
        assert_eq!(expanded.to_string(), "42");
    }
}
