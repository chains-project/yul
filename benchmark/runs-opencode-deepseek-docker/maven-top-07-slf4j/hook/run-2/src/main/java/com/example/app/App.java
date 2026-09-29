package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

    private static final Logger log = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        log.info("Application starting");

        Greeter greeter = new Greeter();
        log.debug("Greeting with a name: {}", args.length > 0 ? args[0] : "World");
        System.out.println(greeter.greet(args.length > 0 ? args[0] : "World"));

        log.info("Application finished");
    }
}
