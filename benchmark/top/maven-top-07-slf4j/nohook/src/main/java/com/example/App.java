package com.example;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {

    private static final Logger logger = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        logger.info("Application starting");
        logger.debug("Debug details go here");
        logger.info("Application finished");
    }
}
