from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    if old not in s:
        raise SystemExit(f"missing anchor: {path}: {old[:120]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")


def patch_options():
    p = "internal/xcfg/options.go"
    s = Path(p).read_text(encoding="utf-8")
    if "type UpstreamSOCKS5 struct" not in s:
        replace_once(p, 'import (\n\t"net/netip"\n', 'import (\n\t"net/netip"\n\t"strings"\n')
        replace_once(p, '\tLocalDNS LocalDNS\n}', '''\tLocalDNS LocalDNS
\t// Upstream is an optional front SOCKS5 proxy, separate from the local SOCKS inbound.
\tUpstream UpstreamSOCKS5
}

type UpstreamSOCKS5 struct {
\tEnabled  bool
\tHost     string
\tPort     uint16
\tUsername string
\tPassword string
}''')
        replace_once(p, '\tTagDNSOut = "dns-out"\n', '\tTagDNSOut = "dns-out"\n\n\tTagUpstream = "upstream-socks5"\n')
        replace_once(p, '\tif o.LocalDNS.Port == 0 {\n\t\to.LocalDNS.Port = DefaultLocalDNSPort\n\t}\n\treturn o\n}', '''\tif o.LocalDNS.Port == 0 {
\t\to.LocalDNS.Port = DefaultLocalDNSPort
\t}
\tif o.Upstream.Enabled {
\t\to.Upstream.Host = strings.TrimSpace(o.Upstream.Host)
\t}
\treturn o
}''')
        replace_once(p, 'func (o Options) check() error {\n', '''func (o Options) check() error {
\tif o.Upstream.Enabled {
\t\tif o.Upstream.Host == "" || strings.ContainsAny(o.Upstream.Host, " \\t\\r\\n") {
\t\t\treturn ErrUpstreamAddress
\t\t}
\t\tif o.Upstream.Port == 0 {
\t\t\treturn ErrUpstreamPort
\t\t}
\t}
''')


def patch_errors():
    p = "internal/xcfg/errors.go"
    s = Path(p).read_text(encoding="utf-8")
    if "ErrUpstreamAddress" not in s:
        replace_once(p, 'var (\n', '''var (
\tErrUpstreamAddress = errors.New("the upstream SOCKS5 address is invalid")
\tErrUpstreamPort = errors.New("the upstream SOCKS5 port is invalid")
''')


def patch_build():
    p = "internal/xcfg/build.go"
    s = Path(p).read_text(encoding="utf-8")
    if "type socksOutbound struct" not in s:
        replace_once(p, '''type dnsOutbound struct {
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
''')
        replace_once(p, '\toutbounds = append(outbounds, proxy)\n\toutbounds = append(outbounds, direct(), blackhole())', '''\toutbounds = append(outbounds, proxy)
\tif o.Upstream.Enabled {
\t\toutbounds = append(outbounds, upstreamSOCKS(o.Upstream))
\t}
\toutbounds = append(outbounds, direct(), blackhole())''')
        replace_once(p, '''\t\trule{
\t\t\tRuleTag:     ruleTagCatchAll,
\t\t\tNetwork:     "tcp,udp",
\t\t\tOutboundTag: TagProxy,
\t\t})''', '''\t\trule{
\t\t\tRuleTag:     ruleTagCatchAll,
\t\t\tNetwork:     "tcp,udp",
\t\t\tOutboundTag: func() string {
\t\t\t\tif o.Upstream.Enabled {
\t\t\t\t\treturn TagUpstream
\t\t\t\t}
\t\t\t\treturn TagProxy
\t\t\t}(),
\t\t})''')
        replace_once(p, '''func dnsOut() dnsOutbound {
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
''')


def patch_plans():
    p = "internal/privsvc/plans.go"
    s = Path(p).read_text(encoding="utf-8")
    if "o.Upstream = xcfg.UpstreamSOCKS5" not in s:
        replace_once(p, '\to.DNS.Intercept = true\n', '''\to.DNS.Intercept = true
\to.Upstream = xcfg.UpstreamSOCKS5{
\t\tEnabled:  req.Upstream.Enabled,
\t\tHost:     req.Upstream.Host,
\t\tPort:     req.Upstream.Port,
\t\tUsername: req.Upstream.Username,
\t\tPassword: req.Upstream.Password,
\t}
''')


patch_options()
patch_errors()
patch_build()
patch_plans()
print("upstream SOCKS5 core patch applied")
