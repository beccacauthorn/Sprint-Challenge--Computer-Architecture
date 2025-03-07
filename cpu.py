"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CMP = 0b10100111 
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.reg[7] = 0xF4
        self.pc = 0
        self.fl = 0b00000000
        self.halted = False 

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, val):
        self.ram[address] = val
        
    def load(self, filename):
        """Load a program into memory."""
        address = 0
        with open(filename) as fp:
            for line in fp:
                comment_split = line.split("#")
                num = comment_split[0].strip()
                if num == '':  # ignore blanks
                    continue
                val = int(num, 2)
                self.ram_write(address, val)
                address += 1
        # For now, we've just hardcoded a program:

        #program = [
        #   # From print8.ls8
        #    0b10000010, # LDI R0,8
        #   0b00000000,
        #    0b00001000,
        #   0b01000111, # PRN R0
        #    0b00000000,
        #   0b00000001, # HLT
        #]

        #for instruction in program:
        #    self.ram[address] = instruction
        #    address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

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
        while not self.halted:
            instruction_to_execute = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            self.execute_instruction(instruction_to_execute, operand_a, operand_b)

    def execute_instruction(self, instruction, operand_a, operand_b):
        if instruction == HLT:
            self.halted = True
            self.pc += 1
        elif instruction == LDI:
            self.reg[operand_a] = operand_b
            self.pc += 3
        elif instruction == PRN:
            print(self.reg[operand_a])
            self.pc += 2
        elif instruction == MUL:
            self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]
            self.pc += 3
        elif instruction == PUSH:
            # decrement the stack pointer
            self.reg[SP] -= 1
            # write the value stored in register onto the stack
            valueFromRegister = self.reg[operand_a]
            self.ram_write(valueFromRegister, self.reg[SP])
            self.pc += 2
        elif instruction == POP:
            # save the value on top of the stack onto the register given
            topmostValue = self.ram_read(self.reg[SP])
            self.reg[operand_a] = topmostValue
            # increment the stack pointer
            self.reg[SP] += 1
            self.pc += 2
        elif instruction == CMP:
            if self.reg[operand_a] == self.reg[operand_b]:
                self.fl = 0b00000001
            if self.reg[operand_a] > self.reg[operand_b]:
                self.fl = 0b00000010
            if self.reg[operand_a] < self.reg[operand_b]:
                self.fl = 0b00000100
            self.pc += 3
        elif instruction == JMP:
            self.pc = self.reg[operand_a]
        elif instruction == JEQ:
            if (self.fl & 0b00000001) == 1:
                self.pc = self.reg[operand_a]
            else:
                self.pc += 2
        elif instruction == JNE:
            if (self.fl & 0b00000001) == 0:
                self.pc = self.reg[operand_a]
            else:
                self.pc += 2

        else:
            print('unrecognized instruction ', instruction)
            quit()
        