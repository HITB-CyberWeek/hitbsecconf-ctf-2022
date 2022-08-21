package main

import (
	"fmt"
	"net/http"

	"github.com/go-chi/render"
	"github.com/go-redis/redis/v8"
	"github.com/google/uuid"
)

type RegisterResp struct {
	ClientID     string `json:"client_id"`
	ClientSecret string `json:"client_secret"`
}

func (rd *RegisterResp) Render(w http.ResponseWriter, r *http.Request) error {
	return nil
}

func NewToken() string {
	return HashHex(uuid.NewString())
}

func RegisterHandler(db *redis.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		clientID, err := db.Incr(ctx, "u").Result()
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		clientSecret := NewToken()

		resp := &RegisterResp{ClientID: fmt.Sprintf("%d", clientID), ClientSecret: clientSecret}
		err = db.HSet(ctx, "0", resp.ClientID, resp.ClientSecret).Err()
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		if err := render.Render(w, r, resp); err != nil {
			render.Render(w, r, ErrRender(err))
			return
		}
	}
}
