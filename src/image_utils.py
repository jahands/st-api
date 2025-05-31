"""
Image processing utilities for text classification.
Based on the original image_manipulate_utils.py
"""

from typing import NamedTuple, cast
import numpy as np
from PIL import Image


class Box(NamedTuple):
    left: int
    top: int
    width: int
    height: int


def filter_rgb_color_range(img: np.ndarray, p0: tuple[int, int, int], p1: tuple[int, int, int]) -> np.ndarray:
    """Filter image to only include pixels within the specified RGB color range."""
    masks = [
        (img >= p0[i]) & (img <= p1[i])
        for i in range(3)
    ]
    return cast(np.ndarray, np.all(masks, axis=0))


def find_structure_points(arr: np.ndarray, x0: int, y0: int) -> list[tuple[int, int]]:
    """Find all connected points starting from (x0, y0). Modifies arr in place."""
    structure_points: list[tuple[int, int]] = []
    fringe = [(x0, y0)]
    while len(fringe):
        (x, y) = fringe.pop()
        if arr[x, y]:
            arr[x, y] = False
            structure_points.append((x, y))
            new_x_vals = [x-1, x, x+1]
            new_y_vals = [y-1, y, y+1]
            for new_x in new_x_vals:
                if new_x < 0 or new_x >= arr.shape[0]:
                    continue
                for new_y in new_y_vals:
                    if new_y < 0 or new_y >= arr.shape[1]:
                        continue
                    if arr[new_x, new_y]:
                        fringe.append((new_x, new_y))
    return structure_points


def points_to_binary_image(points: list[tuple[int, int]]) -> tuple[Box, np.ndarray]:
    """Convert a list of points to a binary image with bounding box."""
    x0 = min(points, key=lambda p: p[0])[0]
    y0 = min(points, key=lambda p: p[1])[1]
    x1 = max(points, key=lambda p: p[0])[0]
    y1 = max(points, key=lambda p: p[1])[1]
    image_position = Box(x0, y0, x1-x0+1, y1-y0+1)
    image = np.zeros((x1-x0+1, y1-y0+1), dtype=bool)
    for x, y in points:
        image[x-x0, y-y0] = True
    return image_position, image


def find_connected_disjoint_structures(arr: np.ndarray) -> list[tuple[Box, np.ndarray]]:
    """Find all connected components in a binary image."""
    structures: list[tuple[Box, np.ndarray]] = []
    for x in range(arr.shape[0]):
        for y in range(arr.shape[1]):
            if arr[x, y]:
                points = find_structure_points(arr, x, y)
                structures.append(points_to_binary_image(points))
    return structures


def pad_combine(images: list[np.ndarray]) -> np.ndarray:
    """Pad all images to the same size and stack them."""
    shape: tuple[int, int] = (
        max([i.shape[0] for i in images]), max([i.shape[1] for i in images]))
    return np.stack([np.pad(img, ((0, shape[0]-img.shape[0]), (0, shape[1]-img.shape[1]))) for img in images])


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Preprocess an image for digit classification.
    
    Args:
        image: PIL Image to process
        
    Returns:
        Binary numpy array ready for structure detection
    """
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array
    image_array = np.array(image)
    
    # Filter for text color range (adjust these values based on your specific use case)
    # These values are from the original eval_forest.py
    filtered = filter_rgb_color_range(image_array, (160, 154, 157), (255, 255, 255))
    
    # Convert to binary
    binary_image = np.all(filtered != 0, -1)
    
    return binary_image


def extract_digit_structures(image: Image.Image) -> list[tuple[Box, np.ndarray]]:
    """
    Extract individual digit structures from an image.
    
    Args:
        image: PIL Image containing digits
        
    Returns:
        List of (bounding_box, binary_image) tuples for each detected structure
    """
    # Preprocess the image
    binary_image = preprocess_image(image)
    
    # Find connected components
    structures = find_connected_disjoint_structures(binary_image)
    
    return structures
