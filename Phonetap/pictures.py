import os
import shutil
import subprocess
from datetime import datetime

from PIL import Image, UnidentifiedImageError
from pathlib import Path
import imagehash
from send2trash import send2trash

from Phonetap.utils import Tracer


class Picture:
    def __init__(self, image_file, hash_size, algorithm):
        self.hash_size = hash_size
        self.file = image_file
        im = Image.open(image_file)
        self._hash = None
        self._pixels = None
        image_path = Path(image_file)
        stats = image_path.stat()
        self.size = stats.st_size
        self.creation_timestamp = stats.st_ctime
        self.creation_date = datetime.fromtimestamp(self.creation_timestamp)

        if algorithm == 'average':
            self._get_hash = lambda im: imagehash.average_hash(im, hash_size=hash_size)
        elif algorithm == 'dhash':
            self._get_hash = lambda im: imagehash.dhash(im, hash_size=hash_size)
        else:
            raise ValueError(f"Invalid value for algorithm : {algorithm}")

    def __lt__(self, other) -> bool:
        if not isinstance(other, Picture):
            raise ValueError(f'cannot compare a {type(self).__name__} with a {type(other).__name__}')
        return (self.pixels < other.pixels  # fewer pixels
                or (self.pixels == other.pixels and self.size < other.size)  # same resolution but smaller file
                or (self.pixels == other.pixels and self.size == other.size  # same resolution and file size but younger
                    and self.creation_timestamp > other.creation_timestamp))

    def __gt__(self, other) -> bool:
        return not self.__lt__(other)

    def similarity(self, other):
        if not isinstance(other, Picture):
            raise ValueError(f'cannot compare a {type(self).__name__} with a {type(other).__name__}')
        return 1 - (self.hash - other.hash) / len(self.hash.hash.flatten())

    @property
    def hash(self):
        if not self._hash:
            im = Image.open(self.file)
            self._pixels = im.width * im.height
            self._hash = self._get_hash(im)
        return self._hash

    @property
    def pixels(self):
        if not self._pixels:
            im = Image.open(self.file)
            self._pixels = im.width * im.height
        return self._pixels


def get_hash(image, show, hash_size):
    im = Image.open(image)
    if show:
        im.show()
    return im, imagehash.average_hash(im, hash_size=hash_size)


def compare(first, second, show, hash_size):
    # Load the images
    im1, hash1 = get_hash(first, show, hash_size)
    im2, hash2 = get_hash(second, show, hash_size)

    # 1. Calculate the Hamming Distance (D)
    # The distance is the number of bits that are different.
    distance = hash1 - hash2  # This subtraction is overloaded to compute the Hamming distance

    # 2. Get the maximum possible distance
    MAX_DISTANCE = len(hash1.hash.flatten())  # This will typically be 64 for an average_hash

    # 3. Calculate the Similarity Factor (Percentage)
    similarity_factor = 100 * (1 - distance / MAX_DISTANCE)

    print(f"Hamming Distance: {distance}")
    print(f"Similarity Factor: {similarity_factor:.2f}%")


def deduplicate(folder, file_types, run_mode, verbose, show, hash_size, algorithm, similarity):
    dry_run = (run_mode == "dry")
    tracer = Tracer(verbose=verbose or dry_run)
    ptracer = Tracer(verbose=verbose or dry_run, indent=None, newline='\r')
    itracer = Tracer(verbose=verbose or dry_run, indent=2)

    extensions = ['.' + e for e in file_types.split(',')]
    similarity = similarity / 100  # entered as a percentage
    pic_dic = {}
    max_distance = 0
    for pic in os.listdir(folder):
        if any((pic.endswith(e) for e in extensions)):
            pic_file = os.path.join(folder, pic)
            try:
                picture = Picture(pic_file, hash_size=hash_size, algorithm=algorithm)
            except UnidentifiedImageError as ex:
                tracer.trace(str(ex))
                continue
            hash = picture.hash
            if max_distance == 0:
                max_distance = len(hash.hash.flatten())  # This will typically be 64 for an average_hash
            similar_hash = next((k for k in pic_dic.keys() if 1 - (k - hash) / max_distance >= similarity), None)
            if similar_hash is None:
                pic_dic[hash] = {'file': pic_file, 'images': [picture]}
                if show:
                    pass
                    # im.show()
                ptracer.chat(original=pic_file)
            else:
                images = pic_dic[similar_hash]['images']
                images.append(picture)
                pic_dic[similar_hash]['images'] = sorted(images, reverse=True)
                tracer.chat(file=pic_file, similar_to=pic_dic[similar_hash]['file'])
                if show:  # keep all the references and delay delete
                    pic_dic[similar_hash]['file'] = pic_dic[similar_hash]['images'][0].file
                else:
                    for im in images[1:]:
                        tracer.chat(redundant=im.file)
                        send2trash(im.file)
                    pic_dic[similar_hash]['images'] = images[1]
    for hash, pics in pic_dic.items():
        images = pics['images']
        if len(images) < 2:
            continue
        best = images[0]
        itracer.trace(
            keep=best.file,
            redundant={im.file: im.similarity(best) for im in images[1:]}
        )
        if show and run_mode in ('dry', 'bin', 'del'):
            for image in images:
                subprocess.run(["cmd", '/c', 'start', image.file])
            input('Press enter to continue')
        if run_mode == 'dry':
            pass
        elif run_mode == 'bin':
            for im in images[1:]:
                send2trash(im.file)
        elif run_mode == 'del':
            for im in images[1:]:
                os.remove(im.file)
        elif run_mode == 'shelve':
            im = images[0]
            shelf = '.'.join(im.file.split('.')[:-1])  # remove extension
            os.makedirs(shelf, exist_ok=True)
            for im in images:
                shutil.move(im.file, shelf)
