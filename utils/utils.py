
def find_dict(my_list, key, value):
    """
    Ищет словарь в списке my_list, который содержит значение value для ключа key.
    """
    for d in my_list:
        if str(d.get(key)) == value:
            return d
    return None


def update_category(categories, user_categories, category_id):
    user_categories.append({
        "id": category_id,
        "name": find_dict(categories, "_id", category_id)["name"]
    })
    return user_categories


def delete_category(user_categories, category_id):
    for d in user_categories:
        if str(d.get("id")) == category_id:
            user_categories.remove(d)
            break
    return user_categories
