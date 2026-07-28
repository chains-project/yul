package com.example.app;

import net.logstash.logback.argument.StructuredArguments;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {
  private static final Logger log = LoggerFactory.getLogger(App.class);

  public static void main(String[] args) {
    log.info("application starting", StructuredArguments.keyValue("version", "1.0.0-SNAPSHOT"));
    log.info("processing request", StructuredArguments.keyValue("userId", 42), StructuredArguments.keyValue("action", "login"));
  }
}
