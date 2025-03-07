import pybinsim2

if __name__ == "__main__":

    with pybinsim2.BinSim('config/demo1.cfg') as binsim:
        binsim.stream_start()

