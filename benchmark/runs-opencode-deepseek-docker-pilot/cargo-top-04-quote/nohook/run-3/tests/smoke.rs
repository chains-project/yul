use codegen_macros::{make_consts, make_fn, Describe};

make_fn!(greet);
make_consts!(3);

#[derive(Describe)]
struct Widget;

#[derive(Describe)]
enum Color {
    Red,
}

#[test]
fn function_macro_works() {
    assert_eq!(greet(), "greet");
}

#[test]
fn const_macro_works() {
    assert_eq!(CONST_0 + CONST_1 + CONST_2, 3);
}

#[test]
fn derive_macro_works() {
    assert_eq!(Widget.describe(), "a struct named Widget");
    assert_eq!(Color::Red.describe(), "an enum named Color");
}
