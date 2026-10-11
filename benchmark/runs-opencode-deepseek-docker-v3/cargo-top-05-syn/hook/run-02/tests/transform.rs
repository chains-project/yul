use ast_transform::timed;
use quote::quote;
use syn::{ItemFn, ReturnType, Type, parse_str};

#[timed]
fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[test]
fn timed_macro_preserves_behaviour() {
    assert_eq!(add(2, 3), 5);
}

#[test]
fn parses_inspects_and_reemits_a_syntax_tree() {
    let source = "fn answer() -> u32 { 42 }";

    let mut func: ItemFn = parse_str(source).expect("valid Rust function");

    assert!(func.sig.ident == "answer");

    match &func.sig.output {
        ReturnType::Type(_, ty) => assert!(matches!(**ty, Type::Path(_))),
        ReturnType::Default => panic!("expected an explicit return type"),
    }

    func.sig.ident = syn::Ident::new("answer_transformed", func.sig.ident.span());
    let emitted = quote!(#func).to_string();

    assert!(emitted.contains("answer_transformed"));
}
