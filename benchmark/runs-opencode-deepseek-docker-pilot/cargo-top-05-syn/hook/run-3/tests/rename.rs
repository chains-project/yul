use syntax_transform::rename;

#[rename(foo, bar)]
fn renamed() -> i32 {
    let foo = 1;
    foo
}

#[test]
fn attribute_macro_rewrites_the_item() {
    assert_eq!(renamed(), 1);
}
