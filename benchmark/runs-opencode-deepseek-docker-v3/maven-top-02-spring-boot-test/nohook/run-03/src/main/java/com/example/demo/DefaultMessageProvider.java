package com.example.demo;

import org.springframework.stereotype.Component;

@Component
public class DefaultMessageProvider implements MessageProvider {

    @Override
    public String getMessage() {
        return "Hello";
    }
}
