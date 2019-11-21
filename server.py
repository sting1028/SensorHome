from flask import Flask, render_template
import os, sys, click, logging
from multiprocessing import Process
from threading import Timer
from pathlib import Path
from datetime import datetime
from DataManager import DataManager

app = Flask(__name__)
global data_manager


@click.option('debug', default=False, is_flag=True)
@click.option('--port', default=8888)
def startServer(port, debug):
    log_config()
    global data_manager
    data_manager = DataManager(debug=debug)
    logger = logging.getLogger(__name__)
    logger.info(f'Running SensorHome server in port {port}.')
    app.run(port=port, debug=debug, host='0.0.0.0')


def startDataRead():
    global data_manager
    data_manager.readSensorData()
    Timer(60, startDataRead).start()


@app.route('/')
def index():
    global data_manager
    results_time, results_temp, results_pressure = data_manager.fetchDB()
    return render_template('index.html',
                           x_data=results_time,
                           temp=results_temp,
                           pressure=results_pressure)


def log_config():
    date_time = datetime.now().strftime('%Y%m%d%H%M%S')
    log_folder = Path('log/')
    # print('Log folder exists:', os.path.exists(log_folder))
    if not os.path.exists(log_folder):
        # logging.info(f'Path {path} does not exists, creating one..')
        os.mkdir(log_folder)
    log_filename = f"{Path(f'log/{date_time}')}.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format=
        '{asctime} - {levelname} - {name} - {lineno} - {funcName} ::: {message}',
        filename=log_filename,
        style='{',
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


if __name__ == '__main__':
    p1 = Process(target=startDataRead).start()
    p2 = Process(target=startServer).start()
    p1.join()
    p2.join()
    # # insertDB('11-19-13:49',23.6,100020)
    # fetchDB()
    # creatTB()