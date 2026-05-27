from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import DEFAULT_TEMPERATURE_K


DataSource = Literal["uploaded", "user-input", "MOCK / EXAMPLE", "calculated", "estimated", "示例数据", "真实数据", "用户输入"]


class UnitValue(BaseModel):
    value: Any
    unit: str | None = None
    source: str = "uploaded"


class MoleculeCreate(BaseModel):
    key: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=200)
    smiles: str = Field(min_length=1, max_length=500)
    role: str = ""
    substituents: str | None = None
    source: str = "user-input"


class MoleculeRead(MoleculeCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    descriptors: dict[str, Any] | None = None


class GaussianInputRequest(BaseModel):
    name: str = "DCS"
    job_type: str = "isolated monomer opt/freq/NBO"
    method: str = "B3LYP"
    basis: str = "Def2SVP"
    dispersion: str = "GD3BJ"
    charge: int = 0
    multiplicity: int = 1
    memory: str = "48GB"
    nproc: int = 16
    checkpoint_name: str | None = None
    title: str | None = None
    coordinates: str = ""
    fragment_coordinates: str | None = None
    ts_chk: str | None = None
    job_notes: str | None = None

    @field_validator("nproc")
    @classmethod
    def nproc_positive(cls, value: int) -> int:
        if value < 1:
            raise ValueError("nproc must be positive")
        return value


class GaussianInputResponse(BaseModel):
    file_name: str
    content: str
    job_type: str
    warnings: list[str] = []
    provenance: str = "已生成输入文件；服务器未执行 Gaussian"


class ParsedGaussianLog(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    file: str
    normal_termination: UnitValue
    scf_hartree: UnitValue
    zpe_correction_hartree: UnitValue
    thermal_correction_energy_hartree: UnitValue
    thermal_correction_enthalpy_hartree: UnitValue
    thermal_correction_gibbs_hartree: UnitValue
    sum_electronic_zpe_hartree: UnitValue
    sum_electronic_thermal_enthalpy_hartree: UnitValue
    sum_electronic_thermal_free_hartree: UnitValue
    gibbs_hartree: UnitValue
    frequencies_cm_1: UnitValue = Field(alias="frequencies_cm-1")
    n_imag: UnitValue
    lowest_freq_cm_1: UnitValue = Field(alias="lowest_freq_cm-1")
    homo_hartree: UnitValue
    lumo_hartree: UnitValue
    gap_ev: UnitValue
    dipole_debye: UnitValue
    mulliken_charges: UnitValue
    npa_charges: UnitValue
    wiberg_bond_indices: UnitValue
    spin_multiplicity: UnitValue
    mulliken_spin_densities: UnitValue
    nbo_interactions: UnitValue
    counterpoise_corrected_energy_hartree: UnitValue
    quality: Literal["complete", "partial", "failed"]
    missing_fields: list[str]
    chinese_warnings: list[str] = []
    units: dict[str, str]


class GaussianLogTextRequest(BaseModel):
    file_name: str = "uploaded.log"
    text: str


class EnergyComponentsRequest(BaseModel):
    complex_g_hartree: float
    fragment_g_hartree: list[float] = Field(min_length=1)


class BindingEnergyResponse(BaseModel):
    delta_g_bind_kcal_mol: float
    delta_g_bind_hartree: float
    classification: str
    formula: str


class BdeRequest(BaseModel):
    bond_type: Literal["Si-C", "Si–C", "Si-O", "Si–O", "Si-Cl", "Si–Cl", "RO-OR", "RO–OR"] = "Si-C"
    g_fragments_hartree: float
    g_molecule_hartree: float
    source: str = "用户输入"
    evidence_grade: Literal["A", "B", "C", "D"] = "C"
    is_mock: bool = False


class BdeResponse(BaseModel):
    bond_type: str
    bde_hartree: float
    bde_kcal_mol: float
    bde_ev: float
    formula: str
    interpretation: str
    source: str
    evidence_grade: str
    is_mock: bool
    reliability_note: str
    provenance: str


class ScientificEnergyWorkbenchRequest(BaseModel):
    complex_g_hartree: float | None = None
    fragment_g_hartree: list[float] = []
    o_ti_complex_g_hartree: float | None = None
    pi_complex_g_hartree: float | None = None
    free_site_monomer_g_hartree: float | None = None
    ts_g_hartree: float | None = None
    product_g_hartree: float | None = None
    reference_barrier_kcal_mol: float | None = None
    temperature_k: float = DEFAULT_TEMPERATURE_K
    source: str = "用户输入"
    evidence_grade: Literal["A", "B", "C", "D"] = "C"
    is_mock: bool = False


class TiPoisoningRequest(BaseModel):
    o_ti_complex_g_hartree: float
    pi_complex_g_hartree: float


class TiPoisoningResponse(BaseModel):
    delta_g_poison_kcal_mol: float
    label: str
    color: Literal["green", "yellow", "red"]
    formula: str


class InsertionProfileRequest(BaseModel):
    free_site_monomer_g_hartree: float
    pi_complex_g_hartree: float
    ts_g_hartree: float
    product_g_hartree: float | None = None
    reference_barrier_kcal_mol: float | None = None
    temperature_k: float = DEFAULT_TEMPERATURE_K


class InsertionProfileResponse(BaseModel):
    delta_g_pi_kcal_mol: float
    delta_g_barrier_kcal_mol: float
    delta_g_complex_barrier_kcal_mol: float
    delta_g_product_kcal_mol: float | None
    delta_delta_g_barrier_kcal_mol: float | None
    krel: float | None
    temperature_k: float


class RateComparisonRequest(BaseModel):
    barriers_kcal_mol: dict[str, float]
    reference_key: str
    temperature_k: float = DEFAULT_TEMPERATURE_K


class DecisionEngineInput(BaseModel):
    molecule_key: str
    e_intrinsic: float | None = None
    e_al_capture: float | None = None
    e_ti_poison: float | None = None
    e_insert: float | None = None
    e_post: float | None = None
    source: str = "user-input"


class DecisionEngineRequest(BaseModel):
    candidates: list[DecisionEngineInput]


class DecisionEngineCandidate(BaseModel):
    molecule_key: str
    insertion_compatibility_score: float | None
    poisoning_risk_score: float | None
    tea_capture_score: float | None
    steric_penalty_score: float | None
    post_functionalization_score: float | None
    overall_candidate_score: float | None
    label: str
    source: str


class DecisionEngineResponse(BaseModel):
    candidates: list[DecisionEngineCandidate]
    conclusion_template: str
    reliability_note: str


class BondDescriptorRequest(BaseModel):
    molecule_key: str
    descriptors: dict[str, float | None]
    context: str = "before TEA coordination"
    source: str = "user-input"


class TEABindingRequest(BaseModel):
    molecule_key: str
    mode: Literal["Al...Cl", "Al<-O", "Al...C=C", "mixed"]
    monomer_g_hartree: float
    tea_g_hartree: float
    complex_g_hartree: float
    bsse_corrected_complex_hartree: float | None = None
    r_al_o_angstrom: float | None = None
    r_al_cl_angstrom: float | None = None
    n_o_to_al_e2_kcal_mol: float | None = None
    n_cl_to_al_e2_kcal_mol: float | None = None


class ReportRequest(BaseModel):
    project_title: str = "SiO Catalyst Quantum Studio"
    format: Literal["markdown", "json", "csv", "html", "pdf-placeholder"] = "markdown"
    include_mock_examples: bool = True
    payload: dict[str, Any] = {}


class ThesisImportRequest(BaseModel):
    path: str = r"C:\Users\resj6\Desktop\pri\博士学位论文.docx"
    title: str = "基于 Ziegler-Natta 催化剂的乙烯、丙烯与功能 α-烯烃单体配位共聚合反应的空间位阻与电子效应研究"


class ThesisEntityRead(BaseModel):
    category: str
    name: str
    chinese_name: str
    evidence: str
    confidence: float
    source: str


class ThesisImportResponse(BaseModel):
    title: str
    path: str
    text_length: int
    entities: list[ThesisEntityRead]
    catalyst_models: list[dict[str, Any]]
    monomer_families: list[dict[str, Any]]
    warnings: list[str]
    provenance: str


class ReportDocxImportRequest(BaseModel):
    path: str = r"C:\Users\resj6\Downloads\SiO_SiC_过氧化物_PP长链支化交联降解全景深度终稿_半小时增强版 (2).docx"
    title: str = "SiO/SiC/过氧化物/PP 长链支化交联降解全景深度报告"


class ReportKnowledgeEntity(BaseModel):
    category: str
    name: str
    chinese_name: str
    axis: str
    evidence: str
    confidence: float
    evidence_level: str = "C"
    data_source: str = "报告线索"
    reliability: str = "中"
    paper_ready: str = "需要补充验证"
    software_mapping: str
    source: str


class ReportDocxImportResponse(BaseModel):
    title: str
    path: str
    text_length: int
    text_preview: str
    entities: list[ReportKnowledgeEntity]
    mechanism_models: list[dict[str, Any]]
    keyword_counts: dict[str, int]
    report_payload: dict[str, Any]
    warnings: list[str]
    provenance: str


class PolypropyleneRadicalReviewImportRequest(BaseModel):
    path: str
    title: str | None = None


class PolypropyleneRadicalReviewImportResponse(BaseModel):
    title: str
    path: str
    source_type: str
    parse_quality: Literal["readable", "encoded-garbled", "scanned-needs-ocr", "failed"] = "readable"
    source_quality: dict[str, Any] = Field(default_factory=dict)
    text_length: int
    text_preview: str
    entities: list[dict[str, Any]]
    hypotheses: list[dict[str, Any]]
    keyword_counts: dict[str, int]
    warnings: list[str]
    provenance: str


class OcrTextImportRequest(BaseModel):
    source_title: str = Field(min_length=1, max_length=300)
    source_path: str = ""
    ocr_text: str = Field(min_length=1)


class OcrTextImportResponse(BaseModel):
    title: str
    source_path: str
    source_type: str = "ocr-text"
    parse_quality: Literal["readable", "encoded-garbled", "scanned-needs-ocr", "failed"] = "readable"
    source_quality: dict[str, Any] = Field(default_factory=dict)
    text_length: int
    text_preview: str
    entities: list[ReportKnowledgeEntity]
    mechanism_models: list[dict[str, Any]]
    hypotheses: list[dict[str, Any]]
    keyword_counts: dict[str, Any]
    report_payload: dict[str, Any]
    warnings: list[str]
    provenance: str


class ExperimentCsvImportRequest(BaseModel):
    csv_text: str
    dataset_name: str = "用户导入实验数据"
    source: str = "用户输入"


class ExperimentRead(BaseModel):
    monomer: str
    catalyst_system: str
    polymerization_system: str
    temperature_c: float | None = None
    al_ti_ratio: float | None = None
    activity: float | None = None
    insertion_ratio: float | None = None
    hexene_content: float | None = None
    sequence_length: float | None = None
    melting_point_c: float | None = None
    crystallinity_percent: float | None = None
    transparency_percent: float | None = None
    source: str = "user-input"


class DftExperimentCorrelationRequest(BaseModel):
    records: list[dict[str, Any]] = []


class MechanismHypothesisRequest(BaseModel):
    evidence: dict[str, Any] = {}
    include_mock_examples: bool = True


class CubeUploadResponse(BaseModel):
    id: int | None = None
    file_name: str
    cube_type: str
    atom_count: int | None
    grid: dict[str, Any] | None
    metadata: dict[str, Any]
    warning: str | None = None
    provenance: str = "服务器仅读取 cube 文本元数据，不执行文件。"


class ReadOnlyTextParseRequest(BaseModel):
    file_name: str = "uploaded.txt"
    text: str


class McpToolRunRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = {}


class McpPromptRequest(BaseModel):
    topic: str = "Si–O / Si–C / 过氧化物自由基机理"
    include_safety: bool = True


class FourAxisDecisionRequest(BaseModel):
    monomer_key: str = "MCSOMe"
    data: dict[str, Any] = {}


class RadicalKineticsRequest(BaseModel):
    initial: dict[str, float] = {
        "ROOR": 1.0,
        "RO": 0.0,
        "PPH": 1.0,
        "PP_radical": 0.0,
        "monomer": 0.4,
        "coagent": 0.1,
    }
    rate_constants: dict[str, float] = {}
    t_end: float = 10.0
    steps: int = 80


class PeroxideProfileRequest(BaseModel):
    name: str = "dicumyl peroxide"
    peroxide_class: str = "二烷基过氧化物"
    has_carbonyl: bool = False
    roor_bde_kcal_mol: float | None = None
    g_radicals_hartree: float | None = None
    g_peroxide_hartree: float | None = None
    half_life_min: float | None = None
    half_life_temperature_c: float | None = None
    temperature_c: float = 180.0
    residence_time_min: float = 5.0
    oxygen_level_percent: float = 0.0
    source: str = "用户输入"


class RadicalCompetitionRequest(BaseModel):
    peroxide_loading_phr: float = 0.2
    coagent_phr: float = 0.0
    ethylene_mol_percent: float = 0.0
    isotacticity_percent: float = 92.0
    crystallinity_percent: float = 45.0
    oxygen_level_percent: float = 0.0
    temperature_c: float = 180.0
    residence_time_min: float = 5.0
    has_carbonyl: bool = False
    source: str = "用户输入"


class SiCStabilityRequest(BaseModel):
    bde_sic_kcal_mol: float | None = None
    bde_sio_kcal_mol: float | None = None
    bde_sicl_kcal_mol: float | None = None
    radical_attack_barrier_kcal_mol: float | None = None
    g_sic_fragments_hartree: float | None = None
    g_sic_molecule_hartree: float | None = None
    source: str = "用户输入"


class ResidenceTimeWindowRequest(BaseModel):
    name: str = "未命名过氧化物"
    peroxide_class: str = "未指定"
    has_carbonyl: bool = False
    roor_bde_kcal_mol: float | None = None
    half_life_min: float | None = None
    half_life_temperature_c: float | None = None
    temperature_c: float = 180.0
    residence_time_min: float = 5.0
    oxygen_level_percent: float = 0.0
    target_conversion_low_percent: float = 20.0
    target_conversion_high_percent: float = 80.0
    source: str = "用户输入"


class UnifiedLCBFrameworkRequest(BaseModel):
    chi_insert: float | None = None
    chi_hydrolysis: float | None = None
    chi_condensation: float | None = None
    chi_radical_recombination: float | None = None
    chi_beta_scission: float | None = None
    chi_oxidation: float | None = None
    chi_ti_poison: float | None = None
    chi_over_gel: float | None = None
    source: str = "用户输入"


class BoltzmannWeightsRequest(BaseModel):
    energies_kcal_mol: list[float]
    temperature_k: float = DEFAULT_TEMPERATURE_K


class WignerRateRequest(BaseModel):
    delta_delta_g_kcal_mol: float
    temperature_k: float = DEFAULT_TEMPERATURE_K
    nu_imag_1_cm_1: float = 0.0
    nu_imag_2_cm_1: float = 0.0


class AdvancedGaussianTaskRequest(BaseModel):
    task_id: str = "monomer_opt"
    molecule_name: str = "MCSOMe"
    coordinates: list[str] = []
    method: str | None = None
    basis: str | None = None
    charge: int | None = None
    multiplicity: int | None = None
    mem: str | None = None
    nproc: int | None = None


class MoleculeIntelligenceRequest(BaseModel):
    smiles: str = "C=CCCCC[Si](C)(OC)Cl"


class ReactionStateInput(BaseModel):
    name: str
    energy_hartree: float
    source: str = "用户输入"


class ReactionProfileAnalysisRequest(BaseModel):
    states: list[ReactionStateInput]
    temperature_k: float = DEFAULT_TEMPERATURE_K
