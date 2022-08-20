package main

import (
	"crypto/sha256"
	"encoding/hex"
	"net/http"

	"github.com/go-chi/render"
)

type ErrResponse struct {
	Err            error `json:"-"` // low-level runtime error
	HTTPStatusCode int   `json:"-"` // http response status code

	StatusText string `json:"status"`          // user-level status message
	AppCode    int64  `json:"code,omitempty"`  // application-specific error code
	ErrorText  string `json:"error,omitempty"` // application-level error message, for debugging
}

func (e *ErrResponse) Render(w http.ResponseWriter, r *http.Request) error {
	render.Status(r, e.HTTPStatusCode)
	return nil
}

func ErrInvalidRequest(err error) render.Renderer {
	return &ErrResponse{
		Err:            err,
		HTTPStatusCode: 400,
		StatusText:     "Invalid request.",
		ErrorText:      err.Error(),
	}
}

func ErrRender(err error) render.Renderer {
	return &ErrResponse{
		Err:            err,
		HTTPStatusCode: 422,
		StatusText:     "Error rendering response.",
		ErrorText:      err.Error(),
	}
}

type UserData struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func (u *UserData) Bind(r *http.Request) error {
	return nil
}

func HashHex(str string) string {
	hasher := sha256.New()
	hasher.Write([]byte(str))
	return hex.EncodeToString(hasher.Sum(nil))
}

func Hash(b []byte) []byte {
	hasher := sha256.New()
	hasher.Write([]byte(b))
	return hasher.Sum(nil)
}

// func Key(token uint16, filename string) string {
// 	key := make([]byte, 2)
// 	binary.LittleEndian.PutUint16(key, token)
// 	key = append(key, []byte(filename)...)
// 	keyStr := hex.EncodeToString(Hash(key)[:8])
// 	return keyStr
// }
