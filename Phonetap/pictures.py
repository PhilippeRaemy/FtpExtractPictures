import os
import subprocess
from datetime import datetime

from PIL import Image, UnidentifiedImageError
from pathlib import Path
import imagehash
from send2trash import send2trash

from Phonetap.utils import Tracer


class Picture:
    def __init__(self, image_file, hash_size):
        self.file = image_file
        im = Image.open(image_file)
        self.hash = imagehash.average_hash(im, hash_size=hash_size)
        self.pixels = im.width * im.height
        image_path = Path(image_file)
        stats = image_path.stat()
        self.size = stats.st_size
        self.creation_timestamp = stats.st_ctime
        self.creation_date = datetime.fromtimestamp(self.creation_timestamp)

    def __lt__(self, other) -> bool:
        if not isinstance(other, Picture):
            raise ValueError(f'cannot compare a {type(self).__name__} with a {type(other).__name__}')
        return (self.pixels < other.pixels
                or self.size < other.size
                or self.creation_timestamp > other.creation_timestamp)

    def __gt__(self, other) -> bool:
        return other < self

    def similarity(self, other):
        if not isinstance(other, Picture):
            raise ValueError(f'cannot compare a {type(self).__name__} with a {type(other).__name__}')
        return 1 - (self.hash - other.hash) / len(self.hash.flatten())


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


def deduplicate(folder, dry_run, verbose, show, hash_size, file_types, similarity):
    tracer = Tracer(verbose=verbose or dry_run)
    itracer = Tracer(verbose=verbose or dry_run, indent=2)
    tracer.chat('deduplicate',
                folder=folder,
                dry_run=dry_run,
                verbose=verbose,
                show=show,
                hash_size=hash_size,
                similarity=similarity)

    extensions = ['.' + e for e in file_types.split(',')]
    similarity = similarity / 100  # entered as a percentage
    pic_dic = {}
    max_distance = 0
    for pic in os.listdir(folder):
        if any((pic.endswith(e) for e in extensions)):
            pic_file = os.path.join(folder, pic)
            try:
                picture = Picture(pic_file, hash_size=hash_size)
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
                tracer.chat(original=pic_file)
            else:
                images = sorted(pic_dic[similar_hash]['images'] + [picture], reverse=True)
                pic_dic[similar_hash]['images'] = images
                tracer.chat(file=pic_file, similar_to=pic_dic[similar_hash]['file'])
                if show:  # keep all the references and delay delete
                    pic_dic[similar_hash]['file'] = pic_dic[similar_hash]['images'][0].file
                else:
                    for im in images[1:]:
                        tracer.chat(redundant=im.file)
                        send2trash(im.file)
                    pic_dic[similar_hash]['images'] = images[1]
    if show:
        for hash, pics in pic_dic.items():
            images = pics['images']
            if len(images) < 2:
                continue
            for image in images:
                subprocess.run(["cmd", '/c', 'start', image.file])
            itracer.trace(
                keep=images[0].file,
                redundant={im.file: int(100 - (im.hash - hash) / max_distance * 100) for im in images[1:]}
            )
            input('Press enter to continue')
            if not dry_run:
                for im in images[1:]:
                    send2trash(im.file)
