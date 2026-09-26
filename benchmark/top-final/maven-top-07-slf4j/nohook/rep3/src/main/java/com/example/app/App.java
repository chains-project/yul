package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {
    private static final Logger logger = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        logger.info("Application starting");
        System.out.println(new App().greet("world"));
    }

    public String greet(String name) {
        logger.debug("Greeting {}", name);
        return "Hello, " + name + "!";
    }
}
