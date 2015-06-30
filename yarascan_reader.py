"""
Mike Schladt - 2015
yarascan_reader.py - Filters vol.py yarascan results
                   - Allows user to include/exclude processes
"""

import argparse

av_process_names = ['FireSvc.exe', 'HipMgmt.exe', 'FrameworkServi', 'naPrdMgr.exe', 'mcshield.exe',
                    'vstskmgr.exe', 'TaniumClient.e', 'noms.exe']

def process_include_rule(rule, pids) : 
    """
    Determine whether to print rule
    Input : rule : iterable representing lines in a rule
    Input : pids : iterable of process ids
    Output : none : either it prints the rule or not :) 
    """
    for pid in pids : 
        if any("Pid {0}".format(pid) in line for line in rule) :
            print_rule(rule)

def process_exclude_rule(rule, pids) : 
    """
    Determine whether to print rule
    Input : rule : iterable representing lines in a rule
    Input : pids : iterable of process ids
    Output : none : either it prints the rule or not :) 
    """
    for pid in pids : 
        if any("Pid {0}".format(pid) in line for line in rule) :
            return
    #check if -d was given
    if args.exclude_av :
        for process_name in av_process_names : 
            if any("Process {0}".format(process_name) in line for line in rule) :
                return               
    #if function not returned - print
    print_rule(rule)

def process_exclude_av_rule(rule) : 
    """
    Determine whether to print rule
    Input : rule : iterable representing lines in a rule
    Output : none : either it prints the rule or not :) 
    """
    for process_name in av_process_names : 
        if any("Process {0}".format(process_name) in line for line in rule) :
            return
    #if function not returned - print
    print_rule(rule)    
            
def print_rule(rule) :
    """
    Input : rule : iterable representing lines in a rule
    Output : none : prints given rule
    """
    for line in rule :
        print line                
           
if __name__ == "__main__" : 
    parser=argparse.ArgumentParser(description='Filters vol.py yarascan results. Allows user to include/exclude processes')
    group=parser.add_mutually_exclusive_group()
    parser.add_argument('-f', '--filename', type = argparse.FileType('r'), default = '-',
                        help='Yarascan result file (uses STDIN by default)')
    group.add_argument('-i', '--include', type=int, nargs='+',
                       help='Process IDs to include')
    group.add_argument('-e', '--exclude', type=int, nargs='+',
                       help='Process IDs to exclude')
    parser.add_argument('-d', '--exclude_av', action='store_true',
                        help='Exlude known AV processes. May hide cleverly named malware')                   
    args = parser.parse_args()
    
    #open yarascan results file
    infile = args.filename
    print infile
    in_lines = infile.readlines()    

    #read a rule into buffer array
    rule = []   
    for line in in_lines : 
        #check if we are at the start of a new rule
        if "Rule: " in line : 
            #process old rule if needed
            if rule : 
                if args.include : 
                    process_include_rule(rule, args.include)
                elif args.exclude:
                    process_exclude_rule(rule, args.exclude)
                elif args.exclude_av :
                    #this condition should only trigger when -e is not also given
                    process_exclude_av_rule(rule)    
                else : 
                    print_rule(rule)
                    
            #start a new rule    
            rule = [line.strip()]
            
        #check if we are in the middle of a rule
        elif rule :
            rule.append(line.strip())
        
        #else pass -- line is not part of a rule (maybe broken file)