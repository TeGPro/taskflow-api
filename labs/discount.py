def calculate_discount(price: float, discount: float) -> float:
    if discount >= 0 and discount <= 100:
        return price * (1 - discount / 100)
    raise ValueError("Процент скидки должен быть от 0 до 100")