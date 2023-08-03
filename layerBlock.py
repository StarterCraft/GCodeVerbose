# -*- coding: utf-8 -*-
class LayerBlock:
    def __init__(self, ix: int, codeLines: list[str], start: int, end: int):
        self.ix = ix
        self.lines = codeLines
        self.start = start
        self.end = end
        self.range = range(start, end)

    def __len__(self) -> int:
        return len([command for command in self.lines[self.start:self.end] if (command.startswith('G1'))])
    
    def __contains__(self, lno: int) -> bool:
        return lno in self.range
    
    def __repr__(self) -> str:
        return f'Layer {self.ix} on lines {self.start} to {self.end} with total printing commands {len(self)}'
    