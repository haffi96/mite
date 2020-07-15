import asyncio
import functools
import logging
from itertools import count

import ipdb

from .context import Context
from .utils import spec_import

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=None)
def spec_import_cached(journey_spec):
    return spec_import(journey_spec)


class RunnerControllerTransportExample:  # pragma: nocover
    async def hello(self):
        """Returns:
            runner_id
            test_name
            config_list - k, v pairs
            """
        pass

    async def request_work(self, runner_id, current_work, completed_data_ids, max_work):
        """\
        Takes:
            runner_id
            current_work - dict of scenario_id, current volume
            completed_data_ids - list of scenario_id, scenario_data_id pairs
            max_work - may be None to indicate no limit
        Returns:
            work - list of (scenario_id, scenario_data_id,
                            journey_spec, args) - args and scenario_data_id may be None together
            config_list - k, v pairs
            stop
        """
        pass

    async def bye(self, runner_id):
        """\
        Takes:
            runner_id
        """
        pass


class Runner:
    def __init__(
        self,
        transport,
        msg_sender,
        loop_wait_max=0.5,
        max_work=None,
        loop=None,
        debug=False,
    ):
        self._transport = transport
        self._msg_sender = msg_sender
        self._work = {}
        self._stop = False
        self._loop_wait_max = loop_wait_max
        self._max_work = max_work
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._debug = debug

    def _inc_work(self, id):
        if id in self._work:
            self._work[id] += 1
        else:
            self._work[id] = 1

    def _dec_work(self, id):
        self._work[id] -= 1
        if self._work[id] == 0:
            del self._work[id]

    async def run(self):
        # FIXME: this design is fundamentally bogus.  We oscillate between
        # doing actual work and communicating with the controller.  In a fully
        # async world, the communication with the controller would be just
        # another async task.  This requires careful thought though (as Jordan
        # pointed out) -- we want to be sure that we're neither overloading
        # the runner with undone tasks nor running out of tasks and letting
        # the runner starve.  So this is very much a future change.
        context_id_gen = count(1)
        config = {}
        runner_id, test_name, config_list = await self._transport.hello()
        config.update(config_list)
        logger.debug("Entering run loop")

        async def do_work(scenario_id, scenario_data_id, journey_spec, args):
            id_data = {
                'test': test_name,
                'runner_id': runner_id,
                'journey': journey_spec,
                'context_id': next(context_id_gen),
                'scenario_id': scenario_id,
                'scenario_data_id': scenario_data_id,
            }
            context = Context(
                self._msg_sender, config, id_data=id_data, debug=self._debug
            )
            r = await self._execute(
                context, scenario_id, scenario_data_id, journey_spec, args
            )
            return r

        pending = []
        completed_data_ids = []
        while (not self._stop) or self._work:
            work, config_list, self._stop = await self._transport.request_work(
                runner_id,
                self._work,
                completed_data_ids,
                self._max_work if not self._stop else 0,
            )
            completed_data_ids = []
            config._update(config_list)
            for scenario_id, *_ in work:
                self._inc_work(scenario_id)
            # FIXME: why is pending sometimes an empty set?
            pending = list(pending) + [asyncio.create_task(do_work(*job)) for job in work]
            if not pending:
                assert not self._work
                if self._stop:
                    logger.info("breaking for stop")
                    break
                else:
                    # TODO: why does this happen?  it's bad
                    # logger.info("starved for work!!!")
                    continue
            # TODO: restore timeout, maybe handle exceptions?
            done, pending = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED
            )
            for scenario_id, scenario_data_id in map(lambda x: x.result(), done):
                self._dec_work(scenario_id)
                if scenario_data_id is not None:
                    completed_data_ids.append((scenario_id, scenario_data_id))

        # One last time, to send the controller the last batch of our work
        work, config_list, self._stop = await self._transport.request_work(
            runner_id,
            self._work,
            completed_data_ids,
            self._max_work if not self._stop else 0,
        )

        assert len(pending) == 0  # For debugging purposes TODO move to a unit test
        assert len(self._work) == 0
        assert len(work) == 0
        assert self._stop
        await self._transport.bye(runner_id)

    async def _execute(self, context, scenario_id, scenario_data_id, journey_spec, args):
        logger.debug(
            'Runner._execute starting scenario_id=%r scenario_data_id=%r journey_spec=%r args=%r',
            scenario_id,
            scenario_data_id,
            journey_spec,
            args,
        )
        journey = spec_import_cached(journey_spec)
        try:
            async with context.transaction('__root__'):
                if args is None:
                    await journey(context)
                else:
                    await journey(context, *args)
        except Exception as e:
            if not getattr(e, "handled", False):
                if self._debug:
                    ipdb.set_trace()
                    raise
        return scenario_id, scenario_data_id
