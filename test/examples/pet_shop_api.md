# Brontosaurus Petstore


This is a sample Petstore server. You can find out more about Brontosaurus
at http://spacejam.com. For this sample, you can use the api key
special-key to test the authorization filters.


## Table of Contents

[Methods](#methods) (16 total)
* [get_pet](#get_pet)
* [update_pet](#update_pet)
* [create_pet](#create_pet)
* [delete_pet](#delete_pet)
* [find_pet_by_status](#find_pet_by_status)
* ~~[find_pet_by_tags](#find_pet_by_tags)~~
* [get_store_inventory](#get_store_inventory)
* [get_order](#get_order)
* [delete_order](#delete_order)
* [create_order](#create_order)
* [get_user](#get_user)
* [update_user](#update_user)
* [delete_user](#delete_user)
* [login](#login)
* [logout](#logout)
* [create_user](#create_user)

[Data Types](#datatypes) (5 total)
* [#pet](#pet)
* [#order](#order)
* [#user](#user)
* [#category](#category)
* [#tag](#tag)

## <a name="methods">Methods</a>

### <a name='get_pet'>get_pet(object) ⇒ [#pet](#pet)</a>

Fetch a pet by ID

**Parameters:** JSON object
* No extra properties allowed
* Required fields: **id**
* Properties:
  * `"id"` – required integer

**Result type:** [#pet](#pet)

### <a name='update_pet'>update_pet(object) ⇒ [#pet](#pet)</a>

Update a pet by ID

**Parameters:** JSON object
* No extra properties allowed
* Required fields: **id, pet**
* Properties:
  * `"id"` – required integer
    * Description: ID of the pet you want to update.
  * `"pet"` – required JSON object
    * No extra properties allowed
    * Properties:
      * `"name"` – string
      * `"category"` – **[#category](#category)**
      * `"photoUrls"` – JSON array
        * items: string
          * format: uri
      * `"tags"` – JSON array
        * items: **[#tag](#tag)**
      * `"status"` – string
        * Must be one of: `"available"`, `"pending"`, `"sold"`

**Result type:** [#pet](#pet)

### <a name='create_pet'>create_pet(object) ⇒ [#pet](#pet)</a>

Create a new pet entry

**Parameters:** JSON object
* No extra properties allowed
* Properties:
  * `"name"` – required string
  * `"category"` – required **[#category](#category)**
  * `"photoUrls"` – JSON array
    * items: string
      * format: uri
  * `"tags"` – JSON array
    * items: **[#tag](#tag)**
  * `"status"` – required string
    * Must be one of: `"available"`, `"pending"`, `"sold"`
* Required fields: **name, category, status**

**Result type:** [#pet](#pet)

### <a name='delete_pet'>delete_pet(object)</a>

Delete a pet entry by ID

**Parameters:** JSON object
* No extra properties allowed
* Required fields: **id**
* Properties:
  * `"id"` – required integer

**Required headers**:

 * `Authorization` must have format "`^token .+$`"

**No results**

### <a name='find_pet_by_status'>find_pet_by_status(object) ⇒ array of [#pet](#pet)</a>

Find a pet that has any of the given statuses.

**Parameters:** JSON object
* No extra properties allowed
* Required fields: **any_status**
* Properties:
  * `"any_status"` – JSON array
    * minLength: 1
    * items: string
      * Must be one of: `"available"`, `"pending"`, `"sold"`

**Result:** JSON array
* items: **[#pet](#pet)**

### <a name='find_pet_by_tags'>~~find_pet_by_tags(object) ⇒ array of [#pet](#pet)~~</a>

**This method is deprecated:** This method is no longer supported for some reason or another.

Find a pet that has any of the given tags.

**Parameters:** JSON object
* No extra properties allowed
* Required fields: **any_tag**
* Properties:
  * `"any_tag"` – JSON array
    * minLength: 1
    * items: string
      * title: Tag Name

**Result:** JSON array
* items: **[#pet](#pet)**

### <a name='get_store_inventory'>get_store_inventory() ⇒ object</a>

Return a map of statuses to quantities

**No parameters**

**Result:** JSON object
* Required fields: **available, pending, sold**
* Properties:
  * `"available"` – required integer
    * minimum: 0
  * `"pending"` – required integer
    * minimum: 0
  * `"sold"` – required integer
    * minimum: 0

### <a name='get_order'>get_order(object) ⇒ [#order](#order)</a>

Get a purchase order by ID

**Parameters:** JSON object
* No extra properties allowed
* Required fields: **id**
* Properties:
  * `"id"` – required integer

**Result type:** [#order](#order)

### <a name='delete_order'>delete_order(object)</a>

Delete a purchase order by ID

**Parameters:** JSON object
* No extra properties allowed
* Required fields: **id**
* Properties:
  * `"id"` – required integer

**No results**

### <a name='create_order'>create_order(object) ⇒ [#order](#order)</a>

Place an order for a pet.

**Parameters:** JSON object
* Required fields: **petId, quantity**
* Properties:
  * `"petId"` – required integer
    * minimum: 0
  * `"quantity"` – required integer
    * minimum: 1

**Result type:** [#order](#order)

### <a name='get_user'>get_user(object) ⇒ [#user](#user)</a>

Fetch a user by username

**Parameters:** JSON object
* Required fields: **username**
* No extra properties allowed
* Properties:
  * `"username"` – required string
    * minLength: 3

**Result type:** [#user](#user)

### <a name='update_user'>update_user(object) ⇒ [#user](#user)</a>

Update a user

**Parameters:** JSON object
* Required fields: **username_to_update, user**
* Properties:
  * `"username_to_update"` – required string
    * Description: Username for the account we'd like to update
  * `"user"` – required JSON object
    * Description: Properties to set for the user
    * Properties:
      * `"username"` – string
      * `"firstName"` – string
      * `"lastName"` – string
      * `"email"` – string
        * format: email
      * `"password"` – string
        * minLength: 7
      * `"phone"` – string

**Result type:** [#user](#user)

### <a name='delete_user'>delete_user(object)</a>

Delete a user

**Parameters:** JSON object
* No extra properties allowed
* Required fields: **id**
* Properties:
  * `"id"` – required integer

**No results**

### <a name='login'>login(object)</a>

Logs user into the system

**Parameters:** JSON object
* Required fields: **username, password**
* No extra properties allowed
* Properties:
  * `"username"` – required string
    * minLength: 3
  * `"password"` – required password
    * minLength: 7

**No results**

### <a name='logout'>logout()</a>

Logs out a currently logged-in user

**No parameters**

**No results**

### <a name='create_user'>create_user(object) ⇒ [#user](#user)</a>

Create a new user account

**Parameters:** JSON object
* Description: Properties to set for the user
* Properties:
  * `"username"` – string
  * `"firstName"` – string
  * `"lastName"` – string
  * `"email"` – string
    * format: email
  * `"password"` – string
    * minLength: 7
  * `"phone"` – string

**Result type:** [#user](#user)

# <a name="datatypes">Data Types</a>

## <a name="pet">[#pet](#pet)</a>

Methods using this type: [create_pet](#create_pet), [find_pet_by_tags](#find_pet_by_tags), [get_pet](#get_pet), [find_pet_by_status](#find_pet_by_status), [update_pet](#update_pet)

JSON object
* No extra properties allowed
* Required fields: **id, category, name, status**
* Properties:
  * `"id"` – required integer
    * Examples: `0`, `1`, `2`
  * `"category"` – required **[#category](#category)**
  * `"name"` – required string
    * Examples: `"Buster"`, `"Lil Doof"`
  * `"photoUrls"` – JSON array
    * items: string
      * format: uri
    * Examples: `["https://spacejam.com/img/p-jamlogo.gif"]`
  * `"tags"` – JSON array
    * items: **[#tag](#tag)**
  * `"status"` – required string
    * Must be one of: `"available"`, `"pending"`, `"sold"`

## <a name="order">[#order](#order)</a>

Methods using this type: [get_order](#get_order), [create_order](#create_order)

JSON object
* No extra properties allowed
* Required fields: **id, petId, quantity, shipDate, status, complete**
* Properties:
  * `"id"` – required integer
  * `"petId"` – required integer
  * `"quantity"` – required integer
    * minimum: 1
  * `"shipDate"` – required string
    * format: date-time
  * `"status"` – required string
    * Must be one of: `"available"`, `"pending"`, `"sold"`
  * `"complete"` – required boolean

## <a name="user">[#user](#user)</a>

Methods using this type: [get_user](#get_user), [create_user](#create_user), [update_user](#update_user)

JSON object
* No extra properties allowed
* Required fields: **id, username, email, password, userStatus**
* Properties:
  * `"id"` – required integer
  * `"username"` – required string
  * `"firstName"` – string
  * `"lastName"` – string
  * `"email"` – required string
    * format: email
  * `"password"` – required string
    * minLength: 7
  * `"phone"` – string
  * `"userStatus"` – required integer

## <a name="category">[#category](#category)</a>

Methods using this type: [get_pet](#get_pet), [create_pet](#create_pet), [update_pet](#update_pet)

JSON object
* No extra properties allowed
* Required fields: **id, name**
* Properties:
  * `"id"` – required integer
  * `"name"` – required string

## <a name="tag">[#tag](#tag)</a>

Methods using this type: [get_pet](#get_pet), [create_pet](#create_pet), [update_pet](#update_pet)

JSON object
* No extra properties allowed
* Required fields: **id, name**
* Properties:
  * `"id"` – required integer
  * `"name"` – required string

