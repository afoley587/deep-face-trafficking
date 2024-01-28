package schemas

type RegisterUrlRequest struct {
	Url string `json:"url" binding:"required"`
}
