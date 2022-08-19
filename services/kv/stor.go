package main

import (
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/render"
	"github.com/go-redis/redis/v8"
)

func SetHandler(db *redis.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		filename := chi.URLParam(r, "filename")
		if filename == "" {
			render.Render(w, r, ErrInvalidRequest(errors.New("filename should not be empty")))
			return
		}

		tokenStr := r.Header.Get("X-Token")
		if tokenStr == "" {
			render.Render(w, r, ErrInvalidRequest(errors.New("token should not be empty")))
			return
		}

		token, err := strconv.ParseInt(tokenStr, 16, 16)
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		keyStr := Key(uint16(token), filename)

		content := make([]byte, 4096)
		n, err := r.Body.Read(content)
		if err != nil && err != io.EOF {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}
		content = content[:n]

		contentType := r.Header.Get("Content-type")

		err = db.HSet(ctx, keyStr, "Content-type", contentType).Err()
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		err = db.HSet(ctx, keyStr, "Content", string(content)).Err()
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}
	}
}

func GetHandler(db *redis.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		filename := chi.URLParam(r, "filename")
		if filename == "" {
			render.Render(w, r, ErrInvalidRequest(errors.New("filename should not be empty")))
			return
		}

		tokenStr := r.Header.Get("X-Token")
		if tokenStr == "" {
			render.Render(w, r, ErrInvalidRequest(errors.New("token should not be empty")))
			return
		}

		token, err := strconv.ParseInt(tokenStr, 16, 16)
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		keyStr := Key(uint16(token), filename)

		data, err := db.HGetAll(ctx, keyStr).Result()
		if err != nil && err != redis.Nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		resp, err := json.Marshal(data)
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

		w.Write(resp)
	}
}
