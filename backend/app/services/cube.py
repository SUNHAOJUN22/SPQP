from __future__ import annotations

from pathlib import Path
from math import ceil
from typing import Any


MAX_STATS_VALUES = 200_000
MAX_PREVIEW_SAMPLES = 1_800
MAX_SLICE_SIDE = 64


def infer_cube_type(file_name: str) -> str:
    name = file_name.lower()
    if "homo" in name:
        return "HOMO 前线轨道"
    if "lumo" in name:
        return "LUMO 前线轨道"
    if "esp" in name or "potential" in name:
        return "静电势 ESP"
    if "spin" in name:
        return "自旋密度"
    if "diff" in name or "delta" in name:
        return "差分电子密度 Δρ"
    return "总电子密度 ρ(r)"


def parse_cube_metadata(text: str, file_name: str) -> dict[str, Any]:
    lines = text.splitlines()
    if len(lines) < 6:
        raise ValueError("当前文件不是有效 cube 文件。")
    try:
        atom_line = lines[2].split()
        atom_count = abs(int(float(atom_line[0])))
        origin = [float(value) for value in atom_line[1:4]]
        axes = []
        for index in range(3, 6):
            parts = lines[index].split()
            axes.append(
                {
                    "points": int(float(parts[0])),
                    "vector": [float(value) for value in parts[1:4]],
                }
            )
    except (ValueError, IndexError) as exc:
        raise ValueError("当前文件不是有效 cube 文件。") from exc
    atom_rows: list[dict[str, Any]] = []
    for index in range(6, min(6 + atom_count, len(lines))):
        parts = lines[index].split()
        if len(parts) < 5:
            continue
        try:
            atom_rows.append(
                {
                    "atomic_number": int(float(parts[0])),
                    "charge": float(parts[1]),
                    "position_bohr": [float(value) for value in parts[2:5]],
                }
            )
        except ValueError:
            continue

    expected_value_count = axes[0]["points"] * axes[1]["points"] * axes[2]["points"]
    data_stats = _parse_cube_data_stats(lines[6 + atom_count :], expected_value_count)

    return {
        "file_name": Path(file_name).name,
        "cube_type": infer_cube_type(file_name),
        "atom_count": atom_count,
        "grid": {
            "origin_bohr": origin,
            "axes": axes,
            "total_points": axes[0]["points"] * axes[1]["points"] * axes[2]["points"],
        },
        "metadata": {
            "comment_1": lines[0].strip(),
            "comment_2": lines[1].strip(),
            "atoms": atom_rows,
            "data_stats": data_stats,
            "isosurface_metadata": {
                "default_isovalue": 0.02 if "homo" in file_name.lower() or "lumo" in file_name.lower() else 0.001,
                "downsample_policy": "API 只读扫描标量场并返回下采样点；前端完整体数据渲染仍需专用等值面引擎。",
            },
            "warning": "服务器仅读取 cube 文本、元数据和预览标量场，不执行文件。",
        },
    }


def _parse_cube_data_stats(data_lines: list[str], expected_value_count: int) -> dict[str, Any]:
    count = 0
    total = 0.0
    min_value: float | None = None
    max_value: float | None = None
    truncated = False
    for line in data_lines:
        for raw in line.split():
            if count >= MAX_STATS_VALUES:
                truncated = True
                break
            try:
                value = float(raw.replace("D", "E").replace("d", "e"))
            except ValueError:
                continue
            count += 1
            total += value
            min_value = value if min_value is None else min(min_value, value)
            max_value = value if max_value is None else max(max_value, value)
        if truncated:
            break
    return {
        "expected_value_count": expected_value_count,
        "sampled_value_count": count,
        "min": min_value,
        "max": max_value,
        "mean": total / count if count else None,
        "truncated": truncated,
        "value_count_status": "完整" if count >= expected_value_count else "数据缺失",
        "note": "仅用于快速预览 cube 数值范围；真实等值面仍需前端渲染或专用体数据处理。",
    }


def cube_volume_preview(text: str, file_name: str, max_samples: int = MAX_PREVIEW_SAMPLES) -> dict[str, Any]:
    """Return provenance-safe scalar samples for a client-side cube preview."""
    parsed = parse_cube_metadata(text, file_name)
    dimensions = _dimensions(parsed)
    expected = dimensions[0] * dimensions[1] * dimensions[2]
    stride = max(1, ceil(expected / max(1, max_samples)))
    samples: list[dict[str, float | int]] = []
    observed = 0
    positive = 0
    negative = 0

    for index, value in _iter_scalar_values(text.splitlines(), int(parsed["atom_count"] or 0)):
        if index >= expected:
            break
        observed += 1
        positive += int(value > 0)
        negative += int(value < 0)
        if index % stride == 0:
            x, y, z = _linear_to_xyz(index, dimensions)
            samples.append({"x": x, "y": y, "z": z, "value": value})

    return {
        "file_name": parsed["file_name"],
        "cube_type": parsed["cube_type"],
        "grid_dimensions": {"x": dimensions[0], "y": dimensions[1], "z": dimensions[2]},
        "expected_value_count": expected,
        "observed_value_count": observed,
        "sample_stride": stride,
        "sample_count": len(samples),
        "phase_counts": {"positive": positive, "negative": negative, "zero": max(0, observed - positive - negative)},
        "samples": samples,
        "warning": "这是 cube 标量场下采样预览，不是未经验证的真实等值面重建。",
        "provenance": "从已上传 cube 文件只读解析；未执行 cubegen、Gaussian 或 Multiwfn。",
    }


def cube_slice_preview(
    text: str,
    file_name: str,
    axis: str = "z",
    plane_index: int | None = None,
    max_side: int = MAX_SLICE_SIDE,
) -> dict[str, Any]:
    parsed = parse_cube_metadata(text, file_name)
    dimensions = _dimensions(parsed)
    axis_name = axis.lower()
    if axis_name not in {"x", "y", "z"}:
        raise ValueError("剖切轴仅支持 X、Y 或 Z。")
    axis_slot = {"x": 0, "y": 1, "z": 2}[axis_name]
    requested = dimensions[axis_slot] // 2 if plane_index is None else plane_index
    if requested < 0 or requested >= dimensions[axis_slot]:
        raise ValueError("剖切索引超出 cube 网格范围。")

    width_slot, height_slot = _slice_slots(axis_slot)
    width_step = max(1, ceil(dimensions[width_slot] / max(1, max_side)))
    height_step = max(1, ceil(dimensions[height_slot] / max(1, max_side)))
    width_coords = list(range(0, dimensions[width_slot], width_step))
    height_coords = list(range(0, dimensions[height_slot], height_step))
    rows = [[None for _ in width_coords] for _ in height_coords]
    width_index = {coord: index for index, coord in enumerate(width_coords)}
    height_index = {coord: index for index, coord in enumerate(height_coords)}
    expected = dimensions[0] * dimensions[1] * dimensions[2]
    observed = 0

    for index, value in _iter_scalar_values(text.splitlines(), int(parsed["atom_count"] or 0)):
        if index >= expected:
            break
        observed += 1
        xyz = _linear_to_xyz(index, dimensions)
        if xyz[axis_slot] != requested:
            continue
        width_coord = xyz[width_slot]
        height_coord = xyz[height_slot]
        if width_coord in width_index and height_coord in height_index:
            rows[height_index[height_coord]][width_index[width_coord]] = value

    numeric = [value for row in rows for value in row if value is not None]
    return {
        "file_name": parsed["file_name"],
        "cube_type": parsed["cube_type"],
        "axis": axis_name,
        "plane_index": requested,
        "grid_dimensions": {"x": dimensions[0], "y": dimensions[1], "z": dimensions[2]},
        "shape": {"width": len(width_coords), "height": len(height_coords)},
        "steps": {"width": width_step, "height": height_step},
        "values": rows,
        "min": min(numeric) if numeric else None,
        "max": max(numeric) if numeric else None,
        "expected_value_count": expected,
        "observed_value_count": observed,
        "warning": "剖切图来自已上传 cube 标量场下采样；若数据缺失，空格保留为 null。",
        "provenance": "从已上传 cube 文件只读解析；不执行外部化学软件。",
    }


def cube_difference_preview(text_a: str, file_a: str, text_b: str, file_b: str, max_samples: int = MAX_PREVIEW_SAMPLES) -> dict[str, Any]:
    parsed_a = parse_cube_metadata(text_a, file_a)
    parsed_b = parse_cube_metadata(text_b, file_b)
    dimensions_a = _dimensions(parsed_a)
    dimensions_b = _dimensions(parsed_b)
    if dimensions_a != dimensions_b:
        raise ValueError("两个 cube 网格维度不一致，无法计算差分电子密度。")
    expected = dimensions_a[0] * dimensions_a[1] * dimensions_a[2]
    stride = max(1, ceil(expected / max(1, max_samples)))
    values_b = {index: value for index, value in _iter_scalar_values(text_b.splitlines(), int(parsed_b["atom_count"] or 0))}
    samples: list[dict[str, float | int]] = []
    count = 0
    min_delta: float | None = None
    max_delta: float | None = None
    total = 0.0
    positive = 0
    negative = 0
    for index, value_a in _iter_scalar_values(text_a.splitlines(), int(parsed_a["atom_count"] or 0)):
        if index >= expected or index not in values_b:
            break
        delta = value_a - values_b[index]
        count += 1
        total += delta
        min_delta = delta if min_delta is None else min(min_delta, delta)
        max_delta = delta if max_delta is None else max(max_delta, delta)
        positive += int(delta > 0)
        negative += int(delta < 0)
        if index % stride == 0:
            x, y, z = _linear_to_xyz(index, dimensions_a)
            samples.append({"x": x, "y": y, "z": z, "delta": delta})
    return {
        "formula": "Δρ(r) = ρ_A(r) - ρ_B(r)",
        "file_a": parsed_a["file_name"],
        "file_b": parsed_b["file_name"],
        "grid_dimensions": {"x": dimensions_a[0], "y": dimensions_a[1], "z": dimensions_a[2]},
        "expected_value_count": expected,
        "observed_value_count": count,
        "sample_stride": stride,
        "sample_count": len(samples),
        "min_delta": min_delta,
        "max_delta": max_delta,
        "mean_delta": total / count if count else None,
        "phase_counts": {"positive": positive, "negative": negative, "zero": max(0, count - positive - negative)},
        "samples": samples,
        "warning": "差分电子密度来自两个已上传 cube 的逐点只读相减；网格、相位和片段定义必须由用户核验。",
        "provenance": "服务器不执行 cubegen 或 Multiwfn，仅对上传 cube 文本做下采样差分预览。",
    }


def _dimensions(parsed: dict[str, Any]) -> tuple[int, int, int]:
    axes = parsed["grid"]["axes"]
    dimensions = tuple(abs(int(axis["points"])) for axis in axes)
    if any(dimension <= 0 for dimension in dimensions):
        raise ValueError("cube 网格维度无效。")
    return dimensions  # type: ignore[return-value]


def _iter_scalar_values(lines: list[str], atom_count: int):
    index = 0
    for line in lines[6 + atom_count :]:
        for raw in line.split():
            try:
                value = float(raw.replace("D", "E").replace("d", "e"))
            except ValueError:
                continue
            yield index, value
            index += 1


def _linear_to_xyz(index: int, dimensions: tuple[int, int, int]) -> tuple[int, int, int]:
    _, ny, nz = dimensions
    x = index // (ny * nz)
    y = (index // nz) % ny
    z = index % nz
    return x, y, z


def _slice_slots(axis_slot: int) -> tuple[int, int]:
    if axis_slot == 0:
        return 1, 2
    if axis_slot == 1:
        return 0, 2
    return 0, 1
