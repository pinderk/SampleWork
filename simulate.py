# CS121: Polling places
#
# Kyle Pinder
#
# Main file for polling place simulation

import sys
import util
import random
import queue
import click


### YOUR Voter, VoterGenerator, and Precinct classes GO HERE.

class Voter(object):

    def __init__(self, arrival_time, voting_duration):
        '''
        Takes a specified arrival time and voting duration to represent a voter.

        Inputs:
            arrival_time: (float) The arrival time of the voter.
            voting_duration: (float) How long the voter takes to vote.
        '''

        self.arrival_time = arrival_time
        self.voting_duration = voting_duration
        self.start_time = None
        self.departure_time = None

    def get_start_time(self):
        return self._start_time

    def set_start_time(self, start_time):
        self._start_time = start_time

    def get_departure_time(self):
        return self._departure_time

    def set_departure_time(self, departure_time):
        self._departure_time = departure_time


class VoterGenerator(object):

    def __init__(self, arrival_rate, voting_duration_rate, num_voters):
        '''
        Generates a specific number of voters from a specified arrival rate and 
        voting duration rate.

        Inputs:
            arrival_rate: (float) Lambda for gap.
            voting_duration_rate: (float) Lambda for voting duration.
            num_voters: (int) The number of voters.
        '''

        self.num_voters = num_voters
        self.arrival_rate = arrival_rate
        self.voting_duration_rate = voting_duration_rate
        self.current_time = 0
        self.voters_generated = 0

    def next_voter(self):
        '''
        Returns a voter with an arrival time and voting duration.
        '''

        if self.voters_generated >= self.num_voters:
            return None
        (gap, voting_duration) = util.gen_poisson_voter_parameters\
        (self.arrival_rate, self.voting_duration_rate)
        self.current_time += gap
        voter = Voter(self.current_time, voting_duration)
        self.voters_generated += 1
        return voter


def test_VoterGenerator(file_name):
    '''
    Tests the VoterGenerator class.
    '''

    (precincts, seed) = util.load_precincts(file_name)
    for p in precincts:
        random.seed(seed)
        num_voters = p["num_voters"]
        arrival_rate = p["voter_distribution"]["arrival_rate"]
        voting_duration_rate = p["voter_distribution"]["voting_duration_rate"]
        v_list = []
        vg = VoterGenerator(arrival_rate, voting_duration_rate, num_voters)
        for v in range(num_voters):
            voter = vg.next_voter()
            if voter is not None:
                v_list.append(voter)

    return util.print_voters(v_list)


     
class Precinct(object):

    def __init__(self, precinct, num_booths):
        '''
        Generates a precinct with a specified number of voting booths.

        Inputs:
            precinct: A dictionary with values.
            num_booths: (int) The number of voting booths in a precinct.
        '''

        self.num_booths = num_booths
        self.precinct_name = precinct["name"] 
        self.minutes_open = precinct["hours_open"] * 60
        self.q1 = queue.PriorityQueue(num_booths)

    def add_voter(self, voter):
        '''
        Adds a voter to the priority queue of voting booths.
        '''

        self.q1.put(voter.departure_time)

    def remove_voter(self):
        '''
        Removes a voter from the priority queue of voting booths.
        '''

        next_departure = self.q1.get()
        return next_departure

    def size_check(self):
        '''
        Returns the number of people currently in the voting booths.
        '''

        return self.q1.qsize()

    def simulate_precinct(self, voter): 
        '''
        Simulates a precinct by entering voters one at a time.
        '''

        if voter is None:
            return False
        
        if voter.arrival_time <= self.minutes_open:
            if self.size_check() < self.num_booths:
                voter.start_time = voter.arrival_time
            else:
                departing_voter_time = self.remove_voter()
                if voter.arrival_time > departing_voter_time:
                    voter.start_time = voter.arrival_time
                else:
                    voter.start_time = departing_voter_time
            voter.departure_time = voter.start_time + voter.voting_duration
            self.add_voter(voter)
            return True

        else:
            return False        


def simulate_election_day(precincts, seed):
    '''
    Simulates an election given a list of precincts and a random seed.

    Inputs:
        precincts: A list of precinct dictionaries.
        seed: (int) Generates the same random numbers when implemented.

    Returns:
        A dictionary containing the arrival time, voting duration, start time,
        and departure time of the voters that voted.
    '''

    voter_dict = {}

    for precinct in precincts:
        random.seed(seed)
        num_booths = precinct["num_booths"]
        pc = Precinct(precinct, num_booths)
        num_voters = precinct["num_voters"]
        arrival_rate = precinct["voter_distribution"]["arrival_rate"]
        voting_duration_rate = precinct["voter_distribution"]\
        ["voting_duration_rate"]
        v_list = []
        vg = VoterGenerator(arrival_rate, voting_duration_rate, num_voters)
        for v in range(num_voters):
            voter = vg.next_voter()
            if pc.simulate_precinct(voter):
                v_list.append(voter)
            else:
                break
        
        voter_dict[pc.precinct_name] = v_list

    return voter_dict


def find_avg_wait_time(precinct, num_booths, ntrials, initial_seed=0):
    '''
    Computes the average wait time in a precinct with a given number of booths over
    a specified number of trials with incremented seeds.

    Inputs:
        precinct: A precinct dictionary.
        num_booths: (int) The specified number of booths in the precinct.
        ntrials: (int) The number of times the precinct is simulated.
        initial_seed: The seed number that is incremented after every trial.

    Returns:
        The average wait time in the precinct.
    '''
   
    average_wait_time_list = []
    seed = initial_seed
    num_voters = precinct["num_voters"]
    arrival_rate = precinct["voter_distribution"]["arrival_rate"]
    voting_duration_rate = precinct["voter_distribution"]\
    ["voting_duration_rate"]

    for n in range(ntrials):
        random.seed(seed)
        total_wait_time = 0
        total_voters = 0
        avg_wait_time = 0
        vg = VoterGenerator(arrival_rate, voting_duration_rate, num_voters)
        pc = Precinct(precinct, num_booths)
        for n in range(num_voters):
            voter = vg.next_voter()
            if pc.simulate_precinct(voter):
                total_voters += 1
                total_wait_time += (voter.start_time - voter.arrival_time)
            else:
                break
        avg_wait_time = total_wait_time / total_voters
        average_wait_time_list.append(avg_wait_time)
        seed += 1

    average_wait_time_list.sort()

    return average_wait_time_list[ntrials//2]


def find_number_of_booths(precinct, target_wait_time, max_num_booths, ntrials, seed=0):
    '''
    Computes the optimal number of booths in a precinct in order to reach a 
    target wait time.

    Inputs:
        precinct: A precinct dictionary.
        target_wait_time: (float) The desired wait time in the precinct.
        max_num_booths: (int) The maximum number of booths allowed in the precinct.
        ntrials: (int) The number of times the precinct is simulated.
        seed: (int) Generates the same random numbers when implemented.
    '''

    num_booths = 0
    booth_counter = 0
    waiting_time = None

    for r in range(max_num_booths):  
        booth_counter += 1    
        check_wait_time = find_avg_wait_time\
        (precinct, booth_counter, ntrials, seed)
        if check_wait_time < target_wait_time:
            num_booths = booth_counter
            waiting_time = check_wait_time
            return (num_booths, waiting_time)

    return (num_booths, waiting_time)


@click.command(name="simulate")
@click.argument('precincts_file', type=click.Path(exists=True))
@click.option('--max-num-booths', type=int)
@click.option('--target-wait-time', type=float)
@click.option('--print-voters', is_flag=True)
def cmd(precincts_file, max_num_booths, target_wait_time, print_voters):
    precincts, seed = util.load_precincts(precincts_file)

    if target_wait_time is None:
        voters = simulate_election_day(precincts, seed)
        print()
        if print_voters:
            for p in voters:
                print("PRECINCT '{}'".format(p))
                util.print_voters(voters[p])
                print()
        else:
            for p in precincts:
                pname = p["name"]
                if pname not in voters:
                    print("ERROR: Precinct file specified a '{}' precinct".format(pname))
                    print("       But simulate_election_day returned no such precinct")
                    print()
                    return -1
                pvoters = voters[pname]
                if len(pvoters) == 0:
                    print("Precinct '{}': No voters voted.".format(pname))
                else:
                    pl = "s" if len(pvoters) > 1 else ""
                    closing = p["hours_open"]*60.
                    last_depart = pvoters[-1].departure_time
                    avg_wt = sum([v.start_time - v.arrival_time for v in pvoters]) / len(pvoters)
                    print("PRECINCT '{}'".format(pname))
                    print("- {} voter{} voted.".format(len(pvoters), pl))
                    msg = "- Polls closed at {} and last voter departed at {:.2f}."
                    print(msg.format(closing, last_depart))
                    print("- Avg wait time: {:.2f}".format(avg_wt))
                    print()
    else:
        precinct = precincts[0]

        if max_num_booths is None:
            max_num_booths = precinct["num_voters"]

        nb, avg_wt = find_number_of_booths(precinct, target_wait_time, max_num_booths, 20, seed)

        if nb is 0:
            msg = "The target wait time ({:.2f}) is infeasible"
            msg += " in precint '{}' with {} or less booths"
            print(msg.format(target_wait_time, precinct["name"], max_num_booths))
        else:
            msg = "Precinct '{}' can achieve average waiting time"
            msg += " of {:.2f} with {} booths"
            print(msg.format(precinct["name"], avg_wt, nb))


if __name__ == "__main__":
    cmd()
