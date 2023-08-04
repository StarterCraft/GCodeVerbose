# -*- coding: utf-8 -*-
class PrintSequence:
    def __init__(self, codeLines: list[str], seqRange: range, layersCount: int) -> None:
        self.lines = codeLines[seqRange.start:seqRange.stop]
        self.code = '\n'.join(self.lines)
        self.seqRange = seqRange
        self.start = seqRange.start
        self.stop = seqRange.stop
        self.layersCount = layersCount
        self.totalCommands = len([line for line in self.lines if (
            line.startswith('G1') or line.startswith(';TYPE:'))])
    
    def __len__(self) -> int:
        return self.totalCommands
