package com.example.demo;

import org.springframework.stereotype.Service;

@Service
public class GreetingService {

    private final PrefixProvider prefixProvider;

    public GreetingService(PrefixProvider prefixProvider) {
        this.prefixProvider = prefixProvider;
    }

    public String greet(String name) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name must not be blank");
        }
        return prefixProvider.prefix() + ", " + name.trim() + "!";
    }
}
