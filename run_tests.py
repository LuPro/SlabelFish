import subprocess

#TODO sometimes files only differed by trailing whitespace, cmp outputs a certain text to stdout in that case, try to filter that out
def main():
    foundError = False
    #e2e tests
    #------- roundtrip test
    print("Testing roundtrip...", end=" ", flush=True)
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
    print("Testing roundtrip alternate slab...", end=" ", flush=True)
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

    #------- roundtrip with automatic mode
    print("Testing roundtrip in automatic mode...", end=" ", flush=True)
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
    print("Testing decoding...", end=" ", flush=True)
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

    #------- encode test
    print("Testing encode...", end=" ", flush=True)
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




    if (foundError):
        print("Not all tests finished without errors!")
    else:
        print("All tests completed successfully")


if __name__ == '__main__':
    main()
