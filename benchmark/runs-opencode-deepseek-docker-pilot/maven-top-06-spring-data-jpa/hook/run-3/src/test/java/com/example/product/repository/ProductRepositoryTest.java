package com.example.product.repository;

import com.example.product.domain.Product;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

import java.math.BigDecimal;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class ProductRepositoryTest {

    @Autowired
    private ProductRepository productRepository;

    @Test
    void savesAndFindsProduct() {
        Product saved = productRepository.save(new Product("Keyboard", "Mechanical keyboard", new BigDecimal("89.99")));

        assertThat(saved.getId()).isNotNull();
        assertThat(productRepository.findById(saved.getId()))
                .hasValueSatisfying(product -> {
                    assertThat(product.getName()).isEqualTo("Keyboard");
                    assertThat(product.getPrice()).isEqualByComparingTo("89.99");
                    assertThat(product.getCreatedAt()).isNotNull();
                });
    }

    @Test
    void findsByNameIgnoringCase() {
        productRepository.save(new Product("Wireless Mouse", null, new BigDecimal("25.00")));
        productRepository.save(new Product("Mouse Pad", null, new BigDecimal("10.00")));
        productRepository.save(new Product("Webcam", null, new BigDecimal("60.00")));

        List<Product> results = productRepository.findByNameContainingIgnoreCase("mouse");

        assertThat(results).extracting(Product::getName)
                .containsExactlyInAnyOrder("Wireless Mouse", "Mouse Pad");
    }

    @Test
    void findsExpensiveProductsOrderedByPrice() {
        productRepository.save(new Product("Cheap", null, new BigDecimal("5.00")));
        productRepository.save(new Product("Mid", null, new BigDecimal("50.00")));
        productRepository.save(new Product("Expensive", null, new BigDecimal("500.00")));

        List<Product> results = productRepository.findExpensiveProducts(new BigDecimal("50.00"));

        assertThat(results).extracting(Product::getName).containsExactly("Mid", "Expensive");
    }
}
