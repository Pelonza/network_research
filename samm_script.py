# Automated network processing script
# Written by Sammantha Nowak-Wolff and Casey Primozic

import networkx as nx
import os, threading
import Queue

maxRunTime=9

def processAll():
  processAll(False)

# Searches given directory for network files, imports them, and runs process() on each
def processAll(dir):
  if not(dir):
    dir="./"
  else:
    dir=os.path.relpath(dir)
  for file in os.listdir(dir):
    ext = file.split(".")[-1]
    if ext == "gml" or ext == "net":
      print("\nProcessing " + file + ":")
      g=loadNetwork(dir+"/"+file)
      if(g):
        process(g)

# Applies various network analysis functions to the given network
# and prints the results.
def process(a):
  try:
    chordal= nx.is_chordal(a)
    print("Chordal: " + str(chordal))
  except Exception, e:
    print(e)

  try:
    center= nx.center(a)
    print(str(center))
  except Exception, e:
    print(e)

  try:
    transitivity = nx.transitivity(a)
    print(str(transitivity))
  except Exception, e:
    print(e)

  print(nx.info(a))

  res=calc(nx.average_neighbor_degree, (a,), [getAverage, getMax])
  print("Max average neighbor degree: " + str(res[0]))
  print("Average average neighbor degree: " + str(res[1]))

  try:
    res=calc(nx.triangles, (a,), [getAverage, getMax])
  except Exception, e:
    print(e)
  print("Max triangles: " + str(res[0]))
  print("Average triangles: " + str(res[1]))

  res=calc(nx.closeness_centrality, (a,), [getAverage, getMax])
  print("Average closeness centrality: " + str(res[0]))
  print("Max closeness centrality: " + str(res[1]))

  try:
    res=calc(nx.eigenvector_centrality, (a,), [getAverage, getMax])
  except Exception, e:
    print(e)
  print("Average eigenvector centrality: " + str(res[0]))
  print("Max eigenvector centrality: " + str(res[1]))

# Parses a .gml or pajek-formatted network and loads as a networkx network object
def loadNetwork(f):
  try:
    return nx.read_gml(f)
  except Exception, e:
    try:
      return nx.read_pajek(f)
    except Exception, e:
      print("Network cannot be parsed.")
      return False

# Returns the average value for a dictionary of numbers
def getAverage(d):
  if d=="Took too long":
    return d

  sum=0
  for key in d:
    sum += d[key]

  avg = sum/float(len(d))
  return avg

# Returns the maximum value for a dictionary of numbers
def getMax(d):
  if d=="Took too long":
    return d

  max=0
  if len(d) > 0:
    return 0
  for key in d:
    if max<d[key]:
      max=d[key]

  return max

def calc(func, args):
  return calc(func, args, False)

class workerThread(threading.Thread):
  def __init__(self, func, args, q, postProc):
    threading.Thread.__init__(self)
    self.func = func
    self.args = args
    self.q=q
    self.postProc = postProc

  def run(self):
    res=self.func(*self.args)
    if(self.postProc):
      res2=[]
      for proc in self.postProc:
        if res=="error":
          res2.append(res)
        else:
          res2.append(proc(res))
      self.q.put(res2)
    else:
      self.q.put(res)

# args in the form of a tuple, cannot contain q as an argument
# postProc in the form of a list which contains functions which are run on the result of func
def calc(func, args, postProc):
  q=Queue.Queue()
  t = workerThread(calcProcess, (func, args, q,), q, postProc)
  t.start()
  t.join(maxRunTime)
  if t.isAlive():
    return "Took too long"
  else:
    return q.get()

# Function called by the worker thread in calc()
def calcProcess(func, args, q):
  try:
    return func(*args)
  except Exception, e:
    return "error"
