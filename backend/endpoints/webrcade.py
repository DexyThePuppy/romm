from config import ROMM_HOST
from decorators.oauth import protected_route
from endpoints.responses.webrcade import (
    WEBRCADE_SLUG_TO_TYPE_MAP,
    WEBRCADE_SUPPORTED_PLATFORM_SLUGS,
    WebrcadeFeedSchema,
)
from fastapi import APIRouter, Request
from handler import dbh

router = APIRouter()


@protected_route(router.get, "/platforms/webrcade/feed", [])
def platforms_webrcade_feed(request: Request) -> WebrcadeFeedSchema:
    """Get webrcade feed endpoint

    Args:
        request (Request): Fastapi Request object

    Returns:
        WebrcadeFeedSchema: Webrcade feed object schema
    """
    platforms = dbh.get_platform()

    with dbh.session.begin() as session:
        return {
            "title": "RomM Feed",
            "longTitle": "Custom RomM Feed",
            "description": "Custom feed from your RomM library",
            "thumbnail": "https://raw.githubusercontent.com/zurdi15/romm/f2dd425d87ad8e21bf47f8258ae5dcf90f56fbc2/frontend/assets/isotipo.svg",
            "background": "https://raw.githubusercontent.com/zurdi15/romm/release/.github/screenshots/gallery.png",
            "categories": [
                {
                    "title": p.name,
                    "longTitle": f"{p.name} Games",
                    "background": f"{ROMM_HOST}/assets/webrcade/feed/{p.slug.lower()}-background.png",
                    "thumbnail": f"{ROMM_HOST}/assets/webrcade/feed/{p.slug.lower()}-thumb.png",
                    "description": "",
                    "items": [
                        {
                            "title": rom.name,
                            "description": rom.summary,
                            "type": WEBRCADE_SLUG_TO_TYPE_MAP.get(p.slug, p.slug),
                            "thumbnail": f"{ROMM_HOST}/assets/romm/resources/{rom.path_cover_s}",
                            "background": f"{ROMM_HOST}/assets/romm/resources/{rom.path_cover_l}",
                            "props": {"rom": f"{ROMM_HOST}{rom.download_path}"},
                        }
                        for rom in session.scalars(dbh.get_roms(p.slug)).all()
                    ],
                }
                for p in platforms
                if p.slug in WEBRCADE_SUPPORTED_PLATFORM_SLUGS
            ],
        }
