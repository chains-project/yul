package com.example.demo.customer;

import java.net.URI;
import java.util.List;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/customers")
public class CustomerController {

    private final CustomerService customerService;

    public CustomerController(CustomerService customerService) {
        this.customerService = customerService;
    }

    @GetMapping
    public List<Customer> list() {
        return customerService.findAll();
    }

    @PostMapping
    public ResponseEntity<Customer> create(@Valid @RequestBody CreateCustomerRequest request) {
        Customer created = customerService.create(request.name(), request.email());
        return ResponseEntity.created(URI.create("/api/customers/" + created.getId())).body(created);
    }

    public record CreateCustomerRequest(
            @NotBlank String name,
            @NotBlank @Email String email) {
    }
}
