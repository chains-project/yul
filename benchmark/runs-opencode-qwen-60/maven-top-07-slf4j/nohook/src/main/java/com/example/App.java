package com.example;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {
    private static final Logger logger = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        logger.info("Application starting...");
        logger.debug("Debug message - not shown by default");

        App app = new App();
        String result = app.process("SLF4J");
        logger.info("Result: {}", result);

        logger.info("Application finished successfully");
    }

    public String process(String input) {
        logger.debug("Processing input: {}", input);
        if (input == null || input.isEmpty()) {
            logger.warn("Received empty or null input");
            return "No input provided";
        }
        return "Hello from " + input + "!";
    }
}