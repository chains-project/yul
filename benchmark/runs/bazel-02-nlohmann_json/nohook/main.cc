#include <iostream>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
    // Parse JSON from a string.
    json parsed = json::parse(R"({"name": "Ada Lovelace", "year": 1815})");
    std::cout << "Parsed name: " << parsed["name"].get<std::string>() << "\n";

    // Generate JSON from data.
    json generated;
    generated["language"] = "C++";
    generated["uses_bzlmod"] = true;
    generated["dependencies"] = {"nlohmann_json"};

    std::cout << "Generated: " << generated.dump(2) << "\n";
    return 0;
}
