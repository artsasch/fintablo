import unittest
from idle import extract_nds


class TestExtractNDS(unittest.TestCase):

    def test1(self):
        test_input = "ЗАЧИСЛЕНИЕ СРЕДСТВ НА РЕКЛАМНЫЙ АККАУНТ. ВТ.Ч. НДС 20 %"
        expected_output = 20
        self.assertEqual(extract_nds(test_input), expected_output)
        
    def test2(self):
        test_input = "ЗАЧИСЛЕНИЕ СРЕДСТВ НА РЕКЛАМНЫЙ АККАУНТ. ВТ.Ч. НДС 100500 В РАЗМЕРЕ 20 %"
        expected_output = 20
        self.assertEqual(extract_nds(test_input), expected_output)
        
    def test3(self):
        test_input = "ЗАЧИСЛЕНИЕ СРЕДСТВ НА РЕКЛАМНЫЙ АККАУНТ. ВТ.Ч. 20 % НДС"
        expected_output = None
        self.assertEqual(extract_nds(test_input), expected_output)
        
    def test4(self):
        test_input = "ЗАЧИСЛЕНИЕ СРЕДСТВ НА РЕКЛАМНЫЙ АККАУНТ. ВТ.Ч. НДС Я НЕ ЛЮБЛЮ 20 30"
        expected_output = None
        self.assertEqual(extract_nds(test_input), expected_output)
        
    def test5(self):
        test_input = "ЗАЧИСЛЕНИЕ СРЕДСТВ НА РЕКЛАМНЫЙ АККАУНТ. ВТ.Ч. НДС Я НЕ ЛЮБЛЮ 20 30%"
        expected_output = 30
        self.assertEqual(extract_nds(test_input), expected_output)


if __name__ == '__main__':
    unittest.main()
