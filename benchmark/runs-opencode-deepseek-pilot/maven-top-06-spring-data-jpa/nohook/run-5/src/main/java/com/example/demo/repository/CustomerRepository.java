package com.example.demo.repository;

import com.example.demo.domain.Customer;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {

    Optional<Customer> findByEmailIgnoreCase(String email);

    List<Customer> findByLastNameIgnoreCase(String lastName);

    boolean existsByEmailIgnoreCase(String email);
}
