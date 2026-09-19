# Caspian-BYOC

[**Download latest release**](https://github.com/Iman/caspian/releases/latest) | [**Open wiki**](https://github.com/Iman/caspian/wiki/Home)

To build the Windows app and installer locally, see [Windows build instructions](docs/WINDOWS-BUILD.md).

<div dir="ltr" align="left">

[English](README.md) | [فارسی](README.fa.md) | [Русский](README.ru.md) | [中文](README.zh.md) | [العربية](https://github.com/Iman/caspian/wiki/Home.ar) | [اردو](https://github.com/Iman/caspian/wiki/Home.ur) | [Türkçe](https://github.com/Iman/caspian/wiki/Home.tr)

</div>

<div dir="ltr" align="left">

[![ci](https://github.com/Iman/caspian/actions/workflows/ci.yml/badge.svg)](https://github.com/Iman/caspian/actions/workflows/ci.yml) [![release](https://img.shields.io/github/v/release/Iman/caspian?label=release)](https://github.com/Iman/caspian/releases/latest) [![licence AGPL-3.0-or-later](https://img.shields.io/badge/licence-AGPL--3.0--or--later-blue)](LICENSE) [![platform Windows, macOS, Raspberry Pi and Linux](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Raspberry%20Pi%20%7C%20Linux-blue)](https://github.com/Iman/caspian/releases/latest) [![container](https://img.shields.io/badge/ghcr.io-caspian-blue)](https://github.com/Iman/caspian/pkgs/container/caspian) [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Iman/caspian)

</div>

![Your devices join the box's Wi-Fi. The box connects with the config you pasted and tunnels everything to your own server abroad, so your home router and your internet provider see one encrypted connection to one address instead of what you open.](docs/images/flow-en.svg)

Caspian-BYOC turns a Windows PC, Mac running macOS, Raspberry Pi, or Linux
computer into a bring-your-own-config WiFi gateway. Paste a V2Ray or
Xray-compatible proxy configuration into the web panel and press one switch.
Caspian accepts VLESS,
VMess, Shadowsocks, SOCKS, Trojan, and Hysteria2 share links. It also accepts
Clash and Clash.Meta YAML, raw Xray JSON, link lists, and base64 subscription
data. Caspian connects through Xray-core and shares the tunnel as a WiFi
hotspot, so every device that joins is protected without installing an app.
Optional anti-DPI (DPI circumvention) controls, SNI spoofing and TLS splitting, help the connection start on networks that inspect traffic.

![The Caspian panel, connected](docs/images/panel-en.png)

The panel above is a real screenshot from a running box, taken on a Raspberry Pi
5 on 2026-09-03 with the tunnel up, before any device had joined. The network
passphrase, the configuration name and the server address in it are substituted,
and the join code is blurred, because that code encodes the network name and its
password. Nothing else is altered.

The panel opens in English. Choose Persian from the language menu at the top. There is no account, no
telemetry, and the panel fetches nothing from the internet unless you press
Refresh on a subscription address you saved.

![Caspian Control on Windows](docs/images/caspian-control-windows.png)

![Caspian Control on macOS](docs/images/caspian-control-macos.png)

## Anti-DPI: SNI spoofing and TLS splitting

Deep packet inspection (DPI) is how a network reads the start of a connection to decide whether to block it. Caspian carries three optional anti-DPI (DPI circumvention) controls, in the panel beside the saved config:

- **Decoy server name.** Caspian sends a TLS greeting that names a decoy domain before the real proxy stream. The real TLS or REALITY server name and the certificate checks stay exactly as they were.
- **TCP split.** The first TLS greeting leaves in two writes, split near the middle of the server name.
- **TLS-record split.** The greeting record is divided at that point without changing the handshake itself.

Each control is independent and can be combined with the others. Saving reconnects a running tunnel with the new settings. They work with VLESS, VMess and Trojan over the supported IPv4 TCP transports, and the two splits need plain TLS.

DPI bypass depends on the network and its filtering rules. Caspian does not promise to be undetectable or universally "DPI safe". The loopback tests verify unchanged data, a real TLS handshake, and rejection of a wrong certificate name; they do not establish bypass against an internet provider. See [SNI setup, supported platforms, and limits](docs/SNI.md) and [upstream research and credits](docs/THIRD-PARTY.md).

## Upstream SOCKS5

Caspian can optionally establish the connection to your configured tunnel server through an upstream SOCKS5 proxy. The upstream proxy is a **front-proxy for the tunnel connection**, not a replacement for the tunnel itself: client traffic still follows Caspian's normal routing into the configured VLESS, VMess, Shadowsocks, SOCKS, Trojan, or Hysteria2 outbound.

Open **Advanced → Upstream SOCKS5**, enable it, and enter the proxy address and port. Username and password are optional. Saving the settings reconnects a running tunnel with the new configuration.

Example:

```text
Address: 127.0.0.1
Port:    1080
Username: optional
Password: optional
```

The password is never rendered back into the page. Leaving the password field blank keeps the saved password when the username is unchanged; leaving both username and password blank clears upstream authentication.

When enabled, Caspian emits an Xray SOCKS5 outbound and chains the configured tunnel outbound through it. The catch-all route remains pointed at the tunnel outbound, so enabling the upstream does not accidentally route ordinary client traffic into the SOCKS5 proxy by itself.

The repository includes an end-to-end test with an in-process SOCKS5 server. It verifies real VLESS traffic in both unauthenticated and authenticated upstream modes and checks that the SOCKS5 server actually received the connection to the VLESS server.

## Connections and supported formats

Start with Ethernet from your router to the computer running Caspian. Use that computer's built-in Wi-Fi for the hotspot, or a compatible USB Wi-Fi adapter on Linux. This gives the internet connection and hotspot separate adapters. It is the recommended starting arrangement, not a measured speed guarantee.

In these diagrams, [1] is your internet router, [2] is the computer running Caspian, and [3] is your phone or another device. ETH means an Ethernet cable. A USB Ethernet adapter brings internet in; a USB Wi-Fi adapter creates a wireless connection. They do different jobs.

```text
A  [1] --ETH--> [2] --built-in Wi-Fi--> [3]
B  [1] --ETH--> [2] --USB Wi-Fi-------> [3]
C  [1] --Wi-Fi A--> [2] --Wi-Fi B----> [3]
D  [1] --Wi-Fi--> [2: one radio] --Wi-Fi--> [3]
```

| Internet into Caspian | Hotspot to your devices | Linux / Raspberry Pi | macOS |
|---|---|---|---|
| A. Ethernet | Built-in Wi-Fi | Supported when the driver can create a hotspot | Supported arrangement |
| B. Ethernet | External USB Wi-Fi | Requires a Linux driver with access point (AP) support | Not supported as the hotspot by Caspian |
| C. Wi-Fi adapter A | Separate Wi-Fi adapter B | Requires AP support on adapter B | An external USB Wi-Fi hotspot is not supported |
| D. Wi-Fi | The same Wi-Fi radio | Conditional: the driver must allow a station and AP together; the channel may be shared | Not supported on the built-in radio |

These are the arrangements the current code can plan or refuse. They do not certify every adapter, OS update, or laptop. A Wi-Fi adapter that can join your home network may still be unable to create a hotspot. Linux USB arrangements have modelled tests; the existing hardware record does not establish that every USB adapter works. On macOS, use Ethernet and built-in Wi-Fi for the documented path. Plugging in USB Wi-Fi does not remove that restriction.

Caspian accepts VLESS, VMess, Shadowsocks, SOCKS, Trojan, and Hysteria2 links, including the hy2 alias. It also accepts supported Clash/Clash.Meta YAML, Xray JSON, lists of links, and base64 subscription content. It uses whichever entry of a list you choose. A subscription address can be saved beside the config and refreshed when you press the button, through the tunnel. Ask your provider for the actual supported configuration, not an account password or a web page link.

Supported transport names include raw/tcp, ws, grpc, httpupgrade, xhttp/splithttp, and kcp/mkcp. Protocol, transport, and security settings must be compatible; not every combination works. TUIC, WireGuard, SSR, AnyTLS, and Hysteria v1 links are not supported. Do not rename an unsupported protocol to make it pass validation. See the protocol guide for restrictions and test evidence.

[For connection diagrams, cable-first setup, service restarts, and common errors, read the home-user troubleshooting guide.](https://github.com/Iman/caspian/wiki/Troubleshooting)

## Install and read the guides

CPU and RAM: Caspian has no measured minimum RAM, CPU core count, or clock speed yet. Resource use depends on traffic volume, proxy protocol, and simultaneous connections. Idle and load benchmarks are needed before minimum requirements can be published.
