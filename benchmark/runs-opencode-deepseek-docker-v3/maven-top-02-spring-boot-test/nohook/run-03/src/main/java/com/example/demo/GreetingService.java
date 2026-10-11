package com.example.demo;

import org.springframework.stereotype.Service;

@Service
public class GreetingService {

    private final MessageProvider messageProvider;

    public GreetingService(MessageProvider messageProvider) {
        this.messageProvider = messageProvider;
    }

    public String greet(String name) {
        return messageProvider.getMessage() + ", " + name + "!";
    }
}
