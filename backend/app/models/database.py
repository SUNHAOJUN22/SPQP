from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), default="SiO Catalyst Quantum Studio")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_policy: Mapped[str] = mapped_column(String(80), default="mock-data-visible")

    molecules: Mapped[list["Molecule"]] = relationship(back_populates="project")


class Molecule(Base, TimestampMixin):
    __tablename__ = "molecules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    key: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(300))
    smiles: Mapped[str] = mapped_column(String(500))
    substituents: Mapped[str | None] = mapped_column(String(300), nullable=True)
    source: Mapped[str] = mapped_column(String(80), default="示例数据 / MOCK")
    descriptors: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project: Mapped[Project | None] = relationship(back_populates="molecules")
    conformers: Mapped[list["Conformer"]] = relationship(back_populates="molecule")
    jobs: Mapped[list["GaussianJob"]] = relationship(back_populates="molecule")


class Conformer(Base, TimestampMixin):
    __tablename__ = "conformers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    molecule_id: Mapped[int] = mapped_column(ForeignKey("molecules.id"))
    label: Mapped[str] = mapped_column(String(120))
    xyz: Mapped[str | None] = mapped_column(Text, nullable=True)
    energy_hartree: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="generated")

    molecule: Mapped[Molecule] = relationship(back_populates="conformers")


class Fragment(Base, TimestampMixin):
    __tablename__ = "fragments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(160))
    fragment_type: Mapped[str] = mapped_column(String(120), default="未分类片段")
    atom_indices: Mapped[list | None] = mapped_column(JSON, nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(600), nullable=True)
    method: Mapped[str | None] = mapped_column(String(120), nullable=True)
    basis: Mapped[str | None] = mapped_column(String(120), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)
    provenance: Mapped[str] = mapped_column(String(300), default="示例片段，不能作为真实结论")


class GaussianJob(Base, TimestampMixin):
    __tablename__ = "gaussian_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    job_type: Mapped[str] = mapped_column(String(120))
    method: Mapped[str] = mapped_column(String(80))
    basis: Mapped[str] = mapped_column(String(80))
    dispersion: Mapped[str | None] = mapped_column(String(80), nullable=True)
    charge: Mapped[int] = mapped_column(Integer, default=0)
    multiplicity: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    input_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    output_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    parsed_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    molecule: Mapped[Molecule | None] = relationship(back_populates="jobs")


class GaussianOutput(Base, TimestampMixin):
    __tablename__ = "gaussian_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("gaussian_jobs.id"), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255))
    path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    normal_termination: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    parsed_json: Mapped[dict] = mapped_column(JSON)
    quality: Mapped[str] = mapped_column(String(40), default="partial")


class ParsedEnergy(Base, TimestampMixin):
    __tablename__ = "parsed_energies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gaussian_output_id: Mapped[int | None] = mapped_column(ForeignKey("gaussian_outputs.id"), nullable=True)
    label: Mapped[str] = mapped_column(String(120))
    scf_hartree: Mapped[float | None] = mapped_column(Float, nullable=True)
    gibbs_hartree: Mapped[float | None] = mapped_column(Float, nullable=True)
    enthalpy_hartree: Mapped[float | None] = mapped_column(Float, nullable=True)
    zpe_hartree: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(80), default="uploaded")


class BondDescriptor(Base, TimestampMixin):
    __tablename__ = "bond_descriptors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    label: Mapped[str] = mapped_column(String(120))
    descriptor_json: Mapped[dict] = mapped_column(JSON)
    source: Mapped[str] = mapped_column(String(80), default="user-input")


class NBOInteraction(Base, TimestampMixin):
    __tablename__ = "nbo_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gaussian_output_id: Mapped[int | None] = mapped_column(ForeignKey("gaussian_outputs.id"), nullable=True)
    donor: Mapped[str] = mapped_column(String(160))
    acceptor: Mapped[str] = mapped_column(String(160))
    e2_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)


class TEAComplex(Base, TimestampMixin):
    __tablename__ = "tea_complexes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    mode: Mapped[str] = mapped_column(String(80))
    delta_g_bind_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    delta_e_bind_bsse_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(80), default="user-input")


class TiComplex(Base, TimestampMixin):
    __tablename__ = "ti_complexes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    delta_g_poison_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(80), default="user-input")


class InsertionPath(Base, TimestampMixin):
    __tablename__ = "insertion_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    path_label: Mapped[str] = mapped_column(String(120))
    delta_g_pi_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    delta_g_barrier_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    delta_g_complex_barrier_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    krel: Mapped[float | None] = mapped_column(Float, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(80), default="user-input")


class HydrolysisPath(Base, TimestampMixin):
    __tablename__ = "hydrolysis_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    template: Mapped[str] = mapped_column(String(200))
    explicit_water_count: Mapped[int] = mapped_column(Integer, default=1)
    delta_g_hydrolysis_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    delta_g_condensation_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(80), default="user-input")


class CondensationPath(Base, TimestampMixin):
    __tablename__ = "condensation_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    path_label: Mapped[str] = mapped_column(String(160))
    delta_g_condensation_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    leaving_group: Mapped[str | None] = mapped_column(String(80), nullable=True)
    explicit_water_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(600), nullable=True)
    method: Mapped[str | None] = mapped_column(String(120), nullable=True)
    basis: Mapped[str | None] = mapped_column(String(120), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(80), default="kcal/mol")
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)
    provenance: Mapped[str] = mapped_column(String(300), default="后反应缩合路径占位，不能作为真实结论")


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    format: Mapped[str] = mapped_column(String(40))
    content: Mapped[str] = mapped_column(Text)
    provenance: Mapped[dict] = mapped_column(JSON)


class LiteratureSource(Base, TimestampMixin):
    __tablename__ = "literature_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    path: Mapped[str | None] = mapped_column(String(600), nullable=True)
    source_type: Mapped[str] = mapped_column(String(80), default="docx")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_text_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)


class ThesisEntity(Base, TimestampMixin):
    __tablename__ = "thesis_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    literature_source_id: Mapped[int | None] = mapped_column(ForeignKey("literature_sources.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(120))
    name: Mapped[str] = mapped_column(String(240))
    chinese_name: Mapped[str] = mapped_column(String(240))
    evidence: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(120), default="论文抽取")


class CatalystModel(Base, TimestampMixin):
    __tablename__ = "catalyst_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(240))
    role: Mapped[str] = mapped_column(Text)
    active_site: Mapped[str] = mapped_column(String(240))
    thesis_link: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(120), default="论文抽取 + 示例占位")


class MonomerFamily(Base, TimestampMixin):
    __tablename__ = "monomer_families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    chinese_name: Mapped[str] = mapped_column(String(240))
    english_name: Mapped[str] = mapped_column(String(240))
    chain_lengths: Mapped[dict] = mapped_column(JSON, default=dict)
    mechanism_note: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(120), default="论文抽取")


class ExperimentalDataset(Base, TimestampMixin):
    __tablename__ = "experimental_datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(240))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="user-input")
    reliability: Mapped[str] = mapped_column(String(80), default="待核验")


class ExperimentRecord(Base, TimestampMixin):
    __tablename__ = "experiment_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int | None] = mapped_column(ForeignKey("experimental_datasets.id"), nullable=True)
    monomer: Mapped[str] = mapped_column(String(160))
    catalyst_system: Mapped[str] = mapped_column(String(240))
    polymerization_system: Mapped[str] = mapped_column(String(160))
    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    al_ti_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    activity: Mapped[float | None] = mapped_column(Float, nullable=True)
    insertion_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    hexene_content: Mapped[float | None] = mapped_column(Float, nullable=True)
    sequence_length: Mapped[float | None] = mapped_column(Float, nullable=True)
    melting_point_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    crystallinity_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    transparency_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class DftExperimentLink(Base, TimestampMixin):
    __tablename__ = "dft_experiment_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    experiment_record_id: Mapped[int | None] = mapped_column(ForeignKey("experiment_records.id"), nullable=True)
    molecule_key: Mapped[str] = mapped_column(String(120))
    delta_g_pi_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    delta_g_barrier_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    delta_g_poison_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    tea_binding_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    steric_penalty_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    electronic_guiding_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class MechanismHypothesis(Base, TimestampMixin):
    __tablename__ = "mechanism_hypotheses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(Text)
    supporting_evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    falsification: Mapped[dict] = mapped_column(JSON, default=dict)
    required_data: Mapped[dict] = mapped_column(JSON, default=dict)
    current_status: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(120), default="机制模型")


class EvidenceItem(Base, TimestampMixin):
    __tablename__ = "evidence_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hypothesis_id: Mapped[int | None] = mapped_column(ForeignKey("mechanism_hypotheses.id"), nullable=True)
    evidence_type: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    supports: Mapped[bool] = mapped_column(Boolean, default=True)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class CubeFile(Base, TimestampMixin):
    __tablename__ = "cube_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255))
    cube_type: Mapped[str] = mapped_column(String(80))
    path: Mapped[str | None] = mapped_column(String(600), nullable=True)
    atom_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    grid: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    source: Mapped[str] = mapped_column(String(120), default="uploaded")


class ESPExtremum(Base, TimestampMixin):
    __tablename__ = "esp_extrema"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cube_file_id: Mapped[int | None] = mapped_column(ForeignKey("cube_files.id"), nullable=True)
    label: Mapped[str] = mapped_column(String(120))
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(80), default="a.u.")
    position_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(600), nullable=True)
    method: Mapped[str | None] = mapped_column(String(120), nullable=True)
    basis: Mapped[str | None] = mapped_column(String(120), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)
    provenance: Mapped[str] = mapped_column(String(300), default="ESP 极值占位，需真实 cube 或 Multiwfn 输出验证")


class PeroxideSpecies(Base, TimestampMixin):
    __tablename__ = "peroxide_species"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    chinese_name: Mapped[str] = mapped_column(String(240))
    english_name: Mapped[str] = mapped_column(String(240))
    peroxide_class: Mapped[str] = mapped_column(String(160))
    has_carbonyl: Mapped[bool] = mapped_column(Boolean, default=False)
    radical_type: Mapped[str] = mapped_column(String(240))
    roor_bde_kcal_mol: Mapped[float | None] = mapped_column(Float, nullable=True)
    half_life_reference: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    mechanism_note: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(120), default="示例数据 / MOCK")


class RadicalReactionPath(Base, TimestampMixin):
    __tablename__ = "radical_reaction_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(240))
    elementary_step: Mapped[str] = mapped_column(String(240))
    rate_law: Mapped[str] = mapped_column(String(240))
    required_data: Mapped[dict] = mapped_column(JSON, default=dict)
    mechanism_note: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(120), default="机制模型")


class PolymerMicrostructure(Base, TimestampMixin):
    __tablename__ = "polymer_microstructures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    ethylene_mol_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    isotacticity_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    crystallinity_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    melt_flow_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="用户输入")


class ResidenceTimeWindow(Base, TimestampMixin):
    __tablename__ = "residence_time_windows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    peroxide_key: Mapped[str] = mapped_column(String(120), index=True)
    temperature_c: Mapped[float] = mapped_column(Float)
    half_life_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    residence_time_min: Mapped[float] = mapped_column(Float)
    conversion_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(120))
    source: Mapped[str] = mapped_column(String(120), default="用户输入")


class LiteratureEvidenceItem(Base, TimestampMixin):
    __tablename__ = "literature_evidence_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    literature_source_id: Mapped[int | None] = mapped_column(ForeignKey("literature_sources.id"), nullable=True)
    topic: Mapped[str] = mapped_column(String(160))
    evidence: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(160), default="文献抽取")


class Atom(Base, TimestampMixin):
    __tablename__ = "atoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    atom_index: Mapped[int] = mapped_column(Integer)
    element: Mapped[str] = mapped_column(String(12))
    x: Mapped[float | None] = mapped_column(Float, nullable=True)
    y: Mapped[float | None] = mapped_column(Float, nullable=True)
    z: Mapped[float | None] = mapped_column(Float, nullable=True)
    charge: Mapped[float | None] = mapped_column(Float, nullable=True)
    functional_site: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="uploaded")


class Bond(Base, TimestampMixin):
    __tablename__ = "bonds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    atom_i: Mapped[int] = mapped_column(Integer)
    atom_j: Mapped[int] = mapped_column(Integer)
    bond_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    length_angstrom: Mapped[float | None] = mapped_column(Float, nullable=True)
    bond_order: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="uploaded")


class Thermochemistry(Base, TimestampMixin):
    __tablename__ = "thermochemistry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gaussian_output_id: Mapped[int | None] = mapped_column(ForeignKey("gaussian_outputs.id"), nullable=True)
    temperature_k: Mapped[float | None] = mapped_column(Float, nullable=True)
    pressure_atm: Mapped[float | None] = mapped_column(Float, nullable=True)
    zpe_hartree: Mapped[float | None] = mapped_column(Float, nullable=True)
    enthalpy_hartree: Mapped[float | None] = mapped_column(Float, nullable=True)
    gibbs_hartree: Mapped[float | None] = mapped_column(Float, nullable=True)
    correction_source: Mapped[str] = mapped_column(String(120), default="Gaussian parser")
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)


class Frequency(Base, TimestampMixin):
    __tablename__ = "frequencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gaussian_output_id: Mapped[int | None] = mapped_column(ForeignKey("gaussian_outputs.id"), nullable=True)
    mode_index: Mapped[int] = mapped_column(Integer)
    frequency_cm_1: Mapped[float] = mapped_column(Float)
    intensity: Mapped[float | None] = mapped_column(Float, nullable=True)
    assignment: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="uploaded")


class Orbital(Base, TimestampMixin):
    __tablename__ = "orbitals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gaussian_output_id: Mapped[int | None] = mapped_column(ForeignKey("gaussian_outputs.id"), nullable=True)
    label: Mapped[str] = mapped_column(String(80))
    energy_hartree: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_ev: Mapped[float | None] = mapped_column(Float, nullable=True)
    occupancy: Mapped[float | None] = mapped_column(Float, nullable=True)
    spin: Mapped[str | None] = mapped_column(String(40), nullable=True)
    contribution_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="uploaded")


class Charge(Base, TimestampMixin):
    __tablename__ = "charges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gaussian_output_id: Mapped[int | None] = mapped_column(ForeignKey("gaussian_outputs.id"), nullable=True)
    atom_index: Mapped[int] = mapped_column(Integer)
    element: Mapped[str | None] = mapped_column(String(12), nullable=True)
    scheme: Mapped[str] = mapped_column(String(80))
    charge_e: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="uploaded")


class BondOrder(Base, TimestampMixin):
    __tablename__ = "bond_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gaussian_output_id: Mapped[int | None] = mapped_column(ForeignKey("gaussian_outputs.id"), nullable=True)
    atom_i: Mapped[int] = mapped_column(Integer)
    atom_j: Mapped[int] = mapped_column(Integer)
    scheme: Mapped[str] = mapped_column(String(80), default="Wiberg")
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="uploaded")


class QtaimCriticalPoint(Base, TimestampMixin):
    __tablename__ = "qtaim_critical_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(160))
    atom_pair: Mapped[str | None] = mapped_column(String(80), nullable=True)
    rho_bcp: Mapped[float | None] = mapped_column(Float, nullable=True)
    laplacian_rho_bcp: Mapped[float | None] = mapped_column(Float, nullable=True)
    h_bcp: Mapped[float | None] = mapped_column(Float, nullable=True)
    v_bcp: Mapped[float | None] = mapped_column(Float, nullable=True)
    g_bcp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ellipticity: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="uploaded")


class NciRegion(Base, TimestampMixin):
    __tablename__ = "nci_regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(160))
    sign_lambda2_rho: Mapped[float | None] = mapped_column(Float, nullable=True)
    rdg_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    interaction_type: Mapped[str] = mapped_column(String(120))
    color: Mapped[str] = mapped_column(String(40))
    source: Mapped[str] = mapped_column(String(120), default="uploaded")


class RadicalModel(Base, TimestampMixin):
    __tablename__ = "radical_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(240))
    model_type: Mapped[str] = mapped_column(String(120))
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)


class Coagent(Base, TimestampMixin):
    __tablename__ = "coagents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    chinese_name: Mapped[str] = mapped_column(String(240))
    english_name: Mapped[str] = mapped_column(String(240))
    functionality: Mapped[str] = mapped_column(String(120))
    mechanism_note: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(120), default="示例数据 / MOCK")


class RadicalKinetics(Base, TimestampMixin):
    __tablename__ = "radical_kinetics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    residence_time_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    rates: Mapped[dict] = mapped_column(JSON, default=dict)
    fractions: Mapped[dict] = mapped_column(JSON, default=dict)
    source: Mapped[str] = mapped_column(String(120), default="calculated")


class ExperimentalSample(Base, TimestampMixin):
    __tablename__ = "experimental_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    matrix: Mapped[str] = mapped_column(String(160))
    catalyst_system: Mapped[str | None] = mapped_column(String(240), nullable=True)
    formulation: Mapped[dict] = mapped_column(JSON, default=dict)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class GpcData(Base, TimestampMixin):
    __tablename__ = "gpc_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    mn: Mapped[float | None] = mapped_column(Float, nullable=True)
    mw: Mapped[float | None] = mapped_column(Float, nullable=True)
    pdi: Mapped[float | None] = mapped_column(Float, nullable=True)
    high_mw_shoulder: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class MfrData(Base, TimestampMixin):
    __tablename__ = "mfr_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    mfr_g_10min: Mapped[float | None] = mapped_column(Float, nullable=True)
    condition: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class GelData(Base, TimestampMixin):
    __tablename__ = "gel_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    gel_fraction_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    solvent: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class RheologyData(Base, TimestampMixin):
    __tablename__ = "rheology_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    low_frequency_enhancement: Mapped[float | None] = mapped_column(Float, nullable=True)
    strain_hardening_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class FtirData(Base, TimestampMixin):
    __tablename__ = "ftir_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    carbonyl_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    si_o_si_peak: Mapped[float | None] = mapped_column(Float, nullable=True)
    si_oh_peak: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class NmrData(Base, TimestampMixin):
    __tablename__ = "nmr_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    nucleus: Mapped[str] = mapped_column(String(40))
    assignments: Mapped[dict] = mapped_column(JSON, default=dict)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class DielectricData(Base, TimestampMixin):
    __tablename__ = "dielectric_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    dielectric_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    space_charge_metric: Mapped[float | None] = mapped_column(Float, nullable=True)
    condition: Mapped[str | None] = mapped_column(String(160), nullable=True)
    source: Mapped[str] = mapped_column(String(120), default="user-input")


class DSCData(Base, TimestampMixin):
    __tablename__ = "dsc_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    tm_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    tc_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    crystallinity_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(600), nullable=True)
    method: Mapped[str | None] = mapped_column(String(120), nullable=True)
    basis: Mapped[str | None] = mapped_column(String(120), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(80), default="C / %")
    is_mock: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance: Mapped[str] = mapped_column(String(300), default="用户输入 DSC 数据")


class MorphologyData(Base, TimestampMixin):
    __tablename__ = "morphology_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_key: Mapped[str] = mapped_column(String(120), index=True)
    technique: Mapped[str] = mapped_column(String(120), default="SEM/TEM/AFM")
    domain_size_nm: Mapped[float | None] = mapped_column(Float, nullable=True)
    coarsening_resistance: Mapped[str | None] = mapped_column(String(160), nullable=True)
    metrics_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(600), nullable=True)
    method: Mapped[str | None] = mapped_column(String(120), nullable=True)
    basis: Mapped[str | None] = mapped_column(String(120), nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(80), default="nm / descriptor")
    is_mock: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance: Mapped[str] = mapped_column(String(300), default="用户输入相形态数据")


class McpTask(Base, TimestampMixin):
    __tablename__ = "mcp_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tool_name: Mapped[str] = mapped_column(String(160))
    arguments: Mapped[dict] = mapped_column(JSON, default=dict)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(80), default="completed")
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)


class SimulationTool(Base, TimestampMixin):
    __tablename__ = "simulation_tools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    tool_type: Mapped[str] = mapped_column(String(120), index=True)
    display_name: Mapped[str] = mapped_column(String(240))
    executable_path: Mapped[str | None] = mapped_column(String(600), nullable=True)
    is_configured: Mapped[bool] = mapped_column(Boolean, default=False)
    can_execute: Mapped[bool] = mapped_column(Boolean, default=False)
    default_mode: Mapped[str] = mapped_column(String(80), default="template_only")
    safety_level: Mapped[str] = mapped_column(String(80), default="external-disabled")
    allowed_extensions_json: Mapped[list] = mapped_column(JSON, default=list)
    working_directory: Mapped[str | None] = mapped_column(String(600), nullable=True)
    validation_status: Mapped[str] = mapped_column(String(80), default="missing")
    warnings_json: Mapped[list] = mapped_column(JSON, default=list)


class SimulationJob(Base, TimestampMixin):
    __tablename__ = "simulation_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    molecule_id: Mapped[int | None] = mapped_column(ForeignKey("molecules.id"), nullable=True)
    tool_id: Mapped[int | None] = mapped_column(ForeignKey("simulation_tools.id"), nullable=True)
    job_type: Mapped[str] = mapped_column(String(160))
    tool_type: Mapped[str] = mapped_column(String(120), default="parser_only")
    execution_mode: Mapped[str] = mapped_column(String(80), default="template_only")
    status: Mapped[str] = mapped_column(String(80), default="draft")
    input_files_json: Mapped[list] = mapped_column(JSON, default=list)
    output_files_expected_json: Mapped[list] = mapped_column(JSON, default=list)
    generated_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    command_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    will_execute: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_user_confirmation: Mapped[bool] = mapped_column(Boolean, default=True)
    evidence_grade: Mapped[str] = mapped_column(String(8), default="D")
    provenance_json: Mapped[dict] = mapped_column(JSON, default=dict)


class SimulationParseResult(Base, TimestampMixin):
    __tablename__ = "simulation_parse_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("simulation_jobs.id"), nullable=True)
    parser_name: Mapped[str] = mapped_column(String(160))
    source_file: Mapped[str] = mapped_column(String(600))
    source_type: Mapped[str] = mapped_column(String(120), default="text")
    quality: Mapped[str] = mapped_column(String(80), default="partial")
    normalized_json: Mapped[dict] = mapped_column(JSON, default=dict)
    units_json: Mapped[dict] = mapped_column(JSON, default=dict)
    warnings_json: Mapped[list] = mapped_column(JSON, default=list)
    errors_json: Mapped[list] = mapped_column(JSON, default=list)
    evidence_grade: Mapped[str] = mapped_column(String(8), default="D")
    is_mock: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance_json: Mapped[dict] = mapped_column(JSON, default=dict)


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(160))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    severity: Mapped[str] = mapped_column(String(40), default="info")
    source: Mapped[str] = mapped_column(String(120), default="system")
