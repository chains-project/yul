use ast_macros::ast_rename;

#[ast_rename(value, count)]
fn demo() -> i32 {
    let value = 1;
    let value = value + 1;
    value
}

#[test]
fn attribute_rewrites_identifiers() {
    assert_eq!(demo(), 2);
}
