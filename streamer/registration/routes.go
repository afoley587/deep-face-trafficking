package registration

import (
	"fmt"
	"net/http"
	"strconv"

	"streamers/schemas"

	"streamers/writers"

	"github.com/gin-gonic/gin"
	"gocv.io/x/gocv"
)

type Registration struct {
	Source string `json:"source"`
}

var Registrations []Registration

const (
	BUFFSIZE int = 1000
)

func registerWebcam(dev int) {
	frames := 0
	webcam, _ := gocv.VideoCaptureDevice(dev)
	img := gocv.NewMat()

	for {
		webcam.Read(&img)
		frames++
		if frames%BUFFSIZE == 0 {
			fmt.Println("Sending frames")
		}
	}
}

func registerUrl() {
	stream, _ := gocv.OpenVideoCapture("https://www.sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4")
	img := gocv.NewMat()
	w := writers.FileWriter{Prefix: "test"}
	c := make(chan gocv.Mat)
	read := 0
	still_reading := true

	go w.Write(c)

	for {
		still_reading = stream.Read(&img)
		if !still_reading {
			break
		}
		c <- img
		read++
	}
	fmt.Println("Stream is done... add tombstone here")
	fmt.Println("Read " + strconv.Itoa(read) + " frames")
	close(c)
}

func registerIp() {
	fmt.Println("register ip")
}

// GetSubMenuRoutes return a group of routes for submenu
func GetRegistrationRouter(router *gin.Engine) *gin.Engine {

	registrationRoutes := router.Group("/register")
	registrationRoutes.GET("/list", func(c *gin.Context) {
		c.JSON(http.StatusOK, Registrations)
	})
	registrationRoutes.POST("/url", func(c *gin.Context) {
		var req schemas.RegisterUrlRequest
		err := c.BindJSON(&req)

		if err != nil {
			c.JSON(http.StatusConflict, gin.H{
				"message": "Bad Request",
			})
		} else {
			go registerUrl()
			c.JSON(http.StatusOK, gin.H{
				"message": "Registered",
			})
		}

	})
	registrationRoutes.POST("/ip", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "pong",
		})
	})
	registrationRoutes.POST("/webcam", func(c *gin.Context) {
		dev := 0
		go registerWebcam(dev)
		r := &schemas.WebcamRegistrationResponse{Device: dev}
		Registrations = append(Registrations, Registration{Source: "webcam"})
		c.JSON(http.StatusOK, r)
	})
	return router
}
