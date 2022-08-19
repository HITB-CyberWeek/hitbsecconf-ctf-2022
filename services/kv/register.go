package main

import (
	"fmt"
	"net/http"

	"github.com/go-chi/render"
	"github.com/go-redis/redis/v8"
)

func RegisterHandler(db *redis.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		data := &UserData{}
		if err := render.Bind(r, data); err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		val, err := db.HGet(ctx, "p", data.Username).Result()
		if err != nil && err != redis.Nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		if val != "" {
			render.Render(w, r, ErrInvalidRequest(fmt.Errorf("username '%s' already exists", data.Username)))
			return
		}

		err = db.HSet(ctx, "p", data.Username, HashHex(data.Password)).Err()
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}
	}
}
