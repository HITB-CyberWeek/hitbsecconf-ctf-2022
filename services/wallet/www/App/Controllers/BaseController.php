<?php

namespace App\Controllers;

use Rakit\Validation\Validator;
use App\Services\Wallet;
use App\Services\UniqueRule;
use App\Services\ExistRule;

class BaseController
{
    public function __construct($twig, $template, $authRule = "all")
    {
        $this->twig = $twig;
        $this->template = $template;
        $this->context = array('request_uri' => $_SERVER['REQUEST_URI'], 'errors' => []);
        $this->validator = new Validator;
        $this->validator->addValidator('unique', new UniqueRule());
        $this->validator->addValidator('exist', new ExistRule());

        if ($authRule === "not_auth" && isset($_SESSION['user_id'])) {
            header('Location: /');
            exit();
        } elseif ($authRule === "auth" && !isset($_SESSION['user_id'])) {
            header('Location: /signin');
            exit();
        }
        if (isset($_SESSION['user_id'])) {
            $user = \R::load('users', $_SESSION['user_id']);
            $wallet = new Wallet(userId: $_SESSION["user_id"]);
            $this->context['user'] = [
                "id" => $user->id,
                "email" => $user->email,
                "username" => $user->username,
                "balance" => $wallet->data->currentBalance
            ];

        }
    }

    public function view()
    {
        if ($_SERVER["REQUEST_METHOD"] === "POST") {
            $this->post();
        } else {
            $this->get();
        }
    }

    public function get()
    {
        $this->context['session'] = [];
        foreach ($_SESSION as $key => $value) {
            $this->context['session'][$key] = $value;
        }
        $this->context['postc'] = [];
        foreach ($_POST as $key => $value) {
            $this->context['post'][$key] = $value;
        }
        echo $this->twig->render($this->template, $this->context);
    }

    public function post()
    {
        $this->get();
    }
}