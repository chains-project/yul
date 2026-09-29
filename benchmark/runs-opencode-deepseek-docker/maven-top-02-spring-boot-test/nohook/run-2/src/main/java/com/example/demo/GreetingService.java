package com.example.demo;

import org.springframework.stereotype.Service;

@Service
public class GreetingService {

    private final MessageRepository messageRepository;

    public GreetingService(MessageRepository messageRepository) {
        this.messageRepository = messageRepository;
    }

    public String greet(String name) {
        String template = messageRepository.findTemplate();
        return "%s, %s!".formatted(template, name);
    }
}
