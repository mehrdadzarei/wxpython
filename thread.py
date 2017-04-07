import Queue
import threading
import multiprocessing
import subprocess

q = Queue.Queue()
for i in range(30): #put 30 tasks in the queue
    q.put(i)

def worker():
    while True:
        item = q.get()
        #execute a task: call a shell program and wait until it completes
        subprocess.call("echo "+str(item), shell=True) 
        q.task_done()

cpus=multiprocessing.cpu_count() #detect number of cores
print("Creating %d threads" % cpus)
for i in range(cpus):
     t = threading.Thread(target=worker)
     t.daemon = True
     t.start()

q.join() #block until all tasks are done