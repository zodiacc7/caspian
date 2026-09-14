// SPDX-License-Identifier: AGPL-3.0-or-later

package state

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"sync"
	"testing"
	"time"
)

// Every credential in these tests is fabricated. The proxy links are
// syntactically plausible and point at documentation-reserved addresses
// (RFC 5737 192.0.2.0/24, RFC 6761 example.com); no value here works against
// anything.
const (
	fakeProxyLink = "vless://11111111-2222-3333-4444-555555555555@192.0.2.10:443" +
		"?type=tcp&security=reality&pbk=FAKEPUBLICKEYNOTREALFAKEPUBLICKEYNOTREAL0&sid=0123abcd" +
		"&fp=chrome&sni=example.com&spx=%2F#fake-test-node"
	fakeProxyScheme = "vless"
	fakeProxyLabel  = "test node"
	fakePassphrase  = "hotspot-passphrase-not-real"
	fakeSSID        = "Caspian-Test"
	fakePanelPass   = "panel-password-not-real"
)

// fullState returns a State with every single field set to a non-zero value, so
// that a round trip proves each one survives rather than proving that the
// fields somebody remembered survive.
func fullState(t *testing.T) State {
	t.Helper()
	hash, err := hashPassword(fakePanelPass)
	if err != nil {
		t.Fatalf("hashPassword: %v", err)
	}
	return State{
		Version: CurrentVersion,
		Proxy: ProxyConfig{
			Raw:            Secret(fakeProxyLink),
			Scheme:         fakeProxyScheme,
			Label:          fakeProxyLabel,
			Selected:       2,
			SpoofSNI:       Secret("cover.example.invalid"),
			TCPSplit:       true,
			TLSRecordSplit: true,
			AddedAt:        time.Date(2026, 8, 29, 12, 0, 0, 0, time.UTC),

			SubscriptionURL: Secret(fakeSubscriptionURL),
			RefreshedAt:     time.Date(2026, 9, 9, 10, 30, 0, 0, time.UTC),
			Quota:           Quota{Upload: 1, Download: 2, Total: 3, Expire: 4},
		},
		Hotspot: HotspotConfig{
			SSID:       fakeSSID,
			Passphrase: Secret(fakePassphrase),
		},
		Panel: PanelAuth{PasswordHash: Secret(hash)},
		Advanced: Advanced{
			InternetInterface: "eth0",
			HotspotInterface:  "wlan0",
			Channel:           10,
			Band:              "2.4",
			Country:           "GB",
			Subnet:            "10.42.0.0/24",
			DNSMode:           DNSModeTunnel,
			OnTunnelDown:      OnTunnelDownBlock,
			ClientIPv6:        ClientIPv6Block,
			EngineLogLevel:    "warning",
			PanelOnLAN:        true,
			UpstreamEnabled:   true,
			UpstreamHost:      "192.0.2.20",
			UpstreamPort:      3067,
			UpstreamUsername:  Secret("upstream-user"),
			UpstreamPassword:  Secret("upstream-pass"),
		},
		UpdatedAt: time.Date(2026, 8, 29, 12, 0, 0, 0, time.UTC),
	}
}

// assertNoZeroFields walks a value and fails on any field still at its zero
// value. fullState uses it so that adding a field to State without adding it
// here breaks this test instead of silently going untested.
func assertNoZeroFields(t *testing.T, v reflect.Value, path string) {
	t.Helper()
	if v.Kind() == reflect.Struct && v.Type() != reflect.TypeOf(time.Time{}) {
		for i := 0; i < v.NumField(); i++ {
			assertNoZeroFields(t, v.Field(i), path+"."+v.Type().Field(i).Name)
		}
		return
	}
	if v.IsZero() {
		t.Errorf("%s is at its zero value; the round-trip test is not covering it", path)
	}
}

func TestFullStateCoversEveryField(t *testing.T) {
	assertNoZeroFields(t, reflect.ValueOf(fullState(t)), "State")
}

// ---------------------------------------------------------------- first run

func TestLoadFirstRun(t *testing.T) {
	tests := []struct {
		name string
		// prepare returns the directory to load from.
		prepare func(t *testing.T) string
	}{
		{
			name: "directory does not exist",
			prepare: func(t *testing.T) string {
				return filepath.Join(t.TempDir(), "never-created")
			},
		},
		{
			name: "directory exists but is empty",
			prepare: func(t *testing.T) string {
				dir := filepath.Join(t.TempDir(), "empty")
				if err := os.Mkdir(dir, dirMode); err != nil {
					t.Fatalf("Mkdir: %v", err)
				}
				return dir
			},
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			dir := tc.prepare(t)

			st, err := Load(dir)
			if err != nil {
				t.Fatalf("Load on a first run must not error, got: %v", err)
			}
			if !st.FirstRun() {
				t.Error("FirstRun() = false; the panel would show a broken screen instead of setup")
			}
			if !st.NeedsSetup() {
				t.Error("NeedsSetup() = false with no password and no config")
			}

			// The zero state must be usable, which means the fail-closed policy
			// fields are already populated, not empty.
			adv := st.Advanced()
			if adv.DNSMode != DNSModeTunnel {
				t.Errorf("DNSMode = %q, want %q", adv.DNSMode, DNSModeTunnel)
			}
			if adv.OnTunnelDown != OnTunnelDownBlock {
				t.Errorf("OnTunnelDown = %q, want %q", adv.OnTunnelDown, OnTunnelDownBlock)
			}
