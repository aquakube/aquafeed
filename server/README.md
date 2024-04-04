# Server


## AutomationEvents
A command event is an event that something has occured
on the feed automation. A state transition, a request
to do, a request that successfulled completed, etc.

All events follow the format of:
```
{
    "event": "<event_name>",
    "automation_id": "<uuid>",
    "message": "<message>",
    "level": "info | warning | error",
    "details": {
        ...
    }
}
```

Where the `event` is the name of the event, the `automation_id`
is a unique id for each automation as a reference, the `message`
is a human readable message that can be displayed in logs and on
a user interface, a `level` enum to describe the severity of the message,
and the `details` is a dictionary containing
specific details to the `event` type. The `details` are completely
optional because some events don't require them.

The actual payload will always be wrapped in a cloudevent like so:
```
{
    "context": {
        "version": "1.0.0",
        "id": "d2e9599b-710c-4e0a-a8ed-6b87a8bac904",
        "timestamp": "2022-03-15T02:46:44.521Z",
        "type": "feed.automation.event",
        "source": "/feed/automation"
        "action": "create",
        "dataschema": "http://schema.foreveroceans.io/v1/feedAutomationEvent/feedAutomationEvent-1.0.0.json",
        "datacontenttype": "json",
        "datacontentencoding": "",
        "xfodbtable": "feed_automation_events",
    },
    "data": {
        "event": "<event_name>",
        "automation_id": "<uuid>",
        "message": "<message>",
        "details": {
            ...
        }
    }
}
```


### Acknowledged
The command request was recieved by the automation service
and is in the process of being executed.
```
{
    "event": "acknowledged",
    "automation_id": "<uuid>",
    "message": "Automation request recieved and is being executed",
    "details": {
        "settings": {
            ...
        }
    }
}
```

### PreflightFailed
The command request failed a preflight request
```
{
    "event": "preflight_failed",
    "automation_id": "<uuid>",
    "message": "Preflight check <preflight_name> failed",
    "details": {
        "preflight_name": "<preflight_name>",
        "error": "<error>"
    }
}
```

### PreflightPassed
The command request passed a preflight request
```
{
    "event": "preflight_passed",
    "automation_id": "<uuid>",
    "message": "Preflight check <preflight_name> passed",
    "details": {
        "preflight_name": "<preflight_name>",
    }
}
```

### RequestedPause
A request to pause the automation was recieved.
```
{
    "event": "requested_pause",
    "automation_id": "<uuid>",
    "message": "Automation request to pause was acknowledged",
}
```

### RequestedResume
A request to resume the automation was recieved.
```
{
    "event": "requested_resume",
    "automation_id": "<uuid>",
    "message": "Automation request to resume was acknowledged",
}
```

### RequestedStop
A request to stop the automation was recieved.
```
{
    "event": "requested_stop",
    "automation_id": "<uuid>",
    "message": "Automation request to stop was acknowledged",
}
```

### RequestedUpdate
A request to update the automation was recieved.
```
{
    "event": "requested_update",
    "automation_id": "<uuid>",
    "message": "Automation request to update was acknowledged",
    "details": {
        "settings": {
            ...
        }
    }
}
```

### RequestedFaultReset
A request to reset the faulted state of the automation was recieved.
```
{
    "event": "requested_fault_reset",
    "automation_id": "<uuid>",
    "message": "Automation request to reset fault was acknowledged",
}
```

### RequestedReset
A request to reset the automation was recieved. This will exit
the automation regardless of what state it is in and attempt
to stop and reset whatever automation may be executing.
```
{
    "event": "requested_reset",
    "automation_id": "<uuid>",
    "message": "Automation request to reset was acknowledged",
}
```

### AutomationPaused
The command has been paused by the automation service.
```
{
    "event": "automation_paused",
    "automation_id": "<uuid>",
    "message": "Automation has been paused",
}
```

### AutomationFaulted
The command has faulted and needs to be manually reset.
```
{
    "event": "automation_faulted",
    "automation_id": "<uuid>",
    "message": "Automation has faulted",
}
```

### AutomationFaultReset
The command has been manually reset.
```
{
    "event": "automation_fault_reset",
    "automation_id": "<uuid>",
    "message": "Automation fault has been reset",
}
```

### PLCRequestFailed
A request to the PLC failed to be executed.
```
{
    "event": "plc_request_failed",
    "automation_id": "<uuid>",
    "message": "PLC request <plc_request> failed",
    "details": {
        "plc_request": "<plc_request>",
        "error": "<error>"
    }
}
```

### AutomationFailed
The command somehow failed to execute and is no longer running.
```
{
    "event": "automation_failed",
    "automation_id": "<uuid>",
    "message": "Automation failed to execute",
    "details": {
        "error": "<error>"
    }
}
```

### AutomationUpdated
The command was requested to be updated by the automation service.
This is usually a manual (person) requested action to update
a specific parameter.
```
{
    "event": "automation_updated",
    "automation_id": "<uuid>",
    "message": "Automation has been updated",
    "details": {
        "settings": {
            ...
        }
    }
}
```

### AutomationStopped
The command was requested to be stopped by the automation service.
This is usually a manual (person) requested action.
```
{
    "event": "automation_stopped",
    "automation_id": "<uuid>",
    "message": "Automation has been stopped",
}
```

### AutomationPhaseChanged
The command has changed phases: Preflight, Setup, Main, Teardown
```
{
    "event": "automation_phase_changed",
    "automation_id": "<uuid>",
    "message": "Automation has changed phases from <previous_phase> to <current_phase>",
    "details": {
        "previous_phase": "preflight | setup | main | teardown | ready",
        "current_phase": "preflight | setup | main | teardown | ready",
    }
}
```

### AutomationCompleted
The command has completed it's execution and is no longer running.
```
{
    "event": "automation_completed",
    "automation_id": "<uuid>",
    "message": "Automation has completed",
}
```