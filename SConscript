import os
from building import *

# PanelSupportList is header-only (cvi_panels.h + panels/*.h). No .c is
# compiled here; this SConscript exists only to bridge RT-Thread's Kconfig to
# the upstream panel headers:
#
#   * cvi_panels.h selects the single compiled panel_desc via `#if CONFIG_<STEM>`
#     (the same prefixed macro U-Boot/AliOS use).
#   * RT-Thread's mk_rtconfig (tools/env_utility.py) STRIPS one CONFIG_ prefix,
#     so the Kconfig choice symbol DSI_<STEM>=y lands in rtconfig.h as a bare,
#     value-less `#define DSI_<STEM>` — which cvi_panels.h's `#if CONFIG_DSI_<STEM>`
#     never sees (undefined -> 0 -> silently falls back to the default panel).
#
# So we read which panel the Kconfig choice selected (its bare macro is present
# in the parsed rtconfig.h / BuildOptions) and re-inject it as the prefixed,
# valued define CONFIG_<STEM>=1, plus expose the repo root on the include path.
# CPPPATH/CPPDEFINES passed to DefineGroup are appended to the global Env, so
# the consumer (solutions/*/panel/sample_panel.c) sees both.

cwd = GetCurrentDir()

CPPPATH = [cwd]
CPPDEFINES = []

# Panel header stems == Kconfig choice symbols (upper-cased), minus the
# platform helper header. Mirror gen_panel_config.py's stem derivation.
panel_dir = os.path.join(cwd, "panels")
stems = [
    os.path.splitext(f)[0]
    for f in os.listdir(panel_dir)
    if f.endswith(".h") and f != "panel_platform.h"
]

selected = None
for stem in stems:
    if GetDepend(stem.upper()):
        selected = stem.upper()
        break

# Match cvi_panels.h's #else fallback so the SConscript and the header agree
# when the choice is left at its default / unparsed.
if selected is None:
    selected = "DSI_HX8394_720X1280_NULL_4LANE_60FPS"

CPPDEFINES += ["CONFIG_%s=1" % selected]

group = DefineGroup(
    "PanelSupportList", [], depend=[""], CPPPATH=CPPPATH, CPPDEFINES=CPPDEFINES
)

Return("group")
