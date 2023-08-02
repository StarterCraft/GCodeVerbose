class PrintSequence:
    def __init__(self, codeLines: list[str], seqRange: range, layersCount: int, ranges: list[range] = []) -> None:
        self.lines = codeLines[seqRange.start:seqRange.stop]
        self.code = '\n'.join(self.lines)
        self.seqRange = seqRange
        self.start = seqRange.start
        self.stop = seqRange.stop
        self.layersCount = layersCount
