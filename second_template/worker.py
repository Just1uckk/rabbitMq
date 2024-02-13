import os
import sys
import time

import pika


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # durable - make a rabbit durable when crashes
    channel.queue_declare(queue='task_queue', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")
        time.sleep(body.count(b'.'))
        print(" [x] Done")
        # if worker closed - sending request to queue again
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # do not send a new message while items not fully processed
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue',
                          on_message_callback=callback)

    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
