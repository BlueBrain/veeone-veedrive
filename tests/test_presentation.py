import pymongo
import pytest

from veedrive import config

presentation_test_id = "1509d5ec-163f-4a79-8942-4a8b74dbd438"


@pytest.mark.asyncio
async def test_save_and_load_presentation(testing_backend):
    mongo_client = pymongo.MongoClient(config.DB_HOST, config.DB_PORT)
    mongo_client.drop_database(config.DB_NAME)
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


@pytest.mark.asyncio
async def test_listing_presentations(testing_backend):
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


@pytest.mark.asyncio
async def test_deleting_presentations(testing_backend):
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
