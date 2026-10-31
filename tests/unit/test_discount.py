from labs.discount import calculate_discount
from pytest import raises

def test_discount_normal():
    assert calculate_discount(100, 10) == 90
    
def test_discount_full():
    assert calculate_discount(100, 100) == 0
    
def test_discount_invalid():
    with raises(ValueError):
        calculate_discount(100, 150)
        
def test_discount_zero():
    assert calculate_discount(100, 0) == 100