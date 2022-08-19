package main

import (
	"errors"
	"fmt"
	"math/rand"
	"net/http"

	"github.com/go-chi/render"
	"github.com/go-redis/redis/v8"
)

type TokenResp struct {
	Token string `json:"token"`
}

// func (u *TokenResp) Bind(r *http.Request) error {
// 	return nil
// }

func (rd *TokenResp) Render(w http.ResponseWriter, r *http.Request) error {
	return nil
}

func NewToken() uint16 {
	return uint16(rand.Intn(65536))
}

func NewTokenHandler(db *redis.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		data := &UserData{}
		if err := render.Bind(r, data); err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		val, err := db.HGet(ctx, "p", data.Username).Result()
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		if val != HashHex(data.Password) {
			render.Render(w, r, ErrInvalidRequest(errors.New("wrong password")))
			return
		}

		token := fmt.Sprintf("%x", NewToken())
		err = db.HSet(ctx, "0", data.Username, token).Err()
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		tokenResp := &TokenResp{}
		tokenResp.Token = token
		if err := render.Render(w, r, tokenResp); err != nil {
			render.Render(w, r, ErrRender(err))
			return
		}
	}
}
