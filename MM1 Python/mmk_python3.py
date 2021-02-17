"""
The task is to simulate an M/M/k system with a single queue.
Complete the skeleton code and produce results for three experiments.
The study is mainly to show various results of a queue against its ro parameter.
ro is defined as the ratio of arrival rate vs service rate.
For the sake of comparison, while plotting results from simulation, also produce the analytical results.
"""

import heapq
import random
from random import expovariate
import matplotlib.pyplot as plt
import math


# Parameters
class Params:
    def __init__(self, lambd, mu, k, num_delays_required):
        self.lambd = lambd  # interarrival rate
        self.mu = mu  # service rate
        self.k = k
        self.num_delays_required = num_delays_required
    # Note lambd and mu are not mean value, they are rates i.e. (1/mean)

# Write more functions if required


# States and statistical counters
class States:
    def __init__(self):
        # States
        self.queue = []
        # Declare other states variables that might be needed
        self.QUEUE_LIMIT = 100
        self.server_status = 0
        self.total_of_delay = 0.0
        self.num_custs_delayed = 0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.time_last_event = 0.0
        # Statistics
        self.util = 0.0
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0

    def update(self, sim, event):

        time_since_last_event = sim.simclock - self.time_last_event
        self.time_last_event = sim.simclock
        self.area_num_in_q += len(sim.states.queue) * time_since_last_event
        # self.avgQlength = self.area_num_in_q/sim.simclock
        self.area_server_status += sim.states.server_status * time_since_last_event
        # self.util = self.area_server_status/sim.simclock
        # self.util = sim.params.lambd/sim.params.mu

    def finish(self, sim):
        # Complete this function
        None

    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        self.avgQlength = self.area_num_in_q/sim.simclock
        self.avgQdelay = sim.states.total_of_delay/sim.states.num_custs_delayed
        self.util = self.area_server_status/sim.simclock
        print('MMk Results: lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        print('MMk Total customer served: %d' % (self.served))
        print('MMk Average queue length: %lf' % (self.avgQlength))
        print('MMk Average customer delay in queue: %lf' % (self.avgQdelay))
        print('MMk Time-average server utility: %lf' % (self.util))
        print('MMk server utility: %lf' % (sim.params.lambd/sim.params.mu))

    def getResults(self, sim):
        return (self.avgQlength, self.avgQdelay, self.util)

# Write more functions if required


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None
        # self.arrivalTime = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType


class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim):
        # Complete this function
        arrivalEvent = ArrivalEvent(self.eventTime, sim)
        sim.scheduleEvent(arrivalEvent)


class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        # Complete this function
        print('Exit event')
        # exit(1)


class ArrivalEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim
        self.delay = 0.0
    def process(self, sim):
        time_arrival_event = expovariate(sim.params.lambd)
        arrivalTime = sim.simclock + time_arrival_event
        arrivalEvent = ArrivalEvent(arrivalTime, sim)
        sim.scheduleEvent(arrivalEvent)
        if(sim.states.server_status == 1):
            print('arrival -- server busy')
            # heapq.heappush(self.eventQ, (event.eventTime, event))
            # heapq.heappush(sim.states.queue, (arrivalEvent.eventTime, arrivalEvent))
            print('arrival time ', self.eventTime)
            heapq.heappush(sim.states.queue, (self.eventTime, sim))
            if(len(sim.states.queue) > sim.states.QUEUE_LIMIT):
                print('overflow at the array arrivalTime at ', sim.simclock)
                exit(2)
            print('arrival -- queue length ', len(sim.states.queue), ' arrival event ', self.eventTime)
            departureEvent = DepartureEvent(sim.simclock, sim, self.eventTime)
            sim.scheduleEvent(departureEvent)
        else:
            print('arrival -- server idle at ', sim.simclock, self.eventTime)
            sim.states.total_of_delay += self.delay
            sim.states.num_custs_delayed += 1
            sim.states.server_status = 1
            sim.states.served += 1
            print('server states ', sim.states.server_status)
            departureEvent = DepartureEvent(sim.simclock+expovariate(sim.params.mu), sim, self.eventTime)
            sim.scheduleEvent(departureEvent)
        # sim.scheduleEvent(arrivalEvent)



class DepartureEvent(Event):
    def __init__(self, eventTime, sim, arrivalTime):
        self.eventTime = eventTime
        self.eventType = 'DEPART'
        self.sim = sim
        self.delay = 0.0
        self.arrivalTime = arrivalTime
    def process(self, sim):
        # Complete this function
        print('departure event with event time ', self.eventTime, ' arrival time ', self.arrivalTime)
        if(len(sim.states.queue) == 0):
            sim.states.server_status = 0
            print('queue is empty, server idle ', sim.simclock)
            exit_event_time = 1.0 * math.exp(30)
            exitEvent = ExitEvent(exit_event_time, sim)
            sim.scheduleEvent(exitEvent)
        else:
            self.arrivalTime, event = heapq.heappop(sim.states.queue)  ## queue theke service niye chole jacce
            print('depart -- queue length ', len(sim.states.queue), self.arrivalTime)
            self.delay = sim.simclock - self.eventTime
            sim.states.total_of_delay += self.delay
            sim.states.num_custs_delayed += 1
            sim.states.served += 1
            print('delay in server ', self.delay, ' with arrival time ', sim.simclock, self.eventTime, self.arrivalTime)
            # time_next_event = expovariate(sim.params.mu)
            # departureEvent = DepartureEvent(sim.simclock+time_next_event, sim, self.arrivalTime)
            # sim.scheduleEvent(departureEvent)
            if(sim.states.num_custs_delayed == sim.params.num_delays_required):
                print('exit event')
                sim.scheduleEvent(ExitEvent(sim.simclock, sim))


class Simulator:
    def __init__(self, seed):
        self.eventQ = []
        self.simclock = 0
        self.seed = seed
        self.params = None
        self.states = None
        self.arrivalTime = None
        self.departureTime = None

    def initialize(self):
        self.simclock = 0
        self.scheduleEvent(StartEvent(0, self))

    def configure(self, params, states):
        self.params = params
        self.states = states

    def now(self):
        return self.simclock

    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))

    def run(self):
        random.seed(self.seed)
        self.initialize()

        while len(self.eventQ) > 0:
            time, event = heapq.heappop(self.eventQ)

            if event.eventType == 'DEPART':
                print(event.eventTime, 'EVENT', event, event.arrivalTime)
            else:
                print(event.eventTime, 'Event', event, '...')
            self.simclock = time

            if event.eventType == 'EXIT':
                break
            elif event.eventType == 'START':
                time_next_event = random.expovariate(self.params.lambd)
                arrivalEvent = ArrivalEvent(self.simclock+time_next_event, self)
                self.scheduleEvent(arrivalEvent)  ## new arrival event push
            else:
                # self.simclock = event.eventTime
                event.process(self) ## arrival and depart
            
            if self.states != None:
                self.states.update(self, event)
            # print(event.eventTime, 'Event', event)
            # self.simclock = event.eventTime
            # event.process(self)
        self.states.finish(self)

    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)


def experiment1():
    seed = 101
    sim = Simulator(seed)
    sim.configure(Params(5.0 / 60, 8.0 / 60, 1, 5), States())
    sim.run()
    sim.printResults()


def experiment2():
    seed = 110
    mu = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for ro in ratios:
        sim = Simulator(seed)
        sim.configure(Params(mu * ro, mu, 1, 10), States())
        sim.run()

        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(ratios, avglength)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(ratios, avgdelay)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(ratios, util)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Util')

    plt.show()


def experiment3():
    # Similar to experiment2 but for different values of k; 1, 2, 3, 4
    # Generate the same plots
    # Fix lambd = (5.0/60), mu = (8.0/60) and change value of k
    None


def main():
    experiment1()
    # experiment2()
    # experiment3()


if __name__ == "__main__":
    main()
