use codegen_macros::Describe;

#[allow(dead_code)]
#[derive(Describe)]
struct Config {
    retries: u32,
    timeout: u64,
}

#[allow(dead_code)]
#[derive(Describe)]
enum State {
    Idle,
    Running,
}

#[test]
fn struct_description() {
    assert_eq!(Config::describe(), "Config with 2 fields");
}

#[test]
fn enum_description() {
    assert_eq!(State::describe(), "State with 2 variants");
}
