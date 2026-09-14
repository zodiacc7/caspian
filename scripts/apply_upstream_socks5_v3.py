from pathlib import Path

v2 = Path("scripts/apply_upstream_socks5_v2.py")
s = v2.read_text(encoding="utf-8")
old = '''    pattern = r'(\\t\\tRuleTag:\\s+ruleTagCatchAll,\\n\\t\\tNetwork:\\s+"tcp,udp",\\n)\\t\\tOutboundTag:\\s+TagProxy,\\n\\t\\\\})'
    repl = r'''\1\\t\\tOutboundTag: func() string {\n\\t\\t\\tif o.Upstream.Enabled {\n\\t\\t\\t\\treturn TagUpstream\n\\t\\t\\t}\n\\t\\t\\treturn TagProxy\n\\t\\t}(),\n\\t\\})'''
    s, n = re.subn(pattern, repl, s, count=1)
    if n != 1:
        raise SystemExit("missing anchor: catch-all rule")
'''
# The embedded source is easier to repair by replacing the whole regex section.
start = s.find('    pattern = r\'')
end = s.find('    s = once(s, \'\'\'func dnsOut()', start)
if start < 0 or end < 0:
    raise SystemExit("cannot locate catch-all patch section in v2")
replacement = '''    old_rule = ''' + "'''" + '''\t\trule{\n\t\t\tRuleTag:     ruleTagCatchAll,\n\t\t\tNetwork:     "tcp,udp",\n\t\t\tOutboundTag: TagProxy,\n\t\t})''' + "'''" + '''
    new_rule = ''' + "'''" + '''\t\trule{\n\t\t\tRuleTag:     ruleTagCatchAll,\n\t\t\tNetwork:     "tcp,udp",\n\t\t\tOutboundTag: func() string {\n\t\t\t\tif o.Upstream.Enabled {\n\t\t\t\t\treturn TagUpstream\n\t\t\t\t}\n\t\t\t\treturn TagProxy\n\t\t\t}(),\n\t\t})''' + "'''" + '''
    s = once(s, old_rule, new_rule, "catch-all rule")
'''
s = s[:start] + replacement + s[end:]
exec(compile(s, str(v2), "exec"), globals(), globals())
