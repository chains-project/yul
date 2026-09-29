package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Greeter {

    private static final Logger log = LoggerFactory.getLogger(Greeter.class);

    public String greet(String name) {
        log.debug("Building greeting for '{}'", name);
        return "Hello, " + name + "!";
    }
}
