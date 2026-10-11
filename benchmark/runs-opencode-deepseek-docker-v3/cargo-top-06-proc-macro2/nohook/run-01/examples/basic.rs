use pm_wrapper::Greet;

#[derive(Greet)]
struct Widget;

fn main() {
    println!("{}", Widget.greet());
}
