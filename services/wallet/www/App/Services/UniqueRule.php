<?php

namespace App\Services;

use \Rakit\Validation\Rule;

class UniqueRule extends Rule
{
    protected $message = ":attribute :value has been used";

    protected $fillableParams = ['table', 'column'];

    public function check($value): bool
    {
        $this->requireParameters(['table', 'column']);
        $column = $this->parameter('column');
        $table = $this->parameter('table');
        $obj = \R::findOne($table, " $column = ?", [$value]);
        return is_null($obj);
    }
}