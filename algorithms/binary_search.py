"""
Searches through sorted lists using divide and conquer strategy.
Starts by examining the middle element. If the middle element is equal to the
element we are searching for, we are done. Else, if the element we are
searching for is is greater that  the middle item, we know the lower half
of the list as well as the middle element can be eliminated from
consideration. We repear the process for the upper half.
- Has time complexity of O(log n)
"""


def binary_search_implementation(number_list, search_item):

    list_size = len(number_list) - 1

    first_index = 0
    last_index = list_size

    while first_index <= last_index:
        midpoint = (first_index + last_index)//2

        if number_list[midpoint] == search_item:
            return str(search_item)+' Found at position '+str(midpoint)
        if number_list[midpoint] < search_item:
            first_index = midpoint + 1
        else:
            last_index = midpoint - 1


elements = [1, 2, 3, 4, 5]
print(binary_search_implementation(elements, 4))
