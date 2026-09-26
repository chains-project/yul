# kotlin-jdk7-app

Maven-built Kotlin project targeting JDK 7 bytecode, using `kotlin-stdlib-jdk7`
for JDK 7 API extensions.

## Notes

- The Kotlin compiler has no literal `1.7` JVM target; `1.6` is the closest
  option and produces class file major version 50, which runs on JDK 7+.
  JVM target `1.6` support was removed in Kotlin 2.0, so this project pins
  `kotlin.version` to `1.6.21`, the last line still able to target `1.6`.
- Build with JDK 8–17 in `JAVA_HOME`. The bundled Kotlin 1.6.21 compiler
  crashes trying to parse newer JDK version strings (e.g. JDK 21+), so a very
  recent `JAVA_HOME` will fail with `IllegalArgumentException` during
  compilation even though the project's own bytecode target is unaffected.

```sh
JAVA_HOME=/path/to/jdk8-or-17 mvn compile
```
