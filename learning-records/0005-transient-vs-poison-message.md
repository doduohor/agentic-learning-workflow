# Transient vs poison message distinction understood

The user correctly explained that a missing event_id is not a transient failure because retrying will not make the malformed payload fix itself. Future lessons can assume the user understands the difference between temporary infrastructure failures and stable contract or payload failures that belong in DLQ.
