package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class App {

    private static final Logger log = LoggerFactory.getLogger(App.class);

    private App() {
    }

    public static void main(String[] args) {
        log.info("Application starting");
        Greeter greeter = new Greeter();
        log.debug("Created greeter: {}", greeter);
        String message = greeter.greet("World");
        log.info("Greeting produced: {}", message);
        log.info("Application finished");
    }
}
