

def media_folder_from_folder(folder):
    """
    Gets media folder from folder

    :param Folder: the folder you want to get the media folder from

    :rtype: shuup.MediaFolder
    """

    return folder.media_folder.first()
