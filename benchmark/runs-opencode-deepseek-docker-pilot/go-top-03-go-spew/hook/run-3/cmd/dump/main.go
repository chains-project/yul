package main

import (
	"github.com/davecgh/go-spew/spew"

	"debugtool/inspect"
)

type Server struct {
	Name     string
	Port     int
	Tags     []string
	Labels   map[string]any
	peers    map[*Server]bool
	Callback func(int) error
}

func main() {
	primary := &Server{
		Name: "primary",
		Port: 8080,
		Tags: []string{"prod", "api"},
		Labels: map[string]any{
			"region": "us-east-1",
			"zone":   3,
		},
	}

	replica := &Server{
		Name:   "replica",
		Port:   8081,
		Tags:   []string{"prod", "replica"},
		Labels: map[string]any{"region": "us-west-2"},
	}

	primary.peers = map[*Server]bool{replica: true}
	replica.peers = map[*Server]bool{primary: true}

	inspect.Dump(primary)

	spew.Config = inspect.Config
	spew.Printf("config: %#v\n", primary.Labels)
}
