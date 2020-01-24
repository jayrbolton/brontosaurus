# Test Server


This is a server for running tests on brontosaurus.


## Methods

### `echo`

Is there an echo in here?

**Params type:** [Message](#message)

**Result type:** [Message](#message)

### `invalid_result`

Test a result that fails schema check

**Params type:** [Message](#message)

**Result type:** [Message](#message)

## Data Types

### <a name=#message>Message</a>

Echo message object.

Object with keys:

* `message` - required string - String to echo back to you

