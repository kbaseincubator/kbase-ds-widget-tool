def object_info_to_dict(object_info):
    [
        object_id,
        object_name,
        type_id,
        save_date,
        version,
        saved_by,
        workspace_id,
        workspace_name,
        checksum,
        size,
        metadata,
    ] = object_info

    return {
        'object_id': object_id,
        'object_name': object_name,
        'type_id': type_id,
        'save_date': save_date,
        'version': version,
        'saved_by': saved_by,
        'workspace_id': workspace_id,
        'workspace_name': workspace_name,
        'checksum': checksum,
        'size': size,
        'metadata': metadata,
    }

def workspace_info_to_dict(workspace_info):
    [
        workspace_id,
        workspace_name,
        owner,
        modified_at,
        max_object_id,
        user_permission,
        global_permission,
        lock_status,
        metadata,
    ] = workspace_info

    return {
        'workspace_id': workspace_id,
        'workspace_name': workspace_name,
        'owner': owner,
        'modified_at': modified_at,
        'max_object_id': max_object_id,
        'user_permission': user_permission,
        'global_permission': global_permission,
        'lock_status': lock_status,
        'metadata': metadata,
    }

def get_param(params, key):
    """ 
    Safely gets a parameter from the dict created by parse_qs.

    The parsed search params is not a straight dict, as the value is an array, to
    accommodate multiple parameters (a rare case!).
    """
    value = params.get(key)
    if value is None:
        return None
    if len(value) != 1:
        return None
    return value[0]
