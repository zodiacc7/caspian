// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Iman Samizadeh

package xcfg

import (
	"encoding/json"
	"testing"
)

func TestUpstreamSOCKS5OutboundIncludesCredentials(t *testing.T) {
	raw, err := upstreamSOCKS5OutboundFor(UpstreamSOCKS5{
		Enabled: true, Address: "127.0.0.1", Port: 1080, Username: "user", Password: "pass",
	})
	if err != nil {
		t.Fatal(err)
	}
	var got struct {
		Tag      string `json:"tag"`
		Protocol string `json:"protocol"`
		Settings struct {
			Servers []struct {
				Address string `json:"address"`
				Port    uint16 `json:"port"`
				Users   []struct {
					User string `json:"user"`
					Pass string `json:"pass"`
				} `json:"users"`
			} `json:"servers"`
		} `json:"settings"`
	}
	if err := json.Unmarshal(raw, &got); err != nil {
		t.Fatal(err)
	}
	if got.Tag != TagUpstreamSOCKS5 || got.Protocol != "socks" {
		t.Fatalf("unexpected outbound: %s", raw)
	}
	if len(got.Settings.Servers) != 1 || got.Settings.Servers[0].Address != "127.0.0.1" || got.Settings.Servers[0].Port != 1080 {
		t.Fatalf("unexpected server: %s", raw)
	}
	if len(got.Settings.Servers[0].Users) != 1 ||
		got.Settings.Servers[0].Users[0].User != "user" ||
		got.Settings.Servers[0].Users[0].Pass != "pass" {
		t.Fatalf("credentials were not encoded: %s", raw)
	}
}

func TestUpstreamSOCKS5ChainingPreservesExistingSockopt(t *testing.T) {
	input := json.RawMessage("{\"tag\":\"" + TagProxy + "\",\"protocol\":\"vless\",\"streamSettings\":{\"network\":\"ws\",\"sockopt\":{\"tcpFastOpen\":true}}}")
	raw, err := chainOutboundViaSOCKS5(input, TagUpstreamSOCKS5)
	if err != nil {
		t.Fatal(err)
	}
	var got map[string]json.RawMessage
	if err := json.Unmarshal(raw, &got); err != nil {
		t.Fatal(err)
	}
	var ss map[string]json.RawMessage
	if err := json.Unmarshal(got["streamSettings"], &ss); err != nil {
		t.Fatal(err)
	}
	var sock map[string]json.RawMessage
	if err := json.Unmarshal(ss["sockopt"], &sock); err != nil {
		t.Fatal(err)
	}
	if string(ss["network"]) != "\"ws\"" {
		t.Fatalf("network changed: %s", raw)
	}
	if string(sock["dialerProxy"]) != "\""+TagUpstreamSOCKS5+"\"" {
		t.Fatalf("dialerProxy=%s", sock["dialerProxy"])
	}
	if string(sock["tcpFastOpen"]) != "true" {
		t.Fatalf("existing sockopt lost: %s", raw)
	}
}

func TestUpstreamSOCKS5BuildUsesFrontProxyWithoutChangingRouteTarget(t *testing.T) {
	l := mustParse(t, vlessRealityLink())
	raw, err := Build(Options{
		Link: l,
		Upstream: UpstreamSOCKS5{
			Enabled: true, Address: "127.0.0.1", Port: 1080, Username: "user", Password: "pass",
		},
	})
	if err != nil {
		t.Fatal(err)
	}

	var doc struct {
		Outbounds []struct {
			Tag            string          `json:"tag"`
			Protocol       string          `json:"protocol"`
			StreamSettings json.RawMessage `json:"streamSettings"`
		} `json:"outbounds"`
		Routing struct {
			Rules []struct {
				RuleTag     string `json:"ruleTag"`
				OutboundTag string `json:"outboundTag"`
			} `json:"rules"`
		} `json:"routing"`
	}
	if err := json.Unmarshal(raw, &doc); err != nil {
		t.Fatal(err)
	}

	found := false
	for _, ob := range doc.Outbounds {
		if ob.Tag == TagUpstreamSOCKS5 {
			found = true
			if ob.Protocol != "socks" {
				t.Fatalf("upstream protocol=%q, want socks", ob.Protocol)
			}
		}
	}
	if !found {
		t.Fatal("enabled upstream outbound is missing")
	}

	var ss struct {
		Sockopt struct {
			DialerProxy string `json:"dialerProxy"`
		} `json:"sockopt"`
	}
	if err := json.Unmarshal(doc.Outbounds[0].StreamSettings, &ss); err != nil {
		t.Fatal(err)
	}
	if ss.Sockopt.DialerProxy != TagUpstreamSOCKS5 {
		t.Fatalf("proxy dialerProxy=%q, want %q", ss.Sockopt.DialerProxy, TagUpstreamSOCKS5)
	}

	for _, r := range doc.Routing.Rules {
		if r.RuleTag == ruleTagCatchAll && r.OutboundTag != TagProxy {
			t.Fatalf("catch-all outbound=%q, want %q", r.OutboundTag, TagProxy)
		}
		if r.RuleTag == ruleTagResolvers && r.OutboundTag != TagProxy {
			t.Fatalf("resolver outbound=%q, want %q", r.OutboundTag, TagProxy)
		}
	}
}

func TestUpstreamSOCKS5DisabledDoesNotAddOutbound(t *testing.T) {
	l := mustParse(t, vlessRealityLink())
	raw, err := Build(Options{Link: l})
	if err != nil {
		t.Fatal(err)
	}
	p := decode(t, raw)
	for _, ob := range p.Outbounds {
		if ob.Tag == TagUpstreamSOCKS5 {
			t.Fatal("disabled upstream added an outbound")
		}
	}
	for _, r := range p.Routing.Rules {
		if r.RuleTag == ruleTagCatchAll && r.OutboundTag != TagProxy {
			t.Fatalf("disabled upstream changed catch-all outbound=%q", r.OutboundTag)
		}
	}
}

func TestUpstreamSOCKS5RejectsInvalidConfiguration(t *testing.T) {
	cases := []UpstreamSOCKS5{
		{Enabled: true, Address: "", Port: 1080},
		{Enabled: true, Address: "127.0.0.1", Port: 0},
		{Enabled: true, Address: "127.0.0.1", Port: 1080, Username: "user"},
		{Enabled: true, Address: " 127.0.0.1", Port: 1080},
		{Enabled: true, Address: "127.0.0.1\n", Port: 1080},
	}
	for i, tc := range cases {
		if err := tc.check(); err == nil {
			t.Fatalf("case %d: invalid upstream was accepted", i)
		}
	}
	if err := (UpstreamSOCKS5{}).check(); err != nil {
		t.Fatalf("disabled upstream rejected: %v", err)
	}
	if _, err := upstreamSOCKS5OutboundFor(UpstreamSOCKS5{Enabled: true, Address: "127.0.0.1", Port: 1080, Username: "u"}); err == nil {
		t.Fatal("incomplete credentials were accepted by outbound builder")
	}
}
