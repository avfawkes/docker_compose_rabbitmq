"""model.py"""
import pika
import json
import pickle
import numpy as np
import time
from datetime import datetime

with open('myfile.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)

try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='Features')
    channel.queue_declare(queue='y_predict')

    def callback(ch, method, properties, body):
        features = json.loads(body)
        datetime_str = datetime.fromtimestamp(features['time']).strftime('%Y-%m-%d %A %H:%M:%S %f us |')
        row_index = features['X_row_index']
        print(f'{datetime_str} <- Получен вектор признаков:')
        print(f'  {features}'[:150])
        pred = regressor.predict(np.array(features['X_row']).reshape(1, -1))

        y_dict = {'time': time.time(), 'y_row_index': row_index, 'y': pred[0]}
        channel.basic_publish(exchange='',
                              routing_key='y_predict',
                              body=json.dumps(y_dict))
        datetime_str = datetime.fromtimestamp(y_dict['time']).strftime('%Y-%m-%d %A %H:%M:%S %f us |')
        print(f'{datetime_str} -> Предсказание отправлено в очередь y_predict:')
        print(f'  {y_dict}'[:150])


    channel.basic_consume(
        queue='Features', on_message_callback=callback, auto_ack=True)

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()

except:
    print('Не удалось подключиться к очереди')
    time.sleep(2)
