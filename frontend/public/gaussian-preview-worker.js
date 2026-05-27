self.onmessage = (event) => {
  const text = String(event.data?.text ?? "");
  const fileName = String(event.data?.fileName ?? "本地预览.log");
  const floatPattern = "[-+]?(?:\\d+\\.\\d*|\\.\\d+|\\d+)(?:[DEde][-+]?\\d+)?";
  const toNumber = (value) => {
    if (!value) return null;
    const parsed = Number(String(value).replace(/[Dd]/g, "E"));
    return Number.isFinite(parsed) ? parsed : null;
  };
  const lastMatch = (pattern, flags = "g") => {
    const regex = new RegExp(pattern, flags);
    const matches = [...text.matchAll(regex)];
    if (!matches.length) return null;
    return toNumber(matches[matches.length - 1][1]);
  };
  const allFrequencies = [];
  for (const line of text.split(/\r?\n/)) {
    if (line.includes("Frequencies --")) {
      const values = line.split("--")[1]?.match(new RegExp(floatPattern, "g")) ?? [];
      allFrequencies.push(...values.map(toNumber).filter((value) => value !== null));
    }
  }
  const occ = [];
  const virt = [];
  for (const line of text.split(/\r?\n/)) {
    const lower = line.toLowerCase();
    if (lower.includes("occ. eigenvalues --")) {
      occ.push(...(line.split("--")[1]?.match(new RegExp(floatPattern, "g")) ?? []).map(toNumber).filter((value) => value !== null));
    }
    if (lower.includes("virt. eigenvalues --")) {
      virt.push(...(line.split("--")[1]?.match(new RegExp(floatPattern, "g")) ?? []).map(toNumber).filter((value) => value !== null));
    }
  }
  const homo = occ.length ? occ[occ.length - 1] : null;
  const lumo = virt.length ? virt[0] : null;
  const gapEv = homo !== null && lumo !== null ? (lumo - homo) * 27.211386245988 : null;
  const normalTermination = text.includes("Normal termination of Gaussian");
  const scf = lastMatch(`SCF Done:\\s+E\\([^)]+\\)\\s+=\\s+(${floatPattern})`);
  const gibbs = lastMatch(`Sum of electronic and thermal Free Energies=\\s+(${floatPattern})`);
  const counterpoise = lastMatch(`Counterpoise corrected energy\\s*=\\s*(${floatPattern})`, "gi");
  const nboLikely = text.includes("Second Order Perturbation Theory Analysis");
  const wibergLikely = /Wiberg bond index/i.test(text);
  const npaLikely = text.includes("Summary of Natural Population Analysis");
  const warnings = [];
  if (text && !normalTermination) warnings.push("未检测到 Gaussian 正常终止标记。");
  if (text && gibbs === null) warnings.push("当前文件中未找到吉布斯自由能。");
  if (text && !nboLikely) warnings.push("当前文件中未找到 NBO 二阶微扰分析结果。");
  const coreCount = [scf, gibbs, allFrequencies.length ? allFrequencies.length : null, homo, lumo].filter((value) => value !== null).length;
  const quality = !text ? "待计算" : normalTermination && coreCount >= 4 ? "complete" : coreCount > 0 || normalTermination ? "partial" : "failed";
  self.postMessage({
    file: fileName,
    normal_termination: normalTermination,
    scf_hartree: scf,
    gibbs_hartree: gibbs,
    n_imag: allFrequencies.length ? allFrequencies.filter((value) => value < 0).length : null,
    lowest_freq_cm_1: allFrequencies.length ? Math.min(...allFrequencies) : null,
    homo_hartree: homo,
    lumo_hartree: lumo,
    gap_ev: gapEv,
    counterpoise_corrected_energy_hartree: counterpoise,
    npa_detected: npaLikely,
    wiberg_detected: wibergLikely,
    nbo_e2_detected: nboLikely,
    quality,
    chinese_warnings: warnings,
    provenance: "Web Worker 本地预览；正式结果以 /api/parse/gaussian-log 只读解析为准。"
  });
};
