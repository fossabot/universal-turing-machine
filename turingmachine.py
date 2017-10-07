#!/usr/bin/env python3
# coding=utf-8

import json
import argparse

import time
import os


EMPTY_CHARACTER = ' '


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Implementation of a universal Turing Machine.')
    parser.add_argument('-b', '--initial', type=str, action='store',
                        default='q0', help='Initial state to begin')
    parser.add_argument('-e', '--end', type=str,
                        action='store', default='qdone', help='End state')
    parser.add_argument('-s', '--speed', type=float, action='store',
                        default=.3, help='Rendering speed in seconds')
    parser.add_argument('-r', '--render', action='store_true',
                        default=False, help='Render turing machine')
    parser.add_argument('-a', '--interactive', action='store_true', default=False,
                        help='Interactive mode, speed will be useless when using this parameter')
    required_arguments = parser.add_argument_group('required arguments')
    required_arguments.add_argument('-i', '--instructions', type=str, action='store',
                                    default=False, required=True, help='Instructions, as JSON file')
    required_arguments.add_argument(
        '-t', '--input', type=str, action='store', default=False, required=True, help='Input tape')
    return parser.parse_args()


class TuringMachine(object):
    def __init__(self, instructions, tape, start_state, end_state, render, speed, interactive):
        self.instructions = instructions
        self.tape = list(tape)
        self.state = start_state
        self.end_state = end_state
        self.render = render
        self.speed = speed
        self.interactive = interactive
        self.validate_instruction(self.instructions, self.end_state)

    def run(self):
        counter = 0
        index = 0
        self.render_screen(index, counter)
        if not self.render:
            print("Render mode is disabled. Calculating results, please wait.")
        while self.state != self.end_state:
            counter += 1
            if index == -1:
                self.tape.insert(0, EMPTY_CHARACTER)
                index = 0
            if index < len(self.tape):
                cell = self.tape[index]
            else:
                cell = EMPTY_CHARACTER
                self.tape.append(EMPTY_CHARACTER)
            self.tape[index] = self.instructions[self.state][cell]['write']
            index += self.get_direction(
                self.instructions[self.state][cell]['move'])
            self.state = self.instructions[self.state][cell]['nextState']
            if self.render:
                self.render_screen(index, counter)
        self.render_screen(index, counter)
        return self.list_to_string(self.remove_empty_character(self.tape))

    def render_screen(self, index, counter):
        visible_tape = 15
        padding_start = visible_tape - index
        padding_end = visible_tape - (len(self.tape) - (index + 1))
        dynamic_start = index - visible_tape if index >= visible_tape else 0
        dynamic_end = len(self.tape) - (len(self.tape) - index - visible_tape) if len(
            self.tape) - index > visible_tape else len(self.tape)
        os.system('clear')
        print('Steps Counter {}'.format(str(counter).rjust(7)))
        print('Current State {}'.format(self.state.rjust(7)))
        print('Tape Index {} '.format(str(index).rjust(10)))
        print(visible_tape * 2 * ' ' + '▼')
        self.print_between_pipes(padding_start * ' ' + self.list_to_string(self.tape)
                              [dynamic_start:dynamic_end] + padding_end * ' ')
        print(visible_tape * 2 * ' ' + '▲')
        self.print_character_occurrences(self.tape)
        if self.interactive:
            input()
        else:
            time.sleep(self.speed)

    @staticmethod
    def print_character_occurrences(tape):
        clean_tape = TuringMachine.remove_empty_character(tape)
        occurrences = {character: 0 for character in clean_tape}
        for character in clean_tape:
            occurrences[character] += 1
        print('Character Counter')
        for character, occurrence in occurrences.items():
            print('{}x: {}'.format(occurrence, character))
        print()

    @staticmethod
    def validate_instruction(instructions, end_state):
        for instruction in instructions:
            for case in instructions[instruction]:
                state_to_check = instructions[instruction][case]['nextState']
                if state_to_check not in instructions and state_to_check != end_state:
                    raise Exception('Invalid configuration, the state {} does not exist!'.format(state_to_check))

    @staticmethod
    def list_to_string(to_stringify):
        return str.join('', to_stringify)

    @staticmethod
    def print_between_pipes(string):
        print('|'.join(string[i:i + 1] for i in range(0, len(string))))

    @staticmethod
    def get_direction(direction):
        directions = {'right': 1, 'left': -1}
        return directions[direction] if direction in directions else 0

    @staticmethod
    def remove_empty_character(dirty_list):
        return [character for character in dirty_list if character != EMPTY_CHARACTER]


def main():
    args = parse_arguments()
    try:
        instructions = json.loads(open(args.instructions).read())
        result = TuringMachine(instructions,
                               args.input,
                               args.initial,
                               args.end,
                               args.render,
                               args.speed,
                               args.interactive).run()
        print('Input: {}'.format(args.input))
        print('Output: {}'.format(result))
    except Exception as e:
        print('Something went wrong! Issue: {}'.format(e))


if __name__ == '__main__':
    main()