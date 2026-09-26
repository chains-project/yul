use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;

#[proc_macro]
pub fn identity(input: TokenStream) -> TokenStream {
    let input: TokenStream2 = input.into();
    input.into()
}
