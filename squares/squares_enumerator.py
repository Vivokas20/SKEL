import contextlib
import logging
import signal
import time
from multiprocessing import Queue

import rpy2
import rpy2.robjects as robjects

from .dsl.interpreter import SquaresInterpreter
from . import util, results
from .config import Config
from .decider import LinesDecider
from .tyrell.decider import Example
from .tyrell.enumerator.bitenum import BitEnumerator
from .tyrell.synthesizer import Synthesizer

logger = logging.getLogger('squares')

robjects.r('''
sink("/dev/null")
options(warn=-1)
suppressMessages(library(tidyr))
suppressMessages(library(stringr))
suppressMessages(library(readr))
suppressMessages(library(lubridate))
suppressMessages(library(dplyr))
suppressMessages(library(dbplyr))''')

def do_not_print(msg):
    pass


rpy2.rinterface_lib.callbacks.consolewrite_print = do_not_print
rpy2.rinterface_lib.callbacks.consolewrite_warnerror = do_not_print


def main(args, specification, id: int, conf: Config, queue: Queue):

    util.seed(conf.seed)
    util.store_config(conf)
    util.set_program_queue(queue)

    if args.verbose >= 1:
        logger.setLevel('INFO')
    if args.verbose >= 2:
        logger.setLevel('DEBUG')
    if args.verbose >= 3:
        logging.getLogger('tyrell').setLevel('DEBUG')

    results.specification = specification

    spec = specification.generate_dsl()

    decider = LinesDecider(interpreter=SquaresInterpreter(specification),
                           examples=[Example(input=specification.tables, output='expected_output')],
                           )

    logger.info('Building synthesizer...')
    loc = specification.min_loc
    # loc = max(specification.min_loc, conf.minimum_loc)

    while loc <= specification.max_loc:
        start = time.time()
        enumerator = BitEnumerator(spec, specification, loc=loc)
        t = time.time() - start
        logger.debug(f'Enumeration time: {t}')
        results.init_time += t

        synthesizer = Synthesizer(enumerator=enumerator, decider=decider)

        # print(util.get_config().top_programs)
        start = time.time()
        prog, attempts = synthesizer.synthesize()
        t = time.time() - start
        logger.debug(f'Synthesis time: {t}')

        if prog:
            logger.info(f'Solution found: {prog}')
            queue.put((util.Message.SOLUTION, id, prog, loc, True))
            queue.put((util.Message.DONE, None, None, None, None))
            return

        else:
            logger.info('Increasing the number of lines of code to %d.', loc + 1)
            loc = loc + 1

    results.exceeded_max_loc = True
    logger.error('Process %d reached the maximum number of lines (%d). Giving up...', id, specification.max_loc)