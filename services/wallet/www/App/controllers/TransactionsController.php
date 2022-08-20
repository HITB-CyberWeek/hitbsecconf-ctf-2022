<?php

namespace App\Controllers;

use App\Services\Wallet;

class TransactionsController extends BaseController
{
    public function __construct($twig, $template, $authRule = "all")
    {
        parent::__construct($twig, $template, $authRule);
        $wallet = new Wallet(userId: $_SESSION['user_id']);
        $transactions = [];
        foreach ($wallet->data->ownTransactionsList as $transaction) {

            $transactionData = [
                "id" => $transaction->id,
                "type" => $transaction->type,
                "value" => $transaction->value,
                "comment" => $transaction->comment,
                "runningBalance" => $transaction->runningBalance,
                "otherWalletId" => $transaction->otherWalletId,
                "createdAt" => date('Y/m/d H:i:s', $transaction->createdAt)
            ];
            if ($transaction->otherWalletId != 0) {
                $otherWalletOwner = (new  Wallet($transaction->otherWalletId))->owner();
                $transactionData["otherUsername"] = $otherWalletOwner->username;
            }
            $transactions[] = $transactionData;
        }
        $transactions = array_reverse($transactions);
        $this->context["transactions"] = $transactions;
    }

    function view()
    {
        $this->get();
    }
}