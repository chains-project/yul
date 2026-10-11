package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

    private static final Logger log = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        log.info("Application starting");
        var app = new App();
        log.info("Result: {}", app.greet("world"));
        log.info("Application finished");
    }

    public String greet(String name) {
        log.debug("Greeting {}", name);
        return "Hello, " + name + "!";
    }
}
