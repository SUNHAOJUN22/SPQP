from __future__ import annotations

from app.services.chemistry import describe_molecule
from app.services.literature import default_mechanism_hypotheses


BUILTIN_MOLECULES = [
    {
        "key": "DCS",
        "name": "hex-5-enyl-methyl-dichlorosilane",
        "smiles": "C=CCCCC[Si](C)(Cl)Cl",
        "substituents": "Me / Cl / Cl / hex-5-enyl",
        "role": "氯硅烷基准单体，用作高插入活性的参照结构。",
        "source": "示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "MCSOMe",
        "name": "chloro(hex-5-en-1-yl)methoxy-methylsilane",
        "smiles": "C=CCCCC[Si](C)(OC)Cl",
        "substituents": "Me / Cl / OMe / hex-5-enyl",
        "role": "单甲氧基平衡候选结构，用于优化功能性与插入活性的折中。",
        "source": "示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "DMOS",
        "name": "hex-5-enyl-dimethoxy-methylsilane",
        "smiles": "C=CCCCC[Si](C)(OC)OC",
        "substituents": "Me / OMe / OMe / hex-5-enyl",
        "role": "双甲氧基极限结构，后反应功能性高，但可能具有 O→Ti 毒化与位阻风险。",
        "source": "示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "ethylene",
        "name": "ethylene",
        "smiles": "C=C",
        "substituents": None,
        "role": "插入反应基准单体。",
        "source": "示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "1-hexene",
        "name": "1-hexene",
        "smiles": "C=CCCCC",
        "substituents": None,
        "role": "共聚单体基准结构。",
        "source": "示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "TEA",
        "name": "triethylaluminum",
        "smiles": "CC[Al](CC)CC",
        "substituents": None,
        "role": "TEA 助催化剂 / Lewis 酸相互作用对象。",
        "source": "示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "C4-TMS",
        "name": "3-butenyltrimethylsilane",
        "smiles": "C=CCC[Si](C)(C)C",
        "substituents": "Me / Me / Me / 3-butenyl",
        "role": "论文中的短链三甲基硅烷功能 α-烯烃，用于考察链长压缩下的位阻与插入窗口。",
        "source": "论文抽取 + 示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "C6-TMS",
        "name": "5-hexenyltrimethylsilane",
        "smiles": "C=CCCCC[Si](C)(C)C",
        "substituents": "Me / Me / Me / 5-hexenyl",
        "role": "论文中的中链三甲基硅烷模型单体，用于比较乙烯/丙烯共聚插入趋势。",
        "source": "论文抽取 + 示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "C8-TMS",
        "name": "7-octenyltrimethylsilane",
        "smiles": "C=CCCCCCC[Si](C)(C)C",
        "substituents": "Me / Me / Me / 7-octenyl",
        "role": "论文中的长链三甲基硅烷模型单体，用于检验柔性链长是否缓解或放大空间效应。",
        "source": "论文抽取 + 示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "C4-DCS",
        "name": "3-butenyl-methyl-dichlorosilane",
        "smiles": "C=CCC[Si](C)(Cl)Cl",
        "substituents": "Me / Cl / Cl / 3-butenyl",
        "role": "论文中的短链甲基二氯硅烷单体，用于乙烯体系中氯硅烷电子导向与短链靠近效应分析。",
        "source": "论文抽取 + 示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "C8-DCS",
        "name": "7-octenyl-methyl-dichlorosilane",
        "smiles": "C=CCCCCCC[Si](C)(Cl)Cl",
        "substituents": "Me / Cl / Cl / 7-octenyl",
        "role": "论文中的长链甲基二氯硅烷单体，用于检验链柔性、位阻和助剂导向之间的竞争。",
        "source": "论文抽取 + 示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "propylene",
        "name": "propylene",
        "smiles": "C=CC",
        "substituents": None,
        "role": "丙烯共聚基准单体，用于比较甲基位阻和区域/立构插入差异。",
        "source": "示例数据 / MOCK；不是量子化学结果",
    },
    {
        "key": "TiCl3-Et",
        "name": "simplified Ti active site placeholder",
        "smiles": "[Ti](Cl)(Cl)(Cl)CC",
        "substituents": "TiCl3 / Et",
        "role": "简化 Ti 活性中心占位模型，不代表完整 MgCl2 负载结构。",
        "source": "示例占位 / MOCK；不是验证结构",
    },
    {
        "key": "MgCl2-TiCl4-Et",
        "name": "MgCl2/TiCl4/Et cluster placeholder",
        "smiles": "[Mg](Cl)Cl.[Ti](Cl)(Cl)(Cl)Cl.CC",
        "substituents": "cluster placeholder",
        "role": "负载催化剂团簇占位模型，用于项目组织。",
        "source": "示例占位 / MOCK；不是验证结构",
    },
    {
        "key": "MgCl2-BMMF-TiCl4-iBU",
        "name": "MgCl2/BMMF/TiCl4/iBU cluster placeholder",
        "smiles": "[Mg](Cl)Cl.[Ti](Cl)(Cl)(Cl)Cl.CC(C)C",
        "substituents": "cluster placeholder",
        "role": "给电子体修饰负载催化剂团簇占位模型。",
        "source": "示例占位 / MOCK；不是验证结构",
    },
]


def builtin_molecules_with_descriptors() -> list[dict]:
    rows: list[dict] = []
    for item in BUILTIN_MOLECULES:
        descriptors = describe_molecule(item["smiles"])
        rows.append({**item, "descriptors": descriptors})
    return rows


MOCK_DESCRIPTOR_MATRIX = [
    {
        "molecule": "DCS",
        "si_o_polarity": "待计算",
        "al_capture": "弱导向",
        "ti_poison": "low",
        "insertion_barrier": "baseline",
        "post_functionality": "chlorosilane hydrolysis",
        "source": "示例趋势 / MOCK；请替换为上传 Gaussian 解析数据",
    },
    {
        "molecule": "MCSOMe",
        "si_o_polarity": "moderate",
        "al_capture": "有效预组织",
        "ti_poison": "competitive",
        "insertion_barrier": "near-baseline",
        "post_functionality": "balanced hydrolysis/condensation",
        "source": "示例趋势 / MOCK；请替换为上传 Gaussian 解析数据",
    },
    {
        "molecule": "DMOS",
        "si_o_polarity": "strong",
        "al_capture": "过度捕获风险",
        "ti_poison": "high risk",
        "insertion_barrier": "possibly elevated",
        "post_functionality": "high",
        "source": "示例趋势 / MOCK；请替换为上传 Gaussian 解析数据",
    },
]
