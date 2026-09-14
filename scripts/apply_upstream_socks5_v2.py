from pathlib import Path
import re


def read(path):
    return Path(path).read_text(encoding="utf-8")


def write(path, text):
    Path(path).write_text(text, encoding="utf-8")


def once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"missing anchor: {label}")
    return text.replace(old, new, 1)


# xcfg/options.go
p = "internal/xcfg/options.go"
s = read(p)
if "type UpstreamSOCKS5 struct" not in s:
    s = once(s, 'import (\n\t"net/netip"\n', 'import (\n\t"net/netip"\n\t"strings"\n', "options imports")
    s = once(s, '\tLocalDNS LocalDNS\n}', '''\tLocalDNS LocalDNS
\tUpstream UpstreamSOCKS5
}

type UpstreamSOCKS5 struct {
\tEnabled  bool
\tHost     string
\tPort     uint16
\tUsername string
\tPassword string
}''', "options struct")
    s = once(s, '\tTagDNSOut = "dns-out"\n', '\tTagDNSOut = "dns-out"\n\n\tTagUpstream = "upstream-socks5"\n', "upstream tag")
    s = once(s, '\tif o.LocalDNS.Port == 0 {\n\t\to.LocalDNS.Port = DefaultLocalDNSPort\n\t}\n\treturn o\n}', '''\tif o.LocalDNS.Port == 0 {
\t\to.LocalDNS.Port = DefaultLocalDNSPort
\t}
\tif o.Upstream.Enabled {
\t\to.Upstream.Host = strings.TrimSpace(o.Upstream.Host)
\t}
\treturn o
}''', "normalise")
    s = once(s, 'func (o Options) check() error {\n', '''func (o Options) check() error {
\tif o.Upstream.Enabled {
\t\tif o.Upstream.Host == "" || strings.ContainsAny(o.Upstream.Host, " \\t\\r\\n") {
\t\t\treturn ErrUpstreamAddress
\t\t}
\t\tif o.Upstream.Port == 0 {
\t\t\treturn ErrUpstreamPort
\t\t}
\t}
''', "options validation")
    write(p, s)

# xcfg/errors.go
p = "internal/xcfg/errors.go"
s = read(p)
if "ErrUpstreamAddress" not in s:
    s = once(s, "var (\n", '''var (
\tErrUpstreamAddress = errors.New("the upstream SOCKS5 address is invalid")
\tErrUpstreamPort = errors.New("the upstream SOCKS5 port is invalid")
''', "upstream errors")
    write(p, s)

# xcfg/build.go
p = "internal/xcfg/build.go"
s = read(p)
if "type socksOutbound struct" not in s:
    s = once(s, '''type dnsOutbound struct {
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
    s = once(s, '\toutbounds = append(outbounds, proxy)\n\toutbounds = append(outbounds, direct(), blackhole())', '''\toutbounds = append(outbounds, proxy)
\tif o.Upstream.Enabled {
\t\toutbounds = append(outbounds, upstreamSOCKS(o.Upstream))
\t}
\toutbounds = append(outbounds, direct(), blackhole())''', "outbound list")
    pattern = r'(\t\tRuleTag:\s+ruleTagCatchAll,\n\t\tNetwork:\s+"tcp,udp",\n)\t\tOutboundTag:\s+TagProxy,\n\t\})'
    repl = r'''\1\t\tOutboundTag: func() string {
\t\t\tif o.Upstream.Enabled {
\t\t\t\treturn TagUpstream
\t\t\t}
\t\t\treturn TagProxy
\t\t}(),
\t})'''
    s, n = re.subn(pattern, repl, s, count=1)
    if n != 1:
        raise SystemExit("missing anchor: catch-all rule")
    s = once(s, '''func dnsOut() dnsOutbound {
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
    write(p, s)

# privsvc/plans.go
p = "internal/privsvc/plans.go"
s = read(p)
if "o.Upstream = xcfg.UpstreamSOCKS5" not in s:
    s = once(s, '\to.DNS.Intercept = true\n', '''\to.DNS.Intercept = true
\to.Upstream = xcfg.UpstreamSOCKS5{
\t\tEnabled:  req.Upstream.Enabled,
\t\tHost:     req.Upstream.Host,
\t\tPort:     req.Upstream.Port,
\t\tUsername: req.Upstream.Username,
\t\tPassword: req.Upstream.Password,
\t}
''', "engine upstream")
    write(p, s)

print("core upstream SOCKS5 patch applied")
