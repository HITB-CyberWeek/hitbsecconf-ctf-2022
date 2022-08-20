<?php

namespace App\Controllers;


class RecoveryController extends BaseController
{
    public function __construct($twig, $template, $authRule)
    {
        parent::__construct($twig, $template, $authRule);
        $this->context['recovery_step'] = isset($_POST['step']) ? intval($_POST['step']) : 0;
        $_SESSION['recovery_step'] = $this->context['recovery_step'];
    }

    private function start_recovery()
    {
        $_SESSION['recover_id'] = \R::findOne('users', ' email = ?', [$_POST['email']])->id;
    }

    private function get_code_recovery()
    {
        $secret = \R::findOne('secret', ' users_id = ? AND used = 0 ORDER BY RAND()', [$_SESSION['recover_id']]);
        $_SESSION['secret_index'] = $secret->id;
        $this->context['secret_number'] = $secret->number;
    }

    private function reset_password()
    {
        $secret = \R::findOne('secret', ' id = ?', [$_SESSION['secret_index']]);
        $reset_status = false;
        if ($secret != null && $secret->code === $_POST["code"]) {
            $user = \R::findOne('users', ' id = ?', [$_SESSION['recover_id']]);
            $user->password = password_hash($_POST["password"], PASSWORD_DEFAULT);
            $secret->used = 1;

            \R::store($user) && \R::store($secret);
            session_destroy();
            $reset_status = true;
        }
        return $reset_status;
    }

    private function back_step()
    {
        $this->context['recovery_step'] -= 1;
        $_SESSION['recovery_step'] = $this->context['recovery_step'];
        if (isset($_SESSION['secret_index'])) {
            $this->context['recovery_type'] = 'code';
            $this->get_code_recovery();
        }
    }

    public function post()
    {
        $rules = [
            1 => [
                'email' => 'required|email|exist:users,email',
            ],
            2 => [
                'recovery_type' => 'required|in:code,email'
            ],
            3 => [
                'code' => 'required',
                'password' => 'required|min:6',
            ]
        ];
        $validation = $this->validator->make($_POST, $rules[$this->context['recovery_step']]);
        $validation->validate();
        if ($validation->fails()) {
            $this->context['errors'] = $validation->errors()->firstOfAll();
            $this->back_step();
        } elseif ($this->context['recovery_step'] === 1) {
            $this->start_recovery();
        } elseif ($this->context['recovery_step'] === 2) {
            $this->context['recovery_type'] = isset($_POST['recovery_type']) ? $_POST['recovery_type'] : 'code';
            if ($this->context['recovery_type'] === "code") {
                $this->get_code_recovery();
            } else {
                session_destroy();
            }
        } elseif ($this->context['recovery_step'] === 3) {
           if (!$this->reset_password()) {
                $this->back_step();
                $this->context['errors']['code'] = 'Error code.';
            }
        }
        $this->get();
    }
}