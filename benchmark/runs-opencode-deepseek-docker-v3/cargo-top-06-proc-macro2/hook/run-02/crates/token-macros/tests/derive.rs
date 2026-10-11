use token_macros::Hello;

#[derive(Hello)]
struct Widget;

#[test]
fn derive_expands_in_consumer_crate() {
    assert_eq!(Widget::hello(), "Widget");
}
