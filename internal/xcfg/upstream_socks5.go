// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Iman Samizadeh

package xcfg

import (
	"encoding/json"
	"errors"
	"strings"
)

// TagUpstreamSOCKS5 is the optional front-proxy outbound. It is not a route
// target for client traffic; TagProxy remains the actual tunnel outbound.
const TagUpstreamSOCKS5 = "upstream-socks5"

// UpstreamSOCKS5 describes an optional SOCKS5 front proxy. It is used only to
// establish the connection to the configured tunnel server; client traffic
// still routes to TagProxy.
type UpstreamSOCKS5 struct {
	Enabled  bool
	Address  string
	Port     uint16
	Username string
	Password string
}

func (o UpstreamSOCKS5) check() error {
	if !o.Enabled {
		return nil
	}
	if strings.TrimSpace(o.Address) == "" || strings.TrimSpace(o.Address) != o.Address {
		return errors.New("upstream SOCKS5 address is invalid")
	}
	for _, r := range o.Address {
		if r == 0 || r == ' ' || r == '\t' || r == '\r' || r == '\n' {
			return errors.New("upstream SOCKS5 address is invalid")
		}
	}
	if o.Port == 0 {
		return errors.New("upstream SOCKS5 port is invalid")
	}
	if (o.Username == "") != (o.Password == "") {
		return errors.New("upstream SOCKS5 credentials are incomplete")
	}
	return nil
}

type upstreamSOCKS5Outbound struct {
	Tag      string                 `json:"tag"`
	Protocol string                 `json:"protocol"`
	Settings upstreamSOCKS5Settings `json:"settings"`
}

type upstreamSOCKS5Settings struct {
	Servers []upstreamSOCKS5Server `json:"servers"`
}

type upstreamSOCKS5Server struct {
	Address string               `json:"address"`
	Port    uint16               `json:"port"`
	Users   []upstreamSOCKS5User `json:"users,omitempty"`
}

type upstreamSOCKS5User struct {
	User string `json:"user"`
	Pass string `json:"pass"`
}

func upstreamSOCKS5OutboundFor(o UpstreamSOCKS5) (json.RawMessage, error) {
	if err := o.check(); err != nil {
		return nil, err
	}
	server := upstreamSOCKS5Server{Address: o.Address, Port: o.Port}
	if o.Username != "" {
		server.Users = []upstreamSOCKS5User{{User: o.Username, Pass: o.Password}}
	}
	return json.Marshal(upstreamSOCKS5Outbound{
		Tag:      TagUpstreamSOCKS5,
		Protocol: "socks",
		Settings: upstreamSOCKS5Settings{Servers: []upstreamSOCKS5Server{server}},
	})
}

// chainOutboundViaSOCKS5 injects Xray's streamSettings.sockopt.dialerProxy
// without decoding protocol-specific outbound fields. Existing stream and
// sockopt fields are preserved.
func chainOutboundViaSOCKS5(raw json.RawMessage, dialerProxy string) (json.RawMessage, error) {
	var outbound map[string]json.RawMessage
	if err := json.Unmarshal(raw, &outbound); err != nil {
		return nil, errors.New("upstream SOCKS5 could not modify the proxy outbound")
	}
	streamSettings := map[string]json.RawMessage{}
	if value, ok := outbound["streamSettings"]; ok && string(value) != "null" {
		if err := json.Unmarshal(value, &streamSettings); err != nil {
			return nil, errors.New("upstream SOCKS5 could not read proxy transport settings")
		}
	}
	sockopt := map[string]json.RawMessage{}
	if value, ok := streamSettings["sockopt"]; ok && string(value) != "null" {
		if err := json.Unmarshal(value, &sockopt); err != nil {
			return nil, errors.New("upstream SOCKS5 could not read proxy socket settings")
		}
	}
	dialerProxyJSON, err := json.Marshal(dialerProxy)
	if err != nil {
		return nil, errors.New("upstream SOCKS5 could not encode the dialer")
	}
	sockopt["dialerProxy"] = dialerProxyJSON
	encodedSockopt, err := json.Marshal(sockopt)
	if err != nil {
		return nil, errors.New("upstream SOCKS5 could not encode socket settings")
	}
	streamSettings["sockopt"] = encodedSockopt
	encodedStream, err := json.Marshal(streamSettings)
	if err != nil {
		return nil, errors.New("upstream SOCKS5 could not encode transport settings")
	}
	outbound["streamSettings"] = encodedStream
	return json.Marshal(outbound)
}
