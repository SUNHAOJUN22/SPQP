# Gaussian / cubegen / Multiwfn 外部工具示例

本项目默认不执行 Gaussian、cubegen、Multiwfn。外部程序只能通过受控 runner 显式运行。

## 本机检测结果

当前环境 PATH 与相关环境变量中未检测到：

- `g16` / `g09` / `gaussian`
- `formchk`
- `cubegen`
- `Multiwfn`

因此本轮只能完成示例文件、runner 和 check-only 验证；真实外部程序执行需要在本机安装这些工具并传入路径。

## 示例文件

```text
examples/external-qc/gaussian/water_opt_freq_nbo.gjf
examples/external-qc/gaussian/ethylene_sp_pop.gjf
examples/external-qc/gaussian/mcsome_fast_sp.gjf
examples/external-qc/multiwfn/load_and_quit.inp
```

示例链路：

1. Gaussian 运行 `water_opt_freq_nbo.gjf`，生成 `.log` 和 `.chk`。
2. `formchk water_opt_freq_nbo.chk water_opt_freq_nbo.fchk`。
3. `cubegen 0 Density=SCF water_opt_freq_nbo.fchk water_density.cube 0 h`。
4. `cubegen 0 MO=HOMO water_opt_freq_nbo.fchk water_homo.cube 0 h`。
5. `Multiwfn water_opt_freq_nbo.fchk < load_and_quit.inp`。

## 只检查示例，不执行外部程序

```powershell
backend\.venv\Scripts\python.exe scripts\run_external_qc_examples.py --check-only
```

或：

```powershell
npm run examples:external-qc
```

## 真实执行

Windows 示例：

```powershell
backend\.venv\Scripts\python.exe scripts\run_external_qc_examples.py `
  --execute-external-tools `
  --gaussian "C:\G16W\g16.exe" `
  --formchk "C:\G16W\formchk.exe" `
  --cubegen "C:\G16W\cubegen.exe" `
  --multiwfn "D:\Multiwfn\Multiwfn.exe"
```

Linux 示例：

```bash
python scripts/run_external_qc_examples.py \
  --execute-external-tools \
  --gaussian /opt/g16/g16 \
  --formchk /opt/g16/formchk \
  --cubegen /opt/g16/cubegen \
  --multiwfn /opt/Multiwfn/Multiwfn \
  --gaussian-style stdin
```

## 输出

默认输出目录：

```text
storage/external-qc-runs/<timestamp>/
```

成功执行后应包含：

```text
water_opt_freq_nbo.log
water_opt_freq_nbo.chk
water_opt_freq_nbo.fchk
water_density.cube
water_homo.cube
multiwfn_load_and_quit.stdout.txt
EXTERNAL_QC_RUN_REPORT.md
```

## 安全边界

- runner 默认只检查示例，不执行外部程序。
- 必须显式添加 `--execute-external-tools` 才会执行。
- 示例输出用于链路烟测，不能作为真实科研结论。
- 本应用的主服务仍不默认调用 Gaussian、cubegen 或 Multiwfn。
