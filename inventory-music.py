from collections import defaultdict
from pathlib import Path
from constants import DATA_DRIVE_PATH


def inventory_albums(music_dir: Path) -> dict:
    albums = defaultdict(list)
    for artist in [a for a in
                   sorted(music_dir.glob('*'), key=lambda path: path.name.lower())
                   if a.is_dir()]:
        for album in [a for a in sorted(artist.glob('*'), key=lambda path: path.name.lower()) if a.is_dir()]:
            albums[artist.name.strip()].append(album.name.strip())
    return albums


albums = inventory_albums(Path.home().joinpath(DATA_DRIVE_PATH, 'muzik'))
with open(Path.home().joinpath('Documents', 'inventory-music.txt'), 'w+') as catalog_file:
    for k in sorted(albums, key=str.casefold):
        catalog_file.write(f"{k}\n{{\n")
        for v in sorted(albums[k], key=str.casefold):
            catalog_file.write(f"\t{v}\n")
        catalog_file.write('}\n')
