from django.conf import settings

def mediawiki_site_settings(request):
    return {
        'MEDIAWIKI_API_ENDPOINT': settings.MEDIAWIKI_API_ENDPOINT,
        'MEDIAWIKI_BASE_URL': settings.MEDIAWIKI_BASE_URL,
        'MEDIAWIKI_INDEX_ENDPOINT': settings.MEDIAWIKI_INDEX_ENDPOINT,
        'PROPERTY_BASE_URL': settings.PROPERTY_BASE_URL,
        'USER_BASE_URL': settings.USER_BASE_URL,
        'USER_TALK_BASE_URL': settings.USER_TALK_BASE_URL,
        'CONTRIBUTIONS_BASE_URL': settings.CONTRIBUTIONS_BASE_URL,
        'WIKI_CODENAME': settings.WIKI_CODENAME,
        'USER_DOCS_HOMEPAGE': settings.USER_DOCS_HOMEPAGE,
        'MEDIAWIKI_NAME': settings.MEDIAWIKI_NAME,
        'DISCUSS_PAGE_PREFIX': settings.DISCUSS_PAGE_PREFIX,
        'DISCUSS_PAGE_PRELOAD': settings.DISCUSS_PAGE_PRELOAD,
        'REVERT_PAGE': settings.REVERT_PAGE,
        'REVERT_PRELOAD': settings.REVERT_PRELOAD,
        'WIKILINK_BATCH_PREFIX': settings.WIKILINK_BATCH_PREFIX
    }
