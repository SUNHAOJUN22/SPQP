from fastapi.testclient import TestClient

from app.main import app
from app.services.advanced_parsers import (
    classify_nci_region,
    parse_goodvibes_output,
    parse_nci_output,
    parse_qtaim_output,
)


client = TestClient(app)


def test_goodvibes_qtaim_nci_read_only_parsers() -> None:
    goodvibes = parse_goodvibes_output("o MCSOMe.log 298.15 -100.000 -99.900 -99.850 -99.910", "goodvibes.out")
    assert goodvibes["quality"] == "partial"
    assert goodvibes["entries"][0]["file"] == "MCSOMe.log"
    assert goodvibes["entries"][0]["qh_gibbs_hartree"] == -99.91

    qtaim = parse_qtaim_output("BCP Si-O rho=0.112 laplacian=0.321 H=-0.025 V=-0.090 G=0.065 ellipticity=0.02")
    assert qtaim["quality"] == "partial"
    assert qtaim["bond_critical_points"][0]["label"] == "Si-O"
    assert qtaim["bond_critical_points"][0]["rho_bcp"] == 0.112

    nci = parse_nci_output("region A sign(lambda2)rho=-0.032 RDG=0.18\nregion B sign(lambda2)rho=0.041 RDG=0.22")
    assert nci["quality"] == "partial"
    assert nci["regions"][0]["color"] == "blue"
    assert nci["regions"][1]["color"] == "red"
    assert classify_nci_region(0.0) == ("弱范德华", "green")


def test_advanced_parser_api_returns_chinese_failed_states() -> None:
    assert client.post("/api/parse/goodvibes", json={"text": "", "file_name": "empty.out"}).json()["quality"] == "failed"
    assert client.post("/api/parse/qtaim", json={"text": "", "file_name": "empty.txt"}).json()["warnings"]
    assert client.post("/api/parse/nci", json={"text": "", "file_name": "empty.txt"}).json()["warnings"]


def test_mcp_safe_tool_endpoints_do_not_open_shell_execution() -> None:
    tools = client.get("/api/mcp/tools")
    assert tools.status_code == 200
    assert "不执行 shell" in tools.json()["provenance"]

    resources = client.get("/api/mcp/resources")
    assert resources.status_code == 200
    assert resources.json()["resources"]

    prompt = client.post("/api/mcp/generate-prompt", json={"topic": "MCSOMe O→Ti 毒化"})
    assert prompt.status_code == 200
    assert "安全边界" in prompt.json()["prompt"]
    assert "证据等级" in prompt.json()["prompt"]
    assert "最小计算任务" in prompt.json()["prompt"] or "最小软件任务" in prompt.json()["prompt"]

    run = client.post("/api/mcp/run-tool", json={"tool_name": "validate-upload", "arguments": {"file_name": "safe.log"}})
    assert run.status_code == 200
    assert run.json()["result"]["allowed"] is True

    blocked = client.post("/api/mcp/run-tool", json={"tool_name": "run-shell", "arguments": {"command": "whoami"}})
    assert blocked.status_code == 400
    assert "安全白名单" in blocked.json()["detail"]


def test_top_scientist_protocol_is_structured_and_callable() -> None:
    protocol = client.get("/api/research/top-scientist-protocol")
    assert protocol.status_code == 200
    payload = protocol.json()
    assert payload["name"] == "顶尖科学家能力进化协议"
    assert any(item["key"] == "DCS" for item in payload["research_objects"])
    assert "永远区分聚合阶段与后处理阶段。" in payload["scientific_principles"]
    assert {row["level"] for row in payload["evidence_levels"]} == {"A", "B", "C", "D"}
    assert "minimal_calculation" in payload["falsifiable_task_template"]
    assert any(item["type"] == "机制判据" for item in payload["software_mapping"])
    assert "insertion TS" in payload["quantum_tasks"]
    assert any(item["name"] == "NBO" for item in payload["electronic_analysis_requirements"])
    assert "DCP" in payload["peroxide_analysis_requirements"]["species"]
    assert any(item["method"] == "GPC / MFR" for item in payload["experimental_mapping"])
    assert "忽略过渡态虚频和 IRC" in payload["forbidden_behaviors"]
    assert payload["report_driven_extension"]["evidence_policy"].startswith("报告抽取结果")
    assert "GET /api/literature/report-knowledge" in payload["report_driven_extension"]["software_targets"]

    prompt = client.post("/api/research/top-scientist-prompt", json={"topic": "PP β-scission 与 Si–C 连接臂稳定性"})
    assert prompt.status_code == 200
    assert "四轴定位" in prompt.json()["prompt"]
    assert "证据等级" in prompt.json()["prompt"]
    assert "量子化学任务" in prompt.json()["prompt"]
    assert "过氧化物与羰基三分法" in prompt.json()["prompt"]
    assert "报告驱动闭环" in prompt.json()["prompt"]
    assert "安全边界" in prompt.json()["prompt"]

    tool = client.post(
        "/api/mcp/run-tool",
        json={"tool_name": "generate-top-scientist-prompt", "arguments": {"topic": "DMOS O→Ti 毒化"}},
    )
    assert tool.status_code == 200
    assert tool.json()["result"]["protocol"]["name"] == "顶尖科学家能力进化协议"


def test_prompt_required_alias_endpoints() -> None:
    molecules = client.get("/api/molecules").json()
    conformer = client.post(f"/api/molecules/{molecules[0]['id']}/conformers")
    assert conformer.status_code == 200
    assert "不是 Gaussian 优化几何" in conformer.json()["provenance"]

    gauss = client.post("/api/gaussian/parse-log", json={"text": "", "file_name": "empty.log"})
    assert gauss.status_code == 200
    assert gauss.json()["quality"] == "failed"

    hydrolysis = client.post("/api/analysis/hydrolysis-condensation", json={})
    assert hydrolysis.status_code == 200
    assert "当前数据不足" in hydrolysis.json()["interpretations"][0]

    radical = client.post("/api/analysis/radical-beta-scission", json={"oxygen_level_percent": 0.0})
    assert radical.status_code == 200
    assert "β-scission" in radical.json()["focus"]

    experimental = client.post("/api/experimental/import-gpc", json={"records": [{"sample_key": "A", "mw": 200000}]})
    assert experimental.status_code == 200
    assert experimental.json()["count"] == 1
