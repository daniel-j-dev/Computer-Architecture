"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = True
        self.pc = 0
        self.ram = [None]*256
        self.reg = [None]*8
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

        #address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


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
        #instruction definitions
        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        #run code
        while self.running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)
            if ir == HLT:
                print('shutting down...')
                self.running = False
            elif ir == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif ir == PRN:
                print(self.reg[operand_a])
                self.pc += 2
            elif ir == MUL:
                self.alu('MUL', operand_a, operand_b )
                self.pc += 3
            else:
                print('invalid instruction')
                self.pc += 1

