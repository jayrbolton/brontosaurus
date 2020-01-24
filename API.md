# Brontosaurus Petstore


This is a sample Petstore server. You can find out more about Brontosaurus
at http://spacejam.com. For this sample, you can use the api key
special-key to test the authorization filters.


## Methods

### get_pet(object) ⇒ [#pet](#pet)

Fetch a pet by ID

#### Parameters

JSON object with properties:

* `"id"` – required integer

**Result type:** [#pet](#pet)

### update_pet(object) ⇒ [#pet](#pet)

Update a pet by ID

#### Parameters

JSON object with properties:

* `"id"` – required integer
* `"name"` – optional string
* `"status"` – optional string

**Result type:** [#pet](#pet)

### create_pet(object) ⇒ [#pet](#pet)

Create a new pet entry

#### Parameters

JSON object with properties:

* `"name"` – required string
* `"category"` – required [#category](#category)
* `"photoUrls"` – optional array of string (format: uri)
* `"tags"` – optional [#tag](#tag)
* `"status"` – required string (must be one of "available", "pending", "sold")

**Result type:** [#pet](#pet)

# Data Types

## <a name=#pet>[#pet](#pet)</a>

JSON object with properties:

* `"id"` – required integer
* `"name"` – required string
* `"photoUrls"` – optional array of string (format: uri)
* `"tags"` – optional array of [#tag](#tag)
* `"status"` – required string (must be one of "available", "pending", "sold")

## <a name=#order>[#order](#order)</a>

JSON object with properties:

* `"id"` – required integer
* `"petId"` – required integer
* `"quantity"` – required integer (minimum: 1)
* `"shipDate"` – required string (format: date-time)
* `"status"` – required string (must be one of "placed", "approved", "delivered")
* `"complete"` – required boolean

## <a name=#user>[#user](#user)</a>

JSON object with properties:

* `"id"` – required integer
* `"username"` – required string
* `"firstName"` – optional string
* `"lastName"` – optional string
* `"email"` – required string (format: email)
* `"password"` – required string
* `"phone"` – optional string
* `"userStatus"` – required integer

## <a name=#category>[#category](#category)</a>

JSON object with properties:

* `"id"` – required integer
* `"name"` – required string

## <a name=#tag>[#tag](#tag)</a>

JSON object with properties:

* `"id"` – required integer
* `"name"` – required string

