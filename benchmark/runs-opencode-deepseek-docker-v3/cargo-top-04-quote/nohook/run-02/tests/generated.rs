use codegen_macros::{make_adder, Describe};

make_adder!(add_three, 3);

#[derive(Describe)]
struct Widget;

#[test]
fn expands_function_macro() {
    assert_eq!(add_three(4), 7);
}

#[test]
fn expands_derive_macro() {
    assert_eq!(Widget::describe(), "Widget");
}
