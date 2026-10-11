package com.example;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class App {

    private static final Logger log = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        log.info("Application started");
        log.debug("Debugging detail visible when debug logging is enabled");

        var greeter = new Greeter();
        log.info(greeter.greet("World"));

        log.info("Application finished");
    }
}
