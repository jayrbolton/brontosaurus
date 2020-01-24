```
{
    "title": "User Login",
    "description": "Login form data",
    "type": "object",
    "required": ["email", "password"],
    "additionalProperties": false,
    "properties": {
        "email": {
            "title": "Email",
            "type": "string",
            "format": "email"
        },
        "password": {
            "type": "string",
            "minLength": 7
        },
        "stay_logged_in": {
            "type": "boolean",
            "default": false
        }
    }
}
```

* `type`: object
* `additionalProperties`: false
* `properties`
  * `email`
    * `title`: Email
    * `type`: string
    * `format`: email
