#! python3

from src.core.opgen import OPGen
from src.core.graph import Graph
# from src.core.options import parse_args, setup_graph_env
from src.core.options import parse_args


if __name__ == '__main__':
    opg = OPGen()
    opg.run()

