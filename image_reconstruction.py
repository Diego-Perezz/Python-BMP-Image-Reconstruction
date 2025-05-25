from image import Image  # or your image library
import images  # if needed


class Node:
    """
    A Node in a doubly-linked list, storing an image strip and pointers to prev & next.
    """
    def __init__(self, strip):
        """
        Initialize a Node with the given 'strip'.

        param strip: (Image) The image strip to be stored in this Node.
        """

        self.strip = strip
        self.prev = None
        self.next = None

class LinkedList:
    """
    A doubly-linked list specialized for storing and ordering image strips.
    """
    def __init__(self, strip):
        """
        Initialize the linked list with a single 'strip' as both head and tail.

        param strip: (Image) The initial image strip to place in the LinkedList.
        """
        node = Node(strip)
        self.head = node
        self.tail = node

    def prepend(self, strip):
        """
        Insert a new strip at the head (start) of the list.

        param strip: (Image) The image strip to prepend.
        """
        new_node = Node(strip)
        new_node.next = self.head
        self.head.prev = new_node
        self.head = new_node

    def append(self, strip):
        """
        Insert a new strip at the tail (end) of the list.

        param strip: (Image) The image strip to append.
        """
        new_node = Node(strip)
        new_node.prev = self.tail
        self.tail.next = new_node
        self.tail = new_node

    def to_list(self):
        """
        Convert this linked list into a standard Python list of strips, from head to tail.

        return: (list of Image) All strips in order (head -> tail).
        """
        current = self.head
        ordered_strips = []
        while current:
            ordered_strips.append(current.strip)
            current = current.next
        return ordered_strips




def load_image_strips(file_names):
    """
    Load multiple .bmp images given a list of filenames.

    param file_names: (list of str) Filenames of .bmp image strips.
    return: (list of Image) The list of loaded image strips.
    """
    return [Image.read_bmp(file) for file in file_names]


def rows_comparison(rowA, rowB):
    """
    Compute a sum of squared differences between two rows of pixels.

    param rowA: (list of Pixel) First row of Pixel objects.
    param rowB: (list of Pixel) Second row of Pixel objects.

    return: (int or float) The computed difference measure (lower = more similar).
    """
    return sum(
        (p1.get_r() - p2.get_r()) ** 2 +
        (p1.get_g() - p2.get_g()) ** 2 +
        (p1.get_b() - p2.get_b()) ** 2
        for p1, p2 in zip(rowA, rowB)
    )


def find_bottom_strip(strips):
    """
    Identify the strip that belongs at the bottom by finding the worst "top-row" match
    among all possible comparisons. The logic assumes a strip that cannot match well
    below any other strip is effectively at the bottom.

    param strips: (list of Image) Unsorted strips to examine.

    return: (Image) The single Image determined to be the bottom-most strip.
    """
    best_strip = None
    worst_match_score = -1  # Higher values mean less similarity

    for candidate in strips:
        bottom_row = candidate.pixels[-1]

        # Find the best (lowest) match with another strip’s top row
        best_match_score = min(
            rows_comparison(bottom_row, other.pixels[0])
            for other in strips if other != candidate
        )

        # We select the strip with the **worst** best match
        if best_match_score > worst_match_score:
            worst_match_score = best_match_score
            best_strip = candidate

    return best_strip


def find_most_similar_strip_for_upwards(current_top_strip, candidate_strips):
    """
    Find the best match to place above 'current_top_strip' by comparing
    'current_top_strip' top row to the candidates' bottom rows.

    param current_top_strip: (Image) The strip currently at the top.
    param candidate_strips: (list of Image) Remaining strips to check.

    return: (Image or None) The best match strip to go above, or None if no match is found.
    """

    # We want the new strip's bottom row to match current's top row.
    best_match = None
    best_distance = float("inf")
    
    current_top_row = current_top_strip.pixels[0]
    for candidate in candidate_strips:
        candidate_bottom_row = candidate.pixels[-1]
        distance = rows_comparison(current_top_row, candidate_bottom_row)
        if distance < best_distance:
            best_distance = distance
            best_match = candidate
    return best_match


def build_from_bottom(image_strips):
    """
    Construct a top-to-bottom sequence of strips starting from the identified bottom strip
    and attaching new strips above it until no more matches can be found.

    param image_strips: (list of Image) The set of all strips to order.

    return: (list of Image) The ordered strips from top to bottom.
    """
    # 1. Find & remove the true bottom strip
    bottom_strip = find_bottom_strip(image_strips)
    image_strips.remove(bottom_strip)

    # 2. Initialize linked list with bottom strip
    linked = LinkedList(bottom_strip)

    # 3. Keep PREPENDING new strips on top
    while image_strips:
        current_top_strip = linked.head.strip
        best_match = find_most_similar_strip_for_upwards(current_top_strip, image_strips)
        if best_match is None:
            break
        linked.prepend(best_match)
        image_strips.remove(best_match)

    return linked.to_list()


def merge_ordered_strips(ordered_strips):
    """
    Merge a list of strips (in top-to-bottom order) into a single tall Image.

    param ordered_strips: (list of Image) Strips in the correct vertical order.
    return: (Image) A new Image composed of all strips stacked vertically.
    """
    total_height = sum(strip.get_height() for strip in ordered_strips)
    width = ordered_strips[0].get_width()
    final_image = Image(width, total_height)

    current_height = 0
    for strip in ordered_strips:
        for row in range(strip.get_height()):
            for col in range(strip.get_width()):
                final_image.set_pixel(current_height + row, col, strip.get_pixel(row, col))
        current_height += strip.get_height()
    return final_image


def save_image(image, filename):
    """
    Save the given Image object to disk as a BMP file.

    param image: (Image) The final merged image to save.
    param filename: (str) Destination .bmp filename.
    """
    image.save_bmp(filename)


def main():
    """
    Main execution workflow:
      1) Load 16 strips.
      2) Build from the identified bottom strip upwards.
      3) Merge all strips into a final image.
      4) Save the result.
    """
    file_names = [f"images/image_strip_{i}.bmp" for i in range(16)]
    image_strips = load_image_strips(file_names)

    # Build from the bottom-most (white) strip up
    ordered = build_from_bottom(image_strips)
    
    merged_image = merge_ordered_strips(ordered)
    save_image(merged_image, "final_reconstructed.bmp")

if __name__ == "__main__":
    main()





