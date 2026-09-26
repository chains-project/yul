use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;

#[proc_macro]
pub fn answer(_input: TokenStream) -> TokenStream {
    let expanded: TokenStream2 = quote! {
        42
    };
    expanded.into()
}
