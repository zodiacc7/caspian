from pathlib import Path

def patch(path, replacements):
    p = Path(path)
    s = p.read_text()
    for old, new in replacements:
        if old not in s:
            raise SystemExit(f'marker not found in {path}: {old[:100]!r}')
        s = s.replace(old, new, 1)
    p.write_text(s)

patch('internal/panel/handlers.go', [
    ('\t\tConfigJSON:     cfgJSON,\n\t\tHotspot: HotspotSpec{', '''\t\tConfigJSON: cfgJSON,
\t\tUpstream: UpstreamProxySpec{
\t\t\tEnabled: st.Advanced.UpstreamEnabled, Host: st.Advanced.UpstreamHost,
\t\t\tPort: st.Advanced.UpstreamPort, Username: st.Advanced.UpstreamUsername.Reveal(),
\t\t\tPassword: st.Advanced.UpstreamPassword.Reveal(),
\t\t},
\t\tHotspot: HotspotSpec{'''),
    ('\tonLAN := r.PostFormValue("panel_on_lan") == "1"\n\tconnectionsOnly := r.PostFormValue("connections_only") == "1"\n', '''\tonLAN := r.PostFormValue("panel_on_lan") == "1"
\tconnectionsOnly := r.PostFormValue("connections_only") == "1"
\tupstreamEnabled := r.PostFormValue("upstream_enabled") == "1"
\tupstreamHost := strings.TrimSpace(r.PostFormValue("upstream_host"))
\tupstreamUsername := strings.TrimSpace(r.PostFormValue("upstream_username"))
\tupstreamPassword := r.PostFormValue("upstream_password")
\tupstreamPort := uint16(0)
\tif v := strings.TrimSpace(r.PostFormValue("upstream_port")); v != "" {
\t\tn, e := strconv.ParseUint(v, 10, 16)
\t\tif e != nil || n == 0 { sess.setFlash(Problem{Headline: MsgSaveAdvancedFailed, Advice: MsgSaveFailedAdvice}, ""); p.home(w,r); return }
\t\tupstreamPort = uint16(n)
\t}
\tif upstreamEnabled && (upstreamHost == "" || upstreamPort == 0 || strings.ContainsAny(upstreamHost, " \\t\\r\\n")) {
\t\tsess.setFlash(Problem{Headline: MsgSaveAdvancedFailed, Advice: MsgSaveFailedAdvice}, ""); p.home(w,r); return
\t}
'''),
    ('\t\tst.Advanced.PanelOnLAN = onLAN\n\t\treturn nil\n', '''\t\tst.Advanced.PanelOnLAN = onLAN
\t\tst.Advanced.UpstreamEnabled = upstreamEnabled
\t\tst.Advanced.UpstreamHost = upstreamHost
\t\tst.Advanced.UpstreamPort = upstreamPort
\t\tst.Advanced.UpstreamUsername = state.Secret(upstreamUsername)
\t\tif upstreamPassword != "" { st.Advanced.UpstreamPassword = state.Secret(upstreamPassword) }
\t\treturn nil
''')])

patch('internal/panel/view.go', [
    ('\tPanelOnLAN    bool\n\tConfigFacts   []Fact\n', '''\tPanelOnLAN       bool
\tUpstreamEnabled  bool
\tUpstreamHost     LTR
\tUpstreamPort     LTR
\tUpstreamUsername string
\tConfigFacts      []Fact
'''),
    ('\td.CurrentInternet = LTR(adv.InternetInterface)\n\td.CurrentHotspot = LTR(adv.HotspotInterface)\n', '''\td.CurrentInternet = LTR(adv.InternetInterface)
\td.CurrentHotspot = LTR(adv.HotspotInterface)
\td.UpstreamEnabled = adv.UpstreamEnabled
\td.UpstreamHost = LTR(adv.UpstreamHost)
\tif adv.UpstreamPort != 0 { d.UpstreamPort = LTR(strconv.Itoa(int(adv.UpstreamPort))) }
\td.UpstreamUsername = adv.UpstreamUsername.Reveal()
''')])

p = Path('internal/panel/templates/index.html')
s = p.read_text()
marker = '      <input type="checkbox" name="panel_on_lan" value="1" {{if .PanelOnLAN}}checked{{end}}>'
block = '''      <fieldset class="upstream-box">
        <legend>{{if eq .Dir "rtl"}}پراکسی بالادستی SOCKS5{{else}}Upstream SOCKS5 proxy{{end}}</legend>
        <p class="hint">{{if eq .Dir "rtl"}}اختیاری است؛ ترافیک کاسپین ابتدا به این SOCKS5 می‌رود و نیازی به VLESS یا VMess جداگانه نیست.{{else}}Optional; Caspian sends traffic to this SOCKS5 first. No separate VLESS or VMess configuration is required.{{end}}</p>
        <label><input type="checkbox" name="upstream_enabled" value="1" {{if .UpstreamEnabled}}checked{{end}}> {{if eq .Dir "rtl"}}استفاده از پراکسی بالادستی{{else}}Use upstream proxy{{end}}</label>
        <label for="upstream_host">{{if eq .Dir "rtl"}}آدرس / IP پراکسی{{else}}Proxy address / IP{{end}}</label>
        <input id="upstream_host" name="upstream_host" type="text" value="{{.UpstreamHost}}" dir="ltr" autocomplete="off" spellcheck="false">
        <label for="upstream_port">{{if eq .Dir "rtl"}}پورت{{else}}Port{{end}}</label>
        <input id="upstream_port" name="upstream_port" type="number" min="1" max="65535" value="{{.UpstreamPort}}" dir="ltr">
        <label for="upstream_username">{{if eq .Dir "rtl"}}نام کاربری (اختیاری){{else}}Username (optional){{end}}</label>
        <input id="upstream_username" name="upstream_username" type="text" value="{{.UpstreamUsername}}" dir="ltr" autocomplete="off">
        <label for="upstream_password">{{if eq .Dir "rtl"}}رمز عبور (اختیاری){{else}}Password (optional){{end}}</label>
        <input id="upstream_password" name="upstream_password" type="password" value="" dir="ltr" autocomplete="new-password">
        <p class="hint">{{if eq .Dir "rtl"}}اگر رمز قبلی تنظیم شده و این کادر خالی باشد، رمز قبلی حفظ می‌شود.{{else}}If a password is already set and this field is empty, the existing password is kept.{{end}}</p>
      </fieldset>

'''
if marker not in s:
    raise SystemExit('upstream template marker not found')
p.write_text(s.replace(marker, block + marker, 1))
print('panel patch applied')
