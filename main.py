# -*- coding: utf-8 -*-
#coding=utf-8
from os           import makedirs
from os.path      import sep as pathsep
from typing       import Annotated
from datetime     import datetime
from glob         import glob

from pathlib      import Path
from typer        import run, Argument, Option
from humanize     import precisedelta

from layerBlock   import LayerBlock
from sequence     import PrintSequence
from tqdm         import tqdm

__version__ = 3
printTypes = {
    ';TYPE:SKIN': 'SK',
    ';TYPE:FILL': 'FL',
    ';TYPE:WALL-INNER': 'WI',
    ';TYPE:WALL-OUTER': 'WO',
    ';TYPE:SKIRT': 'AS',
    ';TYPE:BRIM': 'AB',
    ';TYPE:RAFT': 'AR'
}

def getLayerBlock(blocks: list[LayerBlock], lineNo: int) -> LayerBlock | None:
    _blocks = [layerBlock for layerBlock in blocks if (lineNo in layerBlock)]

    return _blocks[0] if _blocks else None

def main(
        paths: Annotated[list[str], Argument(
            file_okay = True,
            dir_okay = False,
            help = 'Desired paths to G-Code files. If none, all G-Code files in the current '
                'directory are used.\n'
                'If --thisdir is used, the paths are appended to the known G-Code file paths '
                'in the current directory.\n'
                'If --recursive is used, the paths are appended to the known G-Code file paths '
                'in the current directory and its\' subdirectories.'
        )] = None,
        thisdir: Annotated[bool, Option(
            '--all', '-a',
            help = 'Include all G-Code files in the current directory.',
            is_flag = True
        )] = False,
        recursive: Annotated[bool, Option(
            '--recursive', '-r',
            help = 'Include all G-Code files in the output directory and its\' subdirectories.',
            is_flag = True
        )] = False,
        to: Annotated[str, Option(
            '--to', '-o',
            file_okay = False,
            dir_okay = True,
            help = 'Directory to output files in. If none, the original files\' '
                'directories are used.'
        )] = '',
        prefix: Annotated[str, Option(
            '--prefix', '-p',
            help = 'Prefix for output file names. If none, no prefix will be used. '
                'Attention: either prefix or suffix has to be provided!'
        )] = '',
        suffix: Annotated[str, Option(
            '--suffix', '-s',
            help = 'Suffix for output file names. If none, no prefix will be used. '
                'Attention: either prefix or suffix has to be provided!'
        )] = '_V',
        overwrite: Annotated[bool, Option(
            '--overwrite', '-w',
            help = 'Overwrite the existing files in the output directory.',
            is_flag = True
        )] = False
        ) -> int:
    '''
    Modify the given G-Code files to verbose printing state.
    '''
    try:
        print('GCodeVerbose version', __version__)
        startTime = datetime.now()

        if (not paths):
            if (thisdir):
                print('Adding all G-Code files in the current directory:', Path.cwd())

                for path in glob(f'{Path.cwd()}/*.gcode'):
                    if (not path.split(pathsep)[-1].split('.')[0].startswith(prefix if prefix else '.') and
                        not path.split(pathsep)[-1].split('.')[0].endswith(suffix)):
                        paths.append(path)

            elif (recursive):
                print('Adding all G-Code files in the current directory and its subdirectiories:', Path.cwd())

                for path in glob(f'{Path.cwd()}/**/*.gcode'):
                    if (not path.split(pathsep)[-1].split('.')[0].startswith(prefix if prefix else '.') and
                        not path.split(pathsep)[-1].split('.')[0].endswith(suffix)):
                        paths.append(path)

            else:
                inputPath = input('Enter the full path to the G-Code file: ')

                if (inputPath):
                    paths.append(inputPath)
                else:
                    print('Adding all G-Code files in the current directory:', Path.cwd())

                    for path in glob(f'{Path.cwd()}/*.gcode'):
                        if (not path.split(pathsep)[-1].split('.')[0].startswith(prefix if prefix else '.') and
                            not path.split(pathsep)[-1].split('.')[0].endswith(suffix)):
                            paths.append(path)

        if (to):
            makedirs(to, exist_ok = True)

        for path_ix, path in enumerate(paths):
            print('\nChecking file no.', path_ix + 1, 'of', len(paths), 'at', path)

            pathParts = path.split(pathsep)
            origDir = pathsep.join(pathParts[:-1])

            fileName = pathParts[-1].split('.')[0]

            outputFileName = f'{to if to else origDir}/{prefix}{fileName}{suffix}.gcode'

            fileStart = datetime.now()

            try:
                with open(outputFileName, 'x') as outputFile:
                    outputFile.write('')
            except FileExistsError:
                if (overwrite):
                    with open(outputFileName, 'w') as outputFile:
                        outputFile.write('')
                else:
                    print('Output file', outputFileName, 'for file', path, 'already exists. Skipping.')
                    continue

            with open(path, 'r') as inputFile, open(outputFileName, 'a+') as outputFile:
                code = inputFile.read()

                if (not code.startswith(';FLAVOR:') or not 'G91 ;' in code):
                    # If not G-Code, don-t process
                    if (code.startswith(';FLAVOR:')):
                        print('FLAVOR definition not found')
                    if ('G91 ;' in code):
                        print('G91 operation is not defined')
                    print(f'{path} is not a valid G-Code file. Skipping.')
                    continue

                codeLines = code.splitlines()

                lcCmt = code.find(';LAYER_COUNT:')
                assert lcCmt > -1, 'Invalid G-Code: layer count is not defined'

                endCmt = code.find('G91')
                assert endCmt > -1, 'Invalid G-Code: end G91 operation is not defined'

                endCmtLine = -1

                for lineNo, line in enumerate(codeLines):
                    if (line.startswith('G91')):
                        endCmtLine = lineNo

                sequences: list[PrintSequence] = []

                layerCounts = [(ix, line) for ix, line in enumerate(codeLines) if line.startswith(';LAYER_COUNT:')]
                for ix, lco in enumerate(layerCounts):
                    sequences.append(
                        PrintSequence(
                        codeLines,
                        range(lco[0], layerCounts[ix + 1][0] if (ix + 1 < len(layerCounts)) else endCmtLine),
                        int(lco[1][13:])
                        ))

                firstSeqStart = sequences[0].seqRange.start
                totalPrintingCommands = len([line for line in codeLines if (line.startswith('G1'))])
                totalTypeSwitches = len([line for line in codeLines if (line.startswith(';TYPE:'))])
                print('Print sequences detected:', len(sequences))
                print('Total printing commands detected:', totalPrintingCommands)
                print('Total printing phase type switches detected:', totalTypeSwitches)
                print('Total to process:', totalPrintingCommands + totalTypeSwitches)

                outputFile.write('\n'.join(codeLines[:firstSeqStart]))

                fileCommandsAdded = 0

                for seq_ix, sequence in enumerate(sequences):
                    seqStart = datetime.now()

                    # Layers blocks are those groups of printing operations, which are done in one layer
                    layerBlocks = [
                        LayerBlock(
                            n + 1,
                            sequence.lines,
                            sequence.lines.index(f';LAYER:{n}'),
                            sequence.lines.index(f';LAYER:{n + 1}')
                            if (f';LAYER:{n + 1}' in sequence.code) else endCmtLine
                            )
                        for n in range(sequence.layersCount)]

                    print('Adding status commands for sequence', seq_ix + 1, 'of', len(sequences), 'with', f'{sequence.layersCount}', 'layers')

                    sequenceCommandsAdded = 0
                    commandsInThisLayerBlock = 0
                    currentLayerBlockId = -1
                    typeChar = ''
                    previousLayerBlockId = 0
                    previousPercentage = -1
                    previousTypeChar = 'PR'

                    with tqdm(total = sequence.totalCommands) as progressPatch:
                        for lineNo, codeLine in enumerate(sequence.lines):
                            layerBlock = getLayerBlock(layerBlocks, lineNo)
                            currentLayerBlockId = layerBlock.ix if layerBlock else -1
                            if (layerBlock):
                                if (codeLine.startswith('G1')):
                                    # This is a G1 command
                                    if (currentLayerBlockId == previousLayerBlockId):
                                        commandsInThisLayerBlock += 1
                                    else:
                                        commandsInThisLayerBlock = 1
                                        previousLayerBlockId = currentLayerBlockId
                                elif (codeLine.startswith(';TYPE:')):
                                    # This is a type changing line
                                    typeChar = printTypes.get(codeLine, 'PR')

                                percentage = round((commandsInThisLayerBlock / len(layerBlock)) * 100)
                                verbose = 'M117 S{} L{}/{} {}% {}'.format(seq_ix + 1, currentLayerBlockId, len(layerBlocks), percentage, typeChar)

                                outputFile.write(codeLine + '\n')

                                if (previousPercentage != percentage or previousTypeChar != typeChar):
                                    outputFile.write(verbose + '\n')
                                    previousPercentage = percentage
                                    previousTypeChar = typeChar

                                    sequenceCommandsAdded += 1
                                    fileCommandsAdded += 1

                                if (codeLine.startswith('G1') or codeLine.startswith(';TYPE:')):
                                    progressPatch.update()
                            else:
                                outputFile.write(codeLine + '\n')

                    seqEnd = datetime.now()
                    seqDelta = seqEnd - seqStart

                    print('Added a total of', sequenceCommandsAdded, 'commands to this sequence.')
                    print('Desired operations for sequence', seq_ix + 1, 'of', len(sequences), 'completed in', precisedelta(seqDelta, format = '%0.0f'))

                outputFile.write(code[endCmt:])

            fileEnd = datetime.now()
            fileDelta = fileEnd - fileStart

            print('Added a total of', fileCommandsAdded, 'commands to this file.')
            print('Desired operations for file', path_ix + 1, 'of', len(paths), 'at', path, 'completed in', precisedelta(fileDelta, format = '%0.0f'))
        else:
            print('No more files found to process.')

        if (paths):
            endTime = datetime.now()
            doneIn = endTime - startTime
            print('Desired operations on', len(paths), 'files completed in', precisedelta(doneIn, format = '%0.0f'))
            print('Thanks.')

        return 0

    except KeyboardInterrupt:
        print('\nAborted by user.')
        return 1

if (__name__ == '__main__'):
    run(main)
