package registration

import (
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"strconv"

	"crypto/md5"
	"streamers/readers"
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
	reader := readers.WebcamReader{Device: dev}

	pref := "webcam_" + strconv.Itoa(dev)
	w := writers.FileWriter{Prefix: pref}
	c := make(chan gocv.Mat)
	d := make(chan int)
	go w.Write(c)
	go reader.Read(c, d)

	read := <-d

	fmt.Println("Webcam is done... add tombstone here")
	fmt.Println("Read " + strconv.Itoa(read) + " frames")
	close(c)

}

func registerUrl(url string) {
	reader := readers.UrlReader{Url: url}
	h := md5.New()
	io.WriteString(h, url)
	w := writers.FileWriter{Prefix: hex.EncodeToString((h.Sum(nil)))}
	c := make(chan gocv.Mat)
	d := make(chan int)
	// var wg sync.WaitGroup
	// wg.Add(2)
	go w.Write(c)
	go reader.Read(c, d)

	read := <-d

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
			url := "https://www.sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
			go registerUrl(url)
			r := &schemas.UrlRegistrationResponse{Url: url}
			Registrations = append(Registrations, Registration{Source: "url"})
			c.JSON(http.StatusOK, r)

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
