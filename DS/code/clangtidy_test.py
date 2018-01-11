import unittest

class TestSummaryEvaluation(unittest.TestCase):
    def setUp(self):
        pass

    def test_error_tests_line(self):
        line = "Errors:   1690"
        bs = ClangTidy()
        bs.gatherTestStatistics(line)
        self.assertEqual("1690", bs.errors)

    def test_warning_tests_line(self):
        line = "Warnings: 166"
        bs = ClangTidy()
        bs.gatherTestStatistics(line)
        self.assertEqual("166", bs.warnings)

    def test_all_in_block_passed(self):
        line = """=====================
                 ClangTidy summary
               =====================
               Errors:   0
               Warnings: 166"""
        bs = ClangTidy()
        bs.gatherTestStatistics(line)
        self.assertEqual("0", bs.errors)

    def test_all_in_block_failed(self):
        line = """=====================
                 ClangTidy summary
               =====================
               Errors:   614
               Warnings: 154"""
        bs = ClangTidy()
        bs.gatherTestStatistics(line)
        self.assertEqual("614", bs.errors)
        self.assertEqual("154", bs.warnings)


if __name__ == "__main__":
    unittest.main()
