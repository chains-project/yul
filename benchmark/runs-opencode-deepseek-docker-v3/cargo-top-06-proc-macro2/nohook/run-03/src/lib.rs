use proc_macro::TokenStream;

mod stable;

#[proc_macro]
pub fn count_tokens(input: TokenStream) -> TokenStream {
    stable::count_tokens(input.into()).into()
}

#[proc_macro]
pub fn tokens_as_str(input: TokenStream) -> TokenStream {
    stable::tokens_as_str(input.into()).into()
}

#[proc_macro_derive(TokenCount)]
pub fn derive_token_count(input: TokenStream) -> TokenStream {
    stable::derive_token_count(input.into()).into()
}
