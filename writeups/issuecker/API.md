# Issuecker
Simple issue tracker

### /register

#### POST
##### Summary

Register a new user

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successful registration |
| 400 | Invalid username or password |

### /login

#### POST
##### Summary

Log in into existing account

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successful registration |
| 400 | Invalid username or password |

### /add_queue

#### POST
##### Summary

Add new queue

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successful queue creation |
| 400 | Failed auth or invalid queue name |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieSecret | |
| cookieName | |

### /add_ticket

#### POST
##### Summary

Add new ticket

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successful ticket creation |
| 400 | Failed auth or invalid ticket title or description |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieSecret | |
| cookieName | |

### /find_tickets

#### POST
##### Summary

Find tickets

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successful ticket search result |
| 400 | Failed auth or invalid queue_id or invalid ticket_id, title or description |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieSecret | |
| cookieName | |

### Models

#### UserPair

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| username | string | _Example:_ `"username"` | Yes |
| password | string | _Example:_ `"password"` | Yes |

#### AddQueueReq

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| queue_name | string | _Example:_ `"My queue"` | Yes |

#### AddQueueRes

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| queue_id | string |  | Yes |
| queue_key | string |  | Yes |

#### AddTicketReq

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| queue_id | string |  | Yes |
| title | string |  | Yes |
| description | string |  | Yes |

#### FindTicketsReq

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| queue_id | string |  | Yes |
| ticket_id | string |  | No |
| title | string |  | No |
| description | string |  | No |

#### FindTicketsRes

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| title | string |  | Yes |
| description | string |  | Yes |

#### AddTicketRes

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| ticket_id | string |  | Yes |
