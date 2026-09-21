use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;

/// Function-like macro entry point required by the compiler.
///
/// The real work happens in `expand`, which is written entirely against
/// `proc_macro2::TokenStream` so it can be unit-tested outside of a
/// `proc-macro` crate (the compiler's own `proc_macro::TokenStream` only
/// exists inside an active macro expansion).
#[proc_macro]
pub fn identity(input: TokenStream) -> TokenStream {
    expand(input.into()).into()
}

fn expand(input: TokenStream2) -> TokenStream2 {
    input
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::str::FromStr;

    #[test]
    fn expand_returns_input_unchanged() {
        let input = TokenStream2::from_str("fn answer() -> u32 { 42 }").unwrap();
        let output = expand(input.clone());
        assert_eq!(input.to_string(), output.to_string());
    }
}
