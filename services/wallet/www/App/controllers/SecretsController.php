<?php

namespace App\Controllers;

class SecretsController extends BaseController
{
    public function __construct($twig, $template, $authRule)
    {
        parent::__construct($twig, $template, $authRule);
        $user = \R::load('users', $_SESSION['user_id']);
        if ($user->sercetsViews) {
            header('Location: /');
        }
    }

    function view()
    {
        $this->get();
    }

    function get()
    {
        $user = \R::load('users', $_SESSION['user_id']);
        foreach ($user->ownSecretList as $secret) {
            $this->context['secrets'][] = [
                'number' => $secret->number,
                'code' => $secret->code
            ];
        }
        $user->sercetsViews = 1;
        \R::store($user);
        parent::get();
    }
}