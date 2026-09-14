from pathlib import Path

v2 = Path("scripts/apply_upstream_socks5_v2.py")
s = v2.read_text(encoding="utf-8")
start = s.find("    pattern = r'")
end = s.find("    s = once(s, '''func dnsOut()", start)
if start < 0 or end < 0:
    raise SystemExit("cannot locate catch-all section")
lines = [
    "    old_rule = '\\t\\trule{\\n\\t\\t\\tRuleTag:     ruleTagCatchAll,\\n\\t\\t\\tNetwork:     \"tcp,udp\",\\n\\t\\t\\tOutboundTag: TagProxy,\\n\\t\\t})'",
    "    new_rule = '\\t\\trule{\\n\\t\\t\\tRuleTag:     ruleTagCatchAll,\\n\\t\\t\\tNetwork:     \"tcp,udp\",\\n\\t\\t\\tOutboundTag: func() string {\\n\\t\\t\\t\\tif o.Upstream.Enabled {\\n\\t\\t\\t\\t\\treturn TagUpstream\\n\\t\\t\\t\\t}\\n\\t\\t\\t\\treturn TagProxy\\n\\t\\t\\t}(),\\n\\t\\t})'",
    "    s = once(s, old_rule, new_rule, \"catch-all rule\")",
]
s = s[:start] + "\\n".join(lines) + "\\n" + s[end:]
exec(compile(s, str(v2), "exec"), globals(), globals())
