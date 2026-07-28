package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class App {
    private static final Logger log = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        MDC.put("requestId", "startup");
        log.info("Application starting");
        log.warn("Example warning with a field: {}", "diskUsage=87%");
        MDC.clear();
    }
}
