package main

import (
	"encoding/binary"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/render"
	"github.com/go-redis/redis/v8"
)

func Key(db *redis.Client, r *http.Request) (string, error) {
	filename := chi.URLParam(r, "filename")
	if filename == "" {
		return "", errors.New("filename should not be empty")
	}

	clientId := r.Header.Get("X-Client-ID")
	if clientId == "" {
		return "", errors.New("client id should not be empty")
	}

	clientSecret := r.Header.Get("X-Client-Secret")
	if clientSecret == "" {
		return "", errors.New("client secret should not be empty")
	}

	clientSecretDB, err := db.HGet(ctx, "0", clientId).Result()
	if err != nil {
		return "", errors.New("err checking secret")
	}

	if clientSecret != clientSecretDB {
		return "", errors.New("wrong secret")
	}

	c, err := strconv.ParseUint(clientId, 10, 64)
	if err != nil {
		return "", errors.New("wrong clientId")
	}

	// TODO: Fix me
	key := make([]byte, 10)
	binary.LittleEndian.PutUint64(key, c)

	key = append(key, []byte(filename)...)
	keyStr := fmt.Sprintf("%d", binary.LittleEndian.Uint64(Hash(key)[len(key)-8:len(key)]))
	return keyStr, nil
}

func SetHandler(db *redis.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		keyStr, err := Key(db, r)
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
		}

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
		keyStr, err := Key(db, r)
		if err != nil {
			render.Render(w, r, ErrInvalidRequest(err))
			return
		}

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
