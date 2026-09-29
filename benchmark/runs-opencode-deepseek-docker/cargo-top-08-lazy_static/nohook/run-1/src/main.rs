use std::sync::LazyLock;

static PRIMES: LazyLock<Vec<u64>> = LazyLock::new(|| {
    let limit = 1_000_000u64;
    let mut sieve = vec![true; limit as usize + 1];
    sieve[0] = false;
    sieve[1] = false;
    let mut p = 2u64;
    while p * p <= limit {
        if sieve[p as usize] {
            let mut multiple = p * p;
            while multiple <= limit {
                sieve[multiple as usize] = false;
                multiple += p;
            }
        }
        p += 1;
    }
    sieve
        .into_iter()
        .enumerate()
        .filter_map(|(n, is_prime)| is_prime.then_some(n as u64))
        .collect()
});

fn is_prime(n: u64) -> bool {
    PRIMES.binary_search(&n).is_ok()
}

fn main() {
    println!("primes up to 1,000,000: {}", PRIMES.len());
    println!("largest prime: {}", PRIMES.last().copied().unwrap());
    println!("is 7919 prime? {}", is_prime(7919));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn prime_count_is_correct() {
        assert_eq!(PRIMES.len(), 78_498);
    }

    #[test]
    fn smallest_and_largest() {
        assert_eq!(PRIMES.first().copied(), Some(2));
        assert_eq!(PRIMES.last().copied(), Some(999_983));
    }

    #[test]
    fn primality_members() {
        assert!(is_prime(2));
        assert!(is_prime(7919));
        assert!(!is_prime(1));
        assert!(!is_prime(7917));
    }
}
