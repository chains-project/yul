use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;

#[proc_macro]
pub fn identity(input: TokenStream) -> TokenStream {
    let tokens: TokenStream2 = input.into();
    expand(tokens).into()
}

fn expand(tokens: TokenStream2) -> TokenStream2 {
    tokens
}
