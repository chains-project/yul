package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

    private static final Logger log = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        log.info("Application starting");

        Greeter greeter = new Greeter();
        log.info(greeter.greet("world"));

        try {
            greeter.greet(null);
        } catch (IllegalArgumentException e) {
            log.warn("Rejected invalid input", e);
        }

        log.info("Application finished");
    }
}
