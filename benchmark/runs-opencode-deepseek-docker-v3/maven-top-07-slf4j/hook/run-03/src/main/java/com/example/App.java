package com.example;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

    private static final Logger log = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        log.info("Application starting");
        Greeter greeter = new Greeter();
        log.info(greeter.greet("World"));
        log.debug("Debug detail only visible when enabled");
        log.info("Application finished");
    }
}
