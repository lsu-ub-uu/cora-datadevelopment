def get_visibility(source_record):
    """
    Returns the visibility status for a publication.

    :return: The visibility status as a string.
    """
    updates = source_record.findall('./administrativeInfo/updaters/userInformation/userAction')
    # Filter out userActions that are 'UPDATED'
    publish_updates = [update for update in updates if update != 'UPDATED']

    if publish_updates:
        last_update = publish_updates[-1]
        if last_update in ("PUBLISHED", "AUTOPUBLISHED"):
            return "published"
    return "unpublished"