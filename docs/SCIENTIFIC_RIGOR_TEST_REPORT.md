# 数理严谨性自动测试报告

- 测试时间：2026-05-28 15:04:32
- 测试环境：Python 3.11.9 / Windows-10-10.0.26300-SP0
- 工作目录：D:\codex2_cataSi-O
- 总检查项：31
- 通过：31
- 失败：0

## 执行命令
```powershell
backend\.venv\Scripts\python.exe scripts\scientific_rigor_audit.py
```

## 数理公式核查结果
已自动检查 ΔGbind、ΔGpoison、ΔGπ、ΔG‡、ΔG‡complex、ΔΔG‡ 与 krel = exp[-ΔΔG‡ / RT]。所有通过项均使用固定常数和显式单位。

## 单位换算核查结果
- Hartree to kcal/mol：627.509474
- Hartree to eV：27.211386245988
- R：0.00198720425864083 kcal mol^-1 K^-1
- 默认温度：350.0 K

## Gaussian parser 核查结果
已覆盖 complete、failed/empty 路径，并检查 SCF、Gibbs、频率、虚频、HOMO/LUMO、gap、偶极矩、Mulliken、NPA、Wiberg、NBO E(2)、Counterpoise 字段。

## 判据边界测试结果
已覆盖 ΔGpoison > +5、0 到 +5、< 0 三段判据，以及缺少 π-complex、O→Ti complex、TS、参考态自由能时的中文错误路径。

## 详细结果
### 常数
- PASS：Hartree 到 kcal/mol：627.509474
- PASS：Hartree 到 eV：27.211386245988
- PASS：气体常数 R：0.00198720425864083
- PASS：默认温度：350.0 K

### 公式
- PASS：ΔGbind 公式：-0.025000000000005684 Hartree / -15.687736850003565 kcal/mol
- PASS：ΔGpoison 公式与有利插入判据：6.275095 kcal/mol, 生产性 C=C 插入占优
- PASS：ΔGπ / ΔG‡ / ΔG‡complex / krel：{"delta_g_pi_kcal_mol": -7.530113688000285, "delta_g_barrier_kcal_mol": 11.295170531982592, "delta_g_complex_barrier_kcal_mol": 18.825284219982876, "delta_g_product_kcal_mol": -25.10037896001284, "delta_delta_g_barrier_kcal_mol": 1.295170531982592, "krel": 0.155337134975891, "temperature_k": 350.0}

### 速率
- PASS：ΔΔG‡=0 时 krel=1：1.0
- PASS：ΔΔG‡>0 时 krel<1：0.01338915420915898
- PASS：ΔΔG‡<0 时 krel>1：74.68731664289446
- PASS：升温降低速率差异：300K=2.278e-04, 600K=1.509e-02
- PASS：极端能垒不产生 NaN/Infinity：[5.184705528587072e+21, 1.9287498479639178e-22]

### parser
- PASS：Gaussian complete 解析：quality=complete, warnings=[]
- PASS：空 Gaussian log 不伪造数据：quality=failed, warnings=['未检测到 Gaussian 正常终止标记。', '当前文件中未找到吉布斯自由能。', '当前文件中未找到 NBO 二阶微扰分析结果。']

### API
- PASS：能量组分：HTTP 200, 14.7 ms
- PASS：TEA 助剂结合：HTTP 200, 5.0 ms
- PASS：Ti 毒化判据：HTTP 200, 4.2 ms
- PASS：插入反应剖面：HTTP 200, 3.8 ms
- PASS：相对速率：HTTP 200, 2.8 ms
- PASS：Si–O 描述符：HTTP 200, 3.4 ms
- PASS：量子判据引擎：HTTP 200, 2.7 ms
- PASS：Gaussian 文本解析：HTTP 200, 2.4 ms
- PASS：中文报告生成：HTTP 200, 29.0 ms

### 错误路径
- PASS：缺少 π-complex：HTTP 422
- PASS：缺少 O→Ti complex：HTTP 422
- PASS：缺少 TS 自由能：HTTP 422
- PASS：缺少参考态自由能：HTTP 422
- PASS：空 Gaussian log：HTTP 200
- PASS：非法文件类型：HTTP 400

### mock
- PASS：mock 判据矩阵来源：HTTP 200
- PASS：mock 报告可靠性声明：HTTP 200

## 失败项和修复项
无失败项。

## 剩余风险
- Gaussian parser 基于文本模式匹配，真实生产日志仍需用更多 Gaussian/NBO/Multiwfn 样本扩充回归集。
- cube 当前已审计元数据、下采样体素预览、剖切预览和差分电子密度预览；真实 marching-cubes 等值面重建仍属于后续阶段。
- 当前自动审计不会执行 Gaussian、cubegen 或 Multiwfn，因此不能替代真实量子化学计算质量审查。

## 数据来源边界
- 真实数据：仅限用户上传并由 parser 只读解析的 Gaussian/cube/CSV 数据。
- 用户输入：通过 API 或界面录入的自由能、实验记录和描述符，需用户保证来源。
- mock/example：内置演示矩阵、候选评分和 UI 图表示例，均不能作为真实科学结论。

## 安全约束
- 本次审计未执行 Gaussian、cubegen、Multiwfn 或用户上传文件。
- 所有 parser 均按只读文本解析执行。
- mock/example 数据在报告和 API provenance 中保持显式标注。