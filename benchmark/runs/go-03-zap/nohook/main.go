package main

import (
	"go.uber.org/zap"
)

func main() {
	logger, err := zap.NewProduction()
	if err != nil {
		panic(err)
	}
	defer logger.Sync()

	logger.Info("service starting",
		zap.String("env", "production"),
	)
	logger.Warn("example warning",
		zap.Int("retry_count", 3),
	)
}
