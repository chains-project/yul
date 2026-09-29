package dynmap

import "fmt"

func Example() {
	data := New().
		Set("user.name", "Ada").
		Set("user.age", 36).
		Set("user.tags", []string{"admin", "dev"}).
		Set("user.tags[1]", "ops").
		Delete("user.age")

	name, _ := data.GetString("user.name")
	tags, _ := data.GetSlice("user.tags")
	age, ok := data.GetInt("user.age")

	fmt.Println(name)
	fmt.Println(tags)
	fmt.Println(age, ok)
	fmt.Println(data.String())

	// Output:
	// Ada
	// [admin ops]
	// 0 false
	// {"user":{"name":"Ada","tags":["admin","ops"]}}
}
