# $t0: store from memory
# $t1, $t2, $t3: arithmetic operation
# $t4: get input
# $t5: 
# $t6 return data

filename = "./tac.txt"

head_input_file = open("data.txt", 'r')
input_file = open(filename, 'r')
output_file = open("assembly.asm", 'w')

mem = {}

mem["func"] = "$t6"

fp = 0

output_file.write(".data\n")
for line in head_input_file:
    output_file.write("\t" + line)

output_file.write("\n.text\n.globl main\n\n")

for line in input_file:
    flag = ""
    command = line.replace("\n","").split(" ")
    if (len(command) == 5 and command[1] == "="):
        output_file.write("#=====Arithmetic Assignment=====\n")
        if ")" in command[len(command)-1]:
            idx1 = command[len(command)-1].index("(")
            idx2 = command[len(command)-1].index(")")
            res = command[len(command)-1][idx1 + len("("): idx2]
            output_file.write("\tlw $a0, " + mem[res])
        elif not command[2].isdigit():
            output_file.write("\tlw $t1, " + mem[command[2]] + "\t# " + command[2] + "\n")
            flag = "F"
            fp += 4
        else:
            flag = "T"

        if not command[4].isdigit():
            output_file.write("\tlw $t2, " + mem[command[4]] + "\t# " + command[4] + "\n")
            flag += "F"
            fp += 4
        else:
            flag += "T"
        
        if flag == "TF":
            if command[2].isdigit():
                output_file.write("\tli $t1, " + str(command[2]) + "\n")
            else:
                output_file.write("\tlw $t1, " + str(mem[command[2]]) + "\n")
        elif flag == "FT":
            if command[4].isdigit():
                output_file.write("\tli $t2, " + str(command[4]) + "\n")
            else:
                output_file.write("\tlw $t2, " + str(mem[command[4]]) + "\n")
        else:
            if command[2].isdigit():
                output_file.write("\tli $t1, " + str(command[2]) + "\n")
            else:
                output_file.write("\tlw $t1, " + str(mem[command[2]]) + "\n")
            if command[4].isdigit():
                output_file.write("\tli $t2, " + str(command[4]) + "\n")
            else:
                output_file.write("\tlw $t2, " + str(mem[command[4]]) + "\n")

        if command[3] == "+":
            output_file.write("\tadd ")
        elif command[3] == "-":
            output_file.write("\tsub ")
        elif command[3] == "*":
            output_file.write("\tmul ")
        elif command[3] == "/":
            output_file.write("\tdiv ")
        
        output_file.write("$t3, $t1, $t2")

        output_file.write("\n")
        output_file.write("\tadd $t0, $t3, $zero\n")
        if command[0] in mem:
            output_file.write("\tsw $t0, " + mem[command[0]] + "\t#"+ command[0] + "\n")
        else:
            output_file.write("\tsw $t0, " + str(fp) + "($s0)\t#"+ command[0] + "\n")
            mem[command[0]] = str(fp) + "($s0)"
            fp += 4

    elif (len(command) == 3 and command[1] == "="):
        output_file.write("#=====Assignment=====\n")
        if ")" in command[len(command)-1]:
            idx1 = command[len(command)-1].index("(")
            idx2 = command[len(command)-1].index(")")
            reg = command[len(command)-1][idx1 + len("("): idx2]
            m = command[len(command)-1][: idx1 + len("(")-1]
            output_file.write("\tlw $t0, " + mem[reg] + "\n")
            output_file.write("\tlw $t0, " + m + "($t0)\n")
        elif not command[2].isdigit():
            if not mem[command[2]] == "$t6":
                output_file.write("\tlw $t0, " + mem[command[2]] + "\t# " + command[2] + "\n")
            else:
                output_file.write("\tadd $t0, " + mem[command[2]] + ", $zero" + "\t# " + command[2] + "\n")
        else:
            output_file.write("\tli $t0, " + command[2] + "\n")
        if command[0] in mem:
            output_file.write("\tsw $t0, " + mem[command[0]] + "\t#"+ command[0] + "\n")
        else:
            output_file.write("\tsw $t0, " + str(fp) + "($s0)\t#"+ command[0] + "\n")
            mem[command[0]] = str(fp) + "($s0)"
            fp += 4
    elif ":" in command[0]:
        output_file.write("#=====Block Begin=====\n")
        if command[0] == "start:":
            output_file.write("main:\n")
            output_file.write("\tlui $s0, 0x1001\n")
        else:
            output_file.write(command[0] + "\n")
    elif command[0] == "goto":
        output_file.write("#=====Jump=====\n")
        output_file.write("\tj " + command[1] + "\n")
    elif command[0] == "disp":
        output_file.write("#=====Display=====\n")
        if '$' in command[1]:
            txt = ""
            for i in range(1, len(command)):
                txt += command[i].replace("$","") + " "
            output_file.write("\tli $v0, 4\n")
            output_file.write("\tla $a0, " + txt + "\n")
            output_file.write("\tsyscall\n")
            output_file.write("\tli $v0 11\n")
            output_file.write("\tli $a0, 0x20 \n")
            output_file.write("\tsyscall\n")
        else:
            for i in range(1, len(command)):
                output_file.write("\tli $v0, 1\n")
                output_file.write("\tlw $v1, " + mem[command[i].replace(",", "")] + "\n")
                output_file.write("\tadd $a0, $v1, $zero\n")
                output_file.write("\tsyscall\n") 
                output_file.write("\tli $v0 11\n")
                output_file.write("\tli $a0, 0x20 \n")
                output_file.write("\tsyscall\n")
        output_file.write("\tli $v0 11\n")
        output_file.write("\tli $a0 10\n")
        output_file.write("\tsyscall\n")
    elif command[0] == "get":
        output_file.write("#=====Input=====\n")
        output_file.write("\tli $v0, 5\n")
        output_file.write("\tsyscall\n")
        output_file.write("\tmove $t4, $v0\n")
        if command[1] in mem:
            output_file.write("\tsw $t4, " + mem[command[1]] + "\t#"+ command[1] + "\n")
        else:
            output_file.write("\tsw $t4, " + str(fp) + "($s0)\t#"+ command[1] + "\n")
            mem[command[1]] = str(fp) + "($s0)"
            fp += 4
    elif command[0] == "if":
        output_file.write("#=====If Condition=====\n")
        output_file.write("\tlw $t1, " + mem[command[1]] + "\t# " + command[1] + "\n")
        output_file.write("\tlw $t2, " + mem[command[3]] + "\t# " + command[3]  + "\n")
        output_file.write("\tsub $t3, $t1, $t2\n")

        if command[2] == "=":
            output_file.write("\tbeq $t3, $zero, " + command[5] + "\n")
        elif command[2] == "<":
            output_file.write("\tbltz $t3, " + command[5] + "\n")
        elif command[2] == ">":
            output_file.write("\tbgtz $t3, " + command[5] + "\n")
        elif command[2] == "<=":
            output_file.write("\tblez $t3, " + command[5] + "\n")
        elif command[2] == ">=":
            output_file.write("\tbgez $t3, " + command[5] + "\n")
    elif command[0] == "send":
        output_file.write("\tlw " + mem["func"] + ", " + mem[command[1]] + "\n")
    elif command[0] == "":
        continue
    else:
        output_file.write("\t" + str(command) + "\n")

output_file.write("\n\tjr $ra")
output_file.close()
input_file.close()