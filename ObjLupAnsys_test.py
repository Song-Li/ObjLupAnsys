#! python3
import unittest
from src.core.opgen import OPGen
from src.core.options import options

class BasicTests(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        options.run_all = True
        self.opgen = OPGen()

    def tearDown(self):
        """Call after every test case."""
        pass

    def test_set_value(self):
        """
        run the os command test
        """
        options.vul_type = 'proto_pollution'
        file_loc = "./tests/packages/set-value"
        self.opgen.get_new_graph(package_name=file_loc)
        self.opgen.test_module(file_loc)
        assert len(self.opgen.graph.detection_res['proto_pollution']) != 0

    def test_property_expr(self):
        """
        run the os command test
        """
        options.vul_type = 'proto_pollution'
        file_loc = "./tests/packages/property-expr"
        self.opgen.get_new_graph(package_name=file_loc)
        self.opgen.test_module(file_loc, vul_type="proto_pollution", G=self.opgen.graph)
        assert len(self.opgen.graph.detection_res['proto_pollution']) != 0

    def test_pp(self):
        """
        run the pp test
        """
        file_loc = "./tests/packages/pp.js"
        options.vul_type = 'proto_pollution'
        self.opgen.get_new_graph(package_name=file_loc)
        self.opgen.test_module(file_loc, vul_type='proto_pollution')
        assert len(self.opgen.graph.detection_res['proto_pollution']) != 0

if __name__ == "__main__":
    unittest.main(warnings='ignore')
