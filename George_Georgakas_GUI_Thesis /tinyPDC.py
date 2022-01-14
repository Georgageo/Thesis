from synchrophasor.pdc import Pdc
from synchrophasor.frame import DataFrame, CommandFrame
import time
import argparse
"""
tinyPDC will connect to pmu_ip:pmu_port and send request
for header message, configuration and eventually
to start sending measurements.
"""


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-PDC", "--pdc", type=str, default='127.0.0.1',
                        help="IP of PMU")

    # parser.add_argument("square", type=int,
    #                     help="display a square of a given number")

    args = parser.parse_args()
    # answer = args.square
    pmu_ip = args.pdc

    pdc = Pdc(pdc_id=7, pmu_ip=pmu_ip, pmu_port=4712)
    pdc.logger.setLevel("DEBUG")

    pdc.run()  # Connect to PMU

    header = pdc.get_header()  # Get header message from PMU
    config = pdc.get_config()  # Get configuration from PMU

    pdc.start()  # Request to start sending measurements
    counter = 1
    while True:

        data = pdc.get()  # Keep receiving data
        # if counter == 14:
        #     pdc.stop()
        #     pdc.quit()
        #     break
        if type(data) == DataFrame:
            print(data.get_measurements())
        if type(data) == CommandFrame:
            if data.get_command() == 'stop':
                # print(data.get_command())
                time.sleep(1)
                pdc.stop()
                pdc.quit()
                break
        # # if counter>10:
        # #     pdc.quit()
        # #     break

        if not data:
            pdc.quit()  # Close connection
            break
        counter+=1