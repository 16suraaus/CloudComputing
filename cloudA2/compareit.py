#!/usr/bin/env cctools_python
# CCTOOLS_PYTHON_VERSION 2.7 2.6


from work_queue import *

import os
import sys

# Main program
if __name__ == '__main__':
  port = 0

  if len(sys.argv) < 2:
    print "compareit <inputfile> ..."
    print "compares DNA sequences from the file to one another"
    sys.exit(1)

  #store sequences with task ID as key
  mydict={}
  
  swaligntool_path = "swaligntool"
  if not os.path.exists(swaligntool_path):
  
      print "swaligntool was not found. Please modify the swaligntool_path accordlingly"
      sys.exit(1);
  try:
      q = WorkQueue(port)
  except:
      print "Instantiation of Work Queue failed!"
      sys.exit(1)

  print "listening on port %d..." % q.port

  seqID1=""
  sequence1=""
  seqID2=""
  sequence2=""

  linecounter=0;
  contents = ""
  with open(sys.argv[1]) as f:
    for line in f.readlines():
      contents += line+"/n"


  # a nested loop that compares the line from the outer to
  # all of the lines in the inner
  # linecounter variable is advanced to avoid duplicate comparisons
  # x->y being compared means y->x will not be
  for myline in contents.split('/n'):
    if(myline.startswith('>')):
      seqID1=myline[1:]
      linecounter+=1
      continue
    sequence1=myline
    linecounter+=1
    
    myfile=open(sys.argv[1])
    for line in myfile.readlines()[linecounter:]:
      if(line.startswith('>') or line[0].isdigit()):
        if line[0].isdigit():
          seqID2=line
        else:
          seqID2=line[1:]
        continue
      sequence2=line
        
      
      command = "./swaligntool   %s %s"%(sequence1.rstrip(), sequence2.rstrip())
 
      t = Task(command)
      #necessary inputs
      t.specify_file(swaligntool_path, "swaligntool", WORK_QUEUE_INPUT, cache=True)
      t.specify_file("swalign", "swalign", WORK_QUEUE_INPUT, cache=True)
      
      taskid = q.submit(t)
      mydict[taskid] =seqID1.rstrip() +"  " + seqID2.rstrip()
      #submit tasks

    myfile.close()
      
      




  os.popen("condor_submit_workers $HOSTNAME " + str(q.port) + " 200")
  print "waiting for tasks to complete..."
  outputfinaldata = open("outputfinal.txt", "w+")
  while not q.empty():
      t = q.wait(5)
      if t:
         
      #find where the score is and append the score along with the two sequences to file for later sorting
          for line in t.output.splitlines():
            if line.startswith("Score:"):
              outputfinaldata.write(line+" ")
          outputfinaldata.write(mydict[t.id].rstrip())
          outputfinaldata.write('\n')
        
          if t.return_status != 0:
            None
  outputfinaldata.close()
  #unix pipeline to sort by socre
  os.popen("cat outputfinal.txt | sort -k2 -n -r > sortedoutputfinal.txt")

  print("Top Ten Matches:")
  
  
  finaldata = open("sortedoutputfinal.txt","r+")

  counter =1

  #loop through scores and print top 10
  for line in finaldata:
    print(str(counter)+": sequence "+line.split()[2]+ " matches "+line.split()[3] + " with a score of "+line.split()[1])
    counter +=1
    if(counter >10):
      break

  #remove leftover condor jobs
  os.popen("condor_rm $USER")

