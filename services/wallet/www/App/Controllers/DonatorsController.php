<?php

namespace App\Controllers;

use App\Services\Wallet;

class DonatorsController extends BaseController
{
    public function __construct($twig, $template, $authRule = "all")
    {
        parent::__construct($twig, $template, $authRule);
        $this->context["donaters"] = [];
        $users = \R::findAll('users', 'donator = 1 Order By id DESC LIMIT 100');
        $all_donate_sum = 0;
        foreach ($users as $user) {
            $wallet = new Wallet(userId: $user->id);
            $user_donate_sum = 0;
            foreach ($wallet->data->ownTransactionsList as $transaction) {
                if ($transaction->type === "donate") {
                    $all_donate_sum -= $transaction->value;
                    $user_donate_sum -= $transaction->value;
                }
            }
            $this->context["donaters"][] = ["email" => $user->email, "donate_sum" => $user_donate_sum];
        }
        usort($this->context["donaters"], function ($a, $b) {
            return $a['donate_sum'] <=> $b['donate_sum'];
        });
        $this->context["donaters"] = array_reverse($this->context["donaters"]);
        $this->context["all_donate_sum"] = $all_donate_sum;
    }

    function view()
    {
        $this->get();
    }
}
