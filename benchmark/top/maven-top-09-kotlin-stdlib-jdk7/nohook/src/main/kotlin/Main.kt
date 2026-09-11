import java.io.StringReader

fun main() {
    val text = StringReader("hello from JDK 7").use { it.readText() }
    println(text)
}
