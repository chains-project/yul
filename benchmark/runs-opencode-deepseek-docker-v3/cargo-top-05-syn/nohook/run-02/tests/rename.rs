use ast_transform::rename;

fn sum(a: i32, b: i32) -> i32 {
    a + b
}

#[rename(from = "add", to = "sum")]
fn call_it() -> i32 {
    add(2, 3)
}

#[rename(from = "x", to = "count")]
fn locals() -> i32 {
    let x = 7;
    x
}

#[test]
fn rewrites_function_calls() {
    assert_eq!(call_it(), 5);
}

#[test]
fn rewrites_bindings_and_their_uses() {
    assert_eq!(locals(), 7);
}
