import pika
import json
import numpy as np
import time
from datetime import datetime
from sklearn.datasets import load_diabetes

X, y = load_diabetes(return_X_y=True)

while True:
    try:
        random_row = np.random.randint(0, X.shape[0] - 1)

        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue='Features')
        channel.queue_declare(queue='y_true')

        X_dict = {'time': time.time(), 'X_row_index': random_row, 'X_row': list(X[random_row])}
        channel.basic_publish(exchange='',
                              routing_key='Features',
                              body=json.dumps(X_dict))
        datetime_str = datetime.fromtimestamp(X_dict['time']).strftime('%Y-%m-%d %A %H:%M:%S %f us |')
        print(f'{datetime_str} -> Сообщение с вектором признаков отправлено в очередь:')
        print(f'  {X_dict}'[:150])

        y_dict = {'time': time.time(), 'y_row_index': random_row, 'y': y[random_row]}
        channel.basic_publish(exchange='',
                              routing_key='y_true',
                              body=json.dumps(y_dict))
        datetime_str = datetime.fromtimestamp(y_dict['time']).strftime('%Y-%m-%d %A %H:%M:%S %f us |')
        print(f'{datetime_str} -> Сообщение с правильным ответом отправлено в очередь:')
        print(f'  {y_dict}'[:150])
        connection.close()
        time.sleep(5)
    except:
        print('Не удалось подключиться к очереди')
        time.sleep(5)
