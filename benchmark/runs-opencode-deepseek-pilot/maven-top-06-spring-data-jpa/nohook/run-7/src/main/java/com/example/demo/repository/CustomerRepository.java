package com.example.demo.repository;

import com.example.demo.domain.Customer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface CustomerRepository extends JpaRepository<Customer, Long> {

    Optional<Customer> findByEmail(String email);

    List<Customer> findByLastName(String lastName);

    boolean existsByEmail(String email);

    @Query("select c from Customer c where lower(c.firstName) like lower(concat(:term, '%'))")
    List<Customer> findByFirstNameStartingWithIgnoreCase(@Param("term") String term);
}
