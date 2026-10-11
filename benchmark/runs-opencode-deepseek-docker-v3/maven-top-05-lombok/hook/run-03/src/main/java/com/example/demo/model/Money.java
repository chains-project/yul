package com.example.demo.model;

import java.math.BigDecimal;
import java.util.Currency;
import lombok.Builder;
import lombok.Value;

@Value
@Builder
public class Money {

    Currency currency;
    BigDecimal amount;
}
