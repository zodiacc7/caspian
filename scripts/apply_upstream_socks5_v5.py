from pathlib import Path


def patch(path, old, new, label):
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    if old not in s:
        raise SystemExit(f"missing anchor: {label}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")


# Options and validation.
p = "internal/xcfg/options.go"
s = Path(p).read_text(encoding="utf-8")
if "type UpstreamSOCKS5 struct" not in s:
    patch(p, 'import (\n\t"net/netip"\n', 'import (\n\t"net/netip"\n\t"strings"\n', "options imports")
    patch(p, '\tLocalDNS LocalDNS\n}', '''\tLocalDNS LocalDNS
\tUpstream UpstreamSOCKS5
}

type UpstreamSOCKS5 struct {
\tEnabled  bool
\tHost     string
\tPort     uint16
\tUsername string
\tPassword string
}''', "options struct")
    patch(p, '\tTagDNSOut = "dns-out"\n', '\tTagDNSOut = "dns-out"\n\n\tTagUpstream = "upstream-socks5"\n', "upstream tag")
    patch(p, '\tif o.LocalDNS.Port == 0 {\n\t\to.LocalDNS.Port = DefaultLocalDNSPort\n\t}\n\treturn o\n}', '''\tif o.LocalDNS.Port == 0 {
\t\to.LocalDNS.Port = DefaultLocalDNSPort
\t}
\tif o.Upstream.Enabled {
\t\to.Upstream.Host = strings.TrimSpace(o.Upstream.Host)
\t}
\treturn o
}''', "normalise")
    patch(p, 'func (o Options) check() error {\n', '''func (o Options) check() error {
\tif o.Upstream.Enabled {
\t\tif o.Upstream.Host == "" || strings.ContainsAny(o.Upstream.Host, " \\t\\r\\n") {
\t\t\treturn ErrUpstreamAddress
\t\t}
\t\tif o.Upstream.Port == 0 {
\t\t\treturn ErrUpstreamPort
\t\t}
\t}
''', "validation")

# Errors.
p = "internal/xcfg/errors.go"
s = Path(p).read_text(encoding="utf-8")
if "ErrUpstreamAddress" not in s:
    patch(p, "var (\n", '''var (
\tErrUpstreamAddress = errors.New("the upstream SOCKS5 address is invalid")
\tErrUpstreamPort = errors.New("the upstream SOCKS5 port is invalid")
''', "errors")

# Build support.
p = "internal/xcfg/build.go"
s = Path(p).read_text(encoding="utf-8")
if "type socksOutbound struct" not in s:
    patch(p, '''type dnsOutbound struct {
\tTag      string         `json:"tag"`
\tProtocol string         `json:"protocol"`
\tSettings dnsOutSettings `json:"settings"`
}
''', '''type dnsOutbound struct {
\tTag      string         `json:"tag"`
\tProtocol string         `json:"protocol"`
\tSettings dnsOutSettings `json:"settings"`
}

type socksOutbound struct {
\tTag      string                `json:"tag"`
\tProtocol string                `json:"protocol"`
\tSettings socksOutboundSettings `json:"settings"`
}

type socksOutboundSettings struct {
\tServers []socksOutboundServer `json:"servers"`
}

type socksOutboundServer struct {
\tAddress string              `json:"address"`
\tPort    uint16              `json:"port"`
\tUsers   []socksOutboundUser `json:"users,omitempty"`
}

type socksOutboundUser struct {
\tUser string `json:"user"`
\tPass string `json:"pass"`
}
''', "build types")
    patch(p, '\toutbounds = append(outbounds, proxy)\n\toutbounds = append(outbounds, direct(), blackhole())', '''\toutbounds = append(outbounds, proxy)
\tif o.Upstream.Enabled {
\t\toutbounds = append(outbounds, upstreamSOCKS(o.Upstream))
\t}
\toutbounds = append(outbounds, direct(), blackhole())''', "outbounds")
    patch(p, '''\trules = append(rules, rule{
\t\tRuleTag:     ruleTagCatchAll,
\t\tNetwork:     "tcp,udp",
\t\tOutboundTag: TagProxy,
\t})''', '''\trules = append(rules, rule{
\t\tRuleTag:     ruleTagCatchAll,
\t\tNetwork:     "tcp,udp",
\t\tOutboundTag: func() string {
\t\t\tif o.Upstream.Enabled {
\t\t\t\treturn TagUpstream
\t\t\t}
\t\t\treturn TagProxy
\t\t}(),
\t})''', "catch-all")
    patch(p, '''func dnsOut() dnsOutbound {
\treturn dnsOutbound{
\t\tTag:      TagDNSOut,
\t\tProtocol: "dns",
\t\tSettings: dnsOutSettings{NonIPQuery: "reject"},
\t}
}
''', '''func dnsOut() dnsOutbound {
\treturn dnsOutbound{
\t\tTag:      TagDNSOut,
\t\tProtocol: "dns",
\t\tSettings: dnsOutSettings{NonIPQuery: "reject"},
\t}
}

func upstreamSOCKS(u UpstreamSOCKS5) socksOutbound {
\ts := socksOutboundServer{Address: u.Host, Port: u.Port}
\tif u.Username != "" || u.Password != "" {
\t\ts.Users = []socksOutboundUser{{User: u.Username, Pass: u.Password}}
\t}
\treturn socksOutbound{
\t\tTag: TagUpstream,
\t\tProtocol: "socks",
\t\tSettings: socksOutboundSettings{Servers: []socksOutboundServer{s}},
\t}
}
''', "upstream outbound")

# Pass the panel request through to xcfg.
p = "internal/privsvc/plans.go"
s = Path(p).read_text(encoding="utf-8")
if "o.Upstream = xcfg.UpstreamSOCKS5" not in s:
    patch(p, '\to.DNS.Intercept = true\n', '''\to.DNS.Intercept = true
\to.Upstream = xcfg.UpstreamSOCKS5{
\t\tEnabled:  req.Upstream.Enabled,
\t\tHost:     req.Upstream.Host,
\t\tPort:     req.Upstream.Port,
\t\tUsername: req.Upstream.Username,
\t\tPassword: req.Upstream.Password,
\t}
''', "engine request")

print("core upstream SOCKS5 patch applied")
