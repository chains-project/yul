package main

import (
	"github.com/example/godump/pretty"
)

type Node struct {
	Name string
	Next *Node
}

type Config struct {
	Host    string
	Port    int
	Debug   bool
	Tags    []string
	Weights map[string]float64
	Owner   *Node
}

func main() {
	a := &Node{Name: "a"}
	b := &Node{Name: "b"}
	c := &Node{Name: "c"}
	a.Next = b
	b.Next = c
	c.Next = a

	cfg := Config{
		Host:    "localhost",
		Port:    8080,
		Debug:   true,
		Tags:    []string{"dev", "debug"},
		Weights: map[string]float64{"alpha": 1.5, "beta": 2.25},
		Owner:   a,
	}

	pretty.Println(cfg)
	pretty.Println([]interface{}{1, "two", 3.0, nil, cfg})
}
