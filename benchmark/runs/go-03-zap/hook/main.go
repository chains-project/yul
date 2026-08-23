package main

import "go.uber.org/zap"

func main() {
	logger, err := zap.NewProduction()
	if err != nil {
		panic(err)
	}
	defer logger.Sync()

	logger.Info("service started")
	logger.Debug("debug details", zap.String("component", "startup"))
	logger.Warn("example warning", zap.Int("retries", 0))
}
