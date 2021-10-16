# Architectural overview & API

sailor-fox is designed around a client-server architecture.
The server is the service `server.py`,
and there are multiple client services that interact directly with chat APIs.

## Command flow at a glance

1. A message is posted in some chat service.
2. A client for that chat service reads the message.
    * If the message does not resemble a command (usually decided by a command prefix), stop here.
    * Otherwise, proceed to 3.
3. The client performs some checks, such as whether the user who sent the message is the bot owner.
   It also cleans the message for forwarding to the server (e.g. removing the prefix)
4. The client POSTs a JSON object to the server.
   The JSON object contains the command,
   as well as some parameters that affect command processing.
5. The server receives and processes the request, then sends back a response containing
   a JSON array of objects, where each object represents an action to perform.
6. The client receives the response and decides how to handle each action.

## `server.py`

This service provides a REST-like API over a local HTTP server (_not_ intended to be run over the web).
The server contains a subclass of `sailor.commands.Processor`, which interprets commands.

> ### Security implications
> The server acts as an HTTP server for local IPC due to its convenience and wide support.
> It assumes that clients are completely honest and trustworthy,
> and should *not* be run as a web server!
> This is both dangerous and unsupported;
> for example, any client can cause a denial of service by simply POSTing
> `{"message": "halt", "is_owner": true}`.

Commands are sent to the server by sending an HTTP POST request to `localhost`, containing a JSON object.
The port number is set in `config.json`.

The server processes the command request and responds with a flat JSON array that contains zero or more objects, where
each object represents an action to take.

## API

### Command POST request

`POST http://localhost:<port number>/`

| Field             | Type                                                | Description
| ---               | ---                                                 | ---
| message           | string                                              | Message to be parsed as a command. Should not contain any command prefixes.
| id?               | string (default random UUID)                        | Provide to keep logs across client and server consistent
| is_owner?         | boolean (default `false`)                           | Whether the person who sent the command is the bot owner
| character_limit?  | integer (default `0` = unlimited)                   | Posts that are longer than this number will be automatically broken up into multiple smaller posts.
| replace_newlines? | boolean (default `false`)                           | Reformats replies to avoid using newlines. Use for services like Twitch chat, which don't support newlines.
| format_name?      | string:[format name](#format-name) (default `null`) | Set to the appropriate format name to enable text formatting
| channel_name?     | string (default `"untitled"`)                       | The name of the chat channel, if applicable

### Format name

| Value       | Behavior
| ---         | ---
| `"discord"` | Use Discord-style markdown formatting
| default     | No text formatting

### Command POST response

| Name | Type
| ---  | ---
| .    |  array of [command action](#command-action)

### Command action

| Field | Type                                               | Description
| ---   | ---                                                | ---
| type  | string:[command action type](#command-action-type) | The type of action
| value | string                                             | The value of the action

### Command action type

| Value              | Client behavior to implement
| ---                | ---
| `"rename_channel"` | Set the channel name to `value`, if applicable
| `"reply"`          | Post `value` in chat
| default            | Client's discretion

### HTTP status codes for command POST response

| Code    | Description
| ---     | ---
| 200     | Command execution succeeded
| 400     | Bad request
| 404     | Command not found
| 500     | Command execution failed
| default | Unknown error

### `curl` example
```
$ curl -L http://localhost:9980 -d '{"message": "ping"}'

[{"type": "reply", "value": ":3"}]
```

## Client services

To create a complete and useful bot, there must be at least one client to a chat service.
Its job is to decide what messages in chat appear to be commands, and forward them to the server.
When the server responds with a list of actions, the client decides how to handle them.

While the server is written in Python, clients can be written in any language.
Multiple unrelated clients can also share the same server instance, allowing a common server
to serve more than one chat service (i.e. less system resources required).
A single client can also access multiple servers (e.g. to have different command sets for
different Discord servers).
