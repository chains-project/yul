use proc_macro::TokenStream;

#[proc_macro]
pub fn my_macro(input: TokenStream) -> TokenStream {
    expand(input.into()).into()
}

fn expand(input: proc_macro2::TokenStream) -> proc_macro2::TokenStream {
    input
}

#[cfg(test)]
mod tests {
    use super::expand;
    use proc_macro2::TokenStream;
    use std::str::FromStr;

    #[test]
    fn passes_input_through() {
        let input = TokenStream::from_str("1 + 1").unwrap();
        let output = expand(input.clone());
        assert_eq!(input.to_string(), output.to_string());
    }
}
