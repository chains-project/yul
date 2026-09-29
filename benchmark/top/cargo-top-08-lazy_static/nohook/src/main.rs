use lazy_static::lazy_static;
use std::collections::HashMap;

lazy_static! {
    static ref CONFIG: HashMap<&'static str, String> = {
        let mut m = HashMap::new();
        m.insert("started_at", format!("{:?}", std::time::SystemTime::now()));
        m.insert("pid", std::process::id().to_string());
        m
    };
}

fn main() {
    println!("pid: {}", CONFIG["pid"]);
    println!("started_at: {}", CONFIG["started_at"]);
}
