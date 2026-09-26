package com.example.demo;

import org.springframework.stereotype.Service;

@Service
public class GreetingService {

    private final GreetingRepository greetingRepository;

    public GreetingService(GreetingRepository greetingRepository) {
        this.greetingRepository = greetingRepository;
    }

    public String greet(long id) {
        String name = greetingRepository.findNameById(id);
        return "Hello, " + name + "!";
    }

}
