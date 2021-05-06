class TestAPI:
    def test_take_backup(self, fastapi_client):
        response = fastapi_client.post("/backup")
        assert response.status_code == 201
        assert response.json() == {"result": "Successfully finished the backup process"}

    def test_prepare_backup(self, fastapi_client):
        response = fastapi_client.post("/prepare")
        assert response.status_code == 200
        assert response.json() == {"result": "Successfully prepared all the backups"}

    def test_list_backups(self, fastapi_client):
        response = fastapi_client.get("/backups")
        assert response.status_code == 200

    def test_delete_backups(self, fastapi_client):
        response = fastapi_client.delete("/delete")
        assert response.status_code == 200
        assert response.json() == {
            "result": "There is no backups or backups removed successfully"
        }
