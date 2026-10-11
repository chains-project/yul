package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Greeter {

    private static final Logger log = LoggerFactory.getLogger(Greeter.class);

    public String greet(String name) {
        if (name == null || name.isBlank()) {
            log.warn("Received blank name; defaulting to 'World'");
            name = "World";
        }
        log.debug("Building greeting for {}", name);
        return "Hello, " + name + "!";
    }
}
