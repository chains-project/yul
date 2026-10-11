use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::parse_macro_input;

/// Expands to a function that returns the answer to everything.
///
/// The [`proc_macro::TokenStream`] boundary is only handled here; the
/// expansion itself is written against [`proc_macro2::TokenStream`] so it can
/// live and be tested outside the compiler.
#[proc_macro]
pub fn make_answer(input: TokenStream) -> TokenStream {
    let output = expand(parse_macro_input!(input as syn::ItemFn));
    output.into()
}

fn expand(func: syn::ItemFn) -> TokenStream2 {
    let name = &func.sig.ident;
    let vis = &func.vis;
    let attrs = &func.attrs;
    quote! {
        #(#attrs)*
        #vis fn #name() -> u32 {
            42
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use quote::quote;

    #[test]
    fn expands_to_constant_function() {
        let input = quote! {
            pub fn answer() -> u32 { 0 }
        };
        let parsed: syn::ItemFn = syn::parse2(input).unwrap();
        let output = expand(parsed).to_string();
        assert!(output.contains("pub fn answer"));
        assert!(output.contains("42"));
    }
}
