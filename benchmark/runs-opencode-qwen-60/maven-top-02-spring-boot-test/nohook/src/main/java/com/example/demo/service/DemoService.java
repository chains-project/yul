package com.example.demo.service;

import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DemoService {

    public String greet(String name) {
        if (name == null || name.isBlank()) {
            return "Hello, Guest!";
        }
        return "Hello, " + name + "!";
    }

    public List<String> getNames(List<String> input) {
        return input;
    }
}