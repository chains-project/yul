package com.example.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Map;
import java.util.Properties;
import org.junit.jupiter.api.Test;

class DatabaseConfigTest {

    private static Properties props(String... kv) {
        Properties p = new Properties();
        for (int i = 0; i < kv.length; i += 2) p.setProperty(kv[i], kv[i + 1]);
        return p;
    }

    @Test
    void fallsBackToDefaults() {
        var cfg = DatabaseConfig.load(Map.of(), new Properties(),
                props("db.url", "jdbc:mysql://h/d", "db.user", "u", "db.password", "p"));
        assertEquals(new DatabaseConfig("jdbc:mysql://h/d", "u", "p"), cfg);
    }

    @Test
    void systemPropertyBeatsEnvBeatsDefaults() {
        var cfg = DatabaseConfig.load(
                Map.of("DB_URL", "jdbc:mysql://env/d", "DB_USER", "envUser"),
                props("db.url", "jdbc:mysql://sys/d"),
                props("db.url", "jdbc:mysql://def/d", "db.user", "defUser", "db.password", "defPw"));
        assertEquals(new DatabaseConfig("jdbc:mysql://sys/d", "envUser", "defPw"), cfg);
    }

    @Test
    void missingUrlFails() {
        assertThrows(IllegalStateException.class,
                () -> DatabaseConfig.load(Map.of(), new Properties(), new Properties()));
    }

    @Test
    void toStringMasksPassword() {
        assertFalse(new DatabaseConfig("u", "x", "secret").toString().contains("secret"));
    }

    @Test
    void mysqlDriverIsOnClasspath() throws Exception {
        Class.forName("com.mysql.cj.jdbc.Driver");
    }
}
