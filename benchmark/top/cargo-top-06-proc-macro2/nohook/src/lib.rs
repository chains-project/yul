use proc_macro2::TokenStream;

/// Public proc-macro entry point. `proc_macro::TokenStream` only exists inside
/// the compiler, so this just converts to/from `proc_macro2::TokenStream` and
/// delegates to `expand`, which is what actually gets tested below.
#[proc_macro]
pub fn answer(input: proc_macro::TokenStream) -> proc_macro::TokenStream {
    expand(input.into()).into()
}

fn expand(input: TokenStream) -> TokenStream {
    if input.is_empty() {
        quote_num(42)
    } else {
        input
    }
}

fn quote_num(n: u64) -> TokenStream {
    n.to_string().parse().unwrap()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_input_expands_to_42() {
        let out = expand(TokenStream::new());
        assert_eq!(out.to_string(), "42");
    }

    #[test]
    fn nonempty_input_passes_through() {
        let input: TokenStream = "7".parse().unwrap();
        let out = expand(input);
        assert_eq!(out.to_string(), "7");
    }
}
