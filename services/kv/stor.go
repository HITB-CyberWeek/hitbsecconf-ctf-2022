package main

import (
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math"
	"net/http"
	"net/url"
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
	filename, err := url.QueryUnescape(filename)
	if err != nil {
		return "", err
		//return "", errors.New("filename err")
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

	c, err := strconv.Atoi(clientId)
	if err != nil {
		return "", errors.New("wrong clientId")
	}

	fmt.Printf("CLIENT_ID:%d\n", c)

	// TODO: Fix me
	key := make([]byte, 2)
	binary.BigEndian.PutUint16(key, uint16(c%math.MaxUint16))

	key = append(key, []byte(filename)...)
	keyHash := Hash(key)

	fmt.Println("DEBUG:")
	fmt.Println(hex.EncodeToString([]byte(filename)))

	fmt.Println(len(key))
	fmt.Println(hex.EncodeToString(key))
	fmt.Println(hex.EncodeToString(keyHash))
	fmt.Println("======")

	keyStr := fmt.Sprintf("%d", binary.LittleEndian.Uint64(keyHash[len(keyHash)-8:]))
	fmt.Printf("keyStr:%s\n", keyStr)
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
			render.Render(w, r, ErrServerError(errors.New("error saving value")))
			return
		}

		err = db.HSet(ctx, keyStr, "Content", string(content)).Err()
		if err != nil {
			render.Render(w, r, ErrServerError(errors.New("error saving value")))
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
		if err != nil {
			render.Render(w, r, ErrServerError(errors.New("error getting value from DB")))
			return
		}

		if err == redis.Nil {
			render.Render(w, r, ErrNotFound())
			return
		}

		resp, err := json.Marshal(data)
		if err != nil {
			render.Render(w, r, ErrServerError(errors.New("error saving value")))
			return
		}

		w.Write(resp)
	}
}
