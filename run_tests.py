import subprocess

def main():
    #e2e tests
    #roundtrip test
    print("Testing roundtrip...")
    result = "empty"
    try:
        result = subprocess.check_output('python slabelfish.py -dqc --in_file="test_slabs/bigger_test_reencode" | python slabelfish.py -eq --ts_dir="testing_data/" --in_file="stdin" | cmp -b test_slabs/bigger_test_reencode', shell=True, encoding="ascii", stderr=subprocess.STDOUT)
    except Exception as e:
        if (e.returncode == 1): #return code 1 for cmp means files differ
            print("FAIL\nInfo:", e.output)
        elif (e.returncode == 2): #return code 2 for cmp means error occurred
            print("FAIL\nException occurred:", e, "\nOutput:", e.output)


if __name__ == '__main__':
    main()
