// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Iman Samizadeh

package privsvc

import (
	"errors"
	"net/netip"
	"time"

	"caspianbyoc.org/caspian/internal/hotspot"
	"caspianbyoc.org/caspian/internal/link"
	"caspianbyoc.org/caspian/internal/netcfg"
	"caspianbyoc.org/caspian/internal/panel"
	"caspianbyoc.org/caspian/internal/xcfg"
)

const (
	dhcpFirstOffset = 50
	dhcpLastOffset  = 200
	dhcpLeaseTime   = 12 * time.Hour
	dnsCacheSize    = 150
)

func (s *Service) netOptionsFor(req panel.StartRequest, socksPort uint16) (netcfg.Options, error) {
	o := s.cfg.netOptions()
	if o.SystemSOCKS.Enabled && socksPort != 0 {
		o.SystemSOCKS.Port = socksPort
	}
	o.UplinkOverride = req.Network.InternetInterface
	if h := req.Hotspot.Interface; h != "" && !s.isVirtualAPName(h) {
		o.HotspotOverride = h
	}
	o.HotspotBand = netcfg.RadioBand(req.Hotspot.Band)
	if req.Hotspot.Subnet != "" {
		p, err := netip.ParsePrefix(req.Hotspot.Subnet)
		if err != nil {
			return o, fail("hotspot subnet", panel.FaultUnknown, err)
		}
		o.HotspotSubnet = p
	}
	return o, nil
}

func (s *Service) engineDocument(l *link.Link, req panel.StartRequest, netOpts netcfg.Options) ([]byte, error) {
	o := xcfg.Defaults()
	o.Link = l
	o.TUN.Disabled = s.cfg.TUNDisabled
	o.TUN.Name = netOpts.TunName
	o.SOCKS.Port = s.socksPortInForce()
	o.LocalDNS.Enabled = true
	o.LocalDNS.Port = s.cfg.LocalDNSPort
	o.DNS.Intercept = true

	// The optional front SOCKS5 is an outbound next hop. It is deliberately
	// separate from the local SOCKS inbound above, so enabling it does not
	// change Caspian's local control/listener port.
	o.Upstream = xcfg.UpstreamSOCKS5{
		Enabled:  req.Upstream.Enabled,
		Host:     req.Upstream.Host,
		Port:     req.Upstream.Port,
		Username: req.Upstream.Username,
		Password: req.Upstream.Password,
	}

	if req.EngineLogLevel != "" {
		o.LogLevel = xcfg.LogLevel(req.EngineLogLevel)
	}

	doc, err := xcfg.Build(o)
	if err != nil {
		return nil, fail("compose engine configuration", panel.FaultEngineRejectedConfig, err)
	}
	return doc, nil
}

func (s *Service) hotspotPlanFor(p *netcfg.Plan, f netcfg.Facts, req panel.StartRequest, country string) (hotspot.Plan, error) {
	channel := p.Channel
	if req.Hotspot.Channel != 0 && !p.ChannelPinned {
		channel = req.Hotspot.Channel
	}
	band := bandForChannel(channel)
	if country == "" {
		return hotspot.Plan{}, fail("country", panel.FaultCountryMissing,
			errors.New("no country is set and the radio did not report one, so the hotspot cannot legally pick a channel"))
	}

	uplink := p.Uplink
	if s.cfg.Backend.Platform() == netcfg.PlatformWindows {
		uplink = p.Tun
	}
	ap := hotspot.APConfig{
		Interface:   p.Hotspot,
		Uplink:      uplink,
		SSID:        req.Hotspot.SSID,
		Passphrase:  req.Hotspot.Passphrase,
		CountryCode: country,
		Channel:     channel,
		Band:        band,
		ControlDir:  s.cfg.HotspotPaths.HostapdControlDir,
	}

	rc := radioConstraintFor(f, p, channel)

	first, err := nthAddress(p.HotspotSubnet, dhcpFirstOffset)
	if err != nil {
		return hotspot.Plan{}, fail("dhcp range", panel.FaultUnknown, err)
	}
	last, err := nthAddress(p.HotspotSubnet, dhcpLastOffset)
	if err != nil {
		return hotspot.Plan{}, fail("dhcp range", panel.FaultUnknown, err)
	}

	dns := hotspot.DNSConfig{
		Interface:  p.Hotspot,
		Subnet:     p.HotspotSubnet,
		Gateway:    p.HotspotGateway,
		RangeStart: first,
		RangeEnd:   last,
		LeaseTime:  dhcpLeaseTime,
		LeaseFile:  s.cfg.HotspotPaths.LeaseFile,
		Upstream:   netip.AddrPortFrom(netip.MustParseAddr("127.0.0.1"), s.cfg.LocalDNSPort),
		CacheSize:  dnsCacheSize,
	}

	newPlan := hotspot.NewPlan
	if s.cfg.Backend.Platform() == netcfg.PlatformWindows {
		newPlan = hotspot.NewMobileHotspotPlan
	}
	plan, err := newPlan(ap, dns, rc)
	if err != nil {
		return hotspot.Plan{}, fail("hotspot configuration", hotspotFault(unitAP, err.Error(), err), err)
	}
	return plan, nil
}
