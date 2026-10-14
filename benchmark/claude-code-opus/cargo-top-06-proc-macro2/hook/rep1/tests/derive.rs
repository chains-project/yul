use my_macros::Hello;

#[derive(Hello)]
struct Greeter;

#[test]
fn derive_works() {
    assert_eq!(Greeter::hello(), "Hello from Greeter!");
}
