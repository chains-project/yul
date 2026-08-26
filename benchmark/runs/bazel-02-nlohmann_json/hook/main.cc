#include <iostream>

#include <nlohmann/json.hpp>

int main() {
    nlohmann::json input = nlohmann::json::parse(R"({"name": "yul", "stars": 42})");
    std::cout << "name = " << input["name"].get<std::string>() << '\n';

    nlohmann::json output;
    output["name"] = input["name"];
    output["stars"] = input["stars"].get<int>() + 1;
    std::cout << output.dump(2) << '\n';

    return 0;
}
