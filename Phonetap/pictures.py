import os
from datetime import datetime

from PIL import Image
from pathlib import Path
import imagehash


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


def deduplicate(folder, dry_run, verbose, show, hash_size, similarity=0.8):
    print('deduplicate')

    pic_dic = {}
    max_distance = 0
    for pic in os.listdir(folder):
        if pic.endswith('.jpg'):
            pic_file = os.path.join(folder, pic)
            picture = Picture(pic_file)
            hash = picture.hash
            if max_distance == 0:
                max_distance = len(hash.hash.flatten())  # This will typically be 64 for an average_hash
            similar_hash = next((k for k in pic_dic.keys() if 1 - (k - hash) / max_distance >= similarity), None)
            if similar_hash is None:
                pic_dic[hash] = {'file': pic_file, 'images': [picture]}
                if show:
                    pass
                    # im.show()
                if verbose:
                    print(f'{pic_file} is original')
            else:
                pic_dic[similar_hash]['images'].append(picture)
                if verbose:
                    print(f'{pic_file} is similar to {pic_dic[similar_hash]['file']}')
