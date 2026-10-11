use proc_macro2::TokenStream;
use quote::quote;
use syn::{DeriveInput, parse2};

pub(crate) fn greet(input: TokenStream) -> TokenStream {
    let input = match parse2::<DeriveInput>(input) {
        Ok(input) => input,
        Err(err) => return err.to_compile_error(),
    };

    let name = &input.ident;

    quote! {
        impl #name {
            pub fn greet(&self) -> ::std::string::String {
                ::std::format!("Hello from {}!", ::std::stringify!(#name))
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::greet;
    use quote::quote;

    #[test]
    fn expands_without_the_compiler() {
        let output = greet(quote! {
            struct Widget;
        })
        .to_string();

        assert!(output.contains("impl Widget"));
        assert!(output.contains("fn greet"));
    }

    #[test]
    fn reports_parse_errors_as_tokens() {
        let output = greet(quote! { not valid rust }).to_string();

        assert!(output.contains("compile_error"));
    }
}
