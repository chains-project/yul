// Command godump prints a sample data structure to demonstrate the printer.
package main

import (
	"fmt"

	"example.com/godump"
)

type service struct {
	Name     string
	Replicas int
	Labels   map[string]string
	Peers    []*service
}

func main() {
	api := &service{
		Name:     "api",
		Replicas: 3,
		Labels:   map[string]string{"env": "prod", "tier": "backend"},
	}
	api.Peers = []*service{api, {Name: "worker"}}

	fmt.Println(godump.Sdump(api))
}
