use codegen_macro::{make_fn, with_name, Getters};

make_fn!(hello);

#[with_name]
fn greet() {}

#[derive(Getters)]
struct User {
    name: String,
    email: String,
}

#[test]
fn generates_function() {
    assert_eq!(hello(), "hello");
}

#[test]
fn attribute_preserves_item_and_adds_code() {
    greet();
    assert_eq!(GREET, "greet");
}

#[test]
fn derives_getters() {
    let user = User {
        name: "Ada".to_owned(),
        email: "ada@example.com".to_owned(),
    };
    assert_eq!(user.get_name(), "Ada");
    assert_eq!(user.get_email(), "ada@example.com");
}
