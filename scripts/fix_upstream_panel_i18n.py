from pathlib import Path
import re


def main():
    template = Path("internal/panel/templates/index.html")
    text = template.read_text()
    new = '''      <fieldset class="upstream-box">
        <legend>{{.T "upstream.title"}}</legend>
        <p class="hint">{{.T "upstream.hint"}}</p>
        <label><input type="checkbox" name="upstream_enabled" value="1" {{if .UpstreamEnabled}}checked{{end}}> {{.T "upstream.enabled"}}</label>
        <label for="upstream_host">{{.T "upstream.host"}}</label>
        <input id="upstream_host" name="upstream_host" type="text" value="{{.UpstreamHost}}" dir="ltr" autocomplete="off" spellcheck="false">
        <label for="upstream_port">{{.T "upstream.port"}}</label>
        <input id="upstream_port" name="upstream_port" type="number" min="1" max="65535" value="{{.UpstreamPort}}" dir="ltr">
        <label for="upstream_username">{{.T "upstream.username"}}</label>
        <input id="upstream_username" name="upstream_username" type="text" value="{{.UpstreamUsername}}" dir="ltr" autocomplete="off">
        <label for="upstream_password">{{.T "upstream.password"}}</label>
        <input id="upstream_password" name="upstream_password" type="password" value="" dir="ltr" autocomplete="new-password">
        <p class="hint">{{.T "upstream.password_hint"}}</p>
      </fieldset>
'''
    pattern = r'(?m)^\s*<fieldset class="upstream-box">.*?^\s*</fieldset>\s*\n'
    text2, count = re.subn(pattern, new, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("upstream template block not found")
    template.write_text(text2)

    messages = Path("internal/panel/i18n_messages.go")
    text = messages.read_text()
    if '"upstream.title"' not in text:
        fa_marker = "var messagesFA = map[Key]string{\n"
        en_marker = "var messagesEN = map[Key]string{\n"
        entries_fa = '''\t"upstream.title": "پراکسی بالادستی SOCKS5",
\t"upstream.hint": "اختیاری است؛ ترافیک کاسپین ابتدا به این SOCKS5 می‌رود و نیازی به VLESS یا VMess جداگانه نیست.",
\t"upstream.enabled": "استفاده از پراکسی بالادستی",
\t"upstream.host": "آدرس / IP پراکسی",
\t"upstream.port": "پورت",
\t"upstream.username": "نام کاربری (اختیاری)",
\t"upstream.password": "رمز عبور (اختیاری)",
\t"upstream.password_hint": "اگر رمز قبلی تنظیم شده و این کادر خالی باشد، رمز قبلی حفظ می‌شود.",
'''
        entries_en = '''\t"upstream.title": "Upstream SOCKS5 proxy",
\t"upstream.hint": "Optional; Caspian sends traffic to this SOCKS5 first. No separate VLESS or VMess configuration is required.",
\t"upstream.enabled": "Use upstream proxy",
\t"upstream.host": "Proxy address / IP",
\t"upstream.port": "Port",
\t"upstream.username": "Username (optional)",
\t"upstream.password": "Password (optional)",
\t"upstream.password_hint": "If a password is already set and this field is empty, the existing password is kept.",
'''
        if fa_marker not in text or en_marker not in text:
            raise SystemExit("message map marker not found")
        text = text.replace(fa_marker, fa_marker + entries_fa, 1)
        text = text.replace(en_marker, en_marker + entries_en, 1)
        messages.write_text(text)


if __name__ == "__main__":
    main()
