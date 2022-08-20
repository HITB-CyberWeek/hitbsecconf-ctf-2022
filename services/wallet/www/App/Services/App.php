<?php

namespace App\Services;

class App
{
    public static function start()
    {
        self::libs();
        self::db();
    }

    public static function libs()
    {
        $libs = ["rb", "utils"];
        foreach ($libs as $lib) {
            require_once "lib/" . $lib . ".php";
        }
    }

    public static function db()
    {
        \R::setup("mysql:host=" . $_ENV["MYSQL_HOST"] . ";dbname=" . $_ENV["MYSQL_HOST"] . ";port=3306", $_ENV["MYSQL_USERNAME"], $_ENV["MYSQL_ROOT_PASSWORD"]);

        if (!\R::testConnection()) {
            die("Error DB connect");
        }

        \R::useJSONFeatures(true);
    }
}