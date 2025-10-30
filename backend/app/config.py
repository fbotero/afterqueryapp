import os
from functools import lru_cache


class Settings:
    # Supabase/Postgres
    #database_url: str = os.getenv("DATABASE_URL") or "postgresql://postgres:AfterQuery2025@db.ystxeblrfwqmrjlaoygl.supabase.co:5432/postgres"
    
    database_url: str = "postgresql://postgres.ystxeblrfwqmrjlaoygl:AfterQuery2025@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
    
    # GitHub App
    #github_app_id: str = os.getenv("GITHUB_APP_ID", "2201683")
    #github_private_key: str = os.getenv("GITHUB_PRIVATE_KEY", "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb2dJQkFBS0NBUUVBb3JBQk1hWnpmYzJuSG0rU2JKVVdYUWVMSlc0WkZHVmJSVVpxRVo2c3ZtRjRZRUpxCmlnM1g1aGZFWDFQMGRuMy9hMlVEblZMd1ZoMVI2WWdEYjNoMjdBaHdoS2JFL2x2SVJGcHBHUko2STNQUm1qc0EKOUsyL0pwQXZic1VvTDRYTEdpSFFoZGMvWDNLQUpQQllrSzNDQVFKYmJYUW9wUmFkcDVvQzdmNytKbEdMRDBscgp2NEpVbUwzbklMTGkzRVU5WXU5dEdiOUJ6R0tsMEFhYWpiL2xsV1dCOGd2OVdYU1BQdzc5YkFEV291aXlGM1lWCk50Y0laeXNrSU1Pc2Zya28zZmFkNkU4Yy82NisyQXczN3NQanFZMnZIODBZOGRteThsNkpxTFRjTy9nSGFQL0oKVUFHdHZjaExvR2gyVUlpR0psZkJ4Nnh6Njc4WFh6WXJoZzlzL3dJREFRQUJBb0lCQUdWOENhS2hSTllyWFo2OAoxc2hwVUNRRU9xYkV3VnhaeGMrM0Z4K2FyZ09zNWR5V1VjT0EwemN6aUVvM0l2NXZwcytsbWRXZ0VWQ0d4Ync2CkhucUEyUjV3UFZCaWYreHo4TC9DN21DM2gvMXBtRXp2bGE4TVczdUE0alhsUXlZeC9mcDFNWkRzTHhvcFlRcXAKNjNXRkRzcDJYL1l0U2RXQ0FDSzNEakRNcWxuWDhaWkt0bjM2a2FIcDRhZUlmQmtnR1ZpR0Q2cndPR01NNGlibApvdXBsTU1XcjlpSjArbmorUVpiL3cxUDBGMTNXeHpkMUpuYUErYUtSM2Z5dWtlT0VLZUV6TGlnRU1IcjVxM1RRClJidk9ULy8wbHlXTjJqMnhQQnoyR3VJeXgzZ09MYU9HbEhIb3puMXRZTkx6UXUyL3VoeDQ1Nm5JNlpPUEtjMkIKTzRFbTVPRUNnWUVBenVwaDVEU0ZXaUQzZ01tRlZwbCtQM2lyVmVqTUhZSTNKK2JkbnBnSk1hdmZtcDhybEpBNApkcG5qWENUVjlEdVRtcVhNa3puWGJRZTZTQjAxOEVwaFFDVDBWTnhKbG5McndkeXVZbTBKdkRQNE11YzMyUXYrCnVqQ3FDN1FZNWVJUGx6WXZja2t0ZWYwaXIvbEUwWXo1ZTNpdG9WbC83c21PejlWc2MrbmtTaWtDZ1lFQXlVZTcKT2txZkdpQUpOR1lyQ0d5N0lQcGM0dmtZRjJIWU0ySDZuMElTS0RweWxKMFdBVzFLNklpQjVHaFl5ZDZ2Q3pUcgpUdjVLdkpPT1F3NkNMMEt5Qlo2RHJGcUUxd1ZUN0l3dWR5T1kvZ0R5RkdXODNTTTg3em1MWFZxaGIvUGFjM2dVCjlWTTNjRXFWM1N6MHZoZmo1M2o3bmxkQWJLaXozeHcxMTRHQXN1Y0NnWUJMUHc4MFp5a3JtcHVIV1VIRk9YS2cKOEdnV2lOOVp4OVg1QzhzQ2RyVzVPNURJY1NQdkZmZUNvZm45czJPZk90ODF1Ui9KVnBxU0N1SmlnVVR4U290TgpRV01kVFRMeHBIODU4OS95NlVaR0Mvd3h2c1lmaDI0dUZhNXhMU0IwMFIzc1ZvY3duNDRMTTlRZWZKN2JPZElzClpibDIyTTVlYnl3aFJyTDNBRkxGNlFLQmdIcWZYcXJXaHpNdFRTNUZCL1pyOTF6UjZnREU3QzVpaDRwV0tJOFoKZTJKU3FUZHNzOWxPc2hJVUI3NFU2L0tmM1ZnZ2R6SjZyU0ZSYTV2aW5PRVo2c2FObVg1STd5RG51QWNtSjdDaApXVFYxY2dXSExaWXpQNDRtS29kSERZN2NxcnNwN3VxK05jb05SbHVtWmJ2aFpoREFuZG9MSWM2UXdIUXVCWWN5CitDc0ZBb0dBWUpmYkJDMFFFOHdyS0xPN2FadDFJUGlaenFlQ0RKSG56a1UyNWliNWlaOGR0ZkhGTmJIK3NpZ1oKK2Z5TXc2bjhjRVY2VXQ4aWpweHZoaEhSQXZYZDlnOXBPTDhucnI3SGt1bnkra1gzSlFFOVZ5NXcyMVduRkVNTAo0U0lVSDU2OS9ta1RKeWQ4cFRhSG5kMmN0czQyaHBQbVNlc3RzUzNTQTFOL2FiVU0wQTA9Ci0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg==")  # PEM content or base64
    #github_installation_id: str = os.getenv("GITHUB_INSTALLATION_ID", "92206831")
    #github_org: str = os.getenv("GITHUB_ORG", "fbotero")


    github_app_id: str = os.getenv("GITHUB_APP_ID", "2207220")
    github_private_key: str = os.getenv(
        "GITHUB_PRIVATE_KEY",
        (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEogIBAAKCAQEAq0Vefg5MnWyQ7sLcigVwaOwoYYKVNpqlSmQNsBrfUyMO+ruE\n"
            "a8PIoC4FmxPyJx1ke+QbdYwVZIWoHMm9s8CEqGjo8ChKNE/4dqSKX7KVNZKBUUgR\n"
            "lR2u5cuBn2BresIC+M2Rix5WfTbv1DMc/CI7l1x0YNw/l5fqJxGl/vJf7pbEdznL\n"
            "YVQHSeMRlxhyCrbJnKqN6UX472maVvr4wsob6L/JwKDoD8OOWoV3njl61ClIreBO\n"
            "VfnKFSBQ/cXA7pV3DVIoYpn9JcZHV8T2lPiyTT9IskA/+bskmWbzZZpIzGyyErsz\n"
            "w5GdM2AxG1vP9KoPtvnNoyM3nkpMfLIWxH+Y/QIDAQABAoIBAESub8MrJswmYkRs\n"
            "/hWXMsnQkizwObgI8enQD7EkRZRIRdSEaAjzHTwm2Hak3AGVhtsr0VslDtsdwhmx\n"
            "SRKRTGFgmLDd50vtGd0yBI91xOIT2ynmNa7PlXhvUI7CErfKn3h4rznTs6lI44n7\n"
            "6U6ux6jeGYlSKWo4MFz0ddW0CoZZZYJWucKMgHSQlFuw/AHkpMuWqutorr9TDvpD\n"
            "PWJ7Y6XUHbiOdChYXrhsZoocwSepAD+AgDcUCwvUz2aZooNyzMFQXE2fP1LFCoqt\n"
            "xT2Jfm0o7JOcGSkT1a9Osmc/tP55u8oni14hCVJ1c5KKSf9r4/xibnd4Vpv2g2OL\n"
            "uZgidB0CgYEA09JrfECdx4KmTZdXQnNZ9TN5FFy7cPAJOYcy8mR8UCZ8dGLz1H//\n"
            "aZQNyzF+DPvhhhADYV4qmUi5lpGAajgShGIpylMIoMGF65RvRfqL6kETi50bH7h5\n"
            "Nq6Z3II9Zg5r1j4nXFEtRMi3m6nw7zlZCOriewcmUlJ3pHsNzPzGe48CgYEAzv3a\n"
            "zkDYMjBoxpFoGUktDcNPtJ3utvLSh1BvziCUAcUXFcVbNQYBbEF+WyvL7XJAumtv\n"
            "2Z3yfYdPhe9h+c27ECmwyEuEfmWXk0JwvbYhbSYn9jKpvZP/IPU/1vqQhQ17WQBy\n"
            "eVfpjqYl9VKUR/VnBvhKiCzlIwznxWThdaULjLMCgYBDPMDXsR8kTGmDqa2OL1V3\n"
            "yv39I65wHBGhjDP000bOnljVDO//HR4zIkb6n9w2POIKjxyzlJOLEpWuoMMVdHUU\n"
            "RqCjU5YiiSt8ayKjIPO2yS9uGtGYURNQ8z1tzH223o8Gc7ZEzJPFCL2XkOsk1JxZ\n"
            "g02e5dcZPIoz0MfBsN9EKwKBgCgdYHNKc9u+MAATnAYSfW3GZUMOvH2uL4jT2Ocs\n"
            "vyJcrO2mMtfi0xHE25UVts7MrqiyO5oEF0Omno3JZ8Z+zXsDaWRX5lSMocSDQtAx\n"
            "ZOb/Vw1KokTAUthzTyz9oFZ412fXQ1gq5nOj1YVmvJ/5ej8KjX84nCufy6cgtuUS\n"
            "2FsrAoGAWkGWFmz9hQ3/UvqVxeo4L22rkyMlbhzgFHcEu1Xh17scg7eUketH8tpW\n"
            "xyqYo/TdrcIAL3LP6iUMDZ59Uzd6VznKaUo0QBb0hgxmeXJe+2ENVn3Qt1ZgMix0\n"
            "ElE828UdgictAOXbEj1lNDV9QPTpEpjzf+rXH0KhtLEWOgsBqYo=\n"
            "-----END RSA PRIVATE KEY-----"
        ),
    )  # PEM content or base64
    github_installation_id: str = os.getenv("GITHUB_INSTALLATION_ID", "92310619")
    github_org: str = os.getenv("GITHUB_ORG", "fbotero")
    # Optional: Personal Access Token for user-owned repo operations
    #github_pat: str = os.getenv("GITHUB_PAT", "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")
    github_pat: str = os.getenv("GITHUB_PAT", "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")
    # Email (Resend)
    resend_api_key: str = os.getenv("RESEND_API_KEY", "re_Mrjfbmg3_ELFz3xTKN9q6SZiBoS7X1zax")

    # App
    app_base_url: str = os.getenv("APP_BASE_URL", "http://localhost:3000")
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


