# 外部量子化学工具可运行示例

本目录提供 Gaussian、formchk、cubegen、Multiwfn 的最小可运行示例。默认只做文件与命令检查，不执行外部程序。

真实执行必须显式传入 `--execute-external-tools` 与工具路径：

```powershell
backend\.venv\Scripts\python.exe scripts\run_external_qc_examples.py `
  --execute-external-tools `
  --gaussian "C:\G16W\g16.exe" `
  --formchk "C:\G16W\formchk.exe" `
  --cubegen "C:\G16W\cubegen.exe" `
  --multiwfn "D:\Multiwfn\Multiwfn.exe"
```

输出默认写入：

```text
storage/external-qc-runs/<timestamp>/
```

## 示例链

1. `gaussian/water_opt_freq_nbo.gjf`
   - Gaussian opt/freq/NBO 烟测。
   - 生成 `water_opt_freq_nbo.chk` 和 `water_opt_freq_nbo.log`。

2. `formchk`
   - 将 `water_opt_freq_nbo.chk` 转为 `water_opt_freq_nbo.fchk`。

3. `cubegen`
   - 从 `.fchk` 生成 `water_density.cube`。
   - 从 `.fchk` 生成 `water_homo.cube`。

4. `multiwfn/load_and_quit.inp`
   - 使用 Multiwfn 加载 `.fchk` 并安全退出，用于验证 Multiwfn 批处理链路。

## 安全边界

- 本应用默认不执行 Gaussian、cubegen、Multiwfn。
- runner 只在显式 `--execute-external-tools` 时执行外部程序。
- 所有输入示例为科研工作流 smoke test，不代表真实研究结论。
