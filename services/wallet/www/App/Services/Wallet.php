<?php

namespace App\Services;

class Wallet
{
    private string $dbName = 'wallets';

    public function __construct(int $walletId = null, $userId = null, int $runningBalance = 0)
    {
        if ($userId != null) {
            $wallet = \R::findOne($this->dbName, ' users_id = ?', [$userId]);
            $walletId = $wallet->id;
        }

        if ($walletId != null) {
            $this->data = \R::load($this->dbName, $walletId);
        } else {
            $this->data = \R::dispense($this->dbName);
            $this->currentBalance = 0;
            $this->deposit($runningBalance, type: "create_wallet", comment: "Registration bonus");
        }
    }

    public function deposit(int $value, int $otherWalletId = 0, string $type = "transaction", string $comment = "")
    {
        $transaction = \R::dispense('transactions');
        $transaction->value = $value;
        $transaction->type = $type;
        $transaction->runningBalance = $this->data->currentBalance;
        $transaction->createdAt = time();
        $transaction->comment = $comment;
        $transaction->otherWalletId = $otherWalletId;
        $this->data->currentBalance += $value;
        $this->data->ownTransactionsList[] = $transaction;
        \R::store($this->data);
    }

    public function withdraw(int $value, int $otherWalletId = 0, string $type = "transaction", string $comment = "")
    {
        if ($value > $this->data->currentBalance) {
            throw new \InvalidArgumentException('This wallet has insufficient balance.');
        }
        $transaction = \R::dispense('transactions');
        $transaction->value = -$value;
        $transaction->type = $type;
        $transaction->runningBalance = $this->data->currentBalance;
        $transaction->createdAt = time();
        $transaction->comment = $comment;
        $transaction->otherWalletId = $otherWalletId;
        $this->data->currentBalance += -$value;
        $this->data->ownTransactionsList[] = $transaction;
        \R::store($this->data);
    }

    public function transfer(Wallet $toWallet, int $value, string $comment)
    {
        $this->withdraw($value, $toWallet->data->id, comment: $comment);
        $toWallet->deposit($value, $this->data->id, comment: $comment);
    }

    public function owner()
    {
        return \R::load('users', $this->data->users_id);
    }

    public function donate(int $value, string $comment)
    {
        $this->withdraw($value, type: "donate", comment: $comment);
        $owner = $this->owner();
        $owner->donator = 1;
        \R::store($owner);
    }

}