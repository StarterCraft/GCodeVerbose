#coding=utf-8
from os           import pathsep, makedirs
from sys          import argv, exit as sexit
from datetime     import datetime
from collections  import Counter

from humanize     import naturaldelta

from layerBlock   import LayerBlock
from sequence     import PrintSequence
from tqdm         import tqdm

code = ''
codeLines = []

def getLayerBlock(blocks: list[LayerBlock], lineNo: int) -> LayerBlock | None:
    _blocks = [layerBlock for layerBlock in blocks if (lineNo in layerBlock)]

    return _blocks[0] if _blocks else None

def main(args: list[str]) -> int:
    try:
        startTime = datetime.now()
        paths: list[str] = []
        makedirs('output', exist_ok = True)

        if (args):
            paths = args[1:]
        else:
            paths.append(input('Enter the full path to the G-Code file: '))

        for lno, path in enumerate(paths):
            print('Checking file no.', lno + 1, 'at', path)

            fileName = path.split(pathsep)[-1]

            outputLines: list[str] = []
                
            fileStart = datetime.now()

            with open(path, 'r') as inputFile, open(f'output/{fileName}', 'w') as outputFile:
                code = inputFile.read()

                if (not code.startswith(';FLAVOR:')):
                    # If not G-Code, don-t process
                    print(f'{fileName} is not a valid G-Code file. Skipping.')
                    continue

                codeLines = code.splitlines()

                lcCmt = code.find(';LAYER_COUNT:')
                assert lcCmt > -1, 'Invalid G-Code: layer count is not defined'
                
                sequences: list[PrintSequence] = []

                layerCounts = [(ix, line) for ix, line in enumerate(codeLines) if line.startswith(';LAYER_COUNT:')]
                for ix, lco in enumerate(layerCounts):
                    sequences.append(
                        PrintSequence(
                        codeLines,
                        range(lco[0], layerCounts[ix + 1][0] if (ix + 1 < len(layerCounts)) else codeLines.index('G91 ;Relative positioning')), 
                        int(lco[1][13:])
                        ))
                    
                firstSeqStart = sequences[0].seqRange.start
                totalCommands = len([line for line in codeLines if (line.startswith('G1'))])
                print('Total movement commands detected:', totalCommands)

                outputLines.extend(codeLines[:firstSeqStart])
                
                print('Patching lines...')

                for seq_ix, sequence in enumerate(sequences):
                    seqStart = datetime.now()
                    print('Sequence', seq_ix + 1, 'of', len(sequences))

                    print('Adding status commands for this sequence')

                    # Layers blocks are those groups of printing operations, which are done in one layer
                    layerBlocks = [
                        LayerBlock(
                            n,
                            sequence.lines,
                            sequence.lines.index(f';LAYER:{n}'), 
                            sequence.lines.index(f';LAYER:{n + 1}')
                            if (f';LAYER:{n + 1}' in sequence.code) else codeLines.index('G91 ;Relative positioning')
                            )
                        for n in range(sequence.layersCount)]
                    
                    commandsProcessed = 0
                    commandsInThisLayerBlock = 0
                    currentLayerBlockId = 0
                    previousLayerBlockId = 0

                    with tqdm(total = totalCommands, colour = '#00ff00') as progressPatch:
                        for lineNo, codeLine in enumerate(sequence.lines):
                            layerBlock = getLayerBlock(layerBlocks, lineNo)
                            currentLayerBlockId = layerBlock.ix if layerBlock else 0
                            if (layerBlock and codeLine.startswith('G1')):
                                if (currentLayerBlockId == previousLayerBlockId):
                                    commandsInThisLayerBlock += 1
                                else:
                                    commandsInThisLayerBlock = 1
                                    previousLayerBlockId = currentLayerBlockId

                                # This is a G1 command
                                percentage = round((commandsInThisLayerBlock / len(layerBlock)) * 100)

                                outputLines.append(codeLine)
                                outputLines.append('M117 L {} {}%'.format(currentLayerBlockId, percentage))

                                commandsProcessed += 1
                                progressPatch.update()
                            else:
                                outputLines.append(codeLine)

                    print()
                    print('Removing duplicate status commands to reduce refresh intensity...')

                    counterDuplicates = Counter([line for line in outputLines if (line.startswith('M117 L'))])

                    with tqdm(total = sum(counterDuplicates.values()) - len(counterDuplicates.keys()), colour = '#00ff00') as progressDuplicates:
                        for line, count in counterDuplicates.items():
                            firstOccurrence = outputLines.index(line)

                            for i in range(count):
                                outputLines.remove(line)
                                progressDuplicates.update()

                            outputLines.insert(firstOccurrence, line)
                            progressDuplicates.update(-1)

                    seqEnd = datetime.now()
                    seqDelta = seqEnd - seqStart

                    print('Desired operations for sequence', seq_ix, 'completed in', naturaldelta(seqDelta))
                    print()

                outputFile.write('\n'.join(outputLines))

            fileEnd = datetime.now()
            fileDelta = fileEnd - fileStart

            print('Desired operations for file', fileName, 'completed in', naturaldelta(fileDelta))

        endTime = datetime.now()
        doneIn = endTime - startTime

        print('\nDesired operations completed in', naturaldelta(doneIn))
        print('Thanks.')
        return 0
    
    except KeyboardInterrupt:
        print('\nAborted by user.')
        return 1

if (__name__ == '__main__'):
    sexit(main(argv))
