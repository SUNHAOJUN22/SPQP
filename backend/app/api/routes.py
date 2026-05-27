from __future__ import annotations

import csv
import io
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.constants import ALLOWED_UPLOAD_EXTENSIONS, HARTREE_TO_KCAL_MOL
from app.data.seed import MOCK_DESCRIPTOR_MATRIX
from app.db.session import get_db
from app.models.database import (
    CatalystModel,
    Conformer,
    CubeFile,
    ExperimentRecord,
    ExperimentalDataset,
    GaussianJob,
    GaussianOutput,
    LiteratureSource,
    LiteratureEvidenceItem,
    MechanismHypothesis,
    McpTask,
    Molecule,
    MonomerFamily,
    PeroxideSpecies,
    Report,
    ThesisEntity,
)
from app.schemas.api import (
    AdvancedGaussianTaskRequest,
    BdeRequest,
    BdeResponse,
    BindingEnergyResponse,
    BondDescriptorRequest,
    BoltzmannWeightsRequest,
    CubeUploadResponse,
    DecisionEngineCandidate,
    DecisionEngineRequest,
    DecisionEngineResponse,
    DftExperimentCorrelationRequest,
    ExperimentCsvImportRequest,
    FourAxisDecisionRequest,
    EnergyComponentsRequest,
    GaussianInputRequest,
    GaussianInputResponse,
    GaussianLogTextRequest,
    InsertionProfileRequest,
    InsertionProfileResponse,
    McpPromptRequest,
    McpToolRunRequest,
    MechanismHypothesisRequest,
    MoleculeIntelligenceRequest,
    MoleculeCreate,
    MoleculeRead,
    ParsedGaussianLog,
    OcrTextImportRequest,
    OcrTextImportResponse,
    PeroxideProfileRequest,
    PolypropyleneRadicalReviewImportRequest,
    PolypropyleneRadicalReviewImportResponse,
    RadicalKineticsRequest,
    RadicalCompetitionRequest,
    RateComparisonRequest,
    ReadOnlyTextParseRequest,
    ReactionProfileAnalysisRequest,
    ReportRequest,
    ReportDocxImportRequest,
    ReportDocxImportResponse,
    ResidenceTimeWindowRequest,
    ScientificEnergyWorkbenchRequest,
    SiCStabilityRequest,
    TEABindingRequest,
    ThesisImportRequest,
    ThesisImportResponse,
    TiPoisoningRequest,
    TiPoisoningResponse,
    UnifiedLCBFrameworkRequest,
    WignerRateRequest,
)
from app.services.advanced_gaussian_builder import GaussianBuilder as AdvancedGaussianBuilder
from app.services.advanced_parsers import parse_goodvibes_output, parse_nci_output, parse_qtaim_output
from app.services.chemistry import describe_molecule, xyz_from_smiles
from app.services.cube import cube_difference_preview, cube_slice_preview, cube_volume_preview, parse_cube_metadata
from app.services.energy import (
    bond_dissociation_energy,
    classify_bde,
    classify_binding,
    decision_scores,
    delta_g_binding,
    delta_g_poison,
    insertion_profile,
    rate_comparison,
)
from app.services.gaussian_parser import parse_gaussian_log_text
from app.services.gaussian_templates import generate_gaussian_input
from app.services.integrated_science import analyze_reaction_profile, integration_source_map
from app.services.literature import (
    REPORT_TITLE,
    default_mechanism_hypotheses,
    extract_docx_text,
    extract_report_driven_knowledge,
    extract_thesis_knowledge,
)
from app.services.mcp_workflow import (
    generate_research_prompt,
    generate_top_scientist_protocol_prompt,
    get_top_scientist_protocol,
    list_mcp_resources,
    list_mcp_tools,
)
from app.services.molecule_intelligence import analyze_molecule_intelligence
from app.services.reports import generate_report
from app.services.radical_v4 import (
    PEROXIDE_LIBRARY,
    analyze_polypropylene_radical_literature,
    assess_text_quality,
    calculate_roor_bde,
    carbonyl_taxonomy,
    experimental_design_matrix,
    import_polypropylene_radical_review,
    peroxide_profile,
    radical_branching_vs_scission,
    residence_time_window,
    sic_stability,
    unified_lcb_framework,
)
from app.services.ultra_science import (
    calculate_boltzmann_weights,
    calculate_bde_sic as ultra_calculate_bde_sic,
    calculate_k_rel_with_tunneling,
    four_axis_model,
    merged_ultra_inventory,
    radical_kinetics_engine,
)

router = APIRouter()


def _upload_name_error(file_name: str | None, allowed_extensions: set[str] | None = None) -> str | None:
    allowed_extensions = allowed_extensions or ALLOWED_UPLOAD_EXTENSIONS
    raw_name = (file_name or "").strip()
    if not raw_name:
        return "文件名为空。"
    if len(raw_name) > 240:
        return "文件名过长。"
    if "\x00" in raw_name or "/" in raw_name or "\\" in raw_name or ".." in raw_name:
        return "检测到非法路径。"
    if PureWindowsPath(raw_name).is_absolute() or PurePosixPath(raw_name).is_absolute():
        return "检测到非法路径。"
    if Path(raw_name).name != raw_name:
        return "检测到非法路径。"
    if Path(raw_name).suffix.lower() not in allowed_extensions:
        return "不允许的文件类型。"
    return None


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "硅氧键催化量子研究平台 API"}


@router.get("/merged/ultra-inventory")
def get_merged_ultra_inventory() -> dict:
    return merged_ultra_inventory()


@router.get("/integration/source-map")
def get_integration_source_map() -> dict:
    return integration_source_map()


@router.get("/integration/gaussian-task-groups")
def get_integration_gaussian_task_groups() -> dict:
    groups = AdvancedGaussianBuilder.get_task_groups()
    return {
        "groups": groups,
        "total_tasks": sum(len(items) for items in groups.values()),
        "provenance": "任务模板已从 Si-O 子项目拆入根项目 backend/app/services/advanced_gaussian_builder.py；服务器只生成文本，不执行 Gaussian 或 cubegen。",
    }


TASK_TITLE_ZH = {
    "monomer_opt": "孤立单体优化 / 频率 / NBO",
    "monomer_sp": "单体高水平单点能修正",
    "si_nmr": "29Si GIAO 核磁计算",
    "sio_bde": "Si–O 键解离能计算",
    "sic_bde": "Si–C 键解离能计算",
    "si_cl_hydrolysis": "Si–Cl 水解模型",
    "si_ome_hydrolysis": "Si–OMe 水解模型",
    "tea_cp": "TEA 络合 Counterpoise 计算",
    "al_o_complex": "Al←O 络合物优化",
    "al_cl_complex": "Al···Cl 络合物优化",
    "al_cc_complex": "Al···C=C 络合物优化",
    "ti_pi_complex": "Ti 生产性 C=C π-络合物",
    "oti_poison": "O→Ti 非生产性毒化络合物",
    "folded_pi_o": "折叠 π+O 双功能络合物",
    "insert_ts": "插入反应过渡态",
    "insert_irc": "插入 IRC 本征反应坐标验证",
    "product_opt": "插入产物优化",
    "distortion_sp": "片段变形单点能",
    "seq_silane_after_hex": "1-己烯后硅烷插入序列",
    "seq_hex_after_silane": "硅烷后 1-己烯插入序列",
    "hydrolysis_ts": "Si–Cl / Si–OMe 水解过渡态",
    "condensation_ts": "Si–OH 缩合过渡态",
    "sio_si_bridge": "Si–O–Si 桥联模型优化",
    "hcl_elim": "HCl / MeOH 离去模型",
    "perox_homolysis": "过氧化物 RO–OR 均裂",
    "h_abstract": "RO• 抽取 PP 叔氢过渡态",
    "pp_beta_ts": "PP 自由基 β-scission 过渡态",
    "pp_recomb": "PP 自由基复合模型",
    "pp_coagent_graft": "PP 自由基 + coagent 接枝过渡态",
    "pp_silane_reaction": "PP 自由基 + 硅烷侧链反应",
    "oxidation_side": "氧化副反应模型",
    "formchk": "formchk 命令模板",
    "cubegen_dens": "cubegen 电子密度模板",
    "cubegen_esp": "cubegen ESP 静电势模板",
    "cubegen_homo_lumo": "cubegen HOMO/LUMO 模板",
    "multiwfn_script": "Multiwfn 脚本模板",
}


@router.get("/scientific-computation/task-matrix")
def scientific_computation_task_matrix() -> dict:
    group_meta = {
        "A": {"label": "单体与键本征", "goal": "获得 DCS/MCSOMe/DMOS 的结构、频率、NBO、29Si NMR 与 Si–O/Si–C/Si–Cl BDE。"},
        "B": {"label": "TEA / Ti 配位竞争", "goal": "比较 Al←O、Al···Cl、Al···C=C、C=C π-complex 与 O→Ti 毒化络合。"},
        "C": {"label": "插入反应路径", "goal": "验证 1,2-re/si 插入 TS、IRC、产物和片段变形能。"},
        "D": {"label": "水解缩合后反应", "goal": "验证 Si–Cl/Si–OMe 水解和 Si–O–Si 缩合是否可行。"},
        "E": {"label": "过氧化物自由基路径", "goal": "验证 RO–OR 均裂、RO• 抽氢、PP β-scission、复合、接枝和氧化副反应。"},
        "F": {"label": "波函数可视化后处理", "goal": "生成 formchk/cubegen/Multiwfn 文本模板；本平台只生成命令草稿，不执行外部程序。"},
    }
    reliability = {
        "A": ["优化正常收敛", "频率无虚频（BDE 片段需核验自旋多重度）", "NBO/WBI/NPA 字段可解析"],
        "B": ["络合物优化正常", "Counterpoise 或片段能量来源清楚", "NBO E(2) 与距离共同支持相互作用"],
        "C": ["TS 恰好一个合理虚频", "IRC 连接 π-complex 与插入产物", "无催化剂簇破碎"],
        "D": ["显式水、离去物和质子转移路径明确", "TS 虚频对应水解/缩合坐标", "产物频率验证无虚频"],
        "E": ["开壳层自旋多重度正确", "TS 虚频对应抽氢/β-scission/接枝", "排除氧化副反应或单独建模"],
        "F": ["仅生成命令模板", "用户手动执行后再上传 cube/fchk/Multiwfn 输出", "不得把未执行模板当结果"],
    }
    groups: list[dict[str, Any]] = []
    for group_id, meta in group_meta.items():
        tasks = []
        for task_id, template in AdvancedGaussianBuilder.TASK_TEMPLATES.items():
            if template.get("group") != group_id:
                continue
            tasks.append(
                {
                    "task_id": task_id,
                    "title": TASK_TITLE_ZH.get(task_id, template["title"]),
                    "english_title": template["title"],
                    "route_or_command": template["keywords"],
                    "memory": template.get("mem"),
                    "nproc": template.get("nproc"),
                    "charge": template.get("charge", "需用户核验"),
                    "multiplicity": template.get("mult", "需用户核验"),
                    "expected_outputs": _expected_task_outputs(task_id),
                    "reliability_criteria": reliability[group_id],
                    "is_utility": bool(template.get("is_utility", False)),
                    "safety_note": "只生成文本模板，不执行 Gaussian、cubegen、Multiwfn 或任何 shell。",
                }
            )
        groups.append({"group_id": group_id, **meta, "tasks": tasks})
    return {
        "groups": groups,
        "total_tasks": sum(len(group["tasks"]) for group in groups),
        "evidence_grade": "D",
        "provenance": "计算任务矩阵来自内置模板；模板本身不是计算结果，不能作为真实科学结论。",
        "safety_boundaries": ["不执行 Gaussian", "不执行 cubegen", "不执行 Multiwfn", "不执行用户上传文件"],
    }


def _expected_task_outputs(task_id: str) -> list[str]:
    if task_id in {"monomer_opt", "monomer_sp", "si_nmr", "sio_bde", "sic_bde"}:
        return ["Gibbs free energy", "frequencies", "NPA/Mulliken charges", "WBI/Mayer", "NBO E(2)", "29Si NMR 或 BDE 片段能量"]
    if task_id in {"tea_cp", "al_o_complex", "al_cl_complex", "al_cc_complex", "ti_pi_complex", "oti_poison", "folded_pi_o"}:
        return ["ΔGbind/ΔGpoison 输入能量", "Al–O/Al–Cl/Ti–O/Ti–C 距离", "n(O)→Al / n(O)→Ti / π(C=C)→Ti E(2)", "QTAIM/NCI 可选证据"]
    if task_id in {"insert_ts", "insert_irc", "product_opt", "distortion_sp", "seq_silane_after_hex", "seq_hex_after_silane"}:
        return ["ΔGπ", "ΔG‡insert", "ΔG‡complex", "TS 虚频", "IRC 连接", "产物自由能"]
    if task_id in {"hydrolysis_ts", "condensation_ts", "sio_si_bridge", "hcl_elim"}:
        return ["ΔGhydrolysis", "ΔGcondensation", "显式水数量", "HCl/MeOH 离去路径", "Si–O–Si 结构证据"]
    if task_id in {"perox_homolysis", "h_abstract", "pp_beta_ts", "pp_recomb", "pp_coagent_graft", "pp_silane_reaction", "oxidation_side"}:
        return ["RO–OR BDE", "H 抽提势垒", "β-scission 势垒", "复合/接枝势垒", "氧化副反应风险"]
    return ["fchk/cube/Multiwfn 输出文件由用户外部生成后上传", "本平台仅解析上传结果"]


@router.post("/scientific-computation/energy-workbench")
def scientific_energy_workbench(payload: ScientificEnergyWorkbenchRequest) -> dict:
    results: dict[str, Any] = {
        "source": payload.source,
        "evidence_grade": payload.evidence_grade,
        "is_mock": payload.is_mock,
        "temperature_k": payload.temperature_k,
        "reliability_note": "该工作台只使用用户输入或上传解析数据计算；没有 A/B 级数据时不能形成可靠结论。",
    }
    warnings: list[str] = []
    if payload.complex_g_hartree is not None and payload.fragment_g_hartree:
        delta_hartree, delta_kcal = delta_g_binding(payload.complex_g_hartree, payload.fragment_g_hartree)
        results["delta_g_bind"] = {
            "hartree": delta_hartree,
            "kcal_mol": delta_kcal,
            "classification": classify_binding(delta_kcal),
            "formula": "ΔGbind = G(complex) − ΣG(fragments)",
        }
    else:
        warnings.append("缺少络合物或片段 Gibbs 自由能，无法计算 ΔGbind。")
    if payload.o_ti_complex_g_hartree is not None and payload.pi_complex_g_hartree is not None:
        delta, label, color = delta_g_poison(payload.o_ti_complex_g_hartree, payload.pi_complex_g_hartree)
        results["delta_g_poison"] = {
            "kcal_mol": delta,
            "label": label,
            "color": color,
            "formula": "ΔGpoison = G(O→Ti complex) − G(C=C π-complex)",
        }
    else:
        warnings.append("缺少 π-complex 或 O→Ti complex 的自由能，无法计算 ΔGpoison。")
    if (
        payload.free_site_monomer_g_hartree is not None
        and payload.pi_complex_g_hartree is not None
        and payload.ts_g_hartree is not None
    ):
        profile = insertion_profile(
            payload.free_site_monomer_g_hartree,
            payload.pi_complex_g_hartree,
            payload.ts_g_hartree,
            payload.product_g_hartree,
            payload.reference_barrier_kcal_mol,
            payload.temperature_k,
        )
        results["insertion_profile"] = profile.__dict__
    else:
        warnings.append("缺少 TS、π-complex 或参考态自由能，无法计算 ΔG‡。")
    results["warnings"] = warnings
    return results


@router.post("/integration/build-gaussian-task")
def build_integration_gaussian_task(payload: AdvancedGaussianTaskRequest) -> dict:
    kwargs = {
        key: value
        for key, value in {
            "method": payload.method,
            "basis": payload.basis,
            "charge": payload.charge,
            "multiplicity": payload.multiplicity,
            "mem": payload.mem,
            "nproc": payload.nproc,
        }.items()
        if value is not None
    }
    content = AdvancedGaussianBuilder.build_task(payload.task_id, payload.molecule_name, payload.coordinates or None, **kwargs)
    is_utility = payload.task_id in AdvancedGaussianBuilder.TASK_TEMPLATES and AdvancedGaussianBuilder.TASK_TEMPLATES[payload.task_id].get("is_utility", False)
    return {
        "task_id": payload.task_id,
        "molecule_name": payload.molecule_name,
        "file_name": f"{payload.molecule_name}_{payload.task_id}.{'txt' if is_utility else 'gjf'}",
        "content": content,
        "is_utility_command": bool(is_utility),
        "warning": "该接口只生成模板文本。utility command 也不会在服务器执行。",
    }


@router.post("/integration/molecule-intelligence")
def molecule_intelligence(payload: MoleculeIntelligenceRequest) -> dict:
    return analyze_molecule_intelligence(payload.smiles)


@router.post("/parse/goodvibes")
def parse_goodvibes(payload: ReadOnlyTextParseRequest) -> dict:
    return parse_goodvibes_output(payload.text, payload.file_name)


@router.post("/parse/qtaim")
def parse_qtaim(payload: ReadOnlyTextParseRequest) -> dict:
    return parse_qtaim_output(payload.text, payload.file_name)


@router.post("/parse/nci")
def parse_nci(payload: ReadOnlyTextParseRequest) -> dict:
    return parse_nci_output(payload.text, payload.file_name)


@router.post("/integration/reaction-profile")
def reaction_profile_analysis(payload: ReactionProfileAnalysisRequest) -> dict:
    try:
        return analyze_reaction_profile([state.model_dump() for state in payload.states], payload.temperature_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/merged/four-axis-decision")
def merged_four_axis_decision(payload: FourAxisDecisionRequest) -> dict:
    scores = four_axis_model.evaluate(payload.data)
    return {
        "monomer_key": payload.monomer_key,
        "scores": {
            "monomer_intrinsic": scores.monomer_intrinsic,
            "catalyst_compatibility": scores.catalyst_compatibility,
            "radical_processability": scores.radical_processability,
            "microphase_performance": scores.microphase_performance,
            "overall": scores.overall,
        },
        "label": scores.label,
        "explanation": scores.explanation,
        "reliability_note": "四轴判据只压缩已提供数据；缺失数据不会被自动补全，示例输入不能作为真实结论。",
    }


@router.post("/merged/radical-kinetics")
def merged_radical_kinetics(payload: RadicalKineticsRequest) -> dict:
    try:
        return radical_kinetics_engine.simulate_rk4(payload.initial, payload.rate_constants, payload.t_end, payload.steps)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/merged/boltzmann-weights")
def merged_boltzmann_weights(payload: BoltzmannWeightsRequest) -> dict:
    try:
        weights = calculate_boltzmann_weights(payload.energies_kcal_mol, payload.temperature_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "energies_kcal_mol": payload.energies_kcal_mol,
        "weights": weights,
        "temperature_k": payload.temperature_k,
        "formula": "wi = exp[-(Gi - Gmin)/RT] / Σ exp[-(Gj - Gmin)/RT]",
    }


@router.post("/merged/wigner-rate")
def merged_wigner_rate(payload: WignerRateRequest) -> dict:
    try:
        return calculate_k_rel_with_tunneling(
            payload.delta_delta_g_kcal_mol,
            payload.temperature_k,
            payload.nu_imag_1_cm_1,
            payload.nu_imag_2_cm_1,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/analysis/peroxide-library")
def peroxide_library(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(PeroxideSpecies).order_by(PeroxideSpecies.id)).all()
    if rows:
        species = [
            {
                "key": row.key,
                "chinese_name": row.chinese_name,
                "english_name": row.english_name,
                "peroxide_class": row.peroxide_class,
                "has_carbonyl": row.has_carbonyl,
                "radical_type": row.radical_type,
                "example_roor_bde_kcal_mol": row.roor_bde_kcal_mol,
                "typical_role": row.mechanism_note,
                "source": row.source,
            }
            for row in rows
        ]
        provenance = "来自数据库过氧化物结构库；仍需核验半衰期和真实计算数据。"
    else:
        species = PEROXIDE_LIBRARY
        provenance = "内置示例过氧化物库 / MOCK；用于界面与机制假说，不能作为真实工艺结论。"
    return {"species": species, "provenance": provenance}


@router.post("/analysis/peroxide-profile")
def peroxide_profile_endpoint(payload: PeroxideProfileRequest) -> dict:
    data = payload.model_dump()
    if data.get("roor_bde_kcal_mol") is None and data.get("g_radicals_hartree") is not None and data.get("g_peroxide_hartree") is not None:
        bde = calculate_roor_bde(float(data["g_radicals_hartree"]), float(data["g_peroxide_hartree"]))
        data["roor_bde_kcal_mol"] = bde["bde_kcal_mol"]
    return peroxide_profile(data)


@router.post("/analysis/radical-branching-vs-scission")
def radical_branching_vs_scission_endpoint(payload: RadicalCompetitionRequest) -> dict:
    return radical_branching_vs_scission(payload.model_dump())


@router.post("/analysis/sic-stability")
def sic_stability_endpoint(payload: SiCStabilityRequest) -> dict:
    data = payload.model_dump()
    if data.get("bde_sic_kcal_mol") is None and data.get("g_sic_fragments_hartree") is not None and data.get("g_sic_molecule_hartree") is not None:
        data["bde_sic_kcal_mol"] = (float(data["g_sic_fragments_hartree"]) - float(data["g_sic_molecule_hartree"])) * HARTREE_TO_KCAL_MOL
    return sic_stability(data)


@router.post("/analysis/residence-time-window")
def residence_time_window_endpoint(payload: ResidenceTimeWindowRequest) -> dict:
    return residence_time_window(payload.model_dump())


@router.post("/analysis/unified-lcb-framework")
def unified_lcb_framework_endpoint(payload: UnifiedLCBFrameworkRequest) -> dict:
    return unified_lcb_framework(payload.model_dump())


@router.get("/analysis/carbonyl-taxonomy")
def carbonyl_taxonomy_endpoint() -> dict:
    return carbonyl_taxonomy()


@router.get("/analysis/peroxide-experimental-design")
def peroxide_experimental_design_endpoint() -> dict:
    return experimental_design_matrix()


def _upsert_by_key(db: Session, model: type, key: str, values: dict) -> None:
    existing = db.scalar(select(model).where(model.key == key))
    if existing is not None:
        for field, value in values.items():
            setattr(existing, field, value)
        return
    db.add(model(**values))


@router.post("/literature/import-thesis", response_model=ThesisImportResponse)
def import_thesis(payload: ThesisImportRequest, db: Session = Depends(get_db)) -> ThesisImportResponse:
    try:
        text = extract_docx_text(payload.path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    knowledge = extract_thesis_knowledge(text)
    source = LiteratureSource(
        title=payload.title,
        path=payload.path,
        source_type="docx",
        summary="博士论文知识抽取：功能 α-烯烃、Ziegler–Natta 催化剂、空间位阻与电子效应。",
        extracted_text_preview=text[:2400],
        provenance={
            "policy": "仅读取 docx 文本，不执行宏或外部命令。",
            "mock_policy": "抽取实体为文献线索，不等同真实量子化学计算结果。",
            "keywords": knowledge["keywords"],
        },
    )
    db.add(source)
    db.flush()
    entity_reads = []
    for entity in knowledge["entities"]:
        row = ThesisEntity(literature_source_id=source.id, **entity)
        db.add(row)
        entity_reads.append(entity)
    for item in knowledge["catalyst_models"]:
        _upsert_by_key(db, CatalystModel, item["key"], item)
    for item in knowledge["monomer_families"]:
        _upsert_by_key(db, MonomerFamily, item["key"], item)
    db.commit()
    return ThesisImportResponse(
        title=payload.title,
        path=payload.path,
        text_length=len(text),
        entities=entity_reads,
        catalyst_models=knowledge["catalyst_models"],
        monomer_families=knowledge["monomer_families"],
        warnings=knowledge["warnings"],
        provenance="已从 docx 只读抽取论文知识；不会把抽取趋势当作真实量子化学结论。",
    )


@router.get("/literature/entities")
def list_literature_entities(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(ThesisEntity).order_by(ThesisEntity.created_at.desc())).all()
    if not rows:
        knowledge = extract_thesis_knowledge("")
        return {
            "entities": knowledge["entities"],
            "provenance": "尚未导入论文全文；返回内置论文主题示例实体。",
        }
    return {
        "entities": [
            {
                "category": row.category,
                "name": row.name,
                "chinese_name": row.chinese_name,
                "evidence": row.evidence,
                "confidence": row.confidence,
                "source": row.source,
            }
            for row in rows
        ],
        "provenance": "来自已导入博士论文 docx 的结构化抽取记录。",
    }


@router.post("/literature/import-polypropylene-radical-review", response_model=PolypropyleneRadicalReviewImportResponse)
def import_polypropylene_radical_review_endpoint(
    payload: PolypropyleneRadicalReviewImportRequest,
    db: Session = Depends(get_db),
) -> PolypropyleneRadicalReviewImportResponse:
    try:
        result = import_polypropylene_radical_review(payload.path, payload.title)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    source = LiteratureSource(
        title=result["title"],
        path=result["path"],
        source_type=result["source_type"],
        summary="聚丙烯过氧化物自由基反应综述/论文只读抽取：PP 降解、交联、长链支化、羰基过氧化物和微结构变量。",
        extracted_text_preview=result["text_preview"],
        provenance={
            "policy": "仅读取文献文本；不执行 PDF、宏、Gaussian、cubegen 或 Multiwfn。",
            "evidence_level": "C",
            "parse_quality": result["parse_quality"],
            "source_quality": result["source_quality"],
            "keyword_counts": result["keyword_counts"],
            "warnings": result["warnings"],
        },
    )
    db.add(source)
    db.flush()
    for entity in result["entities"]:
        db.add(
            LiteratureEvidenceItem(
                literature_source_id=source.id,
                topic=f"{entity['category']} / {entity['chinese_name']}",
                evidence=entity["evidence"],
                confidence=entity["confidence"],
                source=entity["source"],
            )
        )
    db.commit()
    return PolypropyleneRadicalReviewImportResponse(**result)


KNOWN_REAL_INSTANCE_PATHS = [
    {
        "label": "博士论文 DOCX",
        "path": r"C:\Users\resj6\Desktop\pri\博士学位论文.docx",
        "expected_source_type": "docx",
        "role": "Ziegler–Natta 功能 α-烯烃、链长窗口、电子效应与 TEA 作用的 C 级论文线索。",
    },
    {
        "label": "张志箭 PDF",
        "path": r"C:\Users\resj6\Desktop\pri\张志箭_毕业论文打印终版.pdf",
        "expected_source_type": "pdf",
        "role": "PP/EPC/IPC 长链支化、hex-DCS、交联/支化和乙烯/等规度线索。",
    },
    {
        "label": "PP 自由基综述 PDF",
        "path": r"C:\Users\resj6\Desktop\Radical reactions on polypropylene in the solid state.pdf",
        "expected_source_type": "pdf",
        "role": "过氧化物自由基、PP β-scission、固态反应窗口和交联/降解竞争线索。",
    },
    {
        "label": "SiO/SiC/PP 终稿 DOCX",
        "path": r"C:\Users\resj6\Downloads\SiO_SiC_过氧化物_PP长链支化交联降解全景深度终稿_半小时增强版 (2).docx",
        "expected_source_type": "docx-report",
        "role": "报告驱动四轴机制、Si–C 稳定性、羰基三分法和软件化接口线索。",
    },
]


def _literature_source_payload(row: LiteratureSource | None, known: dict[str, str] | None = None) -> dict[str, Any]:
    provenance = row.provenance if row is not None else {}
    known_path = known["path"] if known else (row.path if row else "")
    keyword_counts = provenance.get("keyword_counts", {})
    warnings = list(provenance.get("warnings", []))
    parse_quality = provenance.get("parse_quality") or provenance.get("source_quality", {}).get("quality") or ("missing" if row is None else "readable")
    return {
        "label": known.get("label") if known else row.title if row else "",
        "title": row.title if row else known.get("label", "") if known else "",
        "path": known_path,
        "exists": Path(known_path).exists() if known_path else False,
        "source_id": row.id if row else None,
        "source_type": row.source_type if row else known.get("expected_source_type", "") if known else "",
        "text_length": provenance.get("text_length", len(row.extracted_text_preview or "") if row else 0),
        "parse_quality": parse_quality,
        "source_quality": provenance.get("source_quality", {}),
        "keyword_counts": keyword_counts,
        "warnings": warnings,
        "evidence_level": provenance.get("evidence_level", "C"),
        "paper_ready": "否；当前为 C 级文献线索，不能替代真实计算或实验结论。",
        "role": known.get("role", "") if known else row.summary if row else "",
    }


def _latest_source_for_path(db: Session, path: str) -> LiteratureSource | None:
    return db.scalar(
        select(LiteratureSource)
        .where(LiteratureSource.path == path)
        .order_by(LiteratureSource.created_at.desc())
    )


def _real_instance_summary(db: Session) -> dict[str, Any]:
    instances = [_literature_source_payload(_latest_source_for_path(db, known["path"]), known) for known in KNOWN_REAL_INSTANCE_PATHS]
    return {
        "instances": instances,
        "quality_policy": {
            "readable": "文本层可读，仍仅作为 C 级文献线索。",
            "encoded-garbled": "PDF 文本层疑似字体编码异常，关键词统计不可作为可靠结论；建议提供 OCR 文本或可复制文本版 PDF。",
            "scanned-needs-ocr": "PDF 未提取到可搜索文本；请导入 OCR 文本。",
            "failed": "解析失败，不能抽取实体或关键词。",
        },
        "axis_mapping": {
            "单体轴": ["Si–O", "Si–C", "Si–Cl", "C=C", "DCS/MCSOMe/DMOS"],
            "催化剂轴": ["Ziegler–Natta", "TEA", "Ti", "MgCl2", "O→Ti 毒化"],
            "自由基轴": ["RO–OR", "RO•", "PP•", "β-scission", "LCB", "crosslinking"],
            "微相轴": ["ethylene", "isotacticity", "crystallinity", "EPC", "IPC"],
        },
        "evidence_boundary": "当前真实文件抽取结果属于 C 级文献线索；除非有真实 Gaussian/Multiwfn/NBO/QTAIM/NCI 计算或真实实验数据支撑，否则不能写成 A/B 级结论。",
        "provenance": "该摘要来自 literature_sources 数据表和固定真实文件路径存在性检查；仅读取记录，不执行 OCR、Gaussian、cubegen、Multiwfn 或用户上传文件。",
    }


def _latest_report_knowledge(db: Session) -> dict:
    source = db.scalar(
        select(LiteratureSource)
        .where(LiteratureSource.source_type == "docx-report")
        .order_by(LiteratureSource.created_at.desc())
    )
    if source is None:
        knowledge = extract_report_driven_knowledge("", REPORT_TITLE)
        return {
            **knowledge,
            "source_id": None,
            "text_length": 0,
            "text_preview": "",
            "provenance": "尚未导入报告 docx；返回内置报告方向 C 级线索，不代表真实抽取结果。",
            "protocol": get_top_scientist_protocol(),
        }
    report_knowledge = dict(source.provenance.get("report_knowledge", {}))
    return {
        **report_knowledge,
        "source_id": source.id,
        "text_length": source.provenance.get("text_length", 0),
        "text_preview": source.extracted_text_preview or "",
        "title": source.title,
        "path": source.path or "",
        "provenance": "来自已导入报告 docx 的只读结构化抽取；证据等级为 C，不能替代真实计算/实验结论。",
        "protocol": get_top_scientist_protocol(),
    }


@router.post("/literature/import-report-docx", response_model=ReportDocxImportResponse)
def import_report_docx(payload: ReportDocxImportRequest, db: Session = Depends(get_db)) -> ReportDocxImportResponse:
    try:
        text = extract_docx_text(payload.path)
    except FileNotFoundError:
        text = ""
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    knowledge = extract_report_driven_knowledge(text, payload.title)
    source = LiteratureSource(
        title=payload.title,
        path=payload.path,
        source_type="docx-report",
        summary="报告知识抽取：SiO/SiC/过氧化物/PP 自由基闭环、长链支化、交联、降解和羰基三分法。",
        extracted_text_preview=text[:2400],
        provenance={
            "policy": "仅读取 docx 文本，不执行宏、脚本、Gaussian、cubegen 或 Multiwfn。",
            "evidence_level": "C",
            "mock_policy": "报告抽取线索不能作为真实计算或实验结论。",
            "keyword_counts": knowledge["keyword_counts"],
            "warnings": knowledge["warnings"],
            "text_length": len(text),
            "report_knowledge": knowledge,
        },
    )
    db.add(source)
    db.flush()
    for entity in knowledge["entities"]:
        db.add(
            ThesisEntity(
                literature_source_id=source.id,
                category=entity["category"],
                name=entity["name"],
                chinese_name=entity["chinese_name"],
                evidence=entity["evidence"],
                confidence=entity["confidence"],
                source=entity["source"],
            )
        )
        db.add(
            LiteratureEvidenceItem(
                literature_source_id=source.id,
                topic=f"{entity['axis']} / {entity['chinese_name']} / {entity['evidence_level']}级证据",
                evidence=f"{entity['evidence']}\n软件化映射：{entity['software_mapping']}",
                confidence=entity["confidence"],
                source=entity["source"],
            )
        )
    for model in knowledge["mechanism_models"]:
        db.add(
            LiteratureEvidenceItem(
                literature_source_id=source.id,
                topic=f"{model['axis']} / {model['name']} / {model['evidence_level']}级证据",
                evidence=f"{model['hypothesis']}\n反证条件：{model['falsification']}",
                confidence=0.7,
                source=model["source"],
            )
        )
    db.commit()
    return ReportDocxImportResponse(
        title=payload.title,
        path=payload.path,
        text_length=len(text),
        text_preview=text[:1800],
        entities=knowledge["entities"],
        mechanism_models=knowledge["mechanism_models"],
        keyword_counts=knowledge["keyword_counts"],
        report_payload=knowledge["report_payload"],
        warnings=knowledge["warnings"],
        provenance=knowledge["provenance"],
    )


@router.get("/literature/report-knowledge")
def get_report_knowledge(db: Session = Depends(get_db)) -> dict:
    return _latest_report_knowledge(db)


@router.post("/literature/import-ocr-text", response_model=OcrTextImportResponse)
def import_ocr_text(payload: OcrTextImportRequest, db: Session = Depends(get_db)) -> OcrTextImportResponse:
    text = payload.ocr_text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="OCR 文本为空，无法导入。")
    source_quality = assess_text_quality(text, "ocr-text")
    report_knowledge = extract_report_driven_knowledge(text, payload.source_title)
    radical_knowledge = analyze_polypropylene_radical_literature(text, payload.source_title)
    warnings = list(report_knowledge["warnings"]) + list(radical_knowledge["warnings"])
    source = LiteratureSource(
        title=payload.source_title,
        path=payload.source_path,
        source_type="ocr-text",
        summary="用户导入 OCR 文本：用于修复 PDF 文本层乱码或扫描件的 C 级文献线索抽取。",
        extracted_text_preview=text[:2400],
        provenance={
            "policy": "用户提供 OCR 文本；服务器不执行 OCR 程序、不执行 PDF、Gaussian、cubegen 或 Multiwfn。",
            "evidence_level": "C",
            "parse_quality": source_quality["quality"],
            "source_quality": source_quality,
            "keyword_counts": {
                "report_keywords": report_knowledge["keyword_counts"],
                "radical_keywords": radical_knowledge["keyword_counts"],
            },
            "warnings": warnings,
            "text_length": len(text),
            "report_knowledge": report_knowledge,
        },
    )
    db.add(source)
    db.flush()
    for entity in report_knowledge["entities"]:
        db.add(
            LiteratureEvidenceItem(
                literature_source_id=source.id,
                topic=f"{entity['axis']} / {entity['chinese_name']} / OCR文本 / C级证据",
                evidence=f"{entity['evidence']}\n软件化映射：{entity['software_mapping']}",
                confidence=entity["confidence"],
                source=entity["source"],
            )
        )
    for hypothesis in radical_knowledge["hypotheses"]:
        db.add(
            LiteratureEvidenceItem(
                literature_source_id=source.id,
                topic=f"自由基轴 / {hypothesis['name']} / OCR文本 / C级证据",
                evidence=f"{hypothesis['supporting_evidence'][0]}\n反证条件：{hypothesis['falsification'][0]}",
                confidence=hypothesis["confidence"],
                source=hypothesis["source"],
            )
        )
    db.commit()
    return OcrTextImportResponse(
        title=payload.source_title,
        source_path=payload.source_path,
        parse_quality=source_quality["quality"],
        source_quality=source_quality,
        text_length=len(text),
        text_preview=text[:1800],
        entities=report_knowledge["entities"],
        mechanism_models=report_knowledge["mechanism_models"],
        hypotheses=radical_knowledge["hypotheses"],
        keyword_counts={
            "report_keywords": report_knowledge["keyword_counts"],
            "radical_keywords": radical_knowledge["keyword_counts"],
        },
        report_payload=report_knowledge["report_payload"],
        warnings=warnings,
        provenance="OCR 文本来自用户输入，证据等级为 C；服务器未执行外部 OCR 或化学计算程序。",
    )


@router.get("/literature/source-quality")
def literature_source_quality(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(LiteratureSource).order_by(LiteratureSource.created_at.desc())).all()
    return {
        "sources": [_literature_source_payload(row) for row in rows],
        "quality_labels": ["readable", "encoded-garbled", "scanned-needs-ocr", "failed"],
        "warning": "PDF 乱码时不得把关键词为 0 解释为文献无相关内容；应导入 OCR 文本或可复制文本版 PDF。",
    }


@router.get("/literature/real-instance-summary")
def literature_real_instance_summary(db: Session = Depends(get_db)) -> dict:
    return _real_instance_summary(db)


@router.get("/catalyst-models")
def list_catalyst_models(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(CatalystModel).order_by(CatalystModel.id)).all()
    return {
        "models": [
            {
                "key": row.key,
                "name": row.name,
                "role": row.role,
                "active_site": row.active_site,
                "thesis_link": row.thesis_link,
                "source": row.source,
            }
            for row in rows
        ],
        "provenance": "催化剂模型为论文抽取 + 示例占位；不代表已优化真实团簇结构。",
    }


@router.get("/molecules", response_model=list[MoleculeRead])
def list_molecules(db: Session = Depends(get_db)) -> list[Molecule]:
    return list(db.scalars(select(Molecule).order_by(Molecule.id)).all())


@router.post("/molecules", response_model=MoleculeRead)
def create_molecule(payload: MoleculeCreate, db: Session = Depends(get_db)) -> Molecule:
    existing = db.scalar(select(Molecule).where(Molecule.key == payload.key))
    if existing:
        raise HTTPException(status_code=409, detail="分子编号已存在。")
    molecule = Molecule(**payload.model_dump(), descriptors=describe_molecule(payload.smiles))
    db.add(molecule)
    db.commit()
    db.refresh(molecule)
    return molecule


@router.get("/molecules/{molecule_id}", response_model=MoleculeRead)
def get_molecule(molecule_id: int, db: Session = Depends(get_db)) -> Molecule:
    molecule = db.get(Molecule, molecule_id)
    if molecule is None:
        raise HTTPException(status_code=404, detail="未找到指定分子。")
    return molecule


@router.get("/molecules/{molecule_id}/graph")
def get_molecule_graph(molecule_id: int, db: Session = Depends(get_db)) -> dict:
    molecule = db.get(Molecule, molecule_id)
    if molecule is None:
        raise HTTPException(status_code=404, detail="未找到指定分子。")
    intelligence = analyze_molecule_intelligence(molecule.smiles)
    graph = intelligence.get("graph", {})
    return {
        "molecule_id": molecule.id,
        "key": molecule.key,
        "smiles": molecule.smiles,
        "nodes": graph.get("nodes", []),
        "edges": graph.get("edges", []),
        "functional_sites": intelligence.get("sites", []),
        "provenance": "分子图由 SMILES 只读识别生成；若 RDKit 不可用则为安全占位图，不能替代真实量子化学几何。",
    }


@router.get("/molecules/{molecule_id}/xyz")
def export_molecule_xyz(molecule_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    molecule = db.get(Molecule, molecule_id)
    if molecule is None:
        raise HTTPException(status_code=404, detail="未找到指定分子。")
    return {
        "file_name": f"{molecule.key}.xyz",
        "content": xyz_from_smiles(molecule.smiles),
        "provenance": "由 RDKit 生成的构象；不是量子化学优化几何。",
    }


@router.post("/molecules/{molecule_id}/conformers")
def create_molecule_conformer(molecule_id: int, db: Session = Depends(get_db)) -> dict:
    molecule = db.get(Molecule, molecule_id)
    if molecule is None:
        raise HTTPException(status_code=404, detail="未找到指定分子。")
    xyz = xyz_from_smiles(molecule.smiles)
    conformer = Conformer(
        molecule_id=molecule.id,
        label=f"{molecule.key}-RDKit-{len(molecule.conformers) + 1}",
        xyz=xyz,
        source="RDKit generated / 示例构象",
    )
    db.add(conformer)
    db.commit()
    db.refresh(conformer)
    return {
        "id": conformer.id,
        "molecule_id": molecule.id,
        "label": conformer.label,
        "xyz": conformer.xyz,
        "source": conformer.source,
        "provenance": "生成的 RDKit 构象仅用于起始结构预览，不是 Gaussian 优化几何。",
    }


def _float_or_none(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _row_value(row: dict[str, str], *keys: str) -> str | None:
    lowered = {key.strip().lower(): value.strip() for key, value in row.items() if key is not None and value is not None}
    for key in keys:
        value = lowered.get(key.lower())
        if value is not None:
            return value
    return None


@router.post("/experiments/import-csv")
def import_experiment_csv(payload: ExperimentCsvImportRequest, db: Session = Depends(get_db)) -> dict:
    reader = csv.DictReader(io.StringIO(payload.csv_text))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="当前 CSV 未检测到表头。")
    dataset = ExperimentalDataset(name=payload.dataset_name, description="用户导入实验-DFT 对照数据", source=payload.source, reliability="用户输入，待核验")
    db.add(dataset)
    db.flush()

    records: list[dict] = []
    for row in reader:
        record = ExperimentRecord(
            dataset_id=dataset.id,
            monomer=_row_value(row, "monomer", "单体") or "未命名单体",
            catalyst_system=_row_value(row, "catalyst", "catalyst_system", "催化剂体系") or "当前文件未提供",
            polymerization_system=_row_value(row, "polymerization", "聚合体系") or "当前文件未提供",
            temperature_c=_float_or_none(_row_value(row, "temperature_c", "聚合温度")),
            al_ti_ratio=_float_or_none(_row_value(row, "al_ti_ratio", "Al/Ti 比")),
            activity=_float_or_none(_row_value(row, "activity", "活性")),
            insertion_ratio=_float_or_none(_row_value(row, "insertion_ratio", "插入率")),
            hexene_content=_float_or_none(_row_value(row, "hexene_content", "1-己烯含量")),
            sequence_length=_float_or_none(_row_value(row, "sequence_length", "序列长度")),
            melting_point_c=_float_or_none(_row_value(row, "melting_point_c", "熔点")),
            crystallinity_percent=_float_or_none(_row_value(row, "crystallinity", "结晶度")),
            transparency_percent=_float_or_none(_row_value(row, "transparency", "透明性")),
            source=payload.source,
        )
        db.add(record)
        records.append(
            {
                "monomer": record.monomer,
                "catalyst_system": record.catalyst_system,
                "polymerization_system": record.polymerization_system,
                "activity": record.activity,
                "insertion_ratio": record.insertion_ratio,
                "source": record.source,
            }
        )
    db.commit()
    return {
        "dataset": payload.dataset_name,
        "records": records,
        "count": len(records),
        "provenance": "CSV 数据按用户输入保存，未自动视为真实结论；请在报告中标注来源。",
    }


@router.get("/experiments")
def list_experiments(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(ExperimentRecord).order_by(ExperimentRecord.created_at.desc())).all()
    return {
        "records": [
            {
                "monomer": row.monomer,
                "catalyst_system": row.catalyst_system,
                "polymerization_system": row.polymerization_system,
                "temperature_c": row.temperature_c,
                "al_ti_ratio": row.al_ti_ratio,
                "activity": row.activity,
                "insertion_ratio": row.insertion_ratio,
                "hexene_content": row.hexene_content,
                "sequence_length": row.sequence_length,
                "melting_point_c": row.melting_point_c,
                "crystallinity_percent": row.crystallinity_percent,
                "transparency_percent": row.transparency_percent,
                "source": row.source,
            }
            for row in rows
        ],
        "provenance": "仅返回用户导入或数据库记录；前端示例趋势另行标注 MOCK。",
    }


@router.post("/experimental/import-{data_type}")
def import_experimental_measurement(data_type: str, payload: dict) -> dict:
    allowed = {"gpc", "mfr", "gel", "rheology", "ftir", "nmr", "dsc", "morphology", "dielectric"}
    if data_type not in allowed:
        raise HTTPException(status_code=404, detail="未找到指定实验数据导入类型。")
    records = payload.get("records")
    if not isinstance(records, list):
        raise HTTPException(status_code=422, detail="实验导入需要 records 数组。")
    return {
        "data_type": data_type,
        "count": len(records),
        "records": records,
        "source": payload.get("source", "用户输入"),
        "provenance": "实验表征数据按用户输入接收；当前接口不推断缺失指标，也不输出确定性材料结论。",
    }


@router.post("/gaussian/generate-input", response_model=GaussianInputResponse)
def gaussian_generate_input(payload: GaussianInputRequest) -> GaussianInputResponse:
    return generate_gaussian_input(payload)


@router.post("/parse/gaussian-log", response_model=ParsedGaussianLog)
async def parse_gaussian_log(payload: GaussianLogTextRequest) -> ParsedGaussianLog:
    return parse_gaussian_log_text(payload.text, payload.file_name)


@router.post("/gaussian/parse-log", response_model=ParsedGaussianLog)
async def gaussian_parse_log_alias(payload: GaussianLogTextRequest) -> ParsedGaussianLog:
    return parse_gaussian_log_text(payload.text, payload.file_name)


@router.post("/gaussian/upload-log", response_model=ParsedGaussianLog)
async def upload_gaussian_log(file: UploadFile = File(...), db: Session = Depends(get_db)) -> ParsedGaussianLog:
    name_error = _upload_name_error(file.filename, {".log", ".out"})
    if name_error:
        raise HTTPException(status_code=400, detail=name_error if name_error != "不允许的文件类型。" else "该接口仅接受 .log 和 .out 文件。")
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    settings = get_settings()
    target = settings.upload_dir / Path(file.filename or "gaussian.log").name
    target.write_text(text, encoding="utf-8")
    parsed = parse_gaussian_log_text(text, file.filename or "gaussian.log")
    output = GaussianOutput(
        file_name=Path(file.filename or "gaussian.log").name,
        path=str(target),
        normal_termination=bool(parsed.normal_termination.value),
        parsed_json=parsed.model_dump(),
        quality=parsed.quality,
    )
    db.add(output)
    db.commit()
    return parsed


@router.get("/gaussian/jobs")
def list_gaussian_jobs(db: Session = Depends(get_db)) -> list[dict]:
    jobs = db.scalars(select(GaussianJob).order_by(GaussianJob.created_at.desc())).all()
    return [
        {
            "id": job.id,
            "project_id": job.project_id,
            "molecule_id": job.molecule_id,
            "job_type": job.job_type,
            "method": job.method,
            "basis": job.basis,
            "dispersion": job.dispersion,
            "charge": job.charge,
            "multiplicity": job.multiplicity,
            "status": job.status,
            "input_file_path": job.input_file_path,
            "output_file_path": job.output_file_path,
            "parsed_json": job.parsed_json,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }
        for job in jobs
    ]


@router.get("/gaussian/jobs/{job_id}")
def get_gaussian_job(job_id: int, db: Session = Depends(get_db)) -> dict:
    job = db.get(GaussianJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="未找到指定 Gaussian 任务。")
    return {
        "id": job.id,
        "project_id": job.project_id,
        "molecule_id": job.molecule_id,
        "job_type": job.job_type,
        "method": job.method,
        "basis": job.basis,
        "dispersion": job.dispersion,
        "charge": job.charge,
        "multiplicity": job.multiplicity,
        "status": job.status,
        "input_file_path": job.input_file_path,
        "output_file_path": job.output_file_path,
        "parsed_json": job.parsed_json,
    }


@router.post("/analysis/energy-components", response_model=BindingEnergyResponse)
def energy_components(payload: EnergyComponentsRequest) -> BindingEnergyResponse:
    delta_hartree, delta_kcal = delta_g_binding(payload.complex_g_hartree, payload.fragment_g_hartree)
    return BindingEnergyResponse(
        delta_g_bind_kcal_mol=delta_kcal,
        delta_g_bind_hartree=delta_hartree,
        classification=classify_binding(delta_kcal),
        formula="ΔGbind = G(络合物) - ΣG(片段)",
    )


@router.post("/analysis/bde", response_model=BdeResponse)
def bde_analysis(payload: BdeRequest) -> BdeResponse:
    try:
        result = bond_dissociation_energy(payload.g_fragments_hartree, payload.g_molecule_hartree)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    bond_type = payload.bond_type.replace("-", "–")
    formula_map = {
        "Si–C": "BDE(Si–C) = G(R•) + G(•Si fragment) − G(R–Si)",
        "Si–O": "BDE(Si–O) = G(R•) + G(•O–Si fragment) − G(R–O–Si)",
        "Si–Cl": "BDE(Si–Cl) = G(R•) + G(•Si–Cl fragment) − G(R–Si–Cl)",
        "RO–OR": "BDE(RO–OR) = G(2RO•) − G(RO–OR)",
    }
    reliability_note = (
        "该结果来自用户输入或上传解析能量；BDE 片段必须核验自旋多重度、频率和 provenance。"
        if not payload.is_mock
        else "示例数据不能作为真实科学结论。"
    )
    return BdeResponse(
        bond_type=bond_type,
        bde_hartree=result["bde_hartree"],
        bde_kcal_mol=result["bde_kcal_mol"],
        bde_ev=result["bde_ev"],
        formula=formula_map.get(bond_type, "BDE = ΣG(fragments) − G(parent molecule)"),
        interpretation=classify_bde(bond_type, result["bde_kcal_mol"]),
        source=payload.source,
        evidence_grade=payload.evidence_grade,
        is_mock=payload.is_mock,
        reliability_note=reliability_note,
        provenance="服务器仅按输入 Gibbs 能量计算 BDE，不执行 Gaussian、cubegen、Multiwfn 或用户上传文件。",
    )


@router.post("/analysis/tea-binding")
def tea_binding(payload: TEABindingRequest) -> dict:
    delta_hartree, delta_kcal = delta_g_binding(
        payload.complex_g_hartree,
        [payload.monomer_g_hartree, payload.tea_g_hartree],
    )
    bsse_delta = None
    if payload.bsse_corrected_complex_hartree is not None:
        bsse_delta = (payload.bsse_corrected_complex_hartree - payload.monomer_g_hartree - payload.tea_g_hartree) * HARTREE_TO_KCAL_MOL
    label = classify_binding(delta_kcal)
    if payload.mode == "Al<-O" and (payload.n_o_to_al_e2_kcal_mol or 0.0) > (payload.n_cl_to_al_e2_kcal_mol or 0.0) + 5.0:
        label = "甲氧基主导捕获"
    return {
        "molecule_key": payload.molecule_key,
        "mode": payload.mode,
        "delta_g_bind_kcal_mol": delta_kcal,
        "delta_g_bind_hartree": delta_hartree,
        "delta_e_bind_bsse_kcal_mol": bsse_delta,
        "r_al_o_angstrom": payload.r_al_o_angstrom,
        "r_al_cl_angstrom": payload.r_al_cl_angstrom,
        "n_o_to_al_e2_kcal_mol": payload.n_o_to_al_e2_kcal_mol,
        "n_cl_to_al_e2_kcal_mol": payload.n_cl_to_al_e2_kcal_mol,
        "label": label,
        "source": "由用户提供能量计算；服务器未执行 Gaussian",
    }


@router.post("/analysis/ti-poisoning", response_model=TiPoisoningResponse)
def ti_poisoning(payload: TiPoisoningRequest) -> TiPoisoningResponse:
    delta, label, color = delta_g_poison(payload.o_ti_complex_g_hartree, payload.pi_complex_g_hartree)
    return TiPoisoningResponse(
        delta_g_poison_kcal_mol=delta,
        label=label,
        color=color,  # type: ignore[arg-type]
        formula="ΔGpoison = G(O→Ti 毒化络合物) - G(C=C π-络合物)",
    )


@router.post("/analysis/insertion-profile", response_model=InsertionProfileResponse)
def insertion_profile_endpoint(payload: InsertionProfileRequest) -> InsertionProfileResponse:
    try:
        profile = insertion_profile(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return InsertionProfileResponse(**profile.__dict__)


@router.post("/analysis/rate-comparison")
def rate_comparison_endpoint(payload: RateComparisonRequest) -> dict:
    try:
        rates = rate_comparison(payload.barriers_kcal_mol, payload.reference_key, payload.temperature_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "temperature_k": payload.temperature_k,
        "reference_key": payload.reference_key,
        "rates": rates,
        "formula": "krel = exp[-ΔΔG‡ / RT]",
    }


@router.post("/analysis/bond-descriptors")
def bond_descriptors(payload: BondDescriptorRequest) -> dict:
    d = payload.descriptors
    interpretations: list[str] = []
    if all(d.get(key) is not None for key in ["r_si_o_delta", "nu_si_o_delta", "wbi_si_o_delta", "rho_bcp_delta"]):
        if d["r_si_o_delta"] > 0 and d["nu_si_o_delta"] < 0 and d["wbi_si_o_delta"] < 0 and d["rho_bcp_delta"] < 0:
            interpretations.append("Si–O 键被 Lewis 酸配位削弱。")
    if (d.get("q_o") is not None and d["q_o"] < -0.6) or (d.get("espmin_o") is not None and d["espmin_o"] < -30):
        if (d.get("n_o_to_al_e2") or 0) > 8:
            interpretations.append("O 原子具有较强 Al 捕获潜力。")
    if (d.get("n_o_to_ti_e2") or 0) > 8 and (d.get("delta_g_poison") or 99) < 0:
        interpretations.append("Ti 活性中心存在 O→Ti 毒化风险。")
    return {
        "molecule_key": payload.molecule_key,
        "context": payload.context,
        "descriptors": payload.descriptors,
        "interpretations": interpretations or ["当前输入指标未触发明确机制判据。"],
        "source": payload.source,
    }


@router.post("/analysis/sio-bond")
def sio_bond_analysis(payload: BondDescriptorRequest) -> dict:
    result = bond_descriptors(payload)
    result["analysis_scope"] = "Si–O 键本征属性与 Lewis 酸配位变化"
    result["reliability_note"] = "Si–O 描述符只解释已提供数据；缺失 QTAIM/NBO 指标不会被补全。"
    return result


@router.post("/analysis/sic-bond")
def sic_bond_analysis(payload: SiCStabilityRequest) -> dict:
    return sic_stability_endpoint(payload)


@router.post("/analysis/hydrolysis-condensation")
def hydrolysis_condensation(payload: dict) -> dict:
    hydrolysis = payload.get("delta_g_hydrolysis_kcal_mol")
    condensation = payload.get("delta_g_condensation_kcal_mol")
    interpretations: list[str] = []
    if hydrolysis is None or condensation is None:
        interpretations.append("当前数据不足，无法给出真实水解缩合热力学排序。")
    elif float(condensation) <= 5.0:
        interpretations.append("当前输入显示 Si–O–Si 缩合在热力学上值得优先验证。")
    else:
        interpretations.append("当前缩合自由能偏高，需检查显式水、离去物和工艺条件。")
    return {
        "delta_g_hydrolysis_kcal_mol": hydrolysis,
        "delta_g_condensation_kcal_mol": condensation,
        "explicit_water_count": payload.get("explicit_water_count"),
        "leaving_group": payload.get("leaving_group", "当前文件未提供"),
        "interpretations": interpretations,
        "provenance": "仅使用用户输入或上传解析数据；服务器未执行量子化学计算。",
    }


@router.post("/analysis/radical-beta-scission")
def radical_beta_scission(payload: RadicalCompetitionRequest) -> dict:
    result = radical_branching_vs_scission(payload.model_dump())
    result["focus"] = "PP• β-scission 与支化/氧化竞争"
    return result


@router.post("/analysis/radical-kinetics")
def radical_kinetics_analysis(payload: RadicalKineticsRequest) -> dict:
    result = radical_kinetics_engine.simulate_rk4(payload.initial, payload.rate_constants, payload.t_end, payload.steps)
    result["formula"] = "R_branch = krec[PP•]^2 + kg[PP•][M] + kc[PP•][coagent]; S_LCB = R_branch / (R_branch + R_scission + R_oxidation)"
    result["reliability_note"] = "该动力学模型为可证伪计算框架；速率常数需来自真实计算、实验拟合或明确文献来源。"
    result["provenance"] = "服务器仅求解用户输入的 ODE 参数，不执行外部化学软件。"
    return result


@router.post("/analysis/peroxide-selection")
def peroxide_selection(payload: PeroxideProfileRequest) -> dict:
    result = peroxide_profile_endpoint(payload)
    result["selection_note"] = "过氧化物选择必须同时核验半衰期、温度、氧含量、coagent 和材料微结构。"
    return result


@router.post("/analysis/decision-engine", response_model=DecisionEngineResponse)
def decision_engine(payload: DecisionEngineRequest) -> DecisionEngineResponse:
    candidates: list[DecisionEngineCandidate] = []
    for item in payload.candidates:
        scores = decision_scores(item.model_dump())
        candidates.append(DecisionEngineCandidate(molecule_key=item.molecule_key, source=item.source, **scores))
    return DecisionEngineResponse(
        candidates=candidates,
        conclusion_template=(
            "在当前数据集中，MCSOMe 的 ΔGpoison 为正，说明 O→Ti 非生产性配位相对于 C=C π-络合物不占优势；"
            "同时其插入势垒接近 DCS，并保留 Si–O 后反应位点。因此，MCSOMe 可被视为兼具聚合兼容性和"
            "后反应功能化潜力的平衡候选结构。"
        ),
        reliability_note="该结论为模板。只有在上传 Gaussian 输出或经过验证的用户输入支持后，才能作为真实科学结论。",
    )


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_den = sum((x - x_mean) ** 2 for x in xs) ** 0.5
    y_den = sum((y - y_mean) ** 2 for y in ys) ** 0.5
    if x_den == 0 or y_den == 0:
        return None
    return numerator / (x_den * y_den)


@router.post("/analysis/dft-experiment-correlation")
def dft_experiment_correlation(payload: DftExperimentCorrelationRequest) -> dict:
    rows = payload.records
    barriers: list[float] = []
    activities: list[float] = []
    insertion_barriers: list[float] = []
    insertions: list[float] = []
    for row in rows:
        barrier = row.get("delta_g_barrier_kcal_mol") or row.get("deltaGBarrier") or row.get("barrier")
        activity = row.get("activity")
        insertion = row.get("insertion_ratio") or row.get("insertionRatio") or row.get("insertion")
        if barrier is not None and activity is not None:
            barriers.append(float(barrier))
            activities.append(float(activity))
        if barrier is not None and insertion is not None:
            insertion_barriers.append(float(barrier))
            insertions.append(float(insertion))

    activity_corr = _pearson(barriers, activities)
    insertion_corr = _pearson(insertion_barriers, insertions) if insertions else None
    if not rows:
        explanation = "当前未提供实验-DFT 对照数据，无法计算真实相关性。"
    elif activity_corr is not None and activity_corr < -0.5:
        explanation = "当前数据呈现 ΔG‡ 升高时活性降低的趋势，支持插入势垒控制模型；仍需检查样本量和数据来源。"
    else:
        explanation = "当前数据不足以证明单一 ΔG‡ 可以解释实验趋势，需要同时纳入位阻、电子导向和 TEA 预组织描述符。"
    return {
        "n_records": len(rows),
        "activity_barrier_pearson": activity_corr,
        "insertion_barrier_pearson": insertion_corr,
        "explanation": explanation,
        "reliability_note": "相关性分析只使用用户传入数值，不生成或补全缺失实验数据。",
    }


@router.post("/analysis/mechanism-hypotheses")
def mechanism_hypotheses(payload: MechanismHypothesisRequest, db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(MechanismHypothesis).order_by(MechanismHypothesis.id)).all()
    hypotheses = [
        {
            "key": row.key,
            "name": row.name,
            "summary": row.summary,
            "supporting_evidence": row.supporting_evidence,
            "falsification": row.falsification,
            "required_data": row.required_data,
            "current_status": row.current_status,
            "confidence": row.confidence,
            "source": row.source,
        }
        for row in rows
    ] or default_mechanism_hypotheses()

    evidence = payload.evidence
    if evidence.get("delta_g_poison_kcal_mol") is not None and float(evidence["delta_g_poison_kcal_mol"]) < 0:
        for item in hypotheses:
            if item["key"] == "o-ti-poisoning":
                item["confidence"] = min(0.95, float(item["confidence"]) + 0.2)
                item["current_status"] = "输入 ΔGpoison < 0，O→Ti 非生产性配位在当前证据下更值得优先检验。"
    return {
        "hypotheses": hypotheses,
        "overall_judgement": "当前数据更支持电子效应导向、TEA 预组织和链长窗口效应的组合模型；是否存在 O→Ti 毒化取决于真实 ΔGpoison 与 NBO 数据。",
        "reliability_note": "机制假说为可证伪模型，不是最终结论；必须由真实实验或 Gaussian 输出支撑。",
    }


@router.get("/analysis/mock-decision-matrix")
def mock_decision_matrix() -> dict:
    return {
        "rows": MOCK_DESCRIPTOR_MATRIX,
        "provenance": "示例数据 / MOCK：仅用于界面演示，不能作为真实计算结果引用。",
    }


@router.post("/reports/generate")
def reports_generate(payload: ReportRequest, db: Session = Depends(get_db)) -> dict:
    report_payload = dict(payload.payload)
    report_knowledge = _latest_report_knowledge(db)
    real_instance_summary = _real_instance_summary(db)
    if report_knowledge.get("source_id") is not None:
        for key, value in report_knowledge.get("report_payload", {}).items():
            report_payload.setdefault(key, value)
    report_payload.setdefault("real_instance_test", real_instance_summary)
    content = generate_report(payload.project_title, payload.format, report_payload)
    report = Report(
        project_id=None,
        title=payload.project_title,
        format=payload.format,
        content=content,
        provenance={
            "include_mock_examples": payload.include_mock_examples,
            "policy": "示例数据始终标注，并与上传解析数据、用户输入数据分开记录。",
            "report_knowledge_source_id": report_knowledge.get("source_id"),
            "report_knowledge_policy": "报告 docx 抽取线索为 C 级证据，不能替代真实计算/实验结论。",
            "real_instance_policy": real_instance_summary["evidence_boundary"],
        },
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {
        "id": report.id,
        "title": payload.project_title,
        "format": payload.format,
        "content": content,
        "provenance": report.provenance,
    }


@router.get("/reports/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)) -> dict:
    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="未找到指定报告。")
    return {
        "id": report.id,
        "title": report.title,
        "format": report.format,
        "content": report.content,
        "provenance": report.provenance,
    }


@router.get("/mcp/tools")
def get_mcp_tools() -> dict:
    return list_mcp_tools()


@router.get("/mcp/resources")
def get_mcp_resources() -> dict:
    return list_mcp_resources()


@router.post("/mcp/generate-prompt")
def mcp_generate_prompt(payload: McpPromptRequest) -> dict:
    return generate_research_prompt(payload.topic, payload.include_safety)


@router.get("/research/top-scientist-protocol")
def research_top_scientist_protocol() -> dict:
    return get_top_scientist_protocol()


@router.post("/research/top-scientist-prompt")
def research_top_scientist_prompt(payload: McpPromptRequest) -> dict:
    return generate_top_scientist_protocol_prompt(payload.topic, payload.include_safety)


@router.post("/mcp/run-tool")
def mcp_run_tool(payload: McpToolRunRequest, db: Session = Depends(get_db)) -> dict:
    arguments = payload.arguments
    tool_name = payload.tool_name.replace("-", "_")
    if tool_name == "generate_gaussian_input":
        result = gaussian_generate_input(GaussianInputRequest(**arguments)).model_dump()
    elif tool_name == "parse_gaussian_log":
        result = parse_gaussian_log_text(str(arguments.get("text", "")), str(arguments.get("file_name", "mcp.log"))).model_dump()
    elif tool_name == "parse_cube":
        result = parse_cube_metadata(str(arguments.get("text", "")), str(arguments.get("file_name", "mcp.cube")))
    elif tool_name == "calculate_delta_g_bind":
        fragments = arguments.get("fragment_g_hartrees", arguments.get("fragment_g_hartree", []))
        delta_h, delta_kcal = delta_g_binding(float(arguments["complex_g_hartree"]), [float(value) for value in fragments])
        result = {"delta_g_bind_hartree": delta_h, "delta_g_bind_kcal_mol": delta_kcal, "formula": "ΔGbind = G(complex) − ΣG(fragments)"}
    elif tool_name == "calculate_delta_g_poison":
        delta, label, color = delta_g_poison(float(arguments["o_ti_complex_g_hartree"]), float(arguments["pi_complex_g_hartree"]))
        result = {"delta_g_poison_kcal_mol": delta, "label": label, "color": color, "formula": "ΔGpoison = G(O→Ti) − G(C=C π-complex)"}
    elif tool_name == "calculate_bde_sic":
        result = ultra_calculate_bde_sic(float(arguments["g_fragments_hartree"]), float(arguments["g_molecule_hartree"]))
    elif tool_name == "validate_upload":
        file_name = str(arguments.get("file_name", ""))
        reason = _upload_name_error(file_name)
        result = {"file_name": file_name, "allowed": reason is None, "reason": reason}
    elif tool_name == "peroxide_profile":
        result = peroxide_profile_endpoint(PeroxideProfileRequest(**arguments))
    elif tool_name in {"generate_research_prompt", "generate_chinese_report_prompt"}:
        result = generate_research_prompt(str(arguments.get("topic", "")), bool(arguments.get("include_safety", True)))
    elif tool_name == "generate_top_scientist_prompt":
        result = generate_top_scientist_protocol_prompt(str(arguments.get("topic", "")), bool(arguments.get("include_safety", True)))
    else:
        raise HTTPException(status_code=400, detail="该 MCP 工具未在安全白名单中。")
    task = McpTask(
        tool_name=payload.tool_name,
        arguments=arguments,
        result=result,
        status="completed",
        provenance={"policy": "仅运行内置安全工作流；不执行 shell 或外部化学软件。"},
    )
    db.add(task)
    db.commit()
    return {
        "tool_name": payload.tool_name,
        "result": result,
        "provenance": task.provenance,
    }


@router.post("/cube/upload", response_model=CubeUploadResponse)
async def upload_cube(file: UploadFile = File(...), db: Session = Depends(get_db)) -> CubeUploadResponse:
    name_error = _upload_name_error(file.filename, {".cube", ".cub"})
    if name_error:
        raise HTTPException(status_code=400, detail=name_error if name_error != "不允许的文件类型。" else "当前文件不是有效 cube 文件。")
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    try:
        parsed = parse_cube_metadata(text, file.filename or "density.cube")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    settings = get_settings()
    target = settings.upload_dir / Path(file.filename or "density.cube").name
    target.write_text(text, encoding="utf-8")
    row = CubeFile(
        file_name=parsed["file_name"],
        cube_type=parsed["cube_type"],
        path=str(target),
        atom_count=parsed["atom_count"],
        grid=parsed["grid"],
        metadata_json=parsed["metadata"],
        source="uploaded",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return CubeUploadResponse(
        id=row.id,
        file_name=row.file_name,
        cube_type=row.cube_type,
        atom_count=row.atom_count,
        grid=row.grid,
        metadata=row.metadata_json,
        warning="cube 已登记为真实上传文件，但页面只有在前端渲染器读取后才显示真实等值面。",
    )


@router.get("/cube/{cube_id}/metadata", response_model=CubeUploadResponse)
def get_cube_metadata(cube_id: int, db: Session = Depends(get_db)) -> CubeUploadResponse:
    row = db.get(CubeFile, cube_id)
    if row is None:
        raise HTTPException(status_code=404, detail="未找到指定 cube 文件。")
    return CubeUploadResponse(
        id=row.id,
        file_name=row.file_name,
        cube_type=row.cube_type,
        atom_count=row.atom_count,
        grid=row.grid,
        metadata=row.metadata_json,
    )


@router.post("/cubes/upload", response_model=CubeUploadResponse)
async def upload_cube_alias(file: UploadFile = File(...), db: Session = Depends(get_db)) -> CubeUploadResponse:
    return await upload_cube(file, db)


@router.get("/cubes/{cube_id}/metadata", response_model=CubeUploadResponse)
def get_cube_metadata_alias(cube_id: int, db: Session = Depends(get_db)) -> CubeUploadResponse:
    return get_cube_metadata(cube_id, db)


@router.get("/cubes/{cube_id}/isosurface")
def get_cube_isosurface_metadata(cube_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(CubeFile, cube_id)
    if row is None:
        raise HTTPException(status_code=404, detail="未找到指定 cube 文件。")
    preview = cube_volume_preview(_read_uploaded_cube(row), row.file_name)
    preview["cube_id"] = row.id
    preview["isosurface_metadata"] = row.metadata_json.get("isosurface_metadata", {})
    return preview


@router.get("/cubes/{cube_id}/slice")
def get_cube_slice_metadata(cube_id: int, axis: str = "z", plane_index: int | None = None, db: Session = Depends(get_db)) -> dict:
    row = db.get(CubeFile, cube_id)
    if row is None:
        raise HTTPException(status_code=404, detail="未找到指定 cube 文件。")
    try:
        preview = cube_slice_preview(_read_uploaded_cube(row), row.file_name, axis, plane_index)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    preview["cube_id"] = row.id
    return preview


@router.post("/cubes/difference-density")
def post_cube_difference_density(payload: dict, db: Session = Depends(get_db)) -> dict:
    cube_a_id = payload.get("cube_a_id")
    cube_b_id = payload.get("cube_b_id")
    if not isinstance(cube_a_id, int) or not isinstance(cube_b_id, int):
        raise HTTPException(status_code=422, detail="差分电子密度需要 cube_a_id 和 cube_b_id。")
    row_a = db.get(CubeFile, cube_a_id)
    row_b = db.get(CubeFile, cube_b_id)
    if row_a is None or row_b is None:
        raise HTTPException(status_code=404, detail="未找到用于差分的 cube 文件。")
    try:
        result = cube_difference_preview(_read_uploaded_cube(row_a), row_a.file_name, _read_uploaded_cube(row_b), row_b.file_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result["cube_a_id"] = cube_a_id
    result["cube_b_id"] = cube_b_id
    return result


def _read_uploaded_cube(row: CubeFile) -> str:
    if not row.path:
        raise HTTPException(status_code=404, detail="当前 cube 文件未保留可读取路径。")
    settings = get_settings()
    target = Path(row.path).resolve()
    upload_root = settings.upload_dir.resolve()
    if upload_root not in target.parents and target != upload_root:
        raise HTTPException(status_code=400, detail="检测到非法 cube 文件路径。")
    if not target.exists():
        raise HTTPException(status_code=404, detail="当前 cube 文件已不存在。")
    return target.read_text(encoding="utf-8", errors="replace")


@router.post("/files/validate-upload")
def validate_upload_name(file_name: str) -> dict:
    reason = _upload_name_error(file_name)
    return {
        "file_name": file_name,
        "allowed": reason is None,
        "reason": reason,
        "allowed_extensions": sorted(ALLOWED_UPLOAD_EXTENSIONS),
        "security_note": "文件仅按文本或数据解析，服务器不会执行上传内容。",
    }
