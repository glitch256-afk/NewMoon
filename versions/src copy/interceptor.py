from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled = True
        self.ad_keywords = [
            "doubleclick.net", "google-analytics.com", "googlesyndication.com",
            "adservice.google.", "adnxs.com", "amazon-adsystem.com",
            "facebook.com/tr/", "scorecardresearch.com", "/ads/", "/adserver/",
            "adsystem", "outbrain.com", "taboola.com"
        ]

    def interceptRequest(self, info):
        if not self.enabled:
            return

        url_str = info.requestUrl().toString().lower()
        for keyword in self.ad_keywords:
            if keyword in url_str:
                info.block(True)
                return