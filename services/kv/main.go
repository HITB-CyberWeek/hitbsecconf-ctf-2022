package main

import (
	"context"
	"log"
	"net/http"
	"os"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/render"
	"github.com/go-redis/redis/v8"
)

var ctx = context.Background()

func main() {
	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		log.Fatalln("REDIS_ADDR variable shoud be set!")
		os.Exit(1)
	}

	db := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})

	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(render.SetContentType(render.ContentTypeJSON))
	r.Post("/register", RegisterHandler(db))
	r.Post("/token", NewTokenHandler(db))
	r.Put("/kv/{filename}", SetHandler(db))
	r.Get("/kv/{filename}", GetHandler(db))
	http.ListenAndServe(":3000", r)
}
