use proc_macro::TokenStream;
use tokenstream_wrapper::{parse_str, TokenStreamWrapper};

/// Demo proc-macro that generates a simple struct from a name.
///
/// Usage: `#[demo_struct] struct Foo;`
/// Generates:
/// ```ignore
/// struct Foo {
///     _private: (),
/// }
/// impl Foo {
///     pub fn new() -> Self { Self { _private: () } }
/// }
/// ```
#[proc_macro_derive(demo_struct)]
pub fn demo_struct(input: TokenStream) -> TokenStream {
    let input_str = input.to_string();

    let name = match parse_str(&input_str) {
        Ok(wrapper) => {
            let idents = wrapper.get_idents();
            if idents.is_empty() {
                let input_ts = proc_macro2::TokenStream::from(input.clone());
                return syn::Error::new_spanned(
                    &input_ts,
                    "expected a struct name",
                )
                .to_compile_error()
                .into();
            }
            idents[0].clone()
        }
        Err(e) => {
            return syn::Error::new(
                proc_macro2::Span::call_site(),
                format!("failed to parse input: {}", e),
            )
            .to_compile_error()
            .into();
        }
    };

    let generated = TokenStreamWrapper::ident(&name.to_string())
        .wrap_braces()
        .to_stream();

    generated.into()
}

/// Demo proc-macro function that generates a `println!` call.
///
/// Usage: `#[demo_print]` before a function
/// Generates a println at the start of the function.
#[proc_macro_attribute]
pub fn demo_print(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let output = parse_str(&item.to_string()).unwrap_or_else(|_| TokenStreamWrapper::new());

    let print_call = parse_str("println!(\"hello from demo!\");").unwrap_or_else(|_| TokenStreamWrapper::new());

    let mut result = TokenStreamWrapper::new();
    result.append_stream(&print_call);
    result.append_stream(&output);

    result.to_stream().into()
}