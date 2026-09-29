package com.example.app;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OrderService {

    private static final Logger log = LoggerFactory.getLogger(OrderService.class);

    public void placeOrder(String sku, int quantity) {
        log.debug("Validating order for sku={} quantity={}", sku, quantity);

        if (quantity <= 0) {
            log.warn("Rejected order for sku={}: quantity must be positive (was {})", sku, quantity);
            throw new IllegalArgumentException("quantity must be positive");
        }

        log.info("Placed order for sku={} quantity={}", sku, quantity);
    }
}
