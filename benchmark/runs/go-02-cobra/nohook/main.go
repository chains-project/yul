package main

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

func main() {
	rootCmd := &cobra.Command{
		Use:   "mycli",
		Short: "mycli is a sample command-line tool",
	}

	var name string
	greetCmd := &cobra.Command{
		Use:   "greet",
		Short: "Print a greeting",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Printf("Hello, %s!\n", name)
		},
	}
	greetCmd.Flags().StringVarP(&name, "name", "n", "world", "name to greet")

	rootCmd.AddCommand(greetCmd)

	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}
