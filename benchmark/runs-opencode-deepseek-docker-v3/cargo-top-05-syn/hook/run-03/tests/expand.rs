//! End-to-end test: invoke the proc macro and confirm the emitted items are
//! callable from the surrounding crate.

ast_transform::transform! {
    fn greet() -> &'static str {
        "hello"
    }
}

#[test]
fn macro_rewrites_function_names() {
    assert_eq!(greet_transformed(), "hello");
}
