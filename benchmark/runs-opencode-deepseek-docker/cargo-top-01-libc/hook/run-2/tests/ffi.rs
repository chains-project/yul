use sys_tool::{cpu_count, fnv1a, parse_i64, process_name};

#[test]
fn fnv1a_empty_buffer_matches_reference() {
    assert_eq!(fnv1a(b""), 0xcbf2_9ce4_8422_2325);
}

#[test]
fn fnv1a_known_vectors() {
    assert_eq!(fnv1a(b"hello"), 0xa430_d846_80aa_bd0b);
    assert_eq!(fnv1a(b"sys-tool"), 0x799a_4263_48a9_c6e3);
}

#[test]
fn parse_i64_accepts_and_rejects() {
    assert_eq!(parse_i64("12345").unwrap(), 12345);
    assert_eq!(parse_i64("-42").unwrap(), -42);
    assert!(parse_i64("notanumber").is_err());
    assert!(parse_i64("12x").is_err());
}

#[test]
fn process_name_is_non_empty() {
    let name = process_name().unwrap();
    assert!(!name.is_empty());
}

#[test]
fn cpu_count_is_positive() {
    assert!(cpu_count().unwrap() >= 1);
}
