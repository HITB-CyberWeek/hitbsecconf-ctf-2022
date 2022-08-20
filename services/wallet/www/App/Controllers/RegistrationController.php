<?php

namespace App\Controllers;

use App\Services\Wallet;

class RegistrationController extends BaseController
{


    public function post()
    {
        $validation = $this->validator->make($_POST, [
            'email' => 'required|email|unique:users,email',
            'username' => 'required|min:3',
            'password' => 'required|min:6',
            'confirm_password' => 'required|same:password',
        ]);
        $validation->validate();

        if ($validation->fails()) {
            $this->context['errors'] = $validation->errors()->firstOfAll();
        } else {
            $user = \R::dispense('users');
            $user->password = password_hash($_POST["password"], PASSWORD_DEFAULT);
            $user->email = $_POST["email"];
            $user->donator = 0;
            $user->username = $_POST["username"];
            $user->sercetsViews = 0;
            for ($i = 1; $i <= 50; $i++) {
                $secret = \R::dispense('secret');
                $secret->code = generateRandomString();
                $secret->used = false;
                $secret->number = $i;
                $user->ownSecretList[] = $secret;
            }

            $wallet = new Wallet(runningBalance: 1000);
            $user->ownWalletsList[] = $wallet->data;

            $_SESSION['user_id'] = \R::store($user);

            header('Location: /secrets');
        }
        $this->get();
    }
}