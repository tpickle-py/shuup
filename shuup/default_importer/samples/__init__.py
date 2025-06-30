import os


def get_sample_file_content(file_name):
    path = os.path.join(os.path.dirname(__file__), file_name)
    if os.path.exists(path):
        from six import BytesIO

        return BytesIO(open(path, "rb").read())
