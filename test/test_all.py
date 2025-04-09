import unittest

def load_tests(loader, tests, pattern):
    package1_tests = loader.discover('common', pattern='*Test.py')
    
    all_tests = unittest.TestSuite()
    all_tests.addTests(package1_tests)

    return all_tests


if __name__ == "__main__":
    unittest.main()
    



