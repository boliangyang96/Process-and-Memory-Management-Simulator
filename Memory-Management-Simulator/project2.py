'''
Jiaqi Geng     	gengj3@rpi.edu
Boliang Yang 	yangb5@rpi.edu
Jingpeng Hao	haoj@rpi.edu

'''

import sys
import queue
t_memmove = 1 #time to move one frame of memory


def print_mem(mem):
    print("================================")
    for i in range(0, 8):
        for j in range(0, 32):
            print(mem[i * 32 + j], end = '')
        print()
    print("================================")


def read_file(in_file):
    try:
        fr = open(in_file, "r")
    except FileNotFoundError:
        sys.exit("ERROR: File Not Found\n")
    data = fr.readlines()
    process = []
    mem = []
    #preprocessing the data
    for i in range(len(data)):
        line = data[i]
        if not line[0] == '#' and line != "" and line != "\n":
            words = line.split()
            memory = [words[0], int(words[1])]
            for j in range(2, len(words)):
                time = words[j].split('/')
                memory.append((int(time[0]), int(time[1])))
            process.append(memory)
    fr.close()
    process_list = []
    total_process = 0
    for p in process:
        total_process += (len(p) - 2)
    #using insert sort
    while (total_process > 0):
        j = 0
        #find the smallest part of the arrival time
        for pro in process:
            if len(pro) == 2:
                process.remove(pro)
        prev_process = (process[0][0], process[0][1], process[0][2][0], process[0][2][1] + process[0][2][0])
        for i in range(1, len(process)):
            pro = process[i]
            if len(pro) == 2:
                process.remove(pro)
                continue
            if pro[2][0] < prev_process[2]:
                prev_process = (pro[0], pro[1], pro[2][0], pro[2][1] + pro[2][0])
                j = i
        process_list.append(prev_process)
        process[j].remove(process[j][2])
        if (len(process[j]) == 2):
            process.remove(process[j])
        total_process -= 1
        if total_process == 0:
            break
        #add all other concurrent proces
        for pro in process:
            if pro[2][0] == prev_process[2]:
                prev_process = (pro[0], pro[1], pro[2][0], pro[2][1] + pro[2][0])
                process_list.append(prev_process)
                total_process -= 1
                pro.remove(pro[2])
        for pro in process:
            if len(pro) == 2:
                process.remove(pro)
    #print(process_list)
    #initialize mem
    for i in range(256):
       mem.append('.')
    return mem, process_list


def best_fit(original_process, original_mem):
    mem = list(original_mem)
    process = list(original_process)
    time = 0
    real_time = 0 #real_time >= time ~ real_time = time + defragTime
    leaving_queue = queue.PriorityQueue()
    print_event(0,6,method = "Contiguous -- Best-Fit")

    while len(process) > 0 or not leaving_queue.empty():
        if not leaving_queue.empty():# check leaving queue
            tmp = leaving_queue.get()
            if tmp[0] == time:
                mem = remove_mem(tmp[1],mem)
                print_event(real_time,3,processName = tmp[1])
                print_mem(mem)
                continue
            else:
                leaving_queue.put(tmp)
        current = []
        if len(process) != 0: #has process left
            current_p = process[0]
            if current_p[2] == time:#has incoming process
                print_event(real_time,0,current_p[0],current_p[1])
                index = find_bestfitchuck(mem,current_p[1])
                if index >= 0: #can place process
                    mem = placein_mem(index,current_p[1],current_p[0],mem)
                    print_event(real_time,1,current_p[0])
                    print_mem(mem)
                    leaving_queue.put([current_p[3],current_p[0]])
                else:#mem is full
                    if remain_mem(mem) >= current_p[1]:
                        print_event(real_time,4,processName =current_p[0])
                        timeDefrag, move_space, movedlist = defragmentation(mem)
                        real_time += timeDefrag
                        print_event(real_time,5,move_space=move_space,movedlist=movedlist)
                        print_mem(mem)
                        index = find_bestfitchuck(mem,current_p[1])
                        mem = placein_mem(index,current_p[1],current_p[0],mem)
                        print_event(real_time,1,current_p[0])
                        print_mem(mem)
                        leaving_queue.put([current_p[3],current_p[0]])
                    else:
                        print_event(real_time,2,current_p[0])
                        print_mem(mem)
                process.pop(0)
                if len(process) != 0: #check any process left
                    if process[0][2] == time: #finish other process arrive on same time
                        continue
        time += 1
        real_time += 1
    print_event(real_time,7,method = "Contiguous -- Best-Fit")
    print()


#search empty mem space starting from index start_point
def empty_point(start_point, mem):
    while start_point < 256:
        if mem[start_point] is '.':
            return start_point
        start_point += 1
    return -1

#search empty mem space range starting from index start_point
def empty_range(start_point, mem):
    if start_point == -1:
        return -1
    i = start_point + 1
    while i < 256:
        if mem[i] is not '.':
            return (i - start_point)
        i += 1
    return (i - start_point)

#defragment the memory, return time taken to finish
def defragmentation(mem):
    time = 0
    empty_i = empty_point(0, mem)
    moving_i = empty_i + empty_range(empty_i, mem)
    move_space = 0
    moved_list = []
    while moving_i < 256:
        if mem[moving_i] != '.' and moving_i > empty_i:
            if mem[moving_i] not in moved_list:
                moved_list.append(mem[moving_i])
            mem[empty_i] = mem[moving_i]
            mem[moving_i] = '.'
            empty_i = empty_point(empty_i + 1,mem)
            time += t_memmove
            move_space += 1
        moving_i += 1
    #print(movedlist)
    return time, move_space, moved_list

def find_bestfitchuck(mem,requiredSize):
    fit_queue = queue.PriorityQueue()
    index = 0
    i = 0
    while i < 256:
        if mem[i] == '.':
            for j in range(i,256):
                if mem[j] != '.':
                    fit_queue.put([j - i,i])
                    i = j
                    break
                if j == 255:
                    fit_queue.put([j + 1 - i,i])
                    i = j
        i += 1
    while not fit_queue.empty():
        tmp = fit_queue.get()
        if tmp[0] >= requiredSize:
            return tmp[1]
    if fit_queue.empty():
        return -1


def placein_mem(start_point,length, character, mem):
    i = 0
    while i < length:
        mem[start_point + i] = character
        i += 1
    return mem

def remove_mem(character,mem):
    for i in range(0,256):
        if mem[i] == character:
            mem[i] = '.'
    return mem

def remain_mem(mem):
    j = 0
    for i in range(0,256):
        if mem[i] == '.':
            j += 1
    return j

def next_first_fit(infile):
    try:
        fread = open(infile, "r")
    except FileNotFoundError:
        sys.exit("ERROR: File Not Found\n")
    data = fread.readlines()
    process = []
    t=0
    space=[]

    frame=[]
    ln=0
    arrive=[]
    leave=[]
    arrive_again=[]
    leave_again=[]
    arrive_3=[]
    leave_3=[]
    time=[]
    row_i=[]
    col_i=[]
    time_copy=[]
    times=0

    for line in data:
        words = []
        i = 0
        de_space = line.split()
        while i<len(de_space):
            if i<2:
                words.append(de_space[i])
            else:
                words.append(de_space[i].split('/')[0])
                words.append(de_space[i].split('/')[1])

            i=i+1
        space.append(int(words[1]))
        process.append(words[0])
        arrive.append(int(words[2]))
        leave.append(int(words[2])+int(words[3]))
        if len(words)>4:
            arrive_again.append(int(words[4]))
            leave_again.append(int(words[4])+int(words[5]))
            if len(words)>6:
                arrive_3.append(int(words[6]))
                leave_3.append(int(words[6]) + int(words[7]))
            else:
                arrive_3.append(-1)
                leave_3.append(-1)
        else:
            arrive_again.append(-1)
            leave_again.append(-1)
            arrive_3.append(-1)
            leave_3.append(-1)
    for i in range(len(leave)):
        time.append(leave[i])
    for i in range(len(leave_again)):
        time.append(leave_again[i])
    for i in range(len(leave_3)):
        time.append(leave_3[i])
    for i in range(len(arrive)):
        time.append(arrive[i])
    for i in range(len(arrive_again)):
        time.append(arrive_again[i])
    for i in range(len(arrive_3)):
        time.append(arrive_3[i])

    for i in range(len(leave)):
        time_copy.append(leave[i])
    for i in range(len(leave_again)):
        time_copy.append(leave_again[i])
    for i in range(len(leave_3)):
        time_copy.append(leave_3[i])
    for i in range(len(arrive)):
        time_copy.append(arrive[i])
    for i in range(len(arrive_again)):
        time_copy.append(arrive_again[i])
    for i in range(len(arrive_3)):
        time_copy.append(arrive_3[i])

    index=[x for x in range(len(time))]
    for i in range(len(time)-1):
        for j in range(len(time)-i-1):
            if time[j]>time[j+1]:
                time[j],time[j+1]=time[j+1],time[j]
                index[j],index[j+1]=index[j+1],index[j]
    for i in range(len(time)-1):
        for j in range(len(time)-i-1):
            if time[j]==-1:
                time[j],time[j+1]=time[j+1],time[j]
                index[j],index[j+1] = index[j+1],index[j]

    for i in range(len(index)-1):
        for j in range(len(index)-i-1):
            if time[j]==time[j+1]:
                if index[j]>=0 and index[j]<len(arrive) and index[j+1]>=len(arrive) and index[j+1]<2*len(arrive):
                    if process[(index[j+1])%len(arrive)]<process[(index[j])%len(arrive)]:
                        index[j],index[j+1]=index[j+1],index[j]
                if index[j]>=0 and index[j]<len(arrive) and index[j+1]>=2*len(arrive) and index[j+1]<3*len(arrive):
                    if process[(index[j+1])%len(arrive)]<process[(index[j])%len(arrive)]:
                        index[j],index[j+1]=index[j+1],index[j]
                if index[j]>=len(arrive) and index[j]<2*len(arrive) and index[j+1]>=2*len(arrive) and index[j+1]<3*len(arrive):
                    if process[(index[j+1])%len(arrive)]<process[(index[j])%len(arrive)]:
                        index[j],index[j+1]=index[j+1],index[j]
                if index[j]>=3*len(arrive) and index[j]<4*len(arrive) and index[j+1]>=4*len(arrive) and index[j+1]<5*len(arrive):
                    if process[(index[j+1])%len(arrive)]<process[(index[j])%len(arrive)]:
                        index[j],index[j+1]=index[j+1],index[j]
                if index[j]>=3*len(arrive) and index[j]<4*len(arrive) and index[j+1]>=5*len(arrive) and index[j+1]<6*len(arrive):
                    if process[(index[j+1])%len(arrive)]<process[(index[j])%len(arrive)]:
                        index[j],index[j+1]=index[j+1],index[j]
                if index[j]>=4*len(arrive) and index[j]<5*len(arrive) and index[j+1]>=5*len(arrive) and index[j+1]<6*len(arrive):
                    if process[(index[j+1])%len(arrive)]<process[(index[j])%len(arrive)]:
                        index[j],index[j+1]=index[j+1],index[j]
    while times<2:
        if times==0:
            print("time 0ms: Simulator started (Contiguous -- Next-Fit)")
        else:
            print("")
            print("time 0ms: Simulator started (Contiguous -- First-Fit)")
        start = [0] * len(arrive)
        end = [0] * len(arrive)
        rem = 0
        j = 0
        if times==0:
            while j < 256:
                frame.append('.')
                j += 1
        else:
            while j<256:
                frame[j]='.'
                j+=1
        f_i = 0
        mov_f = 0
        for i in index:
            if time_copy[i] != -1:
                rem = (i) % len(arrive)
            if i < 3 * len(leave):
                if time_copy[i] != -1:
                    num = 0
                    for p_i in range(len(frame)):
                        if frame[p_i] == process[rem]:
                            num += 1
                            frame[p_i] = '.'
                    if num == 0:
                        continue
                    else:
                        print("time %dms: Process %s removed:" % (time_copy[i] + mov_f, process[rem]))
                        t_end = time_copy[i]
                        j = 0
                        while j < 31:
                            print("=", end="")
                            j += 1
                        print("=")
                        j = 0
                        while j < len(frame):
                            if (j + 1) % 32 == 0:
                                print(frame[j])
                            else:
                                print(frame[j], end="")
                            j += 1
                        j = 0
                        while j < 31:
                            print("=", end="")
                            j += 1
                        print("=")
            else:
                if time_copy[i] != -1:
                    print("time %dms: Process %s arrived (requires %d frames)" % (
                    time_copy[i] + mov_f, process[rem], space[rem]))
                    if f_i + space[rem] > len(frame):
                        f_i = 0
                    start[rem] = f_i
                    n_occupied = f_i
                    if space[rem] > frame.count('.'):
                        print("time %dms: Cannot place process %s -- skipped!" % (time_copy[i] + mov_f, process[rem]))
                        j = 0
                        while j < 31:
                            print("=", end="")
                            j += 1
                        print("=")
                        j = 0
                        while j < len(frame):
                            if (j + 1) % 32 == 0:
                                print(frame[j])
                            else:
                                print(frame[j], end="")
                            j += 1
                        j = 0
                        while j < 31:
                            print("=", end="")
                            j += 1
                        print("=")
                        continue
                    else:
                        frame_str = "".join(frame)
                        frame_list = list(frame_str)
                        for fs_i in range(len(frame_str)):
                            if frame_list[fs_i] >= 'A' and frame_list[fs_i] <= 'Z':
                                frame_list[fs_i] = '$'
                        frame_str2 = "".join(frame_list)
                        sep = frame_str2.split('$')
                        sum_block = 0
                        for sep_i in range(len(sep)):
                            if sep[sep_i].count('.') > 0:
                                sum_block += 1
                        spot = [0] * sum_block
                        j = 0
                        for sep_i in range(len(sep)):
                            if sep[sep_i].count('.') > 0:
                                spot[j] = sep_i
                                j += 1
                        spot_start = [0] * sum_block
                        spot_end = [0] * sum_block
                        # j = 0
                        sp = list(spot_start)
                        for j in range(len(spot)):
                            if spot[0] == 0:
                                spot_start[0] = 0
                                spot_end[0] = spot_start[0] + sep[spot[0]].count('.') - 1
                                if j > 0:
                                    spot_start[j] = spot_start[j - 1] + spot[j] - spot[j - 1] + sep[spot[j - 1]].count('.')
                                    spot_end[j] = spot_start[j] + sep[spot[j]].count('.') - 1
                            else:
                                spot_start[0] = spot[0]
                                spot_end[0] = spot_start[0] + sep[spot[0]].count('.') - 1
                                if j > 0:
                                    spot_start[j] = spot_start[j - 1] + spot[j] - spot[j - 1] + sep[spot[j - 1]].count('.')
                                    spot_end[j] = spot_start[j] + sep[spot[j]].count('.') - 1
                        temp = 0
                        flag = 0
                        if times == 0:
                            for sp_i in range(len(spot_start)):
                                if f_i >= spot_start[sp_i] and f_i <= spot_end[sp_i]:
                                    if spot_end[sp_i] - f_i + 1 >= space[rem]:
                                        flag = 1
                                        break
                                    else:
                                        temp = sp_i
                            if flag == 0:
                                if temp + 1 < len(spot_start):

                                    while temp + 1 < len(spot_start):

                                        if spot_end[temp + 1] - spot_start[temp + 1] + 1 >= space[rem]:
                                            flag = 1
                                            f_i = spot_start[temp + 1]
                                            break
                                        else:
                                            temp += 1
                                            if temp + 1 < len(spot_start):
                                                f_i = spot_start[temp + 1]
                                    if flag == 0:
                                        f_i = spot_start[0]
                                else:
                                    f_i = spot_start[0]
                                if flag == 0:
                                    for b_i in range(len(spot_start)):
                                        if spot_end[b_i] - spot_start[b_i] + 1 >= space[rem]:
                                            flag = 1
                                            f_i = spot_start[b_i]
                                            break
                        else:
                            for sp_i in range(len(spot_start)):
                                if spot_end[sp_i] - spot_start[sp_i] + 1 >= space[rem]:
                                    flag = 1
                                    f_i = spot_start[sp_i]
                                    break

                        n_occupied = f_i
                        if flag == 0:
                            print("time %dms: Cannot place process %s -- starting defragmentation" % (
                            time_copy[i] + mov_f, process[rem]))
                            m_frame = []
                            if frame[0] == '.':
                                mov_f += len(frame) - frame.count('.')
                                for j in range(len(frame) - 1):
                                    if frame[j + 1] != '.' and frame[j + 1] != frame[j]:
                                        m_frame.append(frame[j + 1])
                            else:
                                # m_frame.append(frame[0])
                                for j in range(len(frame) - 1):
                                    if frame[j + 1] != '.' and frame[j + 1] != frame[j]:
                                        m_frame.append(frame[j + 1])
                                for j in range(len(frame)):
                                    if frame[j] == '.':
                                        break
                                mov_f += len(frame) - j - frame.count('.')

                            for d_i in range(len(frame) - 1):
                                for d_j in range(len(frame) - d_i - 1):
                                    if frame[d_j] == '.' and frame[d_j + 1] != '.':
                                        frame[d_j], frame[d_j + 1] = frame[d_j + 1], frame[d_j]
                            flag = 1
                            f_i = len(frame) - frame.count('.')
                            print("time %dms: Defragmentation complete (moved %d frames: " % (time_copy[i] + mov_f, mov_f),
                                  end="")
                            for j in range(len(m_frame)):
                                if j != len(m_frame) - 1:
                                    print("%s, " % (m_frame[j]), end="")
                                else:
                                    print("%s" % (m_frame[j]), end="")
                                    print(")")
                            j = 0
                            while j < 31:
                                print("=", end="")
                                j += 1
                            print("=")
                            j = 0
                            while j < len(frame):
                                if (j + 1) % 32 == 0:
                                    print(frame[j])
                                else:
                                    print(frame[j], end="")
                                j += 1
                            j = 0
                            while j < 31:
                                print("=", end="")
                                j += 1
                            print("=")
                        if flag == 1:
                            print("time %dms: Placed process %s:" % (time_copy[i] + mov_f, process[rem]))
                            t_end = time_copy[i]
                            for space_i in range(space[rem]):
                                frame[f_i] = process[rem]
                                f_i += 1
                    j = 0
                    while j < 31:
                        print("=", end="")
                        j += 1
                    print("=")

                    j = 0
                    while j < len(frame):
                        if (j + 1) % 32 == 0:
                            print(frame[j])
                        else:
                            print(frame[j], end="")
                        j += 1
                    j = 0
                    while j < 31:
                        print("=", end="")
                        j += 1
                    print("=")
        if times == 1:
            print("time %dms: Simulator ended (Contiguous -- First-Fit)\n" % (t_end + mov_f))
        else:
            print("time %dms: Simulator ended (Contiguous -- Next-Fit)" % (t_end + mov_f))
        times += 1
    #*********************First Fit
    fread.close()

def print_page_table(page_table):
    print("PAGE TABLE [page,frame]:")
    plist = sorted(page_table.keys())
    
    for p in plist:
        process_info = p + ":"
        i = 0
        for pair in page_table[p]:
            if i%10 == 0 and i != 0:
                tmp = "\n" + "[" + str(pair[0]) + "," + str(pair[1]) + "]"
            else:
                tmp = " " + "[" + str(pair[0]) + "," + str(pair[1]) + "]"
        
            process_info += tmp
            i+=1
            
        print(process_info)


def non_contiguous(original_process, original_mem):
    mem = list(original_mem)
    process = list(original_process)
    
    end_times = {}
    for p in process:
        end_time = p[3]
        if end_time in end_times:
            end_times[end_time].append(p[0])
        else:
            end_times[end_time] = []
            end_times[end_time].append(p[0])
    
    stop_time = max(end_times.keys())
    process_left = len(process)
    
    start_times = {}
    for p in process:
        start_time = p[2]
        if start_time in start_times:
            start_times[start_time].append(p)
        else:
            start_times[start_time] = []
            start_times[start_time].append(p)
    
    page_table = {}
    print_event(0,6,method = "Non-contiguous")
    
    time = 0;
    
    while time <= stop_time:
        if time in end_times:
            for p_name in end_times[time]:
                if p_name in page_table:
                    for pair in page_table[p_name]:
                        mem[pair[1]] = '.'
                    page_table.pop(p_name, None)
                    process_left -= 1
                    print_event(time, 3, p_name)
                    print_mem(mem)
                    print_page_table(page_table)
        
        if time in start_times:
            for current_process in start_times[time]:
                print_event(time, 0, current_process[0], current_process[1])
                start_point = 0
                index = 0
            
                empty_space = remain_mem(mem)
                remain_frame = current_process[1]
                if remain_frame > empty_space:
                    print_event(time, 2, current_process[0])
                    process_left -= 1
                    print_mem(mem)
                    print_page_table(page_table)
                    continue
                
                start_point = empty_point(0, mem)
                print_event(time, 1, current_process[0])
                while remain_frame != 0:
                    if mem[start_point] != '.':
                        start_point = empty_point(0, mem)
                        continue
                    else: 
                        mem[start_point] = current_process[0]
                        if current_process[0] in page_table:
                            page_table[current_process[0]].append([index, start_point])
                        else:
                            page_table[current_process[0]] = []
                            page_table[current_process[0]].append([index, start_point])
                        
                        index += 1
                        start_point += 1
                        remain_frame -= 1
                        
                print_mem(mem)
                print_page_table(page_table)
        
        if process_left == 0:
            break
        
        time += 1
    
    print_event(time, 7,method = "Non-contiguous")
    
    
#helper function to print the event
def print_event(time,eventnumber,processName=None,numframe=None,move_space=None,movedlist=None,method=None):
    if eventnumber == 0:
        print("time %dms: Process %s arrived (requires %d frames)" % (time,processName,numframe))
    elif eventnumber == 1:
        print("time %dms: Placed process %s:" % (time,processName))
    elif eventnumber == 2:
        print("time %dms: Cannot place process %s -- skipped!" % (time,processName))
    elif eventnumber == 3:
        print("time %dms: Process %s removed:" % (time,processName))
    elif eventnumber == 4:
        print("time %dms: Cannot place process %s -- starting defragmentation" % (time,processName))
    elif eventnumber == 5:
        print("time %dms: Defragmentation complete (moved %d frames: %s)" % (time,move_space,', '.join(str(x) for x in movedlist)))
    elif eventnumber == 6:
        print("time %dms: Simulator started (%s)" % (time,method))
    elif eventnumber == 7:
        print("time %dms: Simulator ended (%s)" % (time,method))




def main(argv):
    if not len(argv) == 2:
        sys.exit("ERROR: Invalid arguments\nUSAGE: ./a.out <input-file>\n")
    in_file = argv[1]
    mem,process = read_file(in_file)
    next_first_fit(in_file)
    best_fit(process, mem)
    non_contiguous(process, mem)
    
    
if __name__ == "__main__":
    main(sys.argv)
