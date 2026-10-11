package com.example;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

    private static final Logger log = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        log.info("Application starting");

        Greeter greeter = new Greeter();
        log.debug("Created greeter {}", greeter);
        System.out.println(greeter.greet("World"));

        log.info("Application finished");
    }
}
