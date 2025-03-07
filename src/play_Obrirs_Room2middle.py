import pybinsim2
import datetime

if __name__ == "__main__":

	trackingDataFile = open('trackingdata.txt', 'a')
	now = datetime.datetime.now()
	trackingDataFile.write(str('++++ Scene Obrirs_Room2middle started +++++++++++  ') + str(now.isoformat()) + str('\n'))
	trackingDataFile.close()

	with pybinsim2.BinSim('../config/Obrirs_Room2middle.cfg') as binsim:
		binsim.stream_start()
