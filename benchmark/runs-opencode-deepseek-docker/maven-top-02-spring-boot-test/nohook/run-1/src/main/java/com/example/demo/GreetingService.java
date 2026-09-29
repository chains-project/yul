package com.example.demo;

import org.springframework.stereotype.Service;

@Service
public class GreetingService {

    private final NameRepository nameRepository;

    public GreetingService(NameRepository nameRepository) {
        this.nameRepository = nameRepository;
    }

    public String greet(long id) {
        return "Hello, " + nameRepository.findName(id) + "!";
    }

}
