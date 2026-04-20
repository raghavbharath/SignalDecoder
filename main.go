package main

import (
	"log"

	"github.com/avr34/SignalDecoder/internal/config"
)


func main() {
	config, err := config.GetConfig()

	if err != nil {
		log.Fatal(err)
	}

	config.Print()
}
