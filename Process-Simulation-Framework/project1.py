"""
    Boliang Yang (yangb5@rpi.edu)
    Jiaqi Geng (gengj3@rpi.edu)
    Jingpeng Hao (haoj@rpi.edu)

"""

import sys
from queue import Queue
from queue import PriorityQueue 

def main(argv):
    #check arguments error
    if not len(argv) == 3:
        sys.exit("ERROR: Invalid arguments\nUSAGE: ./a.out <input-file> <stats-output-file>\n")
    #input/ output file name
    infile = argv[1]
    outfile = argv[2]
    #open input file
    try:
        fread = open(infile, "r")
    except FileNotFoundError:
        sys.exit("ERROR: File Not Found\n")
    #get info
    data = fread.readlines()
    process = []
    #preprocessing the data
    for line in data:
        if not line[0] == '#' and line != "" and line != "\n":
            words = line.split('|')
            if not len(words) == 5:
                sys.exit("ERROR: Invalid input file format\n")
            process.append([words[i] if i==0 else int(words[i]) for i in range(len(words))])
    fread.close()
    #run each scheduling algorithm separately
    FCFS_output = FCFS(process,len(process))
    print("")
    SRT_output = SRT(process,len(process))
    print("")
    RR_output = RR(process,len(process))
    #open output file
    fwrite = open(outfile, "w")
    #write data
    fwrite.write(FCFS_output)
    fwrite.write(SRT_output)
    fwrite.write(RR_output)
    fwrite.close()


def FCFS(process,n,m=1,t_cs=8,t_slice=70):
    #set time
    time = 0
    #cpu Queue
    cpu_queue = Queue()
    #terminate flag
    flag = True
    #switch flag
    cs_flag = False
    printEvent(time, eventString(0, "FCFS"), cpu_queue)
    #initialize process profile
    process_profiles = []
    #Check process in IO
    IO_statue = -1
    #Check process in CPU
    CPU_staute = -1
    #set process attributes
    for i in range(n):
        profile = {}
        profile["num_burst"] = process[i][3]
        profile["CPUStartTime"] = 0
        profile["IOStopTime"] = 0
        profile["CPUWaitTime"] = 0
        profile["WaitTime"] = 0
        profile["BurstTime"] = 0
        profile["TurnTime"] = 0
        profile["IO"] = False
        profile["first"] = True
        process_profiles.append(profile)
    #number of context switches
    num_cs = 0
    #number of preemption
    num_pre = 0
    #number of BurstTime
    num_burst = 0
    #context switches start time
    cs_start_time = 0
    cpu_stop_time = 0
    min_arrived_time = 999999
    for i in range(n):
        if process[i][1] < min_arrived_time:
            min_arrived_time = process[i][1]
    while flag:
        #arrived Queue
        arrived_queue = Queue()
        IO_statue = -1
        #Check process in CPU
        for i in range(n):
            if process_profiles[i]["IO"]:
                IO_statue = i
            #add arrived process
            if process[i][1] <= time and process_profiles[i]["first"]:
                arrived_queue.put(process[i][0])
        #check termination condition
        if IO_statue == -1 and CPU_staute == -1 and cpu_queue.empty() and arrived_queue.empty() and time > min_arrived_time:
            flag = False
            break
        #check context switch condition
        elif CPU_staute == -1 and (not cpu_queue.empty()) and time >= min_arrived_time+t_cs/2:
            cs_flag = True
            if cs_start_time == 0:
                cs_start_time = time - 1
        if not cpu_queue.empty():
            #do context switch
            if cs_flag and ((time - cs_start_time) == t_cs or time == min_arrived_time+t_cs/2):
                num_cs += 1
                name = cpu_queue.get()
                for i in range(n):
                    if name == process[i][0]:
                        cp = i
                        break
                printEvent(time, eventString(2, process[cp][0]), cpu_queue)
                cs_flag = False
                #update all attributes
                process_profiles[cp]["WaitTime"] += process_profiles[cp]["CPUWaitTime"]
                process_profiles[cp]["TurnTime"] += process_profiles[cp]["CPUWaitTime"]
                process_profiles[cp]["CPUWaitTime"] = 0
                process_profiles[cp]["CPUStartTime"] = time
                CPU_staute = cp
                process_profiles[cp]["WaitTime"] -= t_cs/2
                cs_start_time = 0
        i = CPU_staute
        #check CPU burst complete
        if (not CPU_staute == -1) and (time - process_profiles[i]["CPUStartTime"]) == process[i][2]:
            cpu_stop_time = time
            num_burst += 1;
            #update all attributes
            process_profiles[i]["TurnTime"] += (process[i][2] + t_cs/2)
            process_profiles[i]["BurstTime"] += process[i][2]
            process_profiles[i]["CPUStartTime"] = 0
            CPU_staute = -1
            process_profiles[i]["num_burst"] -= 1
            #all number of this process has completed
            if process_profiles[i]["num_burst"] == 0:
                printEvent(time, eventString(6, process[i][0]), cpu_queue)
            else:
                printEvent(time, eventString(3, process[i][0],  process_profiles[i]["num_burst"]), cpu_queue)
                #print IO
                if process[i][4] > 0:
                    process_profiles[i]["IO"] = True
                    process_profiles[i]["IOStopTime"] = (time + process[i][4] + t_cs/2)
                    printEvent(time, eventString(4, process[i][0], process_profiles[i]["IOStopTime"]), cpu_queue)
                else:
                    cpu_queue.put(process[i][0])
            #update context switch
            if cs_flag == False:
                cs_flag = True
                cs_start_time = time
        #check IO completed
        for i in range(n):
            if process_profiles[i]["IO"] and time == process_profiles[i]["IOStopTime"]:
                process_profiles[i]["IOStopTime"] = 0
                #add process to the last of the queue
                if cpu_queue.empty() and process_profiles[i]["num_burst"] > 0 and CPU_staute == -1:
                    cs_flag = True
                    if (time - cpu_stop_time) > t_cs/2:
                        cs_start_time = time - t_cs/2
                    else:
                        cs_start_time = time
                cpu_queue.put(process[i][0])
                printEvent(time, eventString(5, process[i][0]), cpu_queue)
                process_profiles[i]["IO"] = False
        #Check process in CPU
        for i in range(n):
            #add arrived process
            if process[i][1] <= time and process_profiles[i]["first"]:
                cpu_queue.put(process[i][0])
                process_profiles[i]["CPUWaitTime"] = 0
                process_profiles[i]["first"] = False
                printEvent(time, eventString(1, process[i][0]), cpu_queue)
        #update wait time
        for i in range(n):
            if (not CPU_staute == i) and (not process_profiles[i]["IO"]):
                process_profiles[i]["CPUWaitTime"] += 1
        #update time
        time += 1
        if cpu_queue.empty() and cs_flag:
            cs_flag = False
            cs_start_time = time
    print("time %dms: %s" %(time + t_cs/2 - 1, eventString(7, "FCFS")))
    wait_time = 0
    burst_time = 0
    turn_time = 0
    #compute average
    for i in range(n):
        wait_time += process_profiles[i]["WaitTime"]
        burst_time += process_profiles[i]["BurstTime"]
        turn_time += process_profiles[i]["TurnTime"]
    wait_time = wait_time * 1.0 / (num_burst * 1.0);
    burst_time = burst_time * 1.0 / (num_burst * 1.0);
    turn_time = turn_time * 1.0 / (num_burst * 1.0);
    return finaloutput("FCFS", burst_time, wait_time, turn_time, num_cs, num_pre)

def SRT(process,n,m=1,t_cs=8,t_slice=70):
    time = 0
    ready_queue = PriorityQueue()
    total_queue = Queue()
    
    checkComplete = True
    TotalContextSwitch = 0
    TotalPreemption = 0
    
    for i in range(n):
        total_queue.put(process[i][0])
    
    process_profiles = []
    for i in range(n):
        profile = {}
        profile["num_burst"] = process[i][3]
        profile["CPUStartTime"] = 0
        profile["CPUrunTime"] = 0
        profile["IOStopTime"] = -1
        profile["CPUWaitTime"] = 0
        profile["WaitTime"] = 0
        profile["BurstTime"] = 0
        profile["TurnTime"] = 0
        profile["IO"] = False
        profile["first"] = True
        profile["remainingTime"] = process[i][2]
        profile["arrivalTime"] = process[i][1]
        profile["isWaiting"] = False
        #profile["cs_time"] = 0
        process_profiles.append(profile)
    
    CPU_profile = {}
    CPU_profile["BeingUsed"] = False
    CPU_profile["CPUfinishTime"] = -1
    CPU_profile["ID"] = -1
    CPU_profile["ContextSwitching"] = False 
    CPU_profile["InContextSwitchStart"] = -1
    CPU_profile["InContextSwitchEnd"] = -1
    CPU_profile["OutContextSwitchStart"] = -1
    CPU_profile["OutContextSwitchEnd"] = -1   
    
    printEvent(time, eventString(0, "SRT"), ready_queue)
    
    while time < 100000:
        
        checkComplete = True
        
        '''
        if (CPU_profile["BeingUsed"]) and (process_profiles[CPU_profile["ID"]]["remainingTime"] == 0):
            CPU_profile["StartContextSwitch"] = time
            CPU_profile["DoingContextSwitch"] = True
            CPU_profile["EndContextSwitch"] = time + t_cs/2
        '''
        
        if time == CPU_profile["InContextSwitchEnd"]:
            #process_profiles[CPU_profile["ID"]]["isWaiting"] = False
            CPU_profile["BeingUsed"] = True
            CPU_profile["CPUfinishTime"] = process_profiles[CPU_profile["ID"]]["remainingTime"] + time
            CPU_profile["ContextSwitching"] = False 
            CPU_profile["InContextSwitchStart"] = -1
            CPU_profile["InContextSwitchEnd"] = -1
            if process_profiles[CPU_profile["ID"]]["first"]:
                printEvent(time, eventString(2, process[CPU_profile["ID"]][0]), ready_queue)
            else:
                printEvent(time, eventString(11, process[CPU_profile["ID"]][0], process_profiles[CPU_profile["ID"]]["remainingTime"]), ready_queue)
        
        if time == CPU_profile["OutContextSwitchEnd"]:
            CPU_profile["ContextSwitching"] = False
            CPU_profile["OutContextSwitchStart"] = -1
            CPU_profile["OutContextSwitchEnd"] = -1
            if process_profiles[CPU_profile["ID"]]["remainingTime"] != 0:
                process_profiles[CPU_profile["ID"]]["isWaiting"] = True
                
            TotalContextSwitch += 1
            CPU_profile["ID"] = -1
            
        if time == CPU_profile["CPUfinishTime"] and CPU_profile["BeingUsed"]:
            CPU_profile["OutContextSwitchStart"] = time
            CPU_profile["OutContextSwitchEnd"] = time + t_cs/2
            CPU_profile["ContextSwitching"] = True
            
            process_profiles[CPU_profile["ID"]]["TurnTime"] += time + t_cs/2 - process_profiles[CPU_profile["ID"]]["arrivalTime"]
            #process_profiles[CPU_profile["ID"]]["WaitTime"] += time + t_cs/2 - process_profiles[CPU_profile["ID"]]["arrivalTime"] - process[CPU_profile["ID"]][2]
            
            process_profiles[CPU_profile["ID"]]["num_burst"] -= 1
            
            if (process_profiles[CPU_profile["ID"]]["num_burst"] == 0):
                printEvent(time, eventString(6, process[CPU_profile["ID"]][0]), ready_queue)
            else:
                process_profiles[CPU_profile["ID"]]["IO"] = True
                process_profiles[CPU_profile["ID"]]["IOStopTime"] = process[CPU_profile["ID"]][4] + time + t_cs/2
                printEvent(time, eventString(3, process[CPU_profile["ID"]][0], process_profiles[CPU_profile["ID"]]["num_burst"]), ready_queue)
                printEvent(time, eventString(4, process[CPU_profile["ID"]][0], process_profiles[CPU_profile["ID"]]["IOStopTime"]), ready_queue)
                
            CPU_profile["BeingUsed"] = False
            CPU_profile["CPUfinishTime"] = -1
            #CPU_profile["ID"] = -1
        
        '''    
        if time == CPU_profile["EndContextSwitch"]:
            CPU_profile["DoingContextSwitch"] = False
        '''
    
        for i in range(n):
            if time == process_profiles[i]["IOStopTime"] and process_profiles[i]["IO"]:
                process_profiles[i]["first"] = True
                #process_profiles[i]["isWaiting"] = True
                if process_profiles[i]["num_burst"] > 0:
                    process_profiles[i]["arrivalTime"] = time
                    process_profiles[i]["isWaiting"] = True
                    process_profiles[i]["remainingTime"] = process[i][2]
                    #ready_queue.put((process_profiles[i]["remainingTime"], process[i][0]))
                    if CPU_profile["BeingUsed"]:
                        if process_profiles[CPU_profile["ID"]]["remainingTime"] > process_profiles[i]["remainingTime"]:
                            TotalPreemption += 1
                            printEvent(time, eventString(12, process[i][0], process[CPU_profile["ID"]][0]), ready_queue)
                            ready_queue.put((process_profiles[i]["remainingTime"], process[i][0]))
                            CPU_profile["OutContextSwitchStart"] = time
                            CPU_profile["OutContextSwitchEnd"] = time + t_cs/2
                            CPU_profile["ContextSwitching"] = True
                            
                            process_profiles[CPU_profile["ID"]]["first"] = False
                            #process_profiles[CPU_profile["ID"]]["isWaiting"] = True
                            ready_queue.put((process_profiles[CPU_profile["ID"]]["remainingTime"], process[CPU_profile["ID"]][0]))
                            CPU_profile["BeingUsed"] = False
                            CPU_profile["CPUfinishTime"] = -1
                            #CPU_profile["ID"] = -1
                        else:
                            #printEvent(time, eventString(5, process[i][0]), ready_queue) 
                            ready_queue.put((process_profiles[i]["remainingTime"], process[i][0]))
                            printEvent(time, eventString(5, process[i][0]), ready_queue) 
                    else:
                        #printEvent(time, eventString(5, process[i][0]), ready_queue)
                        ready_queue.put((process_profiles[i]["remainingTime"], process[i][0]))
                        printEvent(time, eventString(5, process[i][0]), ready_queue) 
                    
                process_profiles[i]["IOStopTime"] = -1
                process_profiles[i]["IO"] = False
        
        
        for i in range(n):
            if process[i][1] == time:
                process_profiles[i]["arrivalTime"] = time
                #ready_queue.put((process_profiles[i]["remainingTime"], process[i][0]))
                #printEvent(time, eventString(1, process[i][0]), ready_queue)
                if CPU_profile["BeingUsed"]:
                    if process_profiles[CPU_profile["ID"]]["remainingTime"] > process_profiles[i]["remainingTime"]:
                        TotalPreemption += 1
                        printEvent(time, eventString(10, process[i][0], process[CPU_profile["ID"]][0]), ready_queue)
                        process_profiles[i]["isWaiting"] = True
                        ready_queue.put((process_profiles[i]["remainingTime"], process[i][0]))
                        
                        CPU_profile["OutContextSwitchStart"] = time
                        CPU_profile["OutContextSwitchEnd"] = time + t_cs/2
                        CPU_profile["ContextSwitching"] = True
                        
                        process_profiles[CPU_profile["ID"]]["first"] = False
                        #process_profiles[CPU_profile["ID"]]["isWaiting"] = True
                        ready_queue.put((process_profiles[CPU_profile["ID"]]["remainingTime"], process[CPU_profile["ID"]][0]))
                        
                        CPU_profile["BeingUsed"] = False
                        CPU_profile["CPUfinishTime"] = -1
                        #CPU_profile["ID"] = -1
                        
                    else:
                        process_profiles[i]["isWaiting"] = True
                        ready_queue.put((process_profiles[i]["remainingTime"], process[i][0]))
                        printEvent(time, eventString(1, process[i][0]), ready_queue)
                else:
                    process_profiles[i]["isWaiting"] = True
                    ready_queue.put((process_profiles[i]["remainingTime"], process[i][0]))
                    printEvent(time, eventString(1, process[i][0]), ready_queue)
                    
        if (not CPU_profile["BeingUsed"]) and (not CPU_profile["ContextSwitching"]) and (not ready_queue.empty()):
            id = -1
            name = ready_queue.get()[1]
            for i in range(n):
                if process[i][0] == name:
                    id = i
                    break
            
            process_profiles[id]["isWaiting"] = False
            
            #print(id)
            CPU_profile["ContextSwitching"] = True
            CPU_profile["InContextSwitchStart"] = time
            CPU_profile["InContextSwitchEnd"] = time + t_cs/2
            #CPU_profile["BeingUsed"] = True
            CPU_profile["ID"] = id
            #CPU_profile["CPUfinishTime"] = process_profiles[id]["remainingTime"] + time
        
        if ready_queue.empty() == False or CPU_profile["BeingUsed"] or CPU_profile["ContextSwitching"]:
            checkComplete = False
        
        for i in range(n):
            if process_profiles[i]["remainingTime"] != 0 or process_profiles[i]["num_burst"] != 0 or process_profiles[i]["IO"] == True:
                checkComplete = False
        
        if checkComplete == True:
            print("time %dms: %s" %(time, eventString(7, "SRT")))
            break
        
        time += 1
        if CPU_profile["BeingUsed"]:
            process_profiles[CPU_profile["ID"]]["remainingTime"] -= 1
        
        for i in range(n):
            if process_profiles[i]["isWaiting"]:
                process_profiles[i]["WaitTime"] += 1
        
        
    TotalTurnTime = 0
    TotalWaitTime = 0
    TotalBurstTime = 0
    TotalNumBurst = 0
    for i in range(n):
        TotalTurnTime += process_profiles[i]["TurnTime"]
        TotalWaitTime += process_profiles[i]["WaitTime"]
        TotalBurstTime += process[i][2] * process[i][3]
        TotalNumBurst += process[i][3]
    
    TotalWaitTime = TotalTurnTime - TotalBurstTime - TotalContextSwitch * t_cs - TotalPreemption * t_cs/2
    
    burst_time = TotalBurstTime * 1.0 / (TotalNumBurst * 1.0)
    wait_time = TotalWaitTime * 1.0 / (TotalNumBurst * 1.0)
    turn_time = TotalTurnTime * 1.0 / (TotalNumBurst * 1.0)
    num_cs = TotalContextSwitch
    num_pre = TotalPreemption
    
    return finaloutput("SRT", burst_time, wait_time, turn_time, num_cs, num_pre)
    
    #for i in range(n): 
        #print(process_profiles[i]["remainingTime"])
    
    #print(ready_queue.get())
    

def RR(process,n,m=1,t_cs=8,t_slice=70):
    #set time
    time = 0
    #cpu Queue
    cpu_queue = Queue()
    #terminate flag
    flag = True
    #switch flag
    cs_flag = False
    printEvent(time, eventString(0, "RR"), cpu_queue)
    #initialize process profile
    process_profiles = []
    #Check process in IO
    IO_statue = -1
    #Check process in CPU
    CPU_staute = -1
    #set process attributes
    for i in range(n):
        profile = {}
        profile["num_burst"] = process[i][3]
        profile["CPUStartTime"] = 0
        profile["CPUrunTime"] = 0
        profile["IOStopTime"] = 0
        profile["CPUWaitTime"] = 0
        profile["WaitTime"] = 0
        profile["BurstTime"] = 0
        profile["TurnTime"] = 0
        profile["IO"] = False
        profile["first"] = True
        process_profiles.append(profile)
    #number of context switches
    num_cs = 0
    #number of preemption
    num_pre = 0
    #number of BurstTime
    num_burst = 0
    #context switches start time
    cs_start_time = 0
    cpu_stop_time = 0
    #current slice time
    current_slice = 0
    min_arrived_time = 999999
    for i in range(n):
        if process[i][1] < min_arrived_time:
            min_arrived_time = process[i][1]
    while flag:
        #arrived Queue
        arrived_queue = Queue()
        IO_statue = -1
        #Check process in CPU
        for i in range(n):
            if process_profiles[i]["IO"]:
                IO_statue = i
            #add arrived process
            if process[i][1] <= time and process_profiles[i]["first"]:
                arrived_queue.put(process[i][0])
        #check termination condition
        if IO_statue == -1 and CPU_staute == -1 and cpu_queue.empty() and arrived_queue.empty() and time > min_arrived_time:
            flag = False
            break
        #check context switch condition
        elif CPU_staute == -1 and (not cpu_queue.empty()) and time >= min_arrived_time+t_cs/2:
            cs_flag = True
            if cs_start_time == 0:
                cs_start_time = time - 1
        if not cpu_queue.empty():
            #do context switch
            if cs_flag and ((time - cs_start_time) == t_cs or time == min_arrived_time+t_cs/2):
                num_cs += 1
                name = cpu_queue.get()
                for i in range(n):
                    if name == process[i][0]:
                        cp = i
                        break
                if process_profiles[i]["CPUrunTime"] > 0:
                    printEvent(time, eventString(11, process[cp][0], (process[i][2] - process_profiles[i]["CPUrunTime"])), cpu_queue)
                else:
                    printEvent(time, eventString(2, process[cp][0]), cpu_queue)
                cs_flag = False
                #update all attributes
                process_profiles[cp]["WaitTime"] += process_profiles[cp]["CPUWaitTime"]
                process_profiles[cp]["TurnTime"] += process_profiles[cp]["CPUWaitTime"]
                process_profiles[cp]["CPUWaitTime"] = 0
                process_profiles[cp]["CPUStartTime"] = time
                current_slice = 0
                CPU_staute = cp
                process_profiles[cp]["WaitTime"] -= t_cs/2
                cs_start_time = 0
        i = CPU_staute
        notcomplete = True
        if (not CPU_staute == -1):
            #check CPU burst complete
            if (process_profiles[i]["CPUrunTime"] + (time - process_profiles[i]["CPUStartTime"])) == process[i][2]:
                notcomplete = False
                cpu_stop_time = time
                num_burst += 1;
                #update all attributes
                process_profiles[i]["TurnTime"] += (process[i][2] + t_cs/2)
                process_profiles[i]["BurstTime"] += process[i][2]
                process_profiles[i]["CPUrunTime"] = 0
                process_profiles[i]["CPUStartTime"] = 0
                CPU_staute = -1
                process_profiles[i]["num_burst"] -= 1
                #all number of this process has completed
                if process_profiles[i]["num_burst"] == 0:
                    printEvent(time, eventString(6, process[i][0]), cpu_queue)
                else:
                    printEvent(time, eventString(3, process[i][0],  process_profiles[i]["num_burst"]), cpu_queue)
                    #print IO
                    if process[i][4] > 0:
                        process_profiles[i]["IO"] = True
                        process_profiles[i]["IOStopTime"] = (time + process[i][4] + t_cs/2)
                        printEvent(time, eventString(4, process[i][0], process_profiles[i]["IOStopTime"]), cpu_queue)
                    else:
                        cpu_queue.put(process[i][0])
                #update context switch
                if cs_flag == False:
                    cs_flag = True
                    cs_start_time = time
            #check slice completed
            if current_slice == t_slice:
                current_slice = 0
                if notcomplete:
                    process_profiles[i]["CPUrunTime"] += (time - process_profiles[i]["CPUStartTime"])
                    #check preemption
                    if cpu_queue.empty():
                        printEvent(time, eventString(9), cpu_queue)
                        process_profiles[i]["CPUStartTime"] = time
                        current_slice += 1
                    elif (not cpu_queue.empty()):
                        printEvent(time, eventString(8, process[i][0], (process[i][2] - process_profiles[i]["CPUrunTime"])), cpu_queue)
                        cpu_queue.put(process[i][0])
                        num_pre += 1
                        CPU_staute = -1
                        if cs_flag == False:
                            cs_flag = True
                            cs_start_time = time
            else:
                current_slice += 1
        #check IO completed
        for i in range(n):
            if process_profiles[i]["IO"] and time == process_profiles[i]["IOStopTime"]:
                process_profiles[i]["IOStopTime"] = 0
                #add process to the last of the queue
                if cpu_queue.empty() and process_profiles[i]["num_burst"] > 0 and CPU_staute == -1:
                    cs_flag = True
                    if (time - cpu_stop_time) > t_cs/2:
                        cs_start_time = time - t_cs/2
                    else:
                        cs_start_time = time
                cpu_queue.put(process[i][0])
                printEvent(time, eventString(5, process[i][0]), cpu_queue)
                process_profiles[i]["IO"] = False
        #Check process in CPU
        for i in range(n):
            #add arrived process
            if process[i][1] <= time and process_profiles[i]["first"]:
                cpu_queue.put(process[i][0])
                process_profiles[i]["CPUWaitTime"] = 0
                process_profiles[i]["first"] = False
                printEvent(time, eventString(1, process[i][0]), cpu_queue)
        #update wait time
        for i in range(n):
            if (not CPU_staute == i) and (not process_profiles[i]["IO"]):
                process_profiles[i]["CPUWaitTime"] += 1
        #update time
        time += 1
        if cpu_queue.empty() and cs_flag:
            cs_flag = False
            cs_start_time = time
    print("time %dms: %s" %(time + t_cs/2 - 1, eventString(7, "RR")))
    wait_time = 0
    burst_time = 0
    turn_time = 0
    #compute average
    for i in range(n):
        wait_time += process_profiles[i]["WaitTime"]
        burst_time += process_profiles[i]["BurstTime"]
        turn_time += process_profiles[i]["TurnTime"]
    wait_time -= num_pre * (t_cs / 2)
    wait_time = wait_time * 1.0 / (num_burst * 1.0);
    burst_time = burst_time * 1.0 / (num_burst * 1.0);
    turn_time = turn_time * 1.0 / (num_burst * 1.0);
    return finaloutput("RR", burst_time, wait_time, turn_time, num_cs, num_pre)

#helper function to print event
def printEvent(t,event,queue):
    if queue is None:
        print("time %dms: %s",t,event)
    else:
        queueS = "Q"
        if queue.empty():
            queueS = "Q <empty>"
        else:
            temp = []
            while not queue.empty():
                k = queue.get()
                if type(queue).__name__=="Queue":
                    queueS+=" "+str(k)
                else:
                    queueS+=" "+str(k[1])
                temp.append(k)
            for a in temp:
                queue.put(a)
        print("time %dms: %s [%s]"% (t,event,queueS))

#helper function to generate event, use status to do the corresponding event
def eventString(status,name=None,time=None):
    if status==0:
        return "Simulator started for %s" % (name)
    elif status==1:
        return "Process %s arrived and added to ready queue" % (name)
    elif status==2:
        return "Process %s started using the CPU" % (name)
    elif status==3:
        if time == 1:
            return "Process %s completed a CPU burst; %d burst to go" % (name,time)
        else:
            return "Process %s completed a CPU burst; %d bursts to go" % (name,time)
    elif status==4:
        return "Process %s switching out of CPU; will block on I/O until time %dms" % (name,time)
    elif status==5:
        return "Process %s completed I/O; added to ready queue" % (name)
    elif status==6:
        return "Process %s terminated" % (name)
    elif status==7:
        return "Simulator ended for %s" % (name)
    elif status==8:
        return "Time slice expired; process %s preempted with %dms to go" % (name,time)
    elif status==9:
        return "Time slice expired; no preemption because ready queue is empty"
    elif status==10:
        return "Process %s arrived and will preempt %s" % (name,time)
    elif status==11:
        return "Process %s started using the CPU with %dms remaining" % (name,time)
    elif status==12:
        return "Process %s completed I/O and will preempt %s" % (name,time)

#helper function to print to file
def finaloutput(name,burstT,waitT,turnaroudT,contextS,preem):
    return "Algorithm %s\n" \
            "-- average CPU burst time: %.2f ms\n" \
            "-- average wait time: %.2f ms\n"\
            "-- average turnaround time: %.2f ms\n"\
            "-- total number of context switches: %d\n"\
            "-- total number of preemptions: %d\n" % (name,burstT,waitT,turnaroudT,contextS,preem)

if __name__ == "__main__":
    main(sys.argv)
