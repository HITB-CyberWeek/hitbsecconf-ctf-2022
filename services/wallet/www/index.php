<?php
session_start();
use App\Services\App;

require_once __DIR__ . "/../vendor/autoload.php";

$loader = new \Twig\Loader\FilesystemLoader('/var/www/html/templates');
$twig = new \Twig\Environment($loader, []);
App::start();
require_once __DIR__ . "/routes.php";
