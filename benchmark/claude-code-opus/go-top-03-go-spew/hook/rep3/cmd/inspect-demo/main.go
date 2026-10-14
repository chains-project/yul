// Command inspect-demo shows the inspect package in action.
package main

import "github.com/example/inspect/inspect"

type Config struct {
	Name    string
	Ports   []int
	Labels  map[string]string
	Backend *Backend
}

type Backend struct {
	Host string
	TLS  bool
}

func main() {
	inspect.Dump(Config{
		Name:    "svc",
		Ports:   []int{80, 443},
		Labels:  map[string]string{"env": "prod", "app": "web"},
		Backend: &Backend{Host: "10.0.0.1", TLS: true},
	})
}
