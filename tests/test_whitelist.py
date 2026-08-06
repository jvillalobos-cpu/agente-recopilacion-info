import pytest
from src.collector.whitelist_validator import WhitelistValidator


def test_whitelist_allowed_domains():
    validator = WhitelistValidator()
    
    assert validator.is_url_allowed("https://www.gob.mx/cofepris/prensa") == True
    assert validator.is_url_allowed("https://cofepris.gob.mx/noticias") == True
    assert validator.is_url_allowed("https://www.elfinanciero.com.mx/empresas") == True
    assert validator.is_url_allowed("https://who.int/news") == True


def test_whitelist_rejected_domains():
    validator = WhitelistValidator()
    
    assert validator.is_url_allowed("https://www.untrusted-fake-news-site.com/article") == False
    assert validator.is_url_allowed("https://randomblog.wordpress.com/health") == False
    assert validator.is_url_allowed("invalid-url-string") == False
