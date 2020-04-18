# This file is a part of Dramatiq.
#
# Copyright (C) 2017,2018 CLEARTYPE SRL <bogdan@cleartype.io>
#
# Dramatiq is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# Dramatiq is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import traceback

from ..common import compute_backoff
from ..errors import Retry
from ..logging import get_logger
from .middleware import Middleware

#: The default minimum amount of backoff to apply to retried tasks.
DEFAULT_MIN_BACKOFF = 15000

#: The default maximum amount of backoff to apply to retried tasks.
#: Must be less than the max amount of time tasks can be delayed by.
DEFAULT_MAX_BACKOFF = 86400000 * 7


class Retries(Middleware):
    """Middleware that automatically retries failed tasks with
    exponential backoff.

    If you need to intentionally retry an actor and you don't want the
    exception to get logged, then consider raising the
    :class:`Retry<dramatiq.Retry>` exception.

    Parameters:
      max_retries(int): The maximum number of times tasks can be retried.
      min_backoff(int): The minimum amount of backoff milliseconds to
        apply to retried tasks.  Defaults to 15 seconds.
      max_backoff(int): The maximum amount of backoff milliseconds to
        apply to retried tasks.  Defaults to 7 days.
      retry_when(Callable[[int, Exception], bool]): An optional
        predicate that can be used to programmatically determine
        whether a task should be retried or not.  This takes
        precedence over `max_retries` when set.
    """

    def __init__(self, *, max_retries=20, min_backoff=None, max_backoff=None, retry_when=None):
        self.logger = get_logger(__name__, type(self))
        self.max_retries = max_retries
        self.min_backoff = min_backoff or DEFAULT_MIN_BACKOFF
        self.max_backoff = max_backoff or DEFAULT_MAX_BACKOFF
        self.retry_when = retry_when

    @property
    def actor_options(self):
        return {
            "max_retries",
            "min_backoff",
            "max_backoff",
            "retry_when",
        }

    def after_process_message(self, broker, message, *, result=None, exception=None):
        if exception is None:
            return

        actor = broker.get_actor(message.actor_name)
        retries = message.options.setdefault("retries", 0)
        max_retries = message.options.get("max_retries") or actor.options.get("max_retries", self.max_retries)
        retry_when = actor.options.get("retry_when", self.retry_when)
        if retry_when is not None and not retry_when(retries, exception) or \
           retry_when is None and max_retries is not None and retries >= max_retries:
            self.logger.warning("Retries exceeded for message %r.", message.message_id)
            message.fail()
            return

        message.options["retries"] += 1
        message.options["traceback"] = traceback.format_exc(limit=30)

        if isinstance(exception, Retry) and exception.delay is not None:
            backoff = exception.delay
        else:
            min_backoff = message.options.get("min_backoff") or actor.options.get("min_backoff", self.min_backoff)
            max_backoff = message.options.get("max_backoff") or actor.options.get("max_backoff", self.max_backoff)
            max_backoff = min(max_backoff, DEFAULT_MAX_BACKOFF)
            _, backoff = compute_backoff(retries, factor=min_backoff, max_backoff=max_backoff)

        self.logger.info("Retrying message %r in %d milliseconds.", message.message_id, backoff)
        broker.enqueue(message, delay=backoff)
