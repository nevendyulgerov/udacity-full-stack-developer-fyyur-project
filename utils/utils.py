def find_area_index_by_location(areas, city, state):
    target_area_index = -1

    for area_index in range(len(areas)):
        area = areas[area_index]
        if area['city'] == city and area['state'] == state:
            target_area_index = area_index
            break

    return target_area_index
