def get_visibility(source_record):
    """
    Returns the visibility status for a publication.

    :return: The visibility status as a string.
    """
    user_action = source_record.find('./administrativeInfo/creatorInfo/userAction')
    updates = source_record.findall('./administrativeInfo/updaters/userInformation/userAction')

    # Filter out userActions that are 'UPDATED'
    publish_updates = [update for update in updates if update.text != 'UPDATED']

    if publish_updates:
        last_update = publish_updates[-1]
        if last_update.text in ("PUBLISHED", "AUTOPUBLISHED"):
            return "published"
        elif last_update.text == "DELETED":
            return "hidden"
    elif user_action is not None and user_action.text == "CREATED":
        return "published"

    return "unpublished"