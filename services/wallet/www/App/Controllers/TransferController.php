<?php

namespace App\Controllers;

use App\Services\Wallet;

class TransferController extends BaseController
{
    public function __construct($twig, $template, $authRule = "all")
    {
        parent::__construct($twig, $template, $authRule);
        $_SESSION['transfer_step'] = isset($_POST['step']) ? intval($_POST['step']) : 0;
        $this->context['other_user'] = [];
        foreach (\R::findAll('users') as $user) {
            if ($user->id != $_SESSION["user_id"]) {
                $this->context['other_user'][] = [
                    "id" => $user->id,
                    "email" => $user->email
                ];
            }
        }
    }

    public function post()
    {

        $rules = [
            0 => [],
            1 => [
                'action' => 'required|in:transfer,donate',
                'sum' => 'required|numeric',
                'comment' => 'required',
            ],
            2 => [],
            3 => [
                'code' => 'required',
            ]
        ];
        if ($_SESSION['transfer_step'] == 1 && isset($_POST['action']) && $_POST['action'] === 'transfer') {
            $rules[1]['to_user_id'] = 'required|numeric';
        }
        $validation = $this->validator->make($_POST, $rules[$_SESSION['transfer_step']]);

        $validation->validate();
        $fromWallet = new Wallet(userId: $_SESSION["user_id"]);

        if ($validation->fails()) {
            $this->context['errors'] = $validation->errors()->firstOfAll();
            $_SESSION['transfer_step'] -= 1;
        } elseif (isset($_POST['sum']) && $_POST['sum'] > $fromWallet->data->currentBalance) {
            $this->context['errors']['sum'] = 'This wallet has insufficient balance.';
            $_SESSION['transfer_step'] -= 1;
        } else {
            if ($_SESSION['transfer_step'] == 1) {
                $_SESSION['transfer_action'] = $_POST['action'];
                $_SESSION['transfer_sum'] = $_POST['sum'];
                $_SESSION['transfer_comment'] = $_POST['comment'];
                if ($_POST['action'] === 'transfer') {
                    $to_user = \R::load('users', $_POST['to_user_id']);
                    $this->context['transfer_to_username'] = $to_user->username;
                    $toWallet = new Wallet(userId: $_POST['to_user_id']);
                    $_SESSION['transfer_to_wallet'] = $toWallet->data->id;
                }
            } elseif ($_SESSION['transfer_step'] == 2) {
                $secret = \R::findOne('secret', ' users_id = ? AND used = 0 ORDER BY RAND()', [$_SESSION['user_id']]);
                $_SESSION['secret_index'] = $secret->id;
                $this->context['secret_number'] = $secret->number;
            } elseif ($_SESSION['transfer_step'] == 3) {
                $secret = \R::findOne('secret', ' id = ?', [$_SESSION['secret_index']]);
                if (!isset($_SESSION['transfer_action'])) {
                    header('Location: /');
                    exit();
                } elseif ($secret != null && $secret->code === $_POST["code"]) {
                    if ($_SESSION['transfer_action'] == 'transfer') {
                        $toWallet = new Wallet(walletId: $_SESSION['transfer_to_wallet']);
                        $fromWallet->transfer($toWallet, $_SESSION['transfer_sum'], $_SESSION['transfer_comment']);
                    } elseif ($_SESSION['transfer_action'] == 'donate') {
                        $fromWallet->donate($_SESSION['transfer_sum'], $_SESSION['transfer_comment']);
                    }
                    $secret->used = 1;
                    \R::store($secret);
                    unset($_SESSION['transfer_action']);
                } else {
                    $_SESSION['transfer_step'] -= 1;
                    $this->context['secret_number'] = $secret->number;
                    $this->context['errors']['code'] = 'Error code.';
                }
            }else{
                header('Location: /transfer');
                exit();
            }
        }
        $this->get();
    }
}
