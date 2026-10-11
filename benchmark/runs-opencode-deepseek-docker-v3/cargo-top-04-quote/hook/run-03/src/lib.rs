//! `codegen-macros` demonstrates generating Rust source code as a token stream.
//!
//! Code generation lives in [`codegen`], which operates on
//! [`proc_macro2::TokenStream`] and is unit testable. The `#[proc_macro]`
//! entry points below are thin wrappers that bridge to `proc_macro`.

mod codegen;

use proc_macro::TokenStream;

/// Expands to a function `answer` returning `42`.
///
/// ```ignore
/// codegen_macros::make_answer!();
/// ```
#[proc_macro]
pub fn make_answer(_input: TokenStream) -> TokenStream {
    codegen::make_answer().into()
}

/// Expands to a function with the given name returning the given value.
///
/// ```ignore
/// codegen_macros::const_fn!(meaning, 42);
/// ```
#[proc_macro]
pub fn const_fn(input: TokenStream) -> TokenStream {
    use syn::parse::Parser;

    let parser = |input: syn::parse::ParseStream| {
        let name: syn::Ident = input.parse()?;
        input.parse::<syn::Token![,]>()?;
        let value: syn::LitInt = input.parse()?;
        syn::Result::Ok((name, value))
    };

    let (name, value) = match parser.parse(input) {
        Ok(parsed) => parsed,
        Err(err) => return err.to_compile_error().into(),
    };

    codegen::const_ident_function(&name, value.base10_parse().unwrap_or(0)).into()
}
