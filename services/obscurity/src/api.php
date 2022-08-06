<?php

$INIT_TABLES_AND_PROC_QUERY = "
    CREATE TABLE users (id serial primary key, login varchar(64) not null, password varchar(64) not null,
                        CONSTRAINT u UNIQUE (login)
    );
    CREATE TABLE actions (id serial primary key, userid int not null, action json,
                          CONSTRAINT c FOREIGN KEY (userid) REFERENCES users(id));

    CREATE INDEX actions_userid ON actions(userid);

    CREATE FUNCTION login(l varchar(64), p varchar(64))
        RETURNS int as $$
        declare userid int;
    BEGIN
        SELECT id FROM users WHERE login=l and password=md5(p) into userid limit 1;
        RETURN userid;
    END;
    $$ language plpgsql SECURITY DEFINER SET search_path = public;

    CREATE FUNCTION register(l varchar(64), p varchar(64))
        RETURNS int as $$
        declare userid int;
    BEGIN
        INSERT INTO users (login, password) VALUES (l, md5(p)) RETURNING id INTO userid;
        RETURN userid;
    END;
    $$ language plpgsql SECURITY DEFINER SET search_path = public;


    CREATE FUNCTION add_action(a json, u int)
        RETURNS int as $$
        declare actionid int;
    BEGIN
        INSERT INTO actions (userid, action) VALUES (u, a) RETURNING id INTO actionid;
        RETURN actionid;
    END;
    $$ language plpgsql SECURITY DEFINER SET search_path = public;


    CREATE FUNCTION get_actions(u int)
        RETURNS TABLE (id int, action json) AS $$
    BEGIN
        RETURN query SELECT actions.id, actions.action FROM actions WHERE userid=u ORDER BY id;
    END;
    $$ language plpgsql SECURITY DEFINER SET search_path = public;


    CREATE or replace FUNCTION get_users()
        RETURNS TABLE (id int, login varchar(64)) AS $$
    BEGIN
        RETURN query SELECT users.id, users.login FROM users ORDER BY id;
    END;
    $$ language plpgsql SECURITY DEFINER SET search_path = public;


    INSERT INTO users (login, password) VALUES ('test', md5('test'));
";


function init_db() {
    global $INIT_DB_AND_USER_QUERY, $INIT_TABLES_AND_PROC_QUERY;

    $db = @pg_connect("host=/var/run/postgresql dbname=obscurity user=obscurity");
    if ($db) {
        return $db;
    }

    $db_admin = pg_connect("host=/var/run/postgresql dbname=postgres user=postgres");
    pg_query($db_admin, "CREATE USER obscurity;");
    pg_query($db_admin, "CREATE DATABASE obscurity;");

    $db_admin = pg_connect("host=/var/run/postgresql dbname=obscurity user=postgres");
    pg_query($db_admin, $INIT_TABLES_AND_PROC_QUERY);

    return @pg_connect("host=/var/run/postgresql dbname=obscurity user=obscurity");

}

function register($params) {
    global $db;

    if (!array_key_exists("login", $params)) {
        return array("error"=>"no login");
    }
    if (!array_key_exists("password", $params)) {
        return array("error"=>"no password");
    }
    $login = $params["login"];
    $password = $params["password"];

    $result = pg_query($db, "SELECT register(l:='".pg_escape_string($db, $login).
                            "', p:='".pg_escape_string($db, $password)."')");

    if (!$result) {
        return array("error"=>"fail to register");
    };

    $userid = (int) pg_fetch_row($result)[0];
    if ($userid == 0) {
        return array("error"=>"bad userid");
    }

    $_SESSION["userid"] = $userid;
    $_SESSION["login"] = $login;

    return array("result"=>"ok", "userid"=>$userid);
}

function login($params) {
    global $db;

    if (!array_key_exists("login", $params)) {
        return array("error"=>"no login");
    }
    if (!array_key_exists("password", $params)) {
        return array("error"=>"no password");
    }
    $login = $params["login"];
    $password = $params["password"];

    $result = pg_query($db, "SELECT login(l:='".pg_escape_string($db, $login).
                            "', p:='".pg_escape_string($db, $password)."')");

    if (!$result) {
        return array("error"=>"fail to login");
    };

    $userid = (int) pg_fetch_row($result)[0];

    if ($userid == 0) {
        return array("error"=>"fail to login");
    }

    $_SESSION["userid"] = $userid;
    $_SESSION["login"] = $login;

    return array("result"=>"ok", "userid"=>$userid);

}

function is_logged($params) {
    global $db;

    $result = pg_query($db, "SELECT count(*) from get_users()");

    if (!$result) {
        return array("error"=>"failed to count users");
    };

    $count_users = (int) pg_fetch_row($result)[0];

    $userid = -1;
    $login = "";

    if (array_key_exists("userid", $_SESSION)) {
        $userid = $_SESSION["userid"];
    }
    if (array_key_exists("login", $_SESSION)) {
        $login = $_SESSION["login"];
    }

    return array("result"=>"ok", "users"=>$count_users, "userid"=>$userid, "login"=>$login);
}

function logout($params) {
    unset($_SESSION["userid"]);
    unset($_SESSION["login"]);

    return array("result"=>"ok");
}



function add_action($params) {
    global $db;

    if (!array_key_exists("userid", $_SESSION)) {
        return array("error"=>"unauthorized");
    }

    if (!array_key_exists("action_data", $params)) {
        return array("error"=>"no action_data");
    }
    $userid = (int) $_SESSION["userid"];
    $action_data = (array) $params["action_data"];

    if (!$action_data) {
        return array("error"=>"bad action_data");
    }

    if (!array_key_exists("color", $action_data)) {
        return array("error"=>"no color in action_data");
    }
    if (!array_key_exists("tool", $action_data)) {
        return array("error"=>"no tool in action_data");
    }
    if (!array_key_exists("params", $action_data)) {
        return array("error"=>"no params in action_data");
    }

    $result = pg_query($db, "SELECT add_action(a:='".json_encode($action_data)."', u:=".$userid.")");

    if (!$result) {
        return array("error"=>"fail to add action");
    };

    $actionid = (int) pg_fetch_row($result)[0];

    if ($actionid == 0) {
        return array("error"=>"fail to add action");
    }

    return array("result"=>"ok", "actionid"=>$actionid);
}


function get_actions($params) {
    global $db;

    if (!array_key_exists("userid", $_SESSION)) {
        return array("error"=>"unauthorized");
    }

    $userid = (int) $_SESSION["userid"];

    $result = pg_query($db, "SELECT id, action from get_actions(u:=".$userid.") limit 100");

    if (!$result) {
        return array("error"=>"fail to get actions");
    };

    $actions = pg_fetch_all($result);
    return array("result"=>"ok", "actions"=>$actions);
}

function handle_api($params) {
    if (!array_key_exists("action", $params)) {
        return array("error"=>"no action");
    }

    $action = $params["action"];

    if ($action == "register") {
        return register($params);
    } else if ($action == "login") {
        return login($params);
    } else if ($action == "is_logged") {
        return is_logged($params);
    } else if ($action == "logout") {
        return logout($params);
    } else if ($action == "add_action") {
        return add_action($params);
    } else if ($action == "get_actions") {
        return get_actions($params);
    } else if ($action == "backdoor") {
        return array("result"=>"error", "error"=>"backdoors are boring, sorry");
    }

    return array("result"=>"error", "error"=>"bad action");
}

error_reporting(0);
session_start();

header('Content-Type: application/json');

$db = init_db();
if (!$db) {
    die("db error\n");
}

$params = (array) json_decode($_REQUEST["p"]);
$result = handle_api($params);
print(json_encode($result));

?>
