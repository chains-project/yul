use lazy_static::lazy_static;
use std::collections::HashMap;
use std::env;

lazy_static! {
    static ref CONFIG: HashMap<String, String> = {
        let mut m = HashMap::new();
        for (key, value) in env::vars() {
            m.insert(key, value);
        }
        m.insert("started_at".to_string(), format!("{:?}", std::time::SystemTime::now()));
        m
    };
}

fn main() {
    println!("Loaded {} config entries", CONFIG.len());
    if let Some(started_at) = CONFIG.get("started_at") {
        println!("started_at = {started_at}");
    }
}
