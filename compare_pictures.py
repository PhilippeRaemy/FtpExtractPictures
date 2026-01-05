from PIL import Image
import imagehash

# Load the images
hash1 = imagehash.average_hash(Image.open("image_A.jpg"))
hash2 = imagehash.average_hash(Image.open("image_B_resized_compressed.jpg"))

# 1. Calculate the Hamming Distance (D)
# The distance is the number of bits that are different.
distance = hash1 - hash2 # This subtraction is overloaded to compute the Hamming distance

# 2. Get the maximum possible distance
MAX_DISTANCE = len(hash1.hash.flatten()) # This will typically be 64 for an average_hash

# 3. Calculate the Similarity Factor (Percentage)
similarity_factor = 100 * (1 - distance / MAX_DISTANCE)

print(f"Hamming Distance: {distance}")
print(f"Similarity Factor: {similarity_factor:.2f}%")