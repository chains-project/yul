package com.example.demo.customer;

import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface CustomerRepository extends JpaRepository<Customer, Long> {

    Optional<Customer> findByEmail(String email);

    List<Customer> findByNameContainingIgnoreCase(String name);

    @Query("select c from Customer c where lower(c.email) = lower(:email)")
    Optional<Customer> findByEmailIgnoreCase(@Param("email") String email);
}
