package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

    private static final Logger log = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        log.info("Application starting");
        log.info(new Greeter().greet(args.length > 0 ? args[0] : "world"));
        log.info("Application finished");
    }
}
