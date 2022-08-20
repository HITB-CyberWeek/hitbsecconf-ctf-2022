<?php

use App\Controllers\IndexController;
use App\Controllers\RegistrationController;
use App\Controllers\AuthController;
use App\Controllers\RecoveryController;
use App\Controllers\TransferController;
use App\Controllers\TransactionsController;
use App\Controllers\SecretsController;
use App\Controllers\DonatorsController;

$router = new \Bramus\Router\Router();

if (isset($_SESSION['user_id'])) {
    $user = \R::findOne('users', $_SESSION['user_id']);
    if (is_null($user)) {
        session_destroy();
        header('Location: /');
    }
}

global $twig;
$router->all('', function () use ($twig) {
    $indexController = new IndexController($twig, 'index.twig');
    $indexController->view();
});

$router->match(
    'GET|POST', 'signup',
    function () use ($twig) {
        $registrationController = new RegistrationController($twig, 'signup.twig', 'not_auth');
        $registrationController->view();
    }
);
$router->match(
    'GET|POST', 'signin',
    function () use ($twig) {
        $authController = new AuthController($twig, 'signin.twig', 'not_auth');
        $authController->view();
    }
);
$router->match(
    'GET|POST', 'recovery',
    function () use ($twig) {
        $recoveryController = new RecoveryController($twig, 'recovery.twig', 'not_auth');
        $recoveryController->view();
    }
);
$router->all(
    'transactions',
    function () use ($twig) {
        $transactionsController = new TransactionsController($twig, 'transactions.twig', 'auth');
        $transactionsController->view();
    }
);
$router->all(
    'transfer',
    function () use ($twig) {
        $transferController = new TransferController($twig, 'transfer.twig', 'auth');
        $transferController->view();
    }
);
$router->all(
    'secrets',
    function () use ($twig) {
        $secretsController = new SecretsController($twig, 'secrets.twig', 'auth');
        $secretsController->view();
    }
);
$router->all(
    'donators',
    function () use ($twig) {
        $donatorsController = new DonatorsController($twig, 'donators.twig', 'all');
        $donatorsController->view();
    }
);

$router->all(
    'exit',
    function () {
        session_destroy();
        header('Location: /');
    }
);

$router->run();
