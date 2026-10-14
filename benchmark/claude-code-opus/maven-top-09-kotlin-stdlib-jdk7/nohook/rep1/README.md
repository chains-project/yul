# kotlin-jdk7-app

A Maven-built Kotlin project that runs on **Java 7**.

## Toolchain constraints

| Setting | Value | Why |
|---|---|---|
| Kotlin | `1.5.32` | The last Kotlin release whose compiler and stdlib still support Java 7. Kotlin 1.6+ needs Java 8 or newer. |
| `jvmTarget` | `1.6` | Kotlin never had a `1.7` target. Java 6 bytecode runs on JDK 7. In 1.5.x this target is deprecated, so you'll see a warning. |
| stdlib | `kotlin-stdlib-jdk7` | Adds JDK 7 APIs such as `AutoCloseable.use` and suppressed-exception support. The old `kotlin-stdlib-jre7` artifact is deprecated. |

**Build JDK:** the Kotlin 1.5 compiler must run on JDK 8–17. On very new JDKs it fails
to start (for example, `IllegalArgumentException: 26.0.2.1` from `JavaVersion.parse`).
The compiled output still runs on Java 7.

## Build & run

```sh
mvn package
java -cp target/classes:$HOME/.m2/repository/org/jetbrains/kotlin/kotlin-stdlib/1.5.32/kotlin-stdlib-1.5.32.jar:$HOME/.m2/repository/org/jetbrains/kotlin/kotlin-stdlib-jdk7/1.5.32/kotlin-stdlib-jdk7-1.5.32.jar com.example.MainKt
```
