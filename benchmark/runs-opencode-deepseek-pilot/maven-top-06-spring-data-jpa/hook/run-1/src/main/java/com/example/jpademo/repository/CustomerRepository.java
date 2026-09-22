package com.example.jpademo.repository;

import com.example.jpademo.model.Customer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {

    Optional<Customer> findByEmail(String email);

    List<Customer> findByLastNameIgnoreCase(String lastName);

    boolean existsByEmail(String email);
}
