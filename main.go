package main

import (
	"log"

	"github.com/ragusauce4357/ECE692-Final-Project/SignalDecoder/internal/config"
)


func main() {
	config, err := config.GetConfig()

	if err != nil {
		log.Fatal(err)
	}

	config.Print()
}
