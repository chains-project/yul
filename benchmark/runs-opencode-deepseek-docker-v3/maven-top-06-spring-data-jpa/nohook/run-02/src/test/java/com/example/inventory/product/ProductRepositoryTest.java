package com.example.inventory.product;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

@DataJpaTest
class ProductRepositoryTest {

    @Autowired
    private ProductRepository repository;

    @Test
    void persistsAndFindsBySku() {
        repository.save(new Product("SKU-1", "Widget", new BigDecimal("9.99"), 10));

        assertThat(repository.findBySku("SKU-1"))
                .isPresent()
                .get()
                .satisfies(product -> {
                    assertThat(product.getId()).isNotNull();
                    assertThat(product.getName()).isEqualTo("Widget");
                    assertThat(product.getPrice()).isEqualByComparingTo("9.99");
                });
    }

    @Test
    void findsByNameIgnoringCase() {
        repository.save(new Product("SKU-2", "Blue Widget", new BigDecimal("1.50"), 3));
        repository.save(new Product("SKU-3", "Red Gadget", new BigDecimal("2.50"), 7));

        List<Product> matches = repository.findByNameContainingIgnoreCase("widget");

        assertThat(matches).extracting(Product::getSku).containsExactly("SKU-2");
    }
}
