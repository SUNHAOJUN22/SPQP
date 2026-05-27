from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_validate_upload_rejects_path_traversal_and_bad_extension() -> None:
    traversal = client.post("/api/files/validate-upload", params={"file_name": "..\\bad.log"})
    assert traversal.status_code == 200
    assert traversal.json()["allowed"] is False
    assert "非法路径" in traversal.json()["reason"]

    bad_type = client.post("/api/files/validate-upload", params={"file_name": "payload.exe"})
    assert bad_type.status_code == 200
    assert bad_type.json()["allowed"] is False
    assert bad_type.json()["reason"] == "不允许的文件类型。"


def test_upload_interfaces_return_chinese_security_errors() -> None:
    gaussian = client.post("/api/gaussian/upload-log", files={"file": ("..\\bad.log", "x", "text/plain")})
    assert gaussian.status_code == 400
    assert "非法路径" in gaussian.json()["detail"]

    cube = client.post("/api/cube/upload", files={"file": ("bad.exe", "x", "text/plain")})
    assert cube.status_code == 400
    assert "cube" in cube.json()["detail"]


def test_report_generation_keeps_mock_data_boundary() -> None:
    response = client.post("/api/reports/generate", json={"project_title": "安全边界报告", "format": "markdown"})
    assert response.status_code == 200
    report = response.json()["content"]
    assert "示例数据" in report
    assert "不能作为真实" in report
