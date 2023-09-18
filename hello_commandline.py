# import sys
# import argparse


# class ArgumentParserForBlender(argparse.ArgumentParser):

#     def _get_argv_after_doubledash(self):
#         try:
#             idx = sys.argv.index("--")
#             return sys.argv[idx + 1:]  # the list after '--'
#         except ValueError as e:  # '--' not in the list:
#             return []

#     # overrides superclass
#     def parse_args(self):
#         return super().parse_args(args=self._get_argv_after_doubledash())


# parser = ArgumentParserForBlender()


# parser.add_argument("-q", "--quack",
#                     action="store_true",
#                     help="Quacks bar times if activated.")
# parser.add_argument("-b", "--bar", type=int, default=10,
#                     help="Number of desired quacks")
# args = parser.parse_args()
# QUACK = args.quack
# BAR = args.bar

# if QUACK:
#     print("QUACK " * BAR)

print(True+True)