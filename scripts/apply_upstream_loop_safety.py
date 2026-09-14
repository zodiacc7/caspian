from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    s = p.read_text()
    if old not in s:
        raise SystemExit(f"marker not found in {path}: {old[:120]!r}")
    p.write_text(s.replace(old, new, 1))


# Keep the upstream SOCKS endpoint itself out of the catch-all/upstream route.
# Literal IPs are matched as IP rules; hostnames are matched as exact domains.
replace_once(
    "internal/xcfg/build.go",
    '"encoding/json"\n',
    '"encoding/json"\n\t"net/netip"\n',
)
replace_once(
    "internal/xcfg/build.go",
    '\tRuleTag     string   `json:"ruleTag"`\n\tInboundTag  []string `json:"inboundTag,omitempty"`\n\tIP          []string `json:"ip,omitempty"`\n',
    '\tRuleTag     string   `json:"ruleTag"`\n\tInboundTag  []string `json:"inboundTag,omitempty"`\n\tDomain      []string `json:"domain,omitempty"`\n\tIP          []string `json:"ip,omitempty"`\n',
)
replace_once(
    "internal/xcfg/build.go",
    '\trules = append(rules, rule{\n\t\tRuleTag: ruleTagCatchAll,\n',
    '''\tif o.Upstream.Enabled {\n\t\tr := rule{RuleTag: ruleTagUpstreamDirect, OutboundTag: TagDirect}\n\t\tif addr, err := netip.ParseAddr(o.Upstream.Host); err == nil {\n\t\t\tr.IP = []string{addr.String()}\n\t\t} else {\n\t\t\thost := o.Upstream.Host\n\t\t\tif host != "" && host[len(host)-1] == '.' {\n\t\t\t\thost = host[:len(host)-1]\n\t\t\t}\n\t\t\tr.Domain = []string{"full:" + host}\n\t\t}\n\t\trules = append(rules, r)\n\t}\n\trules = append(rules, rule{\n\t\tRuleTag: ruleTagCatchAll,\n''',
)
replace_once(
    "internal/xcfg/options.go",
    '\truleTagDNS       = "client-dns-intercept"\n\truleTagCatchAll  = "everything-else"\n',
    '\truleTagDNS          = "client-dns-intercept"\n\truleTagUpstreamDirect = "upstream-socks5-direct"\n\truleTagCatchAll       = "everything-else"\n',
)

# Extend structural test decoding and option coverage.
replace_once(
    "internal/xcfg/build_test.go",
    '\t\t\t\tRuleTag     string   `json:"ruleTag"`\n\t\t\t\tInboundTag  []string `json:"inboundTag"`\n\t\t\t\tIP          []string `json:"ip"`\n',
    '\t\t\t\tRuleTag     string   `json:"ruleTag"`\n\t\t\t\tInboundTag  []string `json:"inboundTag"`\n\t\t\t\tDomain      []string `json:"domain"`\n\t\t\t\tIP          []string `json:"ip"`\n',
)
replace_once(
    "internal/xcfg/build_test.go",
    '\t\t{\n\t\t\t{"log-debug", func(o *Options) { o.LogLevel = LogDebug }},\n',
    '''\t\t{\n\t\t\t{"upstream-off", func(o *Options) {}},\n\t\t\t{"upstream-ip", func(o *Options) {\n\t\t\t\to.Upstream.Enabled = true\n\t\t\t\to.Upstream.Host = "127.0.0.1"\n\t\t\t\to.Upstream.Port = 3067\n\t\t\t}},\n\t\t\t{"upstream-lan-auth", func(o *Options) {\n\t\t\t\to.Upstream.Enabled = true\n\t\t\t\to.Upstream.Host = "192.168.1.100"\n\t\t\t\to.Upstream.Port = 4067\n\t\t\t\to.Upstream.Username = "user"\n\t\t\t\to.Upstream.Password = "pass"\n\t\t\t}},\n\t\t\t{"upstream-hostname", func(o *Options) {\n\t\t\t\to.Upstream.Enabled = true\n\t\t\t\to.Upstream.Host = "proxy.example.test"\n\t\t\t\to.Upstream.Port = 1080\n\t\t\t}},\n\t\t},\n\t\t{\n\t\t\t{"log-debug", func(o *Options) { o.LogLevel = LogDebug }},\n''',
)
replace_once(
    "internal/xcfg/build_test.go",
    '\t\t"LocalDNS.Enabled", "LocalDNS.Listen", "LocalDNS.Port",\n',
    '\t\t"LocalDNS.Enabled", "LocalDNS.Listen", "LocalDNS.Port",\n\t\t"Upstream.Enabled", "Upstream.Host", "Upstream.Port", "Upstream.Username", "Upstream.Password",\n',
)
replace_once(
    "internal/xcfg/build_test.go",
    '\tcase "LocalDNS.Port":\n\t\treturn fmt.Sprint(o.LocalDNS.Port)\n',
    '''\tcase "LocalDNS.Port":\n\t\treturn fmt.Sprint(o.LocalDNS.Port)\n\tcase "Upstream.Enabled":\n\t\treturn fmt.Sprint(o.Upstream.Enabled)\n\tcase "Upstream.Host":\n\t\treturn o.Upstream.Host\n\tcase "Upstream.Port":\n\t\treturn fmt.Sprint(o.Upstream.Port)\n\tcase "Upstream.Username":\n\t\treturn o.Upstream.Username\n\tcase "Upstream.Password":\n\t\treturn o.Upstream.Password\n''',
)

# Add explicit loop-safety property tests before the named-properties section.
marker = '// ---------------------------------------------------------------------------\n// The named properties.\n// ---------------------------------------------------------------------------\n'
new_tests = r'''// TestUpstreamEndpointBypassesUpstreamRoute proves the endpoint itself is
// routed direct. Otherwise a TUN route can feed the connection to the same
// upstream SOCKS outbound it is trying to reach, creating a recursion loop.
func TestUpstreamEndpointBypassesUpstreamRoute(t *testing.T) {
	l := mustParse(t, fixtures()[0].raw())
	cases := []struct {
		name string
		host string
		wantIP string
		wantDomain string
	}{
		{name: "loopback-v4", host: "127.0.0.1", wantIP: "127.0.0.1"},
		{name: "lan-v4", host: "192.168.1.100", wantIP: "192.168.1.100"},
		{name: "loopback-v6", host: "::1", wantIP: "::1"},
		{name: "hostname", host: "proxy.example.test", wantDomain: "full:proxy.example.test"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			o := Defaults()
			o.Link = l
			o.Upstream = UpstreamSOCKS5{Enabled: true, Host: tc.host, Port: 3067}
			raw, err := Build(o)
			if err != nil { t.Fatal(err) }
			p := decode(t, raw)
			var got *struct {
				Domain []string
				IP []string
				OutboundTag string
			}
			for i := range p.Routing.Rules {
				r := &p.Routing.Rules[i]
				if r.RuleTag == ruleTagUpstreamDirect {
					got = &struct { Domain []string; IP []string; OutboundTag string }{r.Domain, r.IP, r.OutboundTag}
					break
				}
			}
			if got == nil { t.Fatalf("missing %q rule", ruleTagUpstreamDirect) }
			if got.OutboundTag != TagDirect { t.Fatalf("endpoint outbound = %q, want %q", got.OutboundTag, TagDirect) }
			if tc.wantIP != "" && (len(got.IP) != 1 || got.IP[0] != tc.wantIP) { t.Fatalf("endpoint IP rule = %#v, want [%q]", got.IP, tc.wantIP) }
			if tc.wantDomain != "" && (len(got.Domain) != 1 || got.Domain[0] != tc.wantDomain) { t.Fatalf("endpoint domain rule = %#v, want [%q]", got.Domain, tc.wantDomain) }
		})
	}
}

func TestUpstreamCatchAllChangesOnlyWhenEnabled(t *testing.T) {
	l := mustParse(t, fixtures()[0].raw())
	for _, enabled := range []bool{false, true} {
		o := Defaults(); o.Link = l; o.Upstream.Enabled = enabled; o.Upstream.Host = "127.0.0.1"; o.Upstream.Port = 3067
		raw, err := Build(o); if err != nil { t.Fatal(err) }
		p := decode(t, raw)
		var got string
		for _, r := range p.Routing.Rules { if r.RuleTag == ruleTagCatchAll { got = r.OutboundTag } }
		want := TagProxy; if enabled { want = TagUpstream }
		if got != want { t.Fatalf("enabled=%v catch-all = %q, want %q", enabled, got, want) }
	}
}

'''
replace_once("internal/xcfg/build_test.go", marker, new_tests + marker)
print("upstream loop-safety patch applied")
