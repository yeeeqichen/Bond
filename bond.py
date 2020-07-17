from sys import argv
folder_path = argv[1]
names = []
with open(folder_path + '/names.txt') as f:
    for line in f:
        a = line.split(' ')
        names.append((a[0], a[1][:-1]))
cnt = 0
with open(folder_path + '/unmatch{}.txt'.format(argv[2]), 'w') as f1:
    with open(folder_path + '/samples{}.txt'.format(argv[2])) as f2:
        for line in f2:
            cnt += 1
            flag = 0
            if cnt % 100 == 0:
                print(cnt)
            for name in names:
                if name[0] in line or name[1] in line:
                    flag = 1
                    break
            if flag == 0:
                print(line)
                f1.write(line)
