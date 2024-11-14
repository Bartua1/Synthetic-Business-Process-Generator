from threading import Thread
from queue import Queue
from data_gen import ProcessGenerator, NameGenerator, LMStudioConnector, ProcessDataGenerator
import time

class ProcessGeneratorWorker(Thread):
    def __init__(self, name_queue, connector, thread_id):
        super().__init__()
        self.name_queue = name_queue
        self.connector = connector
        self.thread_id = thread_id

    def run(self):
        while True:
            try:
                process_name = self.name_queue.get_nowait()
            except Queue.Empty:
                break

            try:
                # Get improved name from LMStudio
                process_name = str(self.connector.get_answer(
                    f"Give me an improved name for the process: {process_name}, return only the name with a maximum of 3 words"
                )).replace('"', '')

                # Generate process
                generator = ProcessGenerator(
                    min_nodes=5,
                    max_nodes=10,
                    min_connections=1,
                    max_connections=3,
                    process_name=process_name,
                    lmstudio_connector=self.connector
                )

                proceso = generator.generate_process()
                print(f"Thread {self.thread_id}: Process {generator.process_name} created")

                # Save the process graph
                generator.visualize_with_graphviz()

                # Generate data
                data_generator = ProcessDataGenerator(
                    process_graph=proceso,
                    num_cases=500,
                    lmstudio_connector=self.connector,
                    process_name=generator.process_name
                )

                # Save to CSV
                data_generator.save_to_csv(f"{generator.process_name}.csv")
                print(f"Thread {self.thread_id}: Data for process {data_generator.process_name} created")

            except Exception as e:
                print(f"Thread {self.thread_id} encountered an error: {str(e)}")

            finally:
                self.name_queue.task_done()

def main(num_threads=4):
    # Initialize name queue
    name_queue = Queue()

    # Get names and populate queue
    nameGen = NameGenerator()
    names = nameGen.get_all_names()
    for _ in range(nameGen.get_total()):
        if names:
            name_queue.put(names.pop())

    # Create connector instances for each thread
    connectors = [LMStudioConnector() for _ in range(num_threads)]

    # Create and start workers
    workers = []
    for i in range(num_threads):
        worker = ProcessGeneratorWorker(name_queue, connectors[i], i)
        workers.append(worker)
        worker.start()

    # Wait for all tasks to complete
    name_queue.join()

    # Wait for all threads to finish
    for worker in workers:
        worker.join()

    print("All processes completed!")

if __name__ == "__main__":
    start_time = time.time()
    main(num_threads=10)
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")