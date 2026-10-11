package com.example;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Greeter {

    private static final Logger log = LoggerFactory.getLogger(Greeter.class);

    public String greet(String name) {
        log.trace("greet() called with name={}", name);
        if (name == null || name.isBlank()) {
            log.warn("Blank name supplied, falling back to default");
            name = "stranger";
        }
        String message = "Hello, " + name + "!";
        log.debug("Returning message: {}", message);
        return message;
    }
}
