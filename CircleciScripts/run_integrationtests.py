import demjson
import sys
from subprocess import Popen, PIPE
import subprocess
import xml.etree.ElementTree as ET
import os
from datetime import datetime
#from sets import Set
def getfailedcases(): 
  
    xmlfile='build/reports/junit.xml'
    tree = ET.parse(xmlfile) 
    root = tree.getroot() 
    testbundle = root.get('name')
    testbundle = testbundle[0:len(testbundle) - 7]

    failedtests = set()

    #TODO  we can filter with condtion 
    for testsuite in root.findall(".//testsuite"):  

        for testcase in testsuite.findall('.//testcase[failure]'): 
            suitename = testsuite.get('name')
            casename = testcase.get('name')
            failedtests.add(testbundle + '/' + suitename + '/' + casename)
    return failedtests 

def runcommand(command, timeout=0,pipein=None, pipeout =  None):
    print("running command: ", command, "......")
    process = Popen(command, shell=True, stdin=pipein, stdout = pipeout)
    wait_times = 0 
    while True:
        try:
            process.communicate(timeout = 10)
        except subprocess.TimeoutExpired:        
            #tell circleci I am still alive, don't kill me
            if wait_times % 30 == 0 :
                print(str(datetime.now())+ ": I am still alive")
            # if time costed exceed timeout, quit
            if timeout >0 and wait_times > timeout * 6 :
                print(str(datetime.now())+ ": time out")
                return 1
            wait_times+=1 

            continue
        break
    exit_code = process.wait()    
    return exit_code

 #run test   
def runtest(otherargments, timeout = 0):
    runcommand("rm raw.log")
    runcommand("rm xcpretty.log")
    testcommand = "xcodebuild   test-without-building  -project AWSiOSSDKv2.xcodeproj -scheme AWSAllTests -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 8,OS=12.1'" 
    testcommand +=" " +  otherargments;
    rawoutput = open('raw.log','w')
    exit_code = runcommand(testcommand,timeout, pipeout = rawoutput)
    rawoutput.close()
    print("Formatting test result .......")
  #  xcprettyoutput = open('xcpretty.log','w')
    xcprettycommand = "cat raw.log | xcpretty -r junit  | tee xcpretty.log"
    runcommand(xcprettycommand)
    return exit_code
   # xcprettyoutput.close()
    


##########################  main function ###############################

jsonfilename=sys.argv[1]

with open(jsonfilename, 'r') as jsonfile:
    jsonstring = jsonfile.read()
testlist = demjson.decode(jsonstring)
testcommandhead = "xcodebuild   test-without-building  -project AWSiOSSDKv2.xcodeproj -scheme AWSAllTests -sdk iphonesimulator -destination 'platform=iOS Simulator,name=iPhone 8,OS=12.1'"
testcommandtail = "    | tee raw.log  | xcpretty -r junit | tee xcpretty.log"
for testname in testlist:


    print("-------------------------------", testname , "-------------------------------");
    
    test = testlist[testname]
    testarguments = ' -only-testing:' + testname
    #create skipping tests parameters 
    skipingtests = ""
    if 'skipingtests' in test:
        for skipingtest in test['skipingtests']:
            skipingtests += ' -skip-testing:' + testname+ "/" + skipingtest
    timeout = 0 
    if 'timeout' in test:
        timeout = test['timeout']

    exit_code = runtest(testarguments + skipingtests, timeout)
    print(testname, "exit code:", exit_code)
    # if test fails, check if the failed tests can be retried
    if exit_code != 0:
        if 'retriabletests' in test:
            retriableset = set()
            suitesname = testname;
            #get retriable test cases
            for retriabletest in test['retriabletests']:
                retriableset.add(suitesname + "/" + retriabletest) 
            print("retriabletests", retriableset)
            allretriable = True 
            #get all failed test cases
            faileds = getfailedcases()
            if len(faileds) == 0 :
                print("test command return an error code, but the failed test cases is 0")
                print("exit code:", exit_code)
                break;
            print("failed tests:",faileds)
            notretriabletests = faileds - retriableset 
            #only retry when all failed test cases are retriable
            if len(notretriabletests) > 0 :
                print("not retriable tests:", notretriabletests)
                break;

            #default retry times is 3
            retriabletimes = 3 
            if 'retriabletimes' in test:
                retriabletimes = test['retriabletimes']
            retrytimes = 1
            
            while retrytimes <= retriabletimes  and exit_code > 0:
                print("retry ", testname, "for ", retrytimes, " times")
                testarguments = ""
                for failed in faileds:
                    testarguments += ' -only-testing:' + failed
                retrytimes += 1
                exit_code = runtest(testarguments, timeout);
                print("retry exit code:", exit_code)                
                if(exit_code != 0 ):
                    faileds = getfailedcases()
    if exit_code != 0 :
        runcommand('mkdir integration_test_result/{0}'.format(testname))
        runcommand('mv raw.log integration_test_result/{0}/raw.log'.format(testname))
        runcommand('mv xcpretty.log integration_test_result/{0}/xcpretty.log'.format(testname))
        runcommand('mv build/reports/junit.xml integration_test_result/{0}/junit.xml'.format(testname))
                        


        



