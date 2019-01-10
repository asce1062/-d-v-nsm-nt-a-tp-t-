"""
Traverse the list to linearly or sequentially, starting from the first element
and move from item to item, following the underlying sequential ordering,
until we either find what we are looking for or until we run out of elements
- Used for unsorted and unordered small lists
- Has time complexity of O(n)- linearly dependent on the elements
"""


def linear_search(elements, search):
    for i in range(0, len(elements)):  # repeat for each item in list
        if search == elements[i]:  # if item at position i is search time
            return (str(search) + " Found in position " + str(i))  # report find

elements = [4, 1, 2, 5, 3]  # set up array
print(linear_search(elements, 5))
