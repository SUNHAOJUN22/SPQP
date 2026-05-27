from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.seed import builtin_molecules_with_descriptors
from app.models.database import CatalystModel, MechanismHypothesis, Molecule, MonomerFamily, PeroxideSpecies, Project, RadicalReactionPath
from app.services.literature import default_mechanism_hypotheses, extract_thesis_knowledge
from app.services.radical_v4 import PEROXIDE_LIBRARY


def init_seed_data(db: Session) -> None:
    project = db.scalar(select(Project).where(Project.name == "SiO Catalyst Quantum Studio"))
    if project is None:
        project = Project(
            name="SiO Catalyst Quantum Studio",
            description="Default MVP project for Si-O functional alpha-olefin catalyst workflow studies.",
        )
        db.add(project)
        db.flush()

    existing_by_key = {row.key: row for row in db.scalars(select(Molecule)).all()}
    for item in builtin_molecules_with_descriptors():
        existing = existing_by_key.get(item["key"])
        if existing is not None:
            for field, value in item.items():
                setattr(existing, field, value)
            continue
        db.add(Molecule(project_id=project.id, **item))

    knowledge = extract_thesis_knowledge("")
    existing_catalysts = {row.key: row for row in db.scalars(select(CatalystModel)).all()}
    for item in knowledge["catalyst_models"]:
        existing = existing_catalysts.get(item["key"])
        if existing is not None:
            for field, value in item.items():
                setattr(existing, field if field != "active_site" else "active_site", value)
            continue
        db.add(CatalystModel(**item))

    existing_families = {row.key: row for row in db.scalars(select(MonomerFamily)).all()}
    for item in knowledge["monomer_families"]:
        existing = existing_families.get(item["key"])
        if existing is not None:
            for field, value in item.items():
                setattr(existing, field, value)
            continue
        db.add(MonomerFamily(**item))

    existing_hypotheses = {row.key: row for row in db.scalars(select(MechanismHypothesis)).all()}
    for item in default_mechanism_hypotheses():
        existing = existing_hypotheses.get(item["key"])
        if existing is not None:
            for field, value in item.items():
                setattr(existing, field, value)
            continue
        db.add(MechanismHypothesis(**item))

    existing_peroxides = {row.key: row for row in db.scalars(select(PeroxideSpecies)).all()}
    for item in PEROXIDE_LIBRARY:
        values = {
            "key": item["key"],
            "chinese_name": item["chinese_name"],
            "english_name": item["english_name"],
            "peroxide_class": item["peroxide_class"],
            "has_carbonyl": item["has_carbonyl"],
            "radical_type": item["radical_type"],
            "roor_bde_kcal_mol": item["example_roor_bde_kcal_mol"],
            "half_life_reference": None,
            "mechanism_note": item["typical_role"],
            "source": item["source"],
        }
        existing = existing_peroxides.get(item["key"])
        if existing is not None:
            for field, value in values.items():
                setattr(existing, field, value)
            continue
        db.add(PeroxideSpecies(**values))

    radical_paths = [
        {
            "key": "roor-homolysis",
            "name": "RO–OR 均裂",
            "elementary_step": "RO–OR → 2RO•",
            "rate_law": "kd[ROOR]，kd = ln2 / t1/2",
            "required_data": ["半衰期", "温度", "RO–OR BDE"],
            "mechanism_note": "控制自由基通量起点，不能等同于最终支化或降解结果。",
            "source": "V4 机制模型",
        },
        {
            "key": "pp-h-abstraction",
            "name": "PP 抽氢",
            "elementary_step": "RO• + PP–H → ROH + PP•",
            "rate_law": "kabs[RO•][PP–H]",
            "required_data": ["PP 三级 C–H 含量", "乙烯含量", "抽氢势垒"],
            "mechanism_note": "聚丙烯三级 C–H 位点越多，越容易形成可 β-scission 的大分子自由基。",
            "source": "V4 机制模型",
        },
        {
            "key": "beta-scission",
            "name": "β-scission 降解",
            "elementary_step": "PP• → 断链自由基 + 末端烯烃",
            "rate_law": "kscission[PP•]",
            "required_data": ["GPC", "末端烯烃", "加工温度", "停留时间"],
            "mechanism_note": "PP 过氧化物处理常见分子量下降通道。",
            "source": "V4 机制模型",
        },
        {
            "key": "recombination-branching",
            "name": "复合/接枝/长链支化",
            "elementary_step": "PP• + 共剂/双官能单体 → 支化或交联结构",
            "rate_law": "kbranch[PP•][coagent]",
            "required_data": ["共剂浓度", "凝胶分数", "流变", "支化指数"],
            "mechanism_note": "只有在链段接近、共剂充足且氧化受控时才可能压过断链。",
            "source": "V4 机制模型",
        },
    ]
    existing_paths = {row.key: row for row in db.scalars(select(RadicalReactionPath)).all()}
    for item in radical_paths:
        existing = existing_paths.get(item["key"])
        if existing is not None:
            for field, value in item.items():
                setattr(existing, field, value)
            continue
        db.add(RadicalReactionPath(**item))
    db.commit()
