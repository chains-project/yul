package com.example.product.repository;

import com.example.product.domain.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    List<Product> findByNameContainingIgnoreCase(String name);

    List<Product> findByPriceBetween(BigDecimal min, BigDecimal max);

    @Query("select p from Product p where p.price >= :min order by p.price asc")
    List<Product> findExpensiveProducts(@Param("min") BigDecimal min);
}
