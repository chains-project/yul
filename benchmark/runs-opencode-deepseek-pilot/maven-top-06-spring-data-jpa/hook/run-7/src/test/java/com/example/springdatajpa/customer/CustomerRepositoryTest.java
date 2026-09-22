package com.example.springdatajpa.customer;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

@DataJpaTest
class CustomerRepositoryTest {

	@Autowired
	private CustomerRepository customerRepository;

	@Test
	void savesAndFindsCustomerByEmail() {
		Customer saved = customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

		Optional<Customer> found = customerRepository.findByEmail("ada@example.com");

		assertThat(found).isPresent();
		assertThat(found.get().getId()).isEqualTo(saved.getId());
		assertThat(found.get().getFirstName()).isEqualTo("Ada");
	}

	@Test
	void findsCustomersByLastName() {
		customerRepository.save(new Customer("Grace", "Hopper", "grace@example.com"));
		customerRepository.save(new Customer("Ada", "Lovelace", "ada@example.com"));

		assertThat(customerRepository.findByLastName("Hopper")).hasSize(1);
	}

}
