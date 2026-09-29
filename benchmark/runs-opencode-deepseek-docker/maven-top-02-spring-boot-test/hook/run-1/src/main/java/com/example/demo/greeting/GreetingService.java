package com.example.demo.greeting;

import org.springframework.stereotype.Service;

@Service
public class GreetingService {

    private final GreetingRepository repository;

    public GreetingService(GreetingRepository repository) {
        this.repository = repository;
    }

    public String greet(long id) {
        String name = this.repository.findName(id);
        return "Hello, " + name + "!";
    }

}
