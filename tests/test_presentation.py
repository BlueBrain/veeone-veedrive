import pytest

from veedrive import config

presentation_test_id = "1509d5ec-163f-4a79-8942-4a8b74dbd438"
presentation_in_folder_id = "2783a682-e79f-4433-930d-1924f205a818"


@pytest.mark.asyncio
async def test_save_and_load_presentation(testing_backend, setup_db):
    presentation_payload = {"id": presentation_test_id, "name": "My presentation"}
    presentation_payload_update = {
        "id": presentation_test_id,
        "name": "My better presentation",
    }

    # Save presentation
    presentation_save_payload_1 = {
        "method": "SavePresentation",
        "id": "1",
        "params": presentation_payload,
    }
    response_save_1 = await testing_backend.send_ws(presentation_save_payload_1)
    assert isinstance(response_save_1["result"], str)

    # Load presentation
    presentation_load_payload_1 = {
        "method": "GetPresentation",
        "id": "2",
        "params": {"id": presentation_test_id},
    }
    response_load_1 = await testing_backend.send_ws(presentation_load_payload_1)
    assert response_load_1["result"]["id"] == presentation_test_id
    assert response_load_1["result"]["name"] == "My presentation"

    # Update presentation
    presentation_save_payload_2 = {
        "method": "SavePresentation",
        "id": "3",
        "params": presentation_payload_update,
    }
    response_save_2 = await testing_backend.send_ws(presentation_save_payload_2)
    assert isinstance(response_save_2["result"], str)

    # Load updated presentation
    presentation_load_payload_2 = {
        "method": "GetPresentation",
        "id": "4",
        "params": {"id": presentation_test_id},
    }
    response_load_2 = await testing_backend.send_ws(presentation_load_payload_2)
    assert response_load_2["result"]["id"] == presentation_test_id
    assert response_load_2["result"]["name"] == "My better presentation"

    presentation_payload_with_folder = {
        "id": presentation_in_folder_id,
        "name": "My presentation in folder",
        "folder": "folder1",
    }
    presentation_save_payload_folder = {
        "method": "SavePresentation",
        "id": "1",
        "params": presentation_payload_with_folder,
    }
    response_save_1 = await testing_backend.send_ws(presentation_save_payload_folder)
    assert isinstance(response_save_1["result"], str)

    presentation_load_folder = {
        "method": "GetPresentation",
        "id": "2",
        "params": {"id": presentation_in_folder_id},
    }
    response_load_1 = await testing_backend.send_ws(presentation_load_folder)
    assert response_load_1["result"]["id"] == presentation_in_folder_id
    assert response_load_1["result"]["name"] == "My presentation in folder"


@pytest.mark.asyncio
async def test_listing_presentations(testing_backend, setup_db):
    request_payload = {
        "method": "ListPresentations",
        "id": "1",
        "params": {},
    }
    response = await testing_backend.send_ws(request_payload)
    assert response["id"] == "1"
    assert response["result"]["count"] == 1
    assert isinstance(response["result"]["results"], list)
    assert response["result"]["results"][0]["id"] == presentation_test_id
    assert response["result"]["results"][0]["name"] == "My better presentation"

    request_payload = {
        "method": "ListPresentations",
        "id": "1",
        "params": {"folder": "folder1"},
    }
    response = await testing_backend.send_ws(request_payload)
    assert response["id"] == "1"
    assert response["result"]["count"] == 1
    assert isinstance(response["result"]["results"], list)
    assert response["result"]["results"][0]["name"] == "My presentation in folder"


@pytest.mark.asyncio
async def test_listing_presentation_versions(testing_backend, setup_db):
    request_payload = {
        "method": "PresentationVersions",
        "id": "1",
        "params": {"id": presentation_test_id},
    }
    await testing_backend.send_ws(request_payload)

    response_load = await testing_backend.send_ws(request_payload)

    assert "result" in response_load
    result_list = response_load["result"]
    assert result_list[0]["id"] == presentation_test_id
    assert result_list[len(result_list) - 1]["id"] == presentation_test_id


@pytest.mark.asyncio
async def test_deleting_presentations(testing_backend, setup_db):
    request_payload = {
        "method": "DeletePresentation",
        "id": "1",
        "params": {"id": presentation_test_id},
    }
    await testing_backend.send_ws(request_payload)

    request_payload = {
        "method": "GetPresentation",
        "id": "1",
        "params": {"id": presentation_test_id},
    }
    response_load = await testing_backend.send_ws(request_payload)

    assert "error" in response_load
    assert response_load["error"]["message"] == "Presentation not found"


@pytest.mark.asyncio
async def test_folder_creation(testing_backend, setup_db):
    request_payload = {
        "method": "CreateFolder",
        "id": "1",
        "params": {"folder_name": "folder1"},
    }
    response_load = await testing_backend.send_ws(request_payload)
    assert response_load["result"] == "OK"

    response_load = await testing_backend.send_ws(request_payload)
    assert response_load["error"]["message"] == "Folder already exists"

    request_payload["params"] = {"folder_name": "folder2"}
    response_load = await testing_backend.send_ws(request_payload)
    assert response_load["result"] == "OK"


@pytest.mark.asyncio
async def test_folder_listing(testing_backend, setup_db):
    request_payload = {
        "method": "ListFolders",
        "id": "1",
    }
    response_load = await testing_backend.send_ws(request_payload)
    assert response_load["result"] == ["folder1", "folder2"]


@pytest.mark.asyncio
async def test_folder_deletion(testing_backend, setup_db):
    request_payload = {
        "method": "RemoveFolder",
        "id": "1",
        "params": {"folder_name": "folder1"},
    }
    response_load = await testing_backend.send_ws(request_payload)
    assert (
        response_load["error"]["message"]
        == "Cannot remove, folder contains presentations"
    )

    request_payload["params"] = {"folder_name": "folder2"}
    response_load = await testing_backend.send_ws(request_payload)
    assert response_load["result"] == "OK"

    response_load = await testing_backend.send_ws(request_payload)
    assert response_load["error"]

    request_payload = {
        "method": "ListFolders",
        "id": "1",
    }
    response_load = await testing_backend.send_ws(request_payload)
    assert response_load["result"] == ["folder1"]


@pytest.mark.asyncio
async def test_saving_presentation_with_same_name(testing_backend, setup_db):
    presentation_save_payload = {
        "method": "SavePresentation",
        "id": "1",
        "params": {"id": presentation_test_id, "name": "My presentation"},
    }
    response_save_1 = await testing_backend.send_ws(presentation_save_payload)
    assert isinstance(response_save_1["result"], str)

    presentation_save_payload = {
        "method": "SavePresentation",
        "id": "1",
        "params": {
            "id": "1509d5ec-163f-4a79-8942-4a8b74dbd430",
            "name": "My presentation" },
    }

    response_load_1 = await testing_backend.send_ws(presentation_save_payload)
    assert response_load_1["error"]["code"] == 10

    presentation_save_payload = {
        "method": "SavePresentation",
        "id": "1",
        "params": {
            "id": "1509d5ec-163f-4a79-8942-4a8b74dbd430",
            "name": "My presentation",
            "folder": "folder1"},
    }
    response_load_1 = await testing_backend.send_ws(presentation_save_payload)
    assert response_load_1["result"] == "ok"
