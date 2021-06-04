import re
import webbrowser
from fractions import Fraction
from inspect import getfullargspec
from math import floor
from pathlib import Path
from subprocess import check_output
from typing import Iterable

from bash_tools import find
from constants import DATA_DRIVE_PATH

BRANDS = ['canon', 'pentax', 'panasonic', 'sony', 'flip', 'nikon', 'minolta', 'samsung', 'leica', 'olympus', 'kodak']
SEPARATION_LENGTH = 15


def print_line():
    print('-' * SEPARATION_LENGTH * 2)


def filter_images_by_camera(model: str, images_paths: Iterable):
    for image in images_paths:
        exif_output = check_output(['exiftool', str(image)]).decode('utf-8')
        if re.search(model, exif_output, flags=re.IGNORECASE):
            yield image


def check_out_flickr():
    canon_ps_model_numbers = []
    for i in range(10):
        canon_ps_model_numbers.append(f'a4{i}0')
    canon_ps_model_numbers.remove('a440')
    canon_ps_model_numbers.append('a495')
    for i in range(1, 10):
        canon_ps_model_numbers.append(f'a5{i}0')
    for i in range(6):
        canon_ps_model_numbers.append(f'a6{i}0')
    for i in range(3):
        canon_ps_model_numbers.append(f'a7{i}0')
    for i in range(2):
        canon_ps_model_numbers.append(f'a8{i}0')
    for i in range(5):
        canon_ps_model_numbers.append(f'a1{i}00')
    for i in range(7):
        canon_ps_model_numbers.append(f'a2{i}00')
    for model in canon_ps_model_numbers:
        webbrowser.open(fr"https://www.flickr.com/search/?text=%22powershot%20{model}%22")


class Lens:
    def __init__(self, brand: str, ev_step: float, smallest_f_number: float, largest_f_number: float,
                 model: str = None):
        assert brand.strip().lower() in BRANDS
        assert 0 < smallest_f_number <= largest_f_number
        assert ev_step > 0
        for arg in getfullargspec(Lens.__init__)[0]:
            exec(f'self.{arg} = {arg}')

    def aperture_list(self):
        return build_aperture_chart(build_f_number_list(self.smallest_f_number, self.largest_f_number, self.ev_step),
                                    self.ev_step)


class Camera:
    def __init__(self, brand: str, model: str, ev_step: float, shortest_exposure_time: float,
                 longest_exposure_time: float, max_iso: int, min_iso=0, lens: Lens = None):
        assert brand.strip().lower() in BRANDS
        assert ev_step > 0
        assert 0 < shortest_exposure_time <= longest_exposure_time
        assert 0 <= min_iso <= max_iso
        for arg in getfullargspec(Camera.__init__)[0]:
            exec(f'self.{arg} = {arg}')

    def aperture_list(self):
        assert self.lens
        return self.lens.aperture_list()


def write_inventory():
    #    with open('camera_inventory.csv', 'w', newline='') as f:
    #        writer = csv.writer(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
    #        writer.writerow()
    #    with open('lens_inventory.csv', 'w', newline='') as f:
    #        writer = csv.writer(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
    #        writer.writerow()
    pass


def calculate_f_number(stops: float) -> float:
    return 2 ** (stops / 2)


def calculate_stop(f_number: float, stop_step: float) -> float:
    apertures = build_f_number_list(calculate_f_number(0), f_number, stop_step=stop_step)
    differences = [abs(value - f_number) for value in apertures]
    min_index = differences.index(min(differences))
    return min_index * stop_step


def build_f_number_list(smallest_f_number: float, largest_f_number: float, stop_step: float, starting_stop: float = 0):
    assert calculate_f_number(starting_stop) <= smallest_f_number
    assert smallest_f_number < largest_f_number
    f_numbers = []
    while True:
        previous_f_number, current_f_number = calculate_f_number(starting_stop - stop_step), calculate_f_number(
            starting_stop)
        if previous_f_number < smallest_f_number <= current_f_number:
            f_number_pair = [previous_f_number, current_f_number]
            difference_pair = [abs(value - smallest_f_number) for value in f_number_pair]
            f_numbers.append(f_number_pair[difference_pair.index(min(difference_pair))])
            break
        starting_stop += stop_step
    while True:
        current_f_number, next_f_number = calculate_f_number(starting_stop), calculate_f_number(
            starting_stop + stop_step)
        if current_f_number <= largest_f_number < next_f_number:
            f_number_pair = [current_f_number, next_f_number]
            difference_pair = [abs(value - largest_f_number) for value in f_number_pair]
            f_numbers.append(f_number_pair[difference_pair.index(min(difference_pair))])
            break
        f_numbers.append(current_f_number)
        starting_stop += stop_step
    assert len(f_numbers) > 0
    return sorted(list(set(f_numbers)))


def build_aperture_chart(f_numbers: list, stop_step: float):
    def is_integer(value: float):
        if value == floor(value):
            return True
        else:
            return False

    chart = []
    for count, aperture in enumerate(f_numbers):
        if aperture > 8 or is_integer(aperture):
            aperture = round(aperture)
        else:
            aperture = round(aperture, 1)
        # aperture = f'{aperture:.1f}'
        aperture = f'{aperture:^{SEPARATION_LENGTH}}'
        light_multiplier = 2 ** (count * stop_step)
        if is_integer(light_multiplier):
            chart.append(f'{aperture}-->{str(Fraction(1, light_multiplier)):^{SEPARATION_LENGTH}}')
        else:
            chart.append(f'{aperture}')
    return '\n'.join(chart)


# return '\n'.join([f'{aperture:^{SEPARATION_LENGTH}.1f}|{check_if_integer(2 ** (count * stop_step)):^{SEPARATION_LENGTH}.1f}' for count, aperture in enumerate(f_numbers)])

def run_this_script():
    print_line()

    a570is = Camera(brand='Canon', model='Powershot A570IS', ev_step=Fraction(1, 3),
                    lens=Lens(brand='Canon', ev_step=Fraction(1, 3), smallest_f_number=XXX.XXX.XXX.XXX,
                              largest_f_number=XXX.XXX.XXX.XXX),
                    shortest_exposure_time=Fraction(1, 2000), longest_exposure_time=15, max_iso=1600)
    print(f'{a570is.brand} {a570is.model}'.center(SEPARATION_LENGTH))
    print(a570is.aperture_list())

    print_line()

    kodak_z915 = Camera(brand='Kodak', model='EasyShare Z915', ev_step=Fraction(1, 3),
                     lens=Lens(brand='Leica', ev_step=Fraction(1, 3), smallest_f_number=XXX.XXX.XXX.XXX,
                               largest_f_number=XXX.XXX.XXX.XXX),
                     shortest_exposure_time=Fraction(1, 2000), longest_exposure_time=60, max_iso=1600)
    print(f'{kodak_z915.brand} {kodak_z915.model}'.center(SEPARATION_LENGTH))
    print(kodak_z915.aperture_list())

    print_line()

    olympus_c5050 = Camera(brand='Olympus', model='Camedia C-5050', ev_step=Fraction(1, 3),
                   lens=Lens(brand='Olympus', ev_step=Fraction(1, 3), smallest_f_number=XXX.XXX.XXX.XXX,
                             largest_f_number=XXX.XXX.XXX.XXX),
                   shortest_exposure_time=Fraction(1, 4000), longest_exposure_time=30, max_iso=12800)
    print(f'{olympus_c5050.brand} {olympus_c5050.model}'.center(SEPARATION_LENGTH))
    print(olympus_c5050.aperture_list())

    write_inventory()

    for count, image in enumerate(filter_images_by_camera('5050',
                                                          find(path=Path.home().joinpath(DATA_DRIVE_PATH, 'numbered',
                                                                                         'photos'),
                                                               file_type='f', name_filter=r'.*\.(?:jpe?g|png)',
                                                               case_sensitive=False))):
        print(image)


if __name__ == '__main__':
    run_this_script()
