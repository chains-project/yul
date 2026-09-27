package com.example.demo.repository;

import com.example.demo.domain.Customer;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {

    Optional<Customer> findByEmail(String email);

    List<Customer> findByNameContainingIgnoreCase(String name);

    @Query("select c from Customer c where c.email like concat('%', :domain)")
    List<Customer> findByEmailDomain(String domain);
}
