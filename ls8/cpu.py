"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = True
        self.pc = 0 #Program Counter
        self.ram = [None]*256 #RAM
        self.flagg = 0 #flag register?

        self.reg = [0]*8 #Registries - R0 through R7
        self.sp = 7 #Stack Pointer - defines which registry # is the stack pointer
        self.reg[self.sp] = 0

        self.return_addr = 0

        self.appsPath = './apps/'

    def load(self):
        """Load a program into memory."""

        #listing apps to load

        import os

        for file in os.listdir(self.appsPath):
            if os.path.isfile(os.path.join(self.appsPath, file)):
                print(file)

        #user choosing app to load

        text = input('\nchoose an app to execute...\n')
        address = 0

        try:
            with open(f'{self.appsPath}{text}') as f:
                for line in f:
                    line_list = line.strip().split('#')
                    clean_line = line_list[0]
                    if clean_line == '':
                        continue

                    try:
                        clean_line = int(clean_line, 2)
                    except ValueError:
                        print(f'Invalid instuction: {clean_line} ')
                        sys.exit(1)

                    self.ram_write(address, clean_line)
                    address += 1
                    
        except FileNotFoundError:
            print(f'File not found: {text}')
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == 'MUL':
            self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flags = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flags = 0b10000010
            else:
                self.flags = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")
    
    def ram_read(self, MAR):
        return self.ram[MAR]
    
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        #instruction functions

        def HLT(): #Halt PC
            print(f'shutting down... last program counter: {self.pc}')
            self.running = False

        def LDI(): #Save data to registry # regID
            regID = self.ram_read(self.pc+1)
            data = self.ram_read(self.pc+2)
            self.reg[regID] = data
            self.pc += 3

        
        def PRN(): #Print value in registry # regID
            regID = self.ram_read(self.pc+1)
            print(self.reg[regID])
            self.pc += 2
        
        def ADD():
            regID1 = self.ram_read(self.pc+1)
            regID2 = self.ram_read(self.pc+2)
            self.alu('ADD', regID1, regID2)

        def MUL(): #Multiply two registries and save the value at registry # regID1
            regID1 = self.ram_read(self.pc+1)
            regID2 = self.ram_read(self.pc+2)
            self.alu('MUL', regID1, regID2)
            self.pc += 3
        
        def PSH(): #Push to the stack
            regID = self.ram_read(self.pc+1)
            self.reg[self.sp] -= 1
            value = self.reg[regID]
            tosa = self.reg[self.sp] #top of stack address
            self.ram[tosa] = value

            self.pc += 2


        def POP(): #Pop from the stack

            reg_num = self.ram[self.pc+1]
            tosa = self.reg[self.sp]
            value = self.ram[tosa]

            self.reg[reg_num] = value

            self.reg[self.sp] += 1
            self.pc += 2

        def CMP(): 
            self.alu('CMP', self.ram[self.pc + 1], self.ram[self.pc + 2])
            self.pc += 3

        def JNE():
            if (self.flags & 0b00000001) == 0:
                JMP()
            else:
                self.pc += 2

        def JEQ():
            if (self.flags & 0b00000001) == 1:
                JMP()
            else:
                self.pc += 2

        def JMP():
            self.pc = self.reg[self.ram[self.pc + 1]]

        branchDict = {
            '1': HLT,
            '130': LDI,
            '71': PRN,
            '162': MUL,
            '69': PSH,
            '70': POP,
            '160': ADD,
            '167': CMP,
            '86': JNE,
            '85': JEQ,
            '84': JMP

        }

        while self.running:

            try:
                ir = self.ram_read(self.pc)

                branchDict[str(ir)]()
            except: #assume incorrect instruction
                self.pc += 1
                print(f'line skipped: {self.pc-1}')


