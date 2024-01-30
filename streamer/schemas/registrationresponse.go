package schemas

type WebcamRegistrationResponse struct {
	Device int `json:"device"`
}

type UrlRegistrationResponse struct {
	Url string `json:"url"`
}

type ErrorUrlRegistrationResponse struct {
	Message string `json:"message"`
}
