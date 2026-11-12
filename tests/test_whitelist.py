from src.collector.whitelist_validator import WhitelistValidator


def test_whitelist_allowed_domains():
    validator = WhitelistValidator()

    # Fuentes Nacionales / Macro
    assert validator.is_url_allowed("https://www.gob.mx/cofepris/prensa") == True
    assert validator.is_url_allowed("https://cofepris.gob.mx/noticias") == True
    assert validator.is_url_allowed("https://www.darkdaily.com/clinical-laboratory") == True
    assert validator.is_url_allowed("https://myadlm.org/education") == True
    assert validator.is_url_allowed("https://ema.org.mx/noticias") == True
    assert validator.is_url_allowed("https://ambc.org.mx/capacitacion") == True

    # Fuentes Regionales y Locales (BC / Tijuana)
    assert validator.is_url_allowed("https://zetatijuana.com/salud-economia") == True
    assert validator.is_url_allowed("https://bajahealthcluster.org/comunicados") == True
    assert validator.is_url_allowed("https://saludbc.gob.mx/boletin") == True
    assert validator.is_url_allowed("https://elsudcaliforniano.com.mx/noticias") == True

    # Subdominio de gob.mx (p. ej. presidencia)
    assert validator.is_url_allowed("https://www.gob.mx/presidencia/prensa/algo") == True


def test_whitelist_rejected_domains():
    validator = WhitelistValidator()

    assert validator.is_url_allowed("https://www.untrusted-fake-news-site.com/article") == False
    assert validator.is_url_allowed("https://randomblog.wordpress.com/health") == False
    assert validator.is_url_allowed("invalid-url-string") == False


def test_validate_and_log_logs_rejection(tmp_path):
    sources_path = tmp_path / "sources.json"
    sources_path.write_text('{"whitelisted_domains": ["gob.mx"]}', encoding="utf-8")
    validator = WhitelistValidator(sources_file_path=str(sources_path))

    assert validator.validate_and_log("https://www.gob.mx/salud", title="OK") == True
    assert validator.validate_and_log("https://www.untrusted.com/x", title="Rechazada") == False
