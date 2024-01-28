package health

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func GetHealthRouter(router *gin.Engine) *gin.Engine {
	healthRoutes := router.Group("/health")
	healthRoutes.GET("/ping", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "pong",
		})
	})
	return router
}
