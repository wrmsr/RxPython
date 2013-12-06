from .defer import Defer
from .empty import Empty
from .fromEvent import FromEvent
from .generate import Generate
from .never import Never
from .range import Range
from .repeat import Repeat
from .returnOp import Return
from .throw import Throw
from .toObservable import ToObservable
from .using import Using

from rx.disposable import Disposable
from rx.exceptions import FutureCanceledException
from rx.observable import AnonymousObservable, Observable
from rx.scheduler import Scheduler
from rx.subject import AsyncSubject

import collections

def truePredicate(c): return True

def flattedSequence(items):
  for item in items:
    isIterable = isinstance(item, collections.Iterable)
    isString = isinstance(item, str)

    if isinstance(item, Observable):
      yield item
    elif isIterable and not isString:
      for element in item:
        yield element
    else:
      yield item


####################
#    Creation      #
####################

def create(subscribe):
  assert callable(subscribe)

  def wrapper(observer):
    a = subscribe(observer)

    if isinstance(a, Disposable):
      return a
    elif callable(a):
      return Disposable.create(a)
    else:
      return Disposable.empty()

  return AnonymousObservable(wrapper)
Observable.create = staticmethod(create)

def defer(observableFactory):
  assert callable(observableFactory)

  return Defer(observableFactory)
Observable.defer = staticmethod(defer)

def empty(scheduler=Scheduler.constantTimeOperations):
  assert isinstance(scheduler, Scheduler)

  return Empty(scheduler)
Observable.empty = staticmethod(empty)

def generate(initialState, condition, iterate, resultSelector, scheduler=Scheduler.iteration):
  assert callable(condition)
  assert callable(iterate)
  assert callable(resultSelector)
  assert isinstance(scheduler, Scheduler)

  return Generate(initialState, condition, iterate, resultSelector, None, None, scheduler)
Observable.generate = staticmethod(generate)

def never():
  return Never()
Observable.never = staticmethod(never)

def rangeOp(start, count, scheduler=Scheduler.iteration):
  assert isinstance(scheduler, Scheduler)

  return Range(start, count, scheduler)
Observable.range = staticmethod(rangeOp)

def repeatValue(value, count=None, scheduler=Scheduler.iteration):
  assert isinstance(scheduler, Scheduler)

  return Repeat(value, count, scheduler)
Observable.repeatValue = staticmethod(repeatValue)

def returnOp(value, scheduler=Scheduler.constantTimeOperations):
  assert isinstance(scheduler, Scheduler)

  return Return(value, scheduler)
Observable.returnValue = staticmethod(returnOp)

def start(action, scheduler=Scheduler.default):
  assert isinstance(scheduler, Scheduler)

  subject = AsyncSubject()

  def scheduled():
    try:
      subject.onNext(action())
      subject.onCompleted()
    except Exception as e:
      subject.onError(e)

    return Disposable.empty()

  scheduler.schedule(scheduled)

  return subject.asObservable()
Observable.start = staticmethod(start)

def throw(exception, scheduler=Scheduler.constantTimeOperations):
  assert isinstance(scheduler, Scheduler)

  return Throw(exception, scheduler)
Observable.throw = staticmethod(throw)

def using(resourceFactory, observableFactory):
  assert callable(resourceFactory)
  assert callable(observableFactory)

  return Using(resourceFactory, observableFactory)
Observable.using = staticmethod(using)

####################
#      From***     #
####################

def fromFuture(future):
  subject = AsyncSubject()

  def callback(f):
    if f.cancelled():
      subject.onError(FutureCanceledException())
    elif f.exception() != None:
      subject.onError(f.exception())
    else:
      subject.onNext(f.result())
      subject.onCompleted()

  if future.done():
    callback(future)
  else:
    future.add_done_callback(callback)

  return subject
Observable.fromFuture = staticmethod(fromFuture)

def fromEvent(addHandler, removeHandler, scheduler=Scheduler.default):
  assert callable(addHandler)
  assert callable(removeHandler)
  assert isinstance(scheduler, Scheduler)

  return FromEvent(addHandler, removeHandler, scheduler)
Observable.fromEvent = staticmethod(fromEvent)

def fromIterable(iterable, scheduler=Scheduler.default):
  assert isinstance(iterable, collections.Iterable)
  assert isinstance(scheduler, Scheduler)

  return ToObservable(iterable, scheduler)
Observable.fromIterable = staticmethod(fromIterable)
