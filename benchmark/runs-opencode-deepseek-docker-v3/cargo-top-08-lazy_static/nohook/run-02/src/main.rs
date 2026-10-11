use std::collections::HashSet;
use std::sync::LazyLock;

const LIMIT: u32 = 100;

static PRIMES: LazyLock<HashSet<u32>> = LazyLock::new(|| {
    let mut sieve = vec![true; (LIMIT + 1) as usize];
    sieve[0] = false;
    sieve[1] = false;

    let mut n = 2;
    while n * n <= LIMIT {
        if sieve[n as usize] {
            let mut multiple = n * n;
            while multiple <= LIMIT {
                sieve[multiple as usize] = false;
                multiple += n;
            }
        }
        n += 1;
    }

    sieve
        .into_iter()
        .enumerate()
        .filter_map(|(value, is_prime)| is_prime.then_some(value as u32))
        .collect()
});

fn main() {
    for n in 2..=20 {
        if PRIMES.contains(&n) {
            println!("{n} is prime");
        }
    }

    println!("computed {} primes up to {LIMIT}", PRIMES.len());
}
