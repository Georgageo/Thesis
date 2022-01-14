import threading
import argparse
from synchrophasor.pmu import Pmu
import time

"""
tinyPMU will listen on ip:port for incoming connections.
When tinyPMU receives command to start sending
measurements - fixed (sample) measurement will
be sent.
"""




if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-PMU", "--pmu", type=str, default='127.0.0.1',
                        help="IP of PMU")

    # parser.add_argument("square", type=int,
    #                     help="display a square of a given number")

    args = parser.parse_args()
    # answer = args.square
    pmu_ip = args.pmu

    pmu = Pmu(ip=pmu_ip, port=4712)
    # pmu = Pmu(ip="127.0.0.1", port=1410)
    pmu.logger.setLevel("DEBUG")

    pmu.set_configuration()  # This will load default PMU configuration specified in IEEE C37.118.2 - Annex D (Table D.2)
    pmu.set_header()  # This will load default header message "Hello I'm tinyPMU!"

    pmu.run()  # PMU starts listening for incoming connections

    counter = 1
    while True:
        if pmu.clients: # Check if there is any connected PDCs
            # pmu.send(pmu.ieee_data_sample)
            if counter<=50:
                pmu.send(pmu.ieee_data_sample)  # Sending sample data frame specified in IEEE C37.118.2 - Annex D (Table D.1)
                counter+=1
            else:
                # pmu.ieee_command_sample.set_command('stop')
                # pmu.send(pmu.ieee_command_sample)
                break
    pmu.ieee_command_sample.set_command('stop')
    pmu.send(pmu.ieee_command_sample)
    time.sleep(3)

    # pmu.join()

