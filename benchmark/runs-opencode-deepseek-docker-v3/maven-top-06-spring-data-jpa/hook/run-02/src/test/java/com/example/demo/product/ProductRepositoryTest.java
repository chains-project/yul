package com.example.demo.product;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

@DataJpaTest
class ProductRepositoryTest {

    @Autowired
    private ProductRepository repository;

    @Test
    void savesAndFindsBySku() {
        repository.saveAndFlush(new Product("Espresso Machine", "ESP-001", new BigDecimal("249.99")));

        assertThat(repository.findBySku("ESP-001"))
                .isPresent()
                .get()
                .extracting(Product::getName)
                .isEqualTo("Espresso Machine");
    }

    @Test
    void detectsExistingSku() {
        repository.saveAndFlush(new Product("Grinder", "GRD-001", new BigDecimal("89.00")));

        assertThat(repository.existsBySku("GRD-001")).isTrue();
        assertThat(repository.existsBySku("MISSING")).isFalse();
    }

    @Test
    void findsByNameCaseInsensitively() {
        repository.saveAndFlush(new Product("Milk Frother", "FRH-001", new BigDecimal("39.50")));

        assertThat(repository.findByNameContainingIgnoreCase("frother")).hasSize(1);
    }

    @Test
    void findsByPriceRange() {
        repository.saveAndFlush(new Product("Cheap", "CHP-001", new BigDecimal("10.00")));
        repository.saveAndFlush(new Product("Mid", "MID-001", new BigDecimal("50.00")));
        repository.saveAndFlush(new Product("Pricey", "PRC-001", new BigDecimal("500.00")));

        assertThat(repository.findByPriceRange(new BigDecimal("20.00"), new BigDecimal("100.00")))
                .extracting(Product::getSku)
                .containsExactly("MID-001");
    }
}
