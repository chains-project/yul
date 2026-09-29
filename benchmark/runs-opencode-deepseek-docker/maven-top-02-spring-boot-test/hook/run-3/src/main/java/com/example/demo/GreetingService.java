package com.example.demo;

import org.springframework.stereotype.Service;

@Service
public class GreetingService {

    private final GreetingRepository repository;

    public GreetingService(GreetingRepository repository) {
        this.repository = repository;
    }

    public String greet(long id) {
        return "Hello, " + repository.findName(id) + "!";
    }
}
