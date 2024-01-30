package main

import (
	"streamers/health"
	"streamers/registration"

	"github.com/gin-gonic/gin"
)

// type Stream struct {
// 	Reader io.
// }

// routes required:
// 1. to register a new webcam:
//		a. from url
//		b. from ip
//		c. from webcam :check:
// 2. to list streams and such
// 3. health endpoints

func main() {
	r := gin.Default()
	registration.GetRegistrationRouter(r)
	health.GetHealthRouter(r)
	r.Run() // listen and serve on 0.0.0.0:8080 (for windows "localhost:8080")
}
