"""empty message

Revision ID: 0019_resources_refactor
Revises: 0018_firmware
Create Date: 2024-05-05 11:20:54.243980

"""

import os
import re
from shutil import rmtree
from urllib.parse import quote

import sqlalchemy as sa
from alembic import op
from config import RESOURCES_BASE_PATH
from models.platform import Platform
from models.rom import Rom

# revision identifiers, used by Alembic.
revision = "0019_resources_refactor"
down_revision = "0018_firmware"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Get the database connection
    connection = op.get_bind()

    # Fetch all entries from the roms table
    platforms = connection.execute(sa.text("select id, slug from platforms")).fetchall()
    platform_map = {platform.id: platform.slug for platform in platforms}

    roms = connection.execute(
        sa.text(
            "SELECT id, name, platform_id, path_cover_s, path_cover_l, path_screenshots FROM roms"
        )
    ).fetchall()

    for rom in roms:
        platform_slug = platform_map.get(rom.platform_id, "")
        platform_folder_name = Platform.fs_safe_folder_name(rom.platform_id)
        rom_folder_name = Rom.fs_safe_folder_name(rom.id)

        old_folder_path = f"{RESOURCES_BASE_PATH}/{platform_slug}/{rom.name}"
        new_folder_path = (
            f"{RESOURCES_BASE_PATH}/{platform_folder_name}/{rom_folder_name}"
        )

        print("INFO:\t  [Resources migration] Renaming folder:")
        print(f"INFO:\t  [Resources migration]  - old: {old_folder_path}")
        print(f"INFO:\t  [Resources migration]  - new: {new_folder_path}")

        try:
            os.makedirs(f"{RESOURCES_BASE_PATH}/{platform_folder_name}", exist_ok=True)
        except OSError as error:
            print(error)

        if os.path.exists(old_folder_path):
            os.rename(old_folder_path, new_folder_path)
        else:
            print(
                f"ERROR:\t  [Resources migration] Folder '{old_folder_path}' does not exist"
            )

        quoted_rom_name = re.escape(quote(rom.name))
        quoted_platform_slug = re.escape(quote(platform_slug))

        updated_path_cover_s = re.sub(
            quoted_platform_slug,
            platform_folder_name,
            re.sub(quoted_rom_name, rom_folder_name, rom.path_cover_s),
        )
        updated_path_cover_l = re.sub(
            quoted_platform_slug,
            platform_folder_name,
            re.sub(quoted_rom_name, rom_folder_name, rom.path_cover_l),
        )
        updated_path_screenshots = re.sub(
            quoted_platform_slug,
            platform_folder_name,
            re.sub(quoted_rom_name, rom_folder_name, rom.path_screenshots),
        )

        connection.execute(
            sa.text(
                """
                UPDATE roms 
                SET path_cover_s = :path_cover_s,
                    path_cover_l = :path_cover_l,
                    path_screenshots = :path_screenshots
                WHERE id = :id
            """
            ),
            {
                "id": rom.id,
                "path_cover_s": updated_path_cover_s,
                "path_cover_l": updated_path_cover_l,
                "path_screenshots": updated_path_screenshots,
            },
        )

    for platform in platforms:
        try:
            rmtree(f"{RESOURCES_BASE_PATH}/{platform.slug}")
        except FileNotFoundError:
            print(
                f"ERROR:\t  [Resources migration] Folder '{RESOURCES_BASE_PATH}/{platform.slug}' does not exist"
            )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
