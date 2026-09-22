package com.example.demo;

import com.example.demo.domain.Customer;
import com.example.demo.service.CustomerService;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.ApplicationArguments;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DataInitializer {

    @Bean
    ApplicationRunner seedCustomers(CustomerService customerService) {
        return args -> {
            customerService.create("Ada", "Lovelace", "ada@example.com");
            customerService.create("Alan", "Turing", "alan@example.com");
            customerService.findAll().forEach(c ->
                    System.out.printf("Seeded customer %d: %s %s <%s>%n",
                            c.getId(), c.getFirstName(), c.getLastName(), c.getEmail()));
        };
    }
}
