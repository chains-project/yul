use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::LitInt;

#[proc_macro]
pub fn make_answer(input: TokenStream) -> TokenStream {
    expand(TokenStream2::from(input)).into()
}

fn expand(input: TokenStream2) -> TokenStream2 {
    let n: LitInt = syn::parse2(input).expect("expected an integer literal");
    quote! { #n }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expands_outside_the_compiler() {
        let output = expand(quote! { 42 });
        assert_eq!(output.to_string(), "42");
    }
}
