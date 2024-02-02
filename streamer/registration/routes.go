package registration

import (
	"io"
	"log"
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
	BUFFSIZE int = 100
)

func registerWebcam(dev int) {
	reader := readers.WebcamReader{Device: dev}

	// pref := "webcam_" + strconv.Itoa(dev)
	// w := writers.FileWriter{Prefix: pref}
	w := writers.PikaWriter{Topic: "streams", Exchange: "videostreams"}

	c := make(chan gocv.Mat)
	d := make(chan int)
	go w.Write(c, BUFFSIZE)
	go reader.Read(c, d)

	read := <-d

	log.Println("Webcam is done... add tombstone here")
	log.Println("Read " + strconv.Itoa(read) + " frames")
	close(c)

}

func registerUrl(url string) {
	reader := readers.UrlReader{Url: url}
	h := md5.New()
	io.WriteString(h, url)
	// w := writers.FileWriter{Prefix: hex.EncodeToString((h.Sum(nil)))}
	w := writers.PikaWriter{Topic: "streams", Exchange: "videostreams"}
	c := make(chan gocv.Mat)
	d := make(chan int, 1)
	// var wg sync.WaitGroup
	// wg.Add(2)
	go w.Write(c, BUFFSIZE)
	go reader.Read(c, d)
	read := <-d

	log.Println("Stream is done... add tombstone here")
	log.Println("Read " + strconv.Itoa(read) + " frames")
	close(c)
}

func registerIp() {
	log.Println("register ip")
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
			r := &schemas.ErrorUrlRegistrationResponse{Message: "Bad Request"}
			c.JSON(http.StatusBadRequest, r)
		} else {
			go registerUrl(req.Url)
			r := &schemas.UrlRegistrationResponse{Url: req.Url}
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
