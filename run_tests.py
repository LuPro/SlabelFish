import subprocess

#TODO sometimes files only differed by trailing whitespace, cmp outputs a certain text to stdout in that case, try to filter that out
def main():
    foundError = False
    #e2e tests
    print("End to End testing of pipeline/CLI usage")
    #------- roundtrip test
    print("Testing Roundtrip...", end=" ", flush=True)
    result = "empty"
    try:
        result = subprocess.check_output('python slabelfish.py -dqc --in_file="testing_data/validation_slab" | python slabelfish.py -eq --ts_dir="testing_data/" --in_file="stdin" | cmp -b -i 16 testing_data/validation_slab', shell=True, encoding="ascii", stderr=subprocess.STDOUT)
        print("PASS")
    except Exception as e:
        foundError = True
        if (e.returncode == 1): #return code 1 for cmp means files differ
            print("FAIL\nInfo:", e.output)
        elif (e.returncode == 2): #return code 2 for cmp means error occurred
            print("FAIL\nException occurred:", e, "\nOutput:", e.output)
    #------- roundtrip test alt slab
    print("        Roundtrip alternate slab...", end=" ", flush=True)
    result = "empty"
    try:
        result = subprocess.check_output('python slabelfish.py -dqc --in_file="testing_data/validation_slab_2" | python slabelfish.py -eq --ts_dir="testing_data/" --in_file="stdin" | cmp -b -i 16 testing_data/validation_slab_2', shell=True, encoding="ascii", stderr=subprocess.STDOUT)
        print("PASS")
    except Exception as e:
        foundError = True
        if (e.returncode == 1): #return code 1 for cmp means files differ
            print("FAIL\nInfo:", e.output)
        elif (e.returncode == 2): #return code 2 for cmp means error occurred
            print("FAIL\nException occurred:", e, "\nOutput:", e.output)
    #------- roundtrip test alt slab
    print("        Roundtrip alternate slab 2...", end=" ", flush=True)
    result = "empty"
    try:
        result = subprocess.check_output('python slabelfish.py -dqc --in_file="testing_data/validation_slab_3" | python slabelfish.py -eq --ts_dir="testing_data/" --in_file="stdin" | cmp -b -i 16 testing_data/validation_slab_3', shell=True, encoding="ascii", stderr=subprocess.STDOUT)
        print("PASS")
    except Exception as e:
        foundError = True
        if (e.returncode == 1): #return code 1 for cmp means files differ
            print("FAIL\nInfo:", e.output)
        elif (e.returncode == 2): #return code 2 for cmp means error occurred
            print("FAIL\nException occurred:", e, "\nOutput:", e.output)

    #------- roundtrip with automatic mode
    print("        Roundtrip in automatic mode...", end=" ", flush=True)
    result = "empty"
    try:
        result = subprocess.check_output('python slabelfish.py -aqc --in_file="testing_data/validation_slab" | python slabelfish.py -aq --ts_dir="testing_data/" --in_file="stdin" | cmp -b -i 16 testing_data/validation_slab', shell=True, encoding="ascii", stderr=subprocess.STDOUT)
        print("PASS")
    except Exception as e:
        foundError = True
        if (e.returncode == 1): #return code 1 for cmp means files differ
            print("FAIL\nInfo:", e.output)
        elif (e.returncode == 2): #return code 2 for cmp means error occurred
            print("FAIL\nException occurred:", e, "\nOutput:", e.output)

    #------- decode test
    print("Testing Decoding...", end=" ", flush=True)
    result = "empty"
    try:
        result = subprocess.check_output('python slabelfish.py -dq --in_file="testing_data/validation_slab_2" | cmp -b -i 16 testing_data/validation_slab_2.json', shell=True, encoding="ascii", stderr=subprocess.STDOUT)
        print("PASS")
    except Exception as e:
        foundError = True
        if (e.returncode == 1): #return code 1 for cmp means files differ
            print("FAIL\nInfo:", e.output)
        elif (e.returncode == 2): #return code 2 for cmp means error occurred
            print("FAIL\nException occurred:", e, "\nOutput:", e.output)
    #------- decode test alternate
    print("        Decoding alternate slab...", end=" ", flush=True)
    result = "empty"
    try:
        result = subprocess.check_output('python slabelfish.py -dq --in_file="testing_data/validation_slab_3" | cmp -b -i 16 testing_data/validation_slab_3.json', shell=True, encoding="ascii", stderr=subprocess.STDOUT)
        print("PASS")
    except Exception as e:
        foundError = True
        if (e.returncode == 1): #return code 1 for cmp means files differ
            print("FAIL\nInfo:", e.output)
        elif (e.returncode == 2): #return code 2 for cmp means error occurred
            print("FAIL\nException occurred:", e, "\nOutput:", e.output)

    #------- encode test
    print("Testing Encoding...", end=" ", flush=True)
    result = "empty"
    try:
        result = subprocess.check_output('python slabelfish.py -eq --ts_dir="testing_data/" --in_file="testing_data/validation_slab_2.json" | cmp -b -i 16 testing_data/validation_slab_2', shell=True, encoding="ascii", stderr=subprocess.STDOUT)
        print("PASS")
    except Exception as e:
        foundError = True
        if (e.returncode == 1): #return code 1 for cmp means files differ
            print("FAIL\nInfo:", e.output)
        elif (e.returncode == 2): #return code 2 for cmp means error occurred
            print("FAIL\nException occurred:", e, "\nOutput:", e.output)
    #------- encode test alternate
    print("        Encoding alternate slab...", end=" ", flush=True)
    result = "empty"
    try:
        result = subprocess.check_output('python slabelfish.py -eq --ts_dir="testing_data/" --in_file="testing_data/validation_slab_3.json" | cmp -b -i 16 testing_data/validation_slab_3', shell=True, encoding="ascii", stderr=subprocess.STDOUT)
        print("PASS")
    except Exception as e:
        foundError = True
        if (e.returncode == 1): #return code 1 for cmp means files differ
            print("FAIL\nInfo:", e.output)
        elif (e.returncode == 2): #return code 2 for cmp means error occurred
            print("FAIL\nException occurred:", e, "\nOutput:", e.output)




    if (foundError):
        print("Not all tests finished without errors!")
    else:
        print("All tests completed successfully")


if __name__ == '__main__':
    main()
