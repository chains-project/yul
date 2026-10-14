package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

    private static final Logger log = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        log.info("Application starting");
        log.info(greet(args.length > 0 ? args[0] : "world"));
    }

    static String greet(String name) {
        log.debug("Building greeting for {}", name);
        return "Hello, " + name + "!";
    }
}
