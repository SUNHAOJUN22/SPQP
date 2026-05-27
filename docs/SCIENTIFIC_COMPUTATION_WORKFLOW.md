# 科学计算验证机制工作流

本平台通过“只生成、只解析、不执行外部化学软件”的方式，把 Si-O / Si-C / Ziegler-Natta / TEA / Ti 毒化 / 过氧化物自由基 / PP 长链支化-交联-降解机制转化为可计算任务、可解析字段、可证伪判据、API、UI 和中文报告输出。

## 1. 安全边界

- 不执行 Gaussian、cubegen、Multiwfn、GoodVibes。
- 不执行用户上传文件。
- Gaussian/cube/NBO/QTAIM/NCI/GoodVibes parser 只读。
- Gaussian、cubegen、Multiwfn 相关内容仅生成输入文件或命令模板，并标注“未执行”。
- mock/example 数据必须写明“示例数据，不能作为真实结论”。

## 2. 计算任务矩阵

后端接口：

- `GET /api/scientific-computation/task-matrix`
- `POST /api/integration/build-gaussian-task`

任务分组：

| 分组 | 中文名称 | 目的 |
| --- | --- | --- |
| A | 单体与键本征 | 单体 opt/freq/NBO、29Si GIAO、Si-O/Si-C/Si-Cl BDE |
| B | TEA / Ti 配位竞争 | Al<-O、Al...Cl、Al...C=C、C=C π-complex、O->Ti 毒化 |
| C | 插入反应路径 | 插入 TS、IRC、产物优化、序列插入 |
| D | 水解缩合后反应 | Si-Cl/Si-OMe 水解、Si-O-Si 缩合、离去物路径 |
| E | 过氧化物自由基路径 | RO-OR 均裂、RO• 抽氢、PP β-scission、复合、接枝、氧化 |
| F | 波函数可视化后处理 | formchk、cubegen density/ESP/HOMO/LUMO、Multiwfn 脚本模板 |

## 3. 公式与单位

单位常数：

- `1 Hartree = 627.509474 kcal/mol`
- `1 Hartree = 2625.499638 kJ/mol`
- `1 Hartree = 27.211386245988 eV`
- `R = 0.00198720425864083 kcal mol^-1 K^-1`
- 默认温度 `T = 350 K`

自由能公式：

- `ΔGbind = G(complex) - ΣG(fragments)`
- `ΔGpoison = G(O->Ti complex) - G(C=C π-complex)`
- `ΔGπ = G(π-complex) - G(free active site + monomer)`
- `ΔG‡insert = G(insertion TS) - G(free active site + monomer)`
- `ΔG‡complex = G(insertion TS) - G(π-complex)`
- `ΔΔG‡ = ΔG‡candidate - ΔG‡reference`
- `krel = exp[-ΔΔG‡ / RT]`

BDE 公式：

- `BDE(Si-C) = G(R•) + G(•Si fragment) - G(R-Si)`
- `BDE(Si-O) = G(R•) + G(•O-Si fragment) - G(R-O-Si)`
- `BDE(RO-OR) = G(2RO•) - G(RO-OR)`

自由基竞争：

- `R_scission = kβ[PP•]`
- `R_branch = krec[PP•]^2 + kg[PP•][M] + kc[PP•][coagent]`
- `S_LCB = R_branch / (R_branch + R_scission + R_oxidation)`

## 4. API 使用示例

### 能量公式工作台

`POST /api/scientific-computation/energy-workbench`

```json
{
  "complex_g_hartree": -150.025,
  "fragment_g_hartree": [-100.0, -50.0],
  "o_ti_complex_g_hartree": -100.0,
  "pi_complex_g_hartree": -100.02,
  "free_site_monomer_g_hartree": -500.0,
  "ts_g_hartree": -499.98,
  "product_g_hartree": -500.04,
  "reference_barrier_kcal_mol": 10.0,
  "temperature_k": 350.0,
  "evidence_grade": "C",
  "is_mock": false
}
```

### BDE 计算

`POST /api/analysis/bde`

```json
{
  "bond_type": "Si-C",
  "g_fragments_hartree": -199.86,
  "g_molecule_hartree": -200.0,
  "evidence_grade": "C",
  "is_mock": false,
  "source": "用户输入"
}
```

## 5. 判据边界

- `ΔGpoison > +5 kcal/mol`：生产性 C=C 插入占优。
- `0 <= ΔGpoison <= +5 kcal/mol`：O->Ti 与 C=C 配位竞争。
- `ΔGpoison < 0`：Ti 活性中心存在毒化风险。
- Si-O 键长增大、WBI 降低、频率红移、ρBCP 降低：Si-O 被 Lewis 酸配位削弱。
- Si-C BDE 高：Si-C 侧链连接稳定。
- Si-C BDE 低或 radical-near-SiC scission barrier 低：Si-C 连接臂存在失效风险。
- Mw 降低、MFR 升高、gel 低：PP β-scission 降解主导。
- SAOS 低频增强、strain hardening、gel 低至中等：有效长链支化或轻度交联。
- carbonyl index 增大、dielectric loss 增大：氧化羰基副反应风险。

## 6. Parser 字段边界

所有 parser 输出必须包含：

- normalized JSON
- units
- quality
- warnings
- provenance
- missing fields = null
- 中文错误提示

真实电子云、ESP、HOMO/LUMO、QTAIM、NCI 只能来自用户上传的真实 cube/fchk/Multiwfn 输出。没有 cube 时必须提示：“当前没有真实 cube 文件，不能显示真实电子云。”

## 7. UI 页面说明

新增页面：

- `科学计算工作流`

页面包含：

- 计算任务矩阵
- 能量公式工作台
- BDE 计算与 Si-C 稳定性
- 证据与安全边界
- 报告输出边界

## 8. 报告边界

报告中所有计算相关结论必须保留证据等级：

- A 级：真实计算且频率/TS/IRC/provenance 完整。
- B 级：真实实验数据且样品、工艺、表征条件明确。
- C 级：文献线索或用户输入，尚未复现。
- D 级：mock/example 或趋势假说，不能作为真实结论。

当前仅由模板、示例或用户输入得到的结果，报告必须写：“当前数据不足，不能形成可靠结论。”
