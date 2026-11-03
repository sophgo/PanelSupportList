#!/usr/bin/env python3
"""扫描 ../panels/*.h，按头文件命名规范生成屏幕支持列表表格，写入
source/panel_support_list.rst。

命名规范（见 PanelSupportList/skills/dsi-panel-header-addition/SKILL.md）:

    {intf}_{driveric}_{wxh}_{moduleid}_{lanenum}lane_{fps}fps[_suffix].h

其中 LVDS 无 lane 字段、I80 末尾带 _hw/_sw/_hw_mcu 等后缀、BT 与个别
LVDS 屏没有分辨率/帧率（timing 内联在结构体里），统一用 NULL 表示缺省。

表格信息以文件名为主索引；缺省字段显示为 “-”。
"""

import os
import re

SCRIPT_DIR = os.path.normpath(os.path.dirname(__file__))
PANEL_HEADER_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "panels"))
RST_PATH = os.path.join(SCRIPT_DIR, "source", "panel_support_list.rst")

# 接口分组的显示顺序与中文标题
INTF_GROUPS = [
    ("dsi", "MIPI-DSI"),
    ("lvds", "LVDS"),
    ("i80", "I80 / MCU"),
    ("bt656", "BT.656"),
    ("bt1120", "BT.1120"),
]

RES_RE = re.compile(r"^\d+x\d+$")
LANE_RE = re.compile(r"^(\d+)lane$")
FPS_RE = re.compile(r"^(\d+)fps$")


def parse_stem(stem):
    """把头文件 stem 解析成屏幕信息字典。

    命名规范: {intf}_{driveric}_{wxh}_{moduleid}_{lanenum}lane_{fps}fps[_suffix]
    moduleid 固定是 driveric 之后、分辨率之后的那个字段；不确定时为 NULL，
    这里原样保留（包括 NULL），不并入备注。
    """
    tokens = stem.split("_")
    intf = tokens[0]
    intf_key = intf

    driveric = tokens[1] if len(tokens) > 1 else "NULL"

    resolution = None
    moduleid = None
    lane = None
    fps = None
    extras = []

    # moduleid 紧跟在分辨率（或 driveric）之后。先定位分辨率位置，
    # 其后第一个 token 即 moduleid；没有分辨率时取第一个 token 作 moduleid。
    rest = tokens[2:]
    res_idx = None
    for i, tok in enumerate(rest):
        if RES_RE.match(tok) or tok == "multi":
            res_idx = i
            break
    moduleid_idx = (res_idx + 1) if res_idx is not None else 0

    for i, tok in enumerate(rest):
        if RES_RE.match(tok):
            resolution = tok.replace("x", "×")
            continue
        if tok == "multi":
            resolution = "multi"
            continue
        m = LANE_RE.match(tok)
        if m:
            lane = m.group(1)
            continue
        m = FPS_RE.match(tok)
        if m:
            fps = m.group(1)
            continue
        # 分辨率之后（或无分辨率时第一个）token 视为 moduleid，原样保留
        if i == moduleid_idx and moduleid is None:
            moduleid = tok
            continue
        # 其余 NULL 占位符不计入备注
        if tok == "NULL":
            continue
        extras.append(tok)

    return {
        "intf": intf_key,
        "driveric": driveric.upper(),
        "resolution": resolution or "",
        "moduleid": moduleid or "NULL",
        "lane": lane or "",
        "fps": fps or "",
        "extra": " ".join(extras) if extras else "",
        "header": stem + ".h",
    }


def collect_panels():
    panels = []
    for entry in sorted(os.listdir(PANEL_HEADER_DIR)):
        if not entry.endswith(".h") or entry == "panel_platform.h":
            continue
        panels.append(parse_stem(os.path.splitext(entry)[0]))
    return panels


def _cell(prefix, text):
    """生成一个 list-table 单元格行；空值输出空单元格（仅留 bullet）。"""
    text = (text or "").strip()
    return (prefix + " " + text) if text else prefix


def build_table(rows):
    """生成一个 .. list-table:: 块。rows 为 [(序号, IC, 分辨率, 模组ID, lane, fps, 备注), ...]"""
    header = ["序号", "驱动 IC", "分辨率", "模组 ID", "Lane", "帧率(Fps)", "备注"]
    lines = []
    lines.append(".. list-table::")
    lines.append("   :widths: 6 18 16 16 8 12 16")
    lines.append("   :header-rows: 1")
    lines.append("   :class: vmid")
    lines.append("")
    # 表头
    lines.append("   * - " + header[0])
    for h in header[1:]:
        lines.append("     - " + h)
    # 数据行
    for row in rows:
        lines.append(_cell("   * -", str(row[0])))
        for cell in row[1:]:
            lines.append(_cell("     -", str(cell)))
    lines.append("")
    return "\n".join(lines)


HEADER_TMPL = """CVITEK Panel Support List
==================================================

版本信息
--------------------------------------------------

.. list-table::
   :widths: 20 30 50 20
   :header-rows: 1

   * - 文档版本
     - 发布日期
     - 更新记录
     - 作者

   * - |version|
     - |release_date|
     - 初始版本，添加屏幕支持列表
     - |author|

法律声明
--------------------------------------------------
本数据手册包含北京晶视智能科技有限公司（下称“晶视智能”）的保密信息。未经授权，禁止使用或披露本数据手册中包含的信息。如您未经授权披露全部或部分保密信息，导致晶视智能遭受任何损失或损害，您应对因之产生的损失/损害承担责任。

本文件内信息如有更改，恕不另行通知。晶视智能不对使用或依赖本文件所含信息承担任何责任。

本数据手册和本文件所含的所有信息均按“原样”提供，无任何明示、暗示、法定或其他形式的保证。晶视智能特别声明未做任何适销性、非侵权性和特定用途适用性的默示保证，亦对本数据手册所使用、包含或提供的任何第三方的软件不提供任何保证；用户同意仅向该第三方寻求与此相关的任何保证索赔。此外，晶视智能亦不对任何其根据用户规格或符合特定标准或公开讨论而制作的可交付成果承担责任。

Legal Notice
--------------------------------------------------
This data sheet contains information that is confidential to Crystal Vision Intelligence Inc. Unauthorized use or disclosure of the information contained herein is prohibited. You may be held responsible for any loss or damages suffered by Crystal Vision Intelligence Inc. for your unauthorized disclosure hereof, in whole or in part.

Information herein is subject to change without noticed. Crystal Vision Intelligence Inc. does not assume any responsibility for any use of, or reliance on, the information contained herein.

This data sheet and All information contained herein is provided "As is" without warranty of any kind, whether express, implied, statutory, or otherwise. Crystal Vision Intelligence Inc. specifically disclaims all implied warranties of merchantability, Non-infringement, and fitness for a particular purpose. Neither does Crystal Vision Intelligence Inc. provide any warranty whatsoever with respect to the software of any third party which may be used by, incorporated in, or supplied with this data sheet, and used agrees to look only to such third party for any warranty claim relating thereto. Crystal Vision Intelligence Inc. shall also not be responsible for any Crystal Vision Intelligence deliverables made to user's specification or to conform to a particular standard or open forum.

屏幕支持列表
--------------------------------------------------

**说明:** 本列表按显示接口分组列出当前 PanelSupportList 中已支持的屏幕配置。各字段（分辨率、Lane 数、帧率等）来源于屏参头文件命名，以对应屏厂数据手册为准；命名中未体现的字段留空。
"""


def main():
    panels = collect_panels()

    sections = []
    for intf_key, title in INTF_GROUPS:
        group = [p for p in panels if p["intf"] == intf_key]
        if not group:
            continue
        rows = []
        for idx, p in enumerate(group, 1):
            rows.append((
                idx,
                p["driveric"],
                p["resolution"],
                p["moduleid"],
                p["lane"],
                p["fps"],
                p["extra"],
            ))
        section = []
        section.append("")
        section.append(title)
        section.append("~" * 50)
        section.append("")
        section.append(".. raw:: latex")
        section.append("")
        section.append("   \\small")
        section.append("   \\renewcommand{\\arraystretch}{1.2}")
        section.append("   \\vspace{0.25cm}")
        section.append("")
        section.append(build_table(rows))
        sections.append("\n".join(section))

    content = HEADER_TMPL + "\n" + "\n".join(sections) + "\n"

    with open(RST_PATH, "w", encoding="utf-8") as fp:
        fp.write(content)

    total = len(panels)
    print("generated %s (%d panels)" % (RST_PATH, total))


if __name__ == "__main__":
    main()
