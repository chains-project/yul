package com.example.demo;

import com.example.demo.model.Product;
import com.example.demo.repository.ProductRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class ProductRepositoryTest {

    @Autowired
    private ProductRepository productRepository;

    @Test
    void savesAndFindsAProduct() {
        Product saved = productRepository.save(new Product("Widget", 9.99));

        assertThat(productRepository.findById(saved.getId()))
                .isPresent()
                .get()
                .extracting(Product::getName)
                .isEqualTo("Widget");
    }
}
