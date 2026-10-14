// Command inspect-demo shows the output of the inspect package.
package main

import "github.com/example/inspect/inspect"

type config struct {
	Name    string
	Ports   []int
	Labels  map[string]string
	Backend *config
	private bool
}

func main() {
	c := &config{
		Name:    "api",
		Ports:   []int{80, 443},
		Labels:  map[string]string{"env": "prod", "app": "web"},
		Backend: &config{Name: "db", Ports: []int{5432}},
		private: true,
	}
	c.Backend.Backend = c // cycle
	inspect.Dump(c)
}
