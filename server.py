from flask import Flask, render_template
import click, logging, sys
# from multiprocessing import Process
from threading import Timer
from pathlib import Path
from datetime import datetime
from SensorDataManager import DataBase, DataCollect

data_base = DataBase(debug=True)
data_collect = DataCollect(debug=True)
app = Flask(__name__)

@click.command()
@click.option('--debug', default=False, is_flag=True)
@click.option('--port', default=8888)
def startServer(port, debug):
    app.run(port=port, debug=debug, host='0.0.0.0',use_reloader=False)


def startDataCollect():
    time_now, temp, pressure = data_collect.readSensorData()
    data_base.insertDB(time_now=time_now, temp=temp, pressure=pressure)
    Timer(60, startDataCollect).start()


def log_config():
    date_time = datetime.now().strftime('%Y%m%d%H%M%S')
    log_folder = Path(sys.path[0],'log/')
    if not log_folder.exists():
        log_folder.mkdir(log_folder)
    log_filename = f"{Path(log_folder,date_time)}.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format=
        '{asctime} - {levelname} - {name} - {lineno} - {funcName} ::: {message}',
        filename=log_filename,
        style='{',
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


@app.route('/')
def index():
    results_time, results_temp, results_pressure = data_base.fetchDB()
    return render_template('index.html',
                           x_data=results_time,
                           temp=results_temp,
                           pressure=results_pressure)



if __name__ == '__main__':
    # log_config()
    # p1 = Process(target=startServer).start()
    # p2 = Process(target=startDataCollect).start()
    # p1.join()
    # p2.join()
    log_config()
    startDataCollect()
    startServer()