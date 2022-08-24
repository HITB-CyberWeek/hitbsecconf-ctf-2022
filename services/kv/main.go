package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/render"
	"github.com/go-redis/redis/v8"
)

var ctx = context.Background()

const INDEX_TEMPLATE = `
<html>
<head>
<title>KV Service</title>
</head>
<body>
<h1>KV Service</h1>
<p>Welcome to the KV service!</p>
<p><code>/register</code> and then put and get (<code>/kv/{filename}</code>) your data!
<p>Currently stored keys: %d</p>
</body>
</html>
`

func IndexHandler(db *redis.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		keysCount, err := db.DBSize(ctx).Result()
		if err != nil {
			render.Render(w, r, ErrServerError(errors.New("error getting keys count from DB")))
			return
		}

		resp := fmt.Sprintf(INDEX_TEMPLATE, keysCount)
		w.Write([]byte(resp))
	}
}

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
	r.Put("/kv/{filename}", SetHandler(db))
	r.Get("/kv/{filename}", GetHandler(db))
	r.Get("/", IndexHandler(db))
	http.ListenAndServe(":3000", r)
}
