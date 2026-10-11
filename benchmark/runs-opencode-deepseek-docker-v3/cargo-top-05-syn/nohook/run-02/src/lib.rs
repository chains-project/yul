//! A procedural-macro crate that parses Rust source code into a syntax tree it
//! can inspect and transform.
//!
//! Parsing is built on [`syn`]: the annotated item is turned into a
//! [`syn::ItemFn`] (or, for [`identifiers!`], a [`syn::File`]) and then walked
//! with `syn::visit` to inspect it and `syn::visit_mut` to rewrite it before
//! emitting the result with [`quote`].
//!
//! # Provided macros
//!
//! * [`rename`] — rewrite every occurrence of one identifier into another
//!   inside the annotated function.
//! * [`identifiers!`] — parse a string of Rust source and expand to the sorted
//!   list of every identifier it contains.

#![forbid(unsafe_code)]

mod ast;

use proc_macro::TokenStream;
use proc_macro2::Span;
use quote::quote;
use syn::parse::Parser;
use syn::{parse_macro_input, LitStr};

/// Rewrite identifiers inside the annotated function.
///
/// Arguments are supplied as string literals:
///
/// * `from` — the identifier to look for.
/// * `to` — the identifier that replaces it.
///
/// Both names must be valid Rust identifiers and `from` must actually occur in
/// the function, otherwise a compile error is emitted.
///
/// ```
/// use ast_transform::rename;
///
/// fn sum(a: i32, b: i32) -> i32 { a + b }
///
/// #[rename(from = "add", to = "sum")]
/// fn total() -> i32 { add(2, 3) }
///
/// fn main() {
///     assert_eq!(total(), 5);
/// }
/// ```
#[proc_macro_attribute]
pub fn rename(attr: TokenStream, item: TokenStream) -> TokenStream {
    let mut from: Option<String> = None;
    let mut to: Option<String> = None;

    let args = syn::meta::parser(|meta| {
        if meta.path.is_ident("from") {
            from = Some(meta.value()?.parse::<LitStr>()?.value());
            Ok(())
        } else if meta.path.is_ident("to") {
            to = Some(meta.value()?.parse::<LitStr>()?.value());
            Ok(())
        } else {
            Err(meta.error("unsupported argument; expected `from` and `to`"))
        }
    });

    if let Err(err) = args.parse(attr) {
        return err.to_compile_error().into();
    }

    let (Some(from), Some(to)) = (from, to) else {
        return error(
            "expected both `from = \"...\"` and `to = \"...\"`",
            Span::call_site(),
        );
    };

    let mut syntax = match ast::Ast::parse(item.into()) {
        Ok(syntax) => syntax,
        Err(err) => return err.to_compile_error().into(),
    };

    match syntax.rename(&from, &to) {
        Ok(0) => {
            let known = syntax
                .identifiers()
                .into_iter()
                .collect::<Vec<_>>()
                .join(", ");
            error(
                format!(
                    "`{from}` does not appear in `{}`; identifiers in scope: {known}",
                    syntax.function_name()
                ),
                syntax.function_name().span(),
            )
        }
        Ok(_) => syntax.into_token_stream().into(),
        Err(err) => err.to_compile_error().into(),
    }
}

/// Parse a string literal of Rust source and expand to the sorted list of every
/// identifier used in it.
///
/// ```
/// use ast_transform::identifiers;
///
/// const NAMES: &[&str] = identifiers!("fn add(a: i32, b: i32) -> i32 { a + b }");
///
/// fn main() {
///     assert!(NAMES.contains(&"add"));
///     assert!(NAMES.contains(&"a"));
///     assert!(NAMES.contains(&"i32"));
/// }
/// ```
#[proc_macro]
pub fn identifiers(input: TokenStream) -> TokenStream {
    let source = parse_macro_input!(input as LitStr);

    let file = match ast::Ast::parse_source(&source.value()) {
        Ok(file) => file,
        Err(err) => return err.to_compile_error().into(),
    };

    let names = ast::identifiers_in_file(&file)
        .iter()
        .map(|name| LitStr::new(name, source.span()))
        .collect::<Vec<_>>();

    quote! { &[#(#names),*] }.into()
}

/// Build a `compile_error!(...)` invocation as a token stream.
fn error(message: impl std::fmt::Display, span: Span) -> TokenStream {
    syn::Error::new(span, message).to_compile_error().into()
}
