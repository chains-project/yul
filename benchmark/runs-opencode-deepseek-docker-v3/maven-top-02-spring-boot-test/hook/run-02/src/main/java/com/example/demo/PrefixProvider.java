package com.example.demo;

import org.springframework.stereotype.Component;

@Component
public class PrefixProvider {

    public String prefix() {
        return "Hello";
    }
}
