from PIL import Image
import imagehash

def get_hash(image, show):
    im = Image.open(image)
    if show:
        im.show()
    return im, imagehash.average_hash(im)


def compare(first, second, show=False):
    # Load the images
    im1, hash1 = get_hash(first, show)
    im2, hash2 = get_hash(second, show)

    # 1. Calculate the Hamming Distance (D)
    # The distance is the number of bits that are different.
    distance = hash1 - hash2 # This subtraction is overloaded to compute the Hamming distance

    # 2. Get the maximum possible distance
    MAX_DISTANCE = len(hash1.hash.flatten()) # This will typically be 64 for an average_hash

    # 3. Calculate the Similarity Factor (Percentage)
    similarity_factor = 100 * (1 - distance / MAX_DISTANCE)

    print(f"Hamming Distance: {distance}")
    print(f"Similarity Factor: {similarity_factor:.2f}%")

