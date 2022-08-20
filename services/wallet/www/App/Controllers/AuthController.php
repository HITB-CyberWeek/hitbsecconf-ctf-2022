<?php

namespace App\Controllers;

class AuthController extends BaseController
{
    public function post()
    {
        $validation = $this->validator->make($_POST, [
            'email' => 'required|email|exist:users,email',
            'password' => 'required|min:6',
        ]);
        $validation->validate();

        if ($validation->fails()) {
            $this->context['errors'] = $validation->errors()->firstOfAll();
        } else {
            $user = \R::findOne('users', ' email = ?', [$_POST['email']]);
            if (password_verify($_POST['password'], $user->password)) {
                $_SESSION['user_id'] = $user->id;
                header('Location: /');
            } else {
                $this->context['errors'][] = "Not found user";
            }
        }
        $this->get();
    }
}