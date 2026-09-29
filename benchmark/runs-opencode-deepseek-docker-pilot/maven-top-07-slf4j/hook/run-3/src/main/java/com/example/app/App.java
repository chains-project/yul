package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class App {

    private static final Logger log = LoggerFactory.getLogger(App.class);

    private App() {
    }

    public static void main(String[] args) {
        log.info("Application starting");
        log.debug("Debug detail is hidden unless the level is enabled");
        log.warn("Example warning");
        log.info("Application finished");
    }
}
