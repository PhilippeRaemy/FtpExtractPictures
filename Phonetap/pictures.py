import os

from PIL import Image
import imagehash


def get_hash(image, show):
    im = Image.open(image)
    if show:
        im.show()
    return im, imagehash.average_hash(im, hash_size=64)


def compare(first, second, show=False):
    # Load the images
    im1, hash1 = get_hash(first, show)
    im2, hash2 = get_hash(second, show)

    # 1. Calculate the Hamming Distance (D)
    # The distance is the number of bits that are different.
    distance = hash1 - hash2  # This subtraction is overloaded to compute the Hamming distance

    # 2. Get the maximum possible distance
    MAX_DISTANCE = len(hash1.hash.flatten())  # This will typically be 64 for an average_hash

    # 3. Calculate the Similarity Factor (Percentage)
    similarity_factor = 100 * (1 - distance / MAX_DISTANCE)

    print(f"Hamming Distance: {distance}")
    print(f"Similarity Factor: {similarity_factor:.2f}%")


def deduplicate(folder, dry_run, verbose, show, similarity=0.8):
    print('deduplicate')

    pic_dic = {}
    max_distance = 0
    for pic in os.listdir(folder):
        if pic.endswith('.jpg'):
            pic_file = os.path.join(folder, pic)
            im, hash = get_hash(pic_file, False)
            if max_distance == 0:
                max_distance = len(hash.hash.flatten())  # This will typically be 64 for an average_hash
            similar_hash = next((k for k in pic_dic.keys() if 1 - (k - hash) / max_distance >= similarity), None)
            if similar_hash is None:
                pic_dic[hash] = {'file': pic_file, 'images': [im]}
                if show:
                    im.show()
                if verbose:
                    print(f'{pic_file} is original')
            else:
                pic_dic[similar_hash]['images'].append(im)
                if verbose:
                    print(f'{pic_file} is similar to {pic_dic[similar_hash]['file']}')

