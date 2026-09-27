package com.example.demo.customer;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import java.net.URI;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
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

    @GetMapping("/{id}")
    public Customer get(@PathVariable Long id) {
        return customerService.findById(id);
    }

    @PostMapping
    public ResponseEntity<Customer> create(@Valid @RequestBody CustomerRequest request) {
        Customer created = customerService.create(request.name(), request.email());
        return ResponseEntity.created(URI.create("/api/customers/" + created.getId())).body(created);
    }

    @PutMapping("/{id}")
    public Customer update(@PathVariable Long id, @Valid @RequestBody CustomerRequest request) {
        return customerService.update(id, request.name(), request.email());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        customerService.delete(id);
        return ResponseEntity.noContent().build();
    }

    public record CustomerRequest(@NotBlank String name, @Email @NotBlank String email) {
    }
}
