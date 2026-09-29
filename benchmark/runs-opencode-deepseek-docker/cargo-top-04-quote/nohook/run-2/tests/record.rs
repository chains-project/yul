use codegen_macros::make_record;

make_record! {
    struct User {
        id: u64,
        name: String,
    }
}

#[test]
fn generates_struct_with_public_fields() {
    let user = User {
        id: 1,
        name: "Ada".to_owned(),
    };

    assert_eq!(user.id, 1);
    assert_eq!(user.name, "Ada");
}

#[test]
fn generates_field_names_impl() {
    assert_eq!(User::field_names(), &["id", "name"]);
}

#[test]
fn generates_derives() {
    let user = User {
        id: 1,
        name: "Ada".to_owned(),
    };

    assert_eq!(user, user.clone());
    assert_eq!(User::default(), User::default());
}
