"""metric.py"""
import pika
import json
import time
from sklearn.metrics import mean_squared_error as mse
import pandas as pd
from datetime import datetime

df = pd.DataFrame(columns=['y_true', 'y_predict'])

try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='y_true')
    channel.queue_declare(queue='y_predict')


    def callback(ch, method, properties, body):
        label_body = json.loads(body)
        datetime_str = datetime.fromtimestamp(label_body['time']).strftime('%Y-%m-%d %A %H:%M:%S %f us |')
        answer_string = f'Из очереди {method.routing_key} получено значение {label_body}'
        print(f'{datetime_str} -> Из очереди {method.routing_key} получено значение:')
        print(f'  {label_body}'[:150])
        with open('./logs/label_log.txt', 'a') as log:
            log.write(answer_string + '\n')
        df.loc[label_body['y_row_index'], method.routing_key] = label_body['y']
        if len(df.dropna()):
            rmse = mse(df.dropna().y_true, df.dropna().y_predict)**0.5
            print('  RMSE ', round(rmse,5))

    channel.basic_consume(
        queue='y_predict', on_message_callback=callback, auto_ack=True)

    channel.basic_consume(
        queue='y_true', on_message_callback=callback, auto_ack=True)

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()

except:
    print('Не удалось подключиться к очереди')
    time.sleep(3)
