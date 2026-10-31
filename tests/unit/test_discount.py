import pytest

from labs.discount import calculate_discount


# def test_discount_normal():
#     assert calculate_discount(100, 10) == 90


# def test_discount_full():
#     assert calculate_discount(100, 100) == 0


# def test_discount_invalid():
#     with pytest.raises(ValueError):
#         calculate_discount(100, 150)
        


# def test_discount_zero():
#     assert calculate_discount(100, 0) == 100
    
# Реализуем с помощью @pytest.mark.parametrize

@pytest.mark.parametrize("value, discount, expected", [(100, 10, 90), 
                                                        (100, 100, 0), 
                                                        (100, 0, 100)])
class TestDiscount:
    def test_discount(self, value, discount, expected):
        assert calculate_discount(value, discount) == expected



@pytest.mark.parametrize("value, discount", [(100, -10),   
                                                        (100, 101), 
                                                        (100, 150)])
def test_discount_invalid(value, discount):
    with pytest.raises(ValueError):
        calculate_discount(value, discount)
        
@pytest.fixture
def discount_data():
    print("Подготовка данных")
    yield {"price":200,
            "discount": 25,
            "expected": 150}
    print("Очистка данных")

def test_discount_fixture(discount_data):
    assert calculate_discount(discount_data['price'], discount_data['discount']) == discount_data['expected']
    