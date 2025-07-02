import json
import tempfile

from django.test import override_settings

import pytest

from shuup.testing.image_generator import generate_image
from shuup.utils.django_compat import reverse
from shuup_tests.utils.fixtures import REGULAR_USER_PASSWORD, REGULAR_USER_USERNAME


@pytest.mark.django_db
@pytest.mark.parametrize("allow_image_uploads", (False, True))
def test_uploads_allowed_setting(client, allow_image_uploads, regular_user):
    client.login(username=REGULAR_USER_USERNAME, password=REGULAR_USER_PASSWORD)
    with override_settings(
        SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD=allow_image_uploads
    ):
        if allow_image_uploads:
            tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
            generate_image(120, 120).save(tmp_file)
            with open(tmp_file.name, "rb") as data:
                response = client.post(
                    reverse("shuup:media-upload"),
                    data=dict({"file": data}),
                    format="multipart",
                )
            assert response.status_code == 200
            data = json.loads(response.content.decode("utf-8"))
            assert data["file"]["id"]
        else:
            tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
            generate_image(120, 120).save(tmp_file)
            with open(tmp_file.name, "rb") as data:
                response = client.post(
                    reverse("shuup:media-upload"),
                    data=dict({"file": data}),
                    format="multipart",
                )
            assert response.status_code == 403


@pytest.mark.django_db
def test_anon_uploads(client):
    with override_settings(SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD=True):
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        generate_image(120, 120).save(tmp_file)
        with open(tmp_file.name, "rb") as data:
            response = client.post(
                reverse("shuup:media-upload"),
                data=dict({"file": data}),
                format="multipart",
            )
        assert response.status_code == 302  # Anon uploads not allowed


@pytest.mark.django_db
def test_with_invalid_image(client, regular_user):
    client.login(username=REGULAR_USER_USERNAME, password=REGULAR_USER_PASSWORD)
    with override_settings(SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD=True):
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
        tmp_file.write(b"Hello world!")
        tmp_file.seek(0)
        with open(tmp_file.name, "rb") as data:
            response = client.post(
                reverse("shuup:media-upload"),
                data=dict({"file": data}),
                format="multipart",
            )
        assert response.status_code == 400
        data = json.loads(response.content.decode("utf-8"))
        assert "not an image or a corrupted image" in data["error"]


@pytest.mark.django_db
def test_large_file(client, regular_user):
    client.login(username=REGULAR_USER_USERNAME, password=REGULAR_USER_PASSWORD)
    with override_settings(SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD=True):
        with override_settings(SHUUP_FRONT_MAX_UPLOAD_SIZE=10):
            tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg")
            generate_image(120, 120).save(tmp_file)
            with open(tmp_file.name, "rb") as data:
                response = client.post(
                    reverse("shuup:media-upload"),
                    data=dict({"file": data}),
                    format="multipart",
                )
            assert response.status_code == 400
            data = json.loads(response.content.decode("utf-8"))
            assert "Maximum file size reached" in data["error"]
