"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = True
        self.pc = 0 #Program Counter
        self.ram = [None]*256 #RAM

        self.reg = [None]*8 #Registries - R0 through R7
        self.sp = 7 #Stack Pointer - defines which registry # is the stack pointer
        self.reg[self.sp] = 244

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
                    if line == '':
                        continue

                    try:
                        line = int(line, 2)
                    except ValueError:
                        print(f'Invalid instuction: {line} ')
                        sys.exit(1)

                    self.ram_write(address, line)
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

        #instruction functions - "ignore" arguments are passed to get rid of positional argument errors; temporary fix

        def HLT(ignore1, ignore2): #Halt PC
            print('shutting down...')
            self.running = False

        def LDI(regID, data): #Save data to registry # regID
            self.reg[regID] = data
            self.pc += 3
        
        def PRN(regID, ignore): #Print value in registry # regID
            print(self.reg[regID])
            self.pc += 2

        def MUL(regID1, regID2): #Multiply two registries and save the value at registry # regID1
            self.alu('MUL', regID1, regID2)
            self.pc += 3
        
        def PSH(ignore1, ignore2): #Push to the stack
            self.reg[self.sp] -= 1
            reg_num = self.ram[self.pc + 1]
            value = self.reg[reg_num]
            tosa = self.reg[self.sp] #top of stack address
            self.ram[tosa] = value

            self.pc += 2

        def POP(ignore1, ignore2): #Pop from the stack

            reg_num = self.ram[self.pc+1]
            tosa = self.reg[self.sp]
            value = self.ram[tosa]

            self.reg[reg_num] = value

            self.reg[self.sp] += 1
            self.pc += 2
        
        def CALL(ignore1, ignore2): #needs work...
            return_addr = self.pc + 2
            
            self.reg[self.sp] -= 1
            tosa = self.reg[self.sp]
            self.ram[tosa] = return_addr

            reg_num = self.ram[pc + 1]
            value = self.reg[reg_num]

            self.pc = value

        branchDict = {
            '1': HLT,
            '130': LDI,
            '71': PRN,
            '162': MUL,
            '69': PSH,
            '70': POP,
            '80': CALL
        }

        while self.running:

            try:
                ir = self.ram_read(self.pc)
                operand_a = self.ram_read(self.pc+1)
                operand_b = self.ram_read(self.pc+2)

                branchDict[str(ir)](operand_a, operand_b)
            except: #assume incorrect instruction
                self.pc += 1


