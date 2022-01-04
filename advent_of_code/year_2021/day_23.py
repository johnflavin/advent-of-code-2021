#!/usr/bin/env python
"""
A bunch of amphpods in different rooms. They want to be sorted.
Take different amounts of energy to move.

Part 1:
What is the least energy required to organize the amphipods?

Here's what I'm thinking. This is a pathfinding problem, and I can use
A* to find the solution. But it won't be finding the path of a
single amphipod to its destination. We will find a path through a
state space where:
* Each node is a state representing the positions of all amphipods
* The edges between nodes represent a move an amphipod can make

The tricky part here is the number of states. There are a huge number
of potential states. I'm not sure the exact number, but
it's something like (15 8) (choose 8 locations for the 8 amphipods) times
4! (from the different ways to place an A, B, C, or D in each space).
Which is on the order of a million or so? Many of them would be inaccessible
from the starting position so we could certainly prune them, which would
limit the size of the state space somewhat. But I just don't
know if it would be worth it to pregenerate all the states vs create them when
we get to them.

I'll come back to that question in a bit.

We need a few things for any search algorithm:
* Nodes/States: the positions of all the amphipods
* Edges/Moves: Moves that amphipods can make to take them from one state to another
* Weights: The cost of each move
* Start: A particular state that we are given to start from
* End: A particular state that we are trying to reach

If we're doing A* we also need a heuristic: A way to determine
how close a given state is to the end state. This is used to determine
which states to give priority to when checking for new states.
Typically on a grid the heuristic would be a distance. But we'll have to get
a bit more creative to create a heuristic in our state space. I don't
know the best way. But I'm thinking I could maybe use the distance of each amphipod
from its goal position, with an additional penality if one is in the correct state but
blocking one that is in an incorrect goal space. And maybe the cost of the moves
should also be factored in?

I'm looking at this guide to A*:
https://www.redblobgames.com/pathfinding/a-star/introduction.html
The A* algorithm is guaranteed to find the best path if the heuristic is "admissable"
(https://en.wikipedia.org/wiki/Admissible_heuristic) i.e. the heuristic to reach
the goal from state n is always less than or equal to the true cost to reach the
goal from state n.
That makes me think the heuristic should be the cost to move all the amphipods
into the correct spots, ignoring any interactions. Like "how many spaces are you away
from your goal space, and what does it cost to move there".
As if they can move through each other. That will always be less than or equal
to the true cost, since they will definitely need to move at least that many spaces.

"""

import itertools
from abc import ABC
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import InitVar, asdict, dataclass, field
from enum import Enum
from functools import cache
from queue import PriorityQueue
from typing import Optional

from .day_05 import sgn

EXAMPLE = """\
#############
#...........#
###B#C#B#D###
  #A#D#C#A#
  #########"""
PART_ONE_EXAMPLE_RESULT = 12521
PART_TWO_EXAMPLE_RESULT = 44169
PART_ONE_RESULT = 19046
PART_TWO_RESULT = None


# @dataclass(frozen=True)
# class Position:
#     x: int
#     y: int

#     def in_hallway(self):
#         return self.y == 0

#     def __lt__(self, other):
#         return (self.x, self.y) < (other.x, other.y)


# def build_board(extended: bool = False) -> nx.Graph:
#     g = nx.Graph()
#     # hallway is 11 units long
#     g.add_edges_from((Position(x, 0), Position(x + 1, 0)) for x in range(10))
#     # add each room
#     for room_x in range(2, 10, 2):
#         g.add_edges_from(
#             (
#                 (Position(room_x, 0), Position(room_x, 1)),
#                 (Position(room_x, 1), Position(room_x, 2)),
#             )
#         )
#         if extended:
#             g.add_edges_from(
#                 (
#                     (Position(room_x, 2), Position(room_x, 3)),
#                     (Position(room_x, 3), Position(room_x, 4)),
#                 )
#             )
#     return g


# BOARD = build_board()


# class AmphipodType(Enum):
#     def __new__(cls, *args, **kwargs) -> AmphipodType:
#         obj = object.__new__(cls)
#         obj._value_ = args[0]
#         return obj

#     def __init__(self, _, movement_cost: int, destination_x: int):
#         self.movement_cost = movement_cost
#         self.destination_x = destination_x

#     Amber = "A", 1, 2
#     Bronze = "B", 10, 4
#     Copper = "C", 100, 6
#     Desert = "D", 1000, 8


# @dataclass(frozen=True)
# class AmphipodState:
#     type: AmphipodType
#     position: Position
#     at_rest: bool = False

#     def at_destination(self):
#         return (
#             not self.position.in_hallway()
#             and self.position.x == self.type.destination_x
#         )

#     def __lt__(self, other):
#         return self.position < other.position


# def find_minimal_cost_to_solution(
#     initial_state: BoardState, board: nx.Graph = BOARD
# ) -> int:
#     """Dijkstra path-finding algorithm"""
#     frontier: list[tuple[float, BoardState]] = []
#     heapq.heappush(frontier, (0, initial_state))

#     came_from = {}
#     cost_so_far = {}
#     came_from[initial_state] = None
#     cost_so_far[initial_state] = 0

#     while len(frontier) > 0:
#         _, current = heapq.heappop(frontier)

#         if current.is_goal_state():
#             return cost_so_far[current]

#         for next_state, next_cost in generate_next_states(current, board):
#             new_cost = cost_so_far[current] + next_cost
#             if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
#                 cost_so_far[next_state] = new_cost
#                 priority = new_cost + heuristic(next_state)
#                 heapq.heappush(frontier, (priority, next_state))
#                 came_from[next_state] = current


# def generate_next_states(
#     state: BoardState, board: nx.Graph
# ) -> Iterator[tuple[BoardState, int]]:
#     """Generate legal successor states and their costs"""
#     room_depth = len(state.amphipods) // 4

#     def generate_legal_moves(pod: AmphipodState) -> Iterator[tuple[AmphipodState, int]]:
#         # If a pod is in its home room, and no pods of a different type are below it,
#         # move to the lowest available position.
#         if (
#             pod.position.x == pod.type.destination_x
#             and not pod.position.in_hallway()
#             and all(
#                 p.type is p
#                 for p in state.amphipods
#                 if p.position.x == pod.position.x and p.position.y > pod.position.y
#             )
#         ):
#             dest_y = pod.position.y + 1
#             while dest_y <= room_depth and not state.is_position_occupied(
#                 replace(pod.position, y=dest_y)
#             ):
#                 dest_y += 1
#             dest_y -= 1
#             if dest_y > pod.position.y:
#                 yield replace(
#                     pod, position=replace(pod.position, y=dest_y), at_rest=True
#                 ), dest_y - pod.position.y
#             return

#         # If a pod is stopped in the hallway, it can only move if it can reach its
#         # destination, and then it must move toward its destination or into its room.
#         if pod.position.in_hallway() and can_reach_destination(pod):
#             dest_y = 1
#             while dest_y <= room_depth and not state.is_position_occupied(
#                 Position(pod.type.destination_x, dest_y)
#             ):
#                 dest_y += 1
#             dest_y -= 1
#             yield replace(
#                 pod, position=Position(pod.type.destination_x, dest_y), at_rest=True
#             ), abs(pod.position.x - pod.type.destination_x) + dest_y
#             return
#         if pod.position.in_hallway() and pod is not state.last_moved:
#             return

#         # If a pod is in a room and all positions above it are clear, move out of the room.
#         if not pod.position.in_hallway() and all(
#             not state.is_position_occupied(replace(pod.position, y=y))
#             for y in range(0, pod.position.y)
#         ):
#             yield replace(pod, position=replace(pod.position, y=0)), pod.position.y
#             return

#         for next_pos in board.neighbors(pod.position):
#             # All legal moves out of the hallway have been covered above.
#             if pod.position.in_hallway() and not next_pos.in_hallway():
#                 continue
#             if state.is_position_occupied(next_pos):
#                 continue
#             yield replace(pod, position=next_pos), 1

#     def can_reach_destination(pod: AmphipodState) -> bool:
#         here = pod.position.x
#         there = pod.type.destination_x
#         clear_range = range(there, here, sign(here - there))

#         if any(state.is_position_occupied(Position(x, 0)) for x in clear_range):
#             return False
#         if state.is_position_occupied(Position(there, 1)):
#             return False
#         if any(
#             p.type is not pod.type and p.position.x == there for p in state.amphipods
#         ):
#             return False
#         return True

#     # If the last amphipod to move is just outside a room, it must continue moving
#     if (
#         state.last_moved is not None
#         and state.last_moved.position.in_hallway()
#         and state.last_moved.position.x in (2, 4, 6, 8)
#     ):
#         for next_position, move_count in generate_legal_moves(state.last_moved):
#             yield (
#                 move_pod(state, state.last_moved, next_position),
#                 state.last_moved.type.movement_cost * move_count,
#             )
#         return

#     # Otherwise, loop through legal successor states
#     for pod in state.amphipods:
#         if not pod.at_rest:
#             for next_position, move_count in generate_legal_moves(pod):
#                 yield move_pod(
#                     state, pod, next_position
#                 ), pod.type.movement_cost * move_count


# def move_pod(
#     state: BoardState, pod: AmphipodState, new_pod: AmphipodState
# ) -> BoardState:
#     amphipods = frozenset(new_pod if a is pod else a for a in state.amphipods)
#     return BoardState(amphipods, new_pod)


# def heuristic(state: BoardState) -> int:
#     """Minimum cost for all pods to move directly 'home', without impediment"""
#     result = 0
#     room_depth = len(state.amphipods) // 4
#     count_need_to_go_home_by_type = defaultdict(int)
#     for pod in state.amphipods:
#         if pod.position.in_hallway():
#             result += pod.type.movement_cost * abs(
#                 pod.position.x - pod.type.destination_x
#             )
#             count_need_to_go_home_by_type[pod.type] += 1
#         # If pod is in the wrong room, it needs to move to the hallway, over, and back
#         # down into its room.
#         elif pod.position.x != pod.type.destination_x:
#             result += pod.type.movement_cost * (
#                 pod.position.y + abs(pod.position.x - pod.type.destination_x)
#             )
#             count_need_to_go_home_by_type[pod.type] += 1
#         # If there are pods of a different type "below" this pod, it will have to move
#         # to the hallway, out of the way, and back into the room.
#         # But this is more expensive to compute than it's worth.
#         # elif any(p.position.x == pod.position.x and p.position.y > pod.position.y for p in state.amphipods):
#         #     result += pod.type.movement_cost * (pod.position.y + 2)
#         #     count_need_to_go_home_by_type[pod.type] += 1
#         # Otherwise, pod just needs to move to the bottom of its room
#         else:
#             result += pod.type.movement_cost * (room_depth - pod.position.y)

#     for type, count in count_need_to_go_home_by_type.items():
#         result += type.movement_cost * count * (count + 1) // 2

#     return result


@dataclass(frozen=True, order=True)
class Apod:
    name: str
    move_cost: int
    destination_x: int


class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Apods(OrderedEnum):
    A = Apod("A", 1, 2)
    B = Apod("B", 10, 4)
    C = Apod("C", 100, 6)
    D = Apod("D", 1000, 8)


@dataclass(frozen=True, order=True)
class Location:
    y: int
    x: int

    def __post_init__(self):
        if self.y == 0:
            assert self.x in {0, 1, 3, 5, 7, 9, 10}
        else:
            assert self.x in {2, 4, 6, 8}

    @property
    def in_hallway(self):
        return self.y == 0

    def distance(self, other: "Location") -> int:
        if self.y == 0 or other.y == 0 or self.x == other.x:
            # Move in x then down tunnel
            return abs(self.x - other.x) + abs(self.y - other.y)
        else:
            # Have to move up to hallway then down again
            return self.y + abs(self.x - other.x) + other.y


@dataclass(frozen=True, order=True)
class ApodState:
    apod_enum: Apods
    location: Location

    @property
    def apod(self) -> Apod:
        return self.apod_enum.value

    def move(self, new_location: Location) -> "ApodState":
        return ApodState(apod_enum=self.apod_enum, location=new_location)

    @property
    def at_destination(self) -> bool:
        return (
            not self.location.in_hallway and self.location.x == self.apod.destination_x
        )

    @property
    def destination_x(self) -> int:
        return self.apod.destination_x

    def move_cost(self) -> int:
        return self.apod.move_cost

    @property
    def in_hallway(self) -> bool:
        return self.location.in_hallway

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.apod.name}, {self.location})"

    def __repr__(self) -> str:
        return self.__str__()

    # def __lt__(self, other: "ApodState"):
    #     return self.location < other.location


@cache
def build_location_graph(
    tunnel_depth: int,
) -> dict[Location, list[Location]]:
    graph = {
        # Hallway left left
        Location(x=0, y=0): [
            Location(x=1, y=0),
        ],
        # Hallway left right
        Location(x=1, y=0): [
            Location(x=0, y=0),
            Location(x=2, y=1),
            Location(x=3, y=0),
        ],
        # Hallway AB
        Location(y=0, x=3): [
            Location(y=0, x=1),
            Location(y=1, x=2),
            Location(y=1, x=4),
            Location(y=0, x=5),
        ],
        # Hallway BC
        Location(y=0, x=5): [
            Location(y=0, x=3),
            Location(y=1, x=4),
            Location(y=1, x=6),
            Location(y=0, x=7),
        ],
        # Hallway CD
        Location(y=0, x=7): [
            Location(y=0, x=5),
            Location(y=1, x=6),
            Location(y=1, x=8),
            Location(y=0, x=9),
        ],
        # Hallway right left
        Location(y=0, x=9): [
            Location(y=0, x=7),
            Location(y=1, x=8),
            Location(y=0, x=10),
        ],
        # Hallway right right
        Location(y=0, x=10): [
            Location(y=0, x=9),
        ],
    }

    # Add tunnels
    for apod in Apods:
        tunnel_x = apod.value.destination_x
        # tunnel top
        graph[Location(y=1, x=tunnel_x)] = [
            Location(x=tunnel_x - 1, y=0),
            Location(x=tunnel_x + 1, y=0),
            Location(x=tunnel_x, y=2),
        ]

        # tunnel middle
        for depth in range(2, tunnel_depth):
            graph[Location(x=tunnel_x, y=depth)] = [
                Location(x=tunnel_x, y=depth + 1),
                Location(x=tunnel_x, y=depth - 1),
            ]

        # tunnel bottom
        graph[Location(x=tunnel_x, y=tunnel_depth)] = [
            Location(x=tunnel_x, y=tunnel_depth - 1)
        ]
    # print(graph)
    return graph


def calculate_distances(tunnel_depth: int) -> dict[tuple[Location, Location], int]:
    graph = build_location_graph(tunnel_depth)
    distances: dict[tuple[Location, Location], int] = {}
    frontier: set[tuple[Location, Location, int]] = set()

    # prime with zeroth and first order
    for loc0, loc1s in graph.items():
        distances[(loc0, loc0)] = 0

        for loc1 in loc1s:
            distance = loc0.distance(loc1)
            distances[(loc0, loc1)] = distance
            frontier.add((loc0, loc1, distance))

    # Add all other orders by traversing graph
    while frontier:
        loc0, loc1, dist01 = frontier.pop()

        for loc2 in graph[loc1]:
            new_pair = (loc0, loc2)
            new_distance = dist01 + loc1.distance(loc2)
            if new_pair not in distances:
                frontier.add((loc0, loc2, new_distance))
                distances[new_pair] = new_distance
            elif distances[new_pair] > new_distance:
                frontier.discard((loc0, loc2, distances[new_pair]))
                frontier.add((loc0, loc2, new_distance))
                distances[new_pair] = new_distance

    # for locs, dist in distances.items():
    #     print(locs, dist)
    return distances


@cache
def all_locations(tunnel_depth: int) -> list[Location]:
    return sorted(build_location_graph(tunnel_depth).keys())


@dataclass
class GraphInfo:
    tunnel_depth: int
    graph: dict[Location, list[Location]] = field(init=False)
    distance: dict[tuple[Location, Location], int] = field(init=False)
    # end_board_state: BoardState = field(init=False)

    def __post_init__(self):
        self.graph = build_location_graph(self.tunnel_depth)
        self.distance = calculate_distances(self.tunnel_depth)

    def direct_move_cost(self, apod_state: ApodState, destination: Location) -> int:
        return (
            self.distance[(apod_state.location, destination)]
            * apod_state.apod.move_cost
        )


# @dataclass(frozen=True)
# class BoardInfo:
#     tunnel_depth: InitVar[int]
#     hallway_locations: tuple[Location] = field(init=False)
#     tunnel_locations: frozendict[Apod, list[Location]] = field(init=False)

#     def __post_init__(self, tunnel_depth: int):
#         hallway_locations = (
#             Location(0, 0),
#             *[Location(x, 0) for x in range(1, 10, 2)],
#             Location(0, 10),
#         )
#         tunnel_locations = {
#             apod.value: [
#                 Location(apod.value.destination_x, depth)
#                 for depth in range(-1, tunnel_depth - 1, -1)
#             ]
#             for apod in Apods
#         }
#         object.__setattr__(self, "hallway_locations", hallway_locations)
#         object.__setattr__(self, "tunnel_locations", tunnel_locations)


def pretty_print_template(tunnel_depth: int) -> str:
    top = "#############"
    hallway_template = "#{}{}.{}.{}.{}.{}{}#"
    tunnel_top_template = "###{}#{}#{}#{}###"
    tunnel_depths_templates = ["  #{}#{}#{}#{}#"] * (tunnel_depth - 1)
    bottom = "  #########"
    return "\n".join(
        [
            top,
            hallway_template,
            tunnel_top_template,
            *tunnel_depths_templates,
            bottom,
        ]
    )


@dataclass(frozen=True, order=True)
class BoardState:
    apod_states: frozenset[ApodState]
    # last_moved: Optional[ApodState] = field(default=None)

    # def __post_init__(self):
    #     object.__setattr__(
    #         self,
    #         "occupied_locations",
    #         frozenset(apod_state.location for apod_state in self.apod_states),
    #     )
    #     object.__setattr__(
    #         self, "tunnel_depth", len(self.occupied_locations) // len(Apods)
    #     )

    def is_occupied(self, location: Location) -> bool:
        return location in self.occupied_locations

    @property
    @cache
    def tunnel_depth(self) -> int:
        return len(self.occupied_locations) // len(Apods)

    @property
    @cache
    def occupied_locations(self) -> set[Location]:
        return {apod_state.location for apod_state in self.apod_states}

    @property
    @cache
    def apods_by_location(self) -> dict[Location, Apod]:
        return {apod_state.location: apod_state.apod for apod_state in self.apod_states}

    @cache
    def apod_at_location(self, location: Location) -> "Apod | None":
        return self.apods_by_location.get(location)

    @cache
    def apods_in_tunnel(self, tunnel_x: int) -> set[Apod]:
        return {
            apod_state.apod
            for apod_state in self.apod_states
            if apod_state.location.x == tunnel_x
        }

    @property
    @cache
    def non_terminal_apod_states(self) -> set[ApodState]:
        return {apod_state for apod_state in self.apod_states if True}

    def is_occupied_with_correct_type(
        self, location: Location, correct_apod: Apod
    ) -> bool:
        return self.is_occupied(location) and self.apod_at_location == correct_apod

    @cache
    def next_end_location(self, apod_state: ApodState) -> "Location | None":
        for depth in range(self.tunnel_depth, 0, -1):
            bottom = Location(y=depth, x=apod_state.apod.destination_x)
            if not self.is_occupied_with_correct_type(bottom, apod_state.apod):
                return bottom
        else:
            return None

    # def __lt__(self, other: "BoardState"):
    #     return sorted(self.apod_states) < sorted(other.apod_states)

    def pretty_print(self) -> str:

        sorted_apods = sorted(self.apod_states, key=lambda s: s.location)
        # print(sorted_apods)
        all_locs = all_locations(self.tunnel_depth)
        next_apod = sorted_apods.pop(0)
        loc_strs = ["."] * len(all_locs)
        for idx, loc in enumerate(all_locs):
            if loc == next_apod.location:
                loc_strs[idx] = next_apod.apod.name
                try:
                    next_apod = sorted_apods.pop(0)
                except IndexError:
                    break
            # print(loc, loc_strs[-1])

        template = pretty_print_template(self.tunnel_depth)
        return template.format(*loc_strs)

    # num_apods_per_type: int
    # current_state_dict: dict[Apod, tuple[Location, ...]]

    # def __init__(self, locations: Mapping[Apod, Iterable[Location]]):
    #     self.current_state_dict = {
    #         apod: tuple(sorted(locations[apod])) for apod in Apod
    #     }
    #     self.occupied_locations = set(
    #         itertools.chain(*self.current_state_dict.values())
    #     )

    # def apod_locs(self, apod: Apod) -> tuple[Location, ...]:
    #     return self.current_state_dict[apod]

    def neighbors(self, graph: GraphInfo) -> Iterable[tuple["BoardState", int]]:
        """Generate legal successor states and their costs"""

        # def generate_legal_moves(
        #     apod_state: ApodState,
        # ) -> Iterable[Location]:
        #     # Three possibilities:
        #     # 1. We're already in our tunnel
        #     # 1a. But we're trapping a wrong apod underneath
        #     # 1b. Nothing underneath but correct apods or empty spaces
        #     # 2. We're in a wrong tunnel
        #     # # If a pod is in its home room and no pods of a different type are below it,
        #     # # move to the lowest available position.
        #     # if apod_state.at_destination and all(
        #     #     other.apod is apod_state.apod
        #     #     for other in self.apod_states
        #     #     if other.location.x == apod_state.location.x
        #     #     and other.location.y > apod_state.location.y
        #     # ):
        #     #     for depth in range(self.tunnel_depth, apod_state.location.y, -1):
        #     #         depth_loc = Location(x=apod_state.location.x, y=depth)
        #     #         if self.is_occupied(depth_loc):
        #     #             continue
        #     #         yield depth_loc
        #     #         return

        #     # Can the pod reach its destination?
        #     # If so, and if there are no wrong apods there,
        #     # go to the first unoccupied space.
        #     if can_reach_destination_tunnel(apod_state):
        #         lowest_unoccupied: Optional[Location] = None
        #         for depth in range(self.tunnel_depth, apod_state.location.y, -1):
        #             depth_loc = Location(x=apod_state.destination_x, y=depth)
        #             if self.is_occupied(depth_loc):
        #                 if self.apods_by_location[depth_loc] != apod_state.apod:
        #                     # There's a different apod here. Can't move
        #                     break
        #                 else:
        #                     # occupied, but by a correct apod
        #                     continue
        #             # Not occupied!
        #             lowest_unoccupied = lowest_unoccupied or depth_loc
        #         else:
        #             # we didn't break which means all the
        #             ...

        #     # If a pod is in a room and all positions above it are clear,
        #     # move out of the room.
        #     if (
        #         not apod_state.in_hallway
        #         and not apod_state.location.y == 1
        #         and all(
        #             not self.is_occupied(Location(x=apod_state.location.x, y=y))
        #             for y in range(1, apod_state.location.y)
        #         )
        #     ):
        #         yield Location(x=apod_state.location.x, y=1)
        #         return

        #     for next_loc in graph.graph[apod_state.location]:
        #         if self.is_occupied(next_loc):
        #             continue
        #         if (
        #             apod_state.in_hallway
        #             and next_loc.y > 0
        #             and next_loc.x != apod_state.destination_x
        #         ):
        #             # Cannot move from hallway into a tunnel that isn't our destination
        #             continue
        #         yield next_loc

        # def can_reach_destination_tunnel(pod: ApodState) -> bool:
        #     # Do a mini graph traversal here to see if we can find the destination
        #     frontier: set[Location] = set(graph.graph[pod.location])
        #     have_seen: set[Location] = {pod.location}
        #     while frontier:
        #         loc = frontier.pop()

        #         if self.is_occupied(loc):
        #             # Can't move here
        #             continue
        #         if loc.x == pod.destination_x:
        #             # Hit the destination
        #             return True

        #         # We can move here, but it isn't our destination.
        #         # Mark that we've seen this one
        #         have_seen.add(loc)

        #         # Add its next steps to the frontier.
        #         for next_loc in graph.graph[loc]:
        #             if next_loc not in have_seen:
        #                 frontier.add(next_loc)

        #     return False

        def generate_moves(pod: ApodState) -> Iterable[Location]:
            # Do a mini graph traversal with just this one apod
            frontier: set[Location] = set(graph.graph[pod.location])
            have_seen: set[Location] = {pod.location}
            valid_destinations: set[Location] = set()
            while frontier:
                loc = frontier.pop()

                # can't move into occupied spaces
                if self.is_occupied(loc):
                    continue

                # Can we move to this space? Through it?
                if loc.y == 0:
                    # We can always move in the hallway
                    valid_destinations.add(loc)

                    # Mark that we've seen this one
                    have_seen.add(loc)

                    # Add its next steps to the frontier.
                    for next_loc in graph.graph[loc]:
                        if next_loc not in have_seen:
                            frontier.add(next_loc)

                elif loc.x != pod.destination_x:  # Not our tunnel
                    # Are we already in the tunnel? And is this move up?
                    if loc.x != pod.location.x or loc.y > pod.location.y:
                        # This is either entering the wrong tunnel or moving down
                        # when we should be moving up. Invalid.
                        continue

                    # We have no reason to end a turn here, so it isn't a
                    # valid destination. But we might have reason to move through here.
                    # We will continue on and check other positions from here.
                    have_seen.add(loc)

                    # Add its next steps to the frontier.
                    for next_loc in graph.graph[loc]:
                        if next_loc not in have_seen:
                            frontier.add(next_loc)
                else:  # Yes our tunnel
                    # We can move in our tunnel if it isn't occupied by any
                    # incorrect apods.
                    # And if so, we will move to the lowest unoccupied space.
                    lowest_unoccupied: "Location | None" = None
                    for depth in range(self.tunnel_depth, 0, -1):
                        tunnel_loc = Location(y=depth, x=loc.x)
                        apod_in_tunnel_loc = self.apod_at_location(tunnel_loc)
                        if apod_in_tunnel_loc is None:
                            # unoccupied
                            if lowest_unoccupied is None:
                                lowest_unoccupied = tunnel_loc
                        elif apod_in_tunnel_loc != pod.apod:
                            # occupied, incorrect apod
                            break
                        else:
                            # occupied, correct apod
                            pass
                    else:
                        # We didn't find any incorrect apods
                        # That means we can move somewhere in the tunnel
                        assert lowest_unoccupied is not None
                        valid_destinations.add(lowest_unoccupied)

                        # Mark that we've seen this one
                        have_seen.add(loc)

                        # Add its next steps to the frontier, but only if they aren't
                        # also in this tunnel (because we know we would just
                        # do the same thing with them and find the same lowest position)
                        for next_loc in graph.graph[loc]:
                            if (
                                next_loc not in have_seen
                                and next_loc.x != pod.destination_x
                            ):
                                frontier.add(next_loc)

            return valid_destinations

        # loop through legal successor states
        for apod_state in self.non_terminal_apod_states:
            other_states = {other for other in self.apod_states if other != apod_state}
            for next_loc in generate_moves(apod_state):
                # print(next_loc)
                cost = graph.direct_move_cost(apod_state, next_loc)
                new_states = frozenset({apod_state.move(next_loc), *other_states})
                yield self.__class__(new_states), cost

    # def neighbors(self, graph: GraphInfo) -> "Iterable[tuple[BoardState, int]]":
    #     # print("neighbors")
    #     # Try to move each apod
    #     for apod_state in self.apod_states:
    #         states_minus_apod = set(self.apod_states)
    #         states_minus_apod.discard(apod_state)
    #         # print(f"Moving {apod_state}")
    #         # print(f"Others {states_minus_apod}")

    #         # Find possible next steps
    #         for next_loc in graph.graph[apod_state.location]:
    #             # Can I move here?

    #             if next_loc in self.occupied_locations:
    #                 # occupied
    #                 continue
    #             # into my tunnel
    #             elif next_loc.x == apod_state.destination_x:
    #                 # is the tunnel clear of other apods?
    #                 apods_in_tunnel = set(self.apods_in_tunnel(next_loc.x))
    #                 if apods_in_tunnel and apods_in_tunnel != {apod_state.apod}:
    #                     # There are other apods in the tunnel. Can't go in yet.
    #                     continue
    #             # in another tunnel
    #             elif next_loc.x == apod_state.location.x:
    #                 # Am I moving out of the tunnel?
    #                 if next_loc.y >= apod_state.location.y:
    #                     # No, moving deeper in
    #                     continue

    #             # I think this state should be ok

    #             # print(f"{apod_state.location=} {next_loc=}")
    #             cost = graph.direct_move_cost(apod_state, next_loc)
    #             # print(f"{cost=}")

    #             new_states = frozenset({apod_state.move(next_loc), *states_minus_apod})
    #             # print(f"{new_states=}")
    #             yield self.__class__(new_states), cost


def end_state(tunnel_depth: int) -> BoardState:
    return BoardState(
        frozenset(
            ApodState(
                location=Location(x=apod.value.destination_x, y=depth), apod_enum=apod
            )
            for apod in Apods
            for depth in range(1, tunnel_depth + 1)
        )
    )


@dataclass(frozen=True, order=True)
class PrioritizableState:
    priority: float
    state: BoardState = field(compare=False)

    def neighbors(self, graph: GraphInfo) -> Iterable[tuple[BoardState, int]]:
        return self.state.neighbors(graph)


def heuristic(state: BoardState, graph: GraphInfo) -> int:
    """Minimum cost for all pods to move directly 'home', without impediment"""
    result = 0
    # count_need_to_go_home_by_type: dict[Apod, int] = defaultdict(int)
    for apod_state in state.apod_states:
        is_at_destination = apod_state.at_destination
        if is_at_destination:
            result += 0
        else:
            next_unoccupied_end = state.next_end_location(apod_state)
            assert next_unoccupied_end is not None
            result += (
                graph.distance[(apod_state.location, next_unoccupied_end)]
                * apod_state.apod.move_cost
            )
            # count_need_to_go_home_by_type[apod_state.apod] += int(
            #     not apod_state.at_destination
            # )

    # for type, count in count_need_to_go_home_by_type.items():
    #     result += type.move_cost * count * (count + 1) // 2

    return result


# def apod_heuristic(
#     apod: Apods,
#     s: BoardState,
#     graph: GraphInfo,
# ) -> int:
#     """Cost to move the amphipods of type apod from their locations to the end,
#     (mostly) ignoring all other amphipods"""
#     locs = s.apod_locs(apod)
#     all_occupied_locs = s.occupied_locations
#     non_apod_locs = all_occupied_locs - set(locs)
#     end_locs = graph.end_locs[apod]
#     end_locs_s = set(end_locs)
#     num_end_locs = len(end_locs)
#     non_apod_in_end_locs = [end_loc in non_apod_locs for end_loc in end_locs]
#     empty_end_locs = [end_loc not in all_occupied_locs for end_loc in end_locs]
#     empty_or_non_apod_end_locs = [
#         end_loc
#         for end_loc, na, empty in zip(end_locs, non_apod_in_end_locs, empty_end_locs)
#         if na or empty
#     ]

#     estimated_costs = [0] * len(locs)
#     if locs == end_locs:
#         # Fast path if everything is in the right place
#         return 0
#     for loc_idx, loc in enumerate(locs):
#         if loc in end_locs_s:
#             # This one is in an end loc of the right type
#             end_loc_idx = end_locs.index(loc)

#             # Are there any incorrect apods trapped below this one?
#             if any(non_apod_in_end_locs[:end_loc_idx]):
#                 # Need to move this apod out of the way and back.
#                 # num_end_locs - loc_idx to move up + 2 for the move out to the hall
#                 unblock_move_cost = 2 + num_end_locs - loc_idx

#                 # We double it because we need to move out then back
#                 estimated_costs[loc_idx] = 2 * unblock_move_cost
#             # Are there any empties below this?
#             elif any(empty_end_locs[:end_loc_idx]):
#                 # Simply move down
#                 estimated_costs[loc_idx] = sum(empty_end_locs[:end_loc_idx])
#             else:
#                 # No non-apods and no empties = everything below is correct
#                 # No move required
#                 estimated_costs[loc_idx] = 0
#         else:
#             # Ordinary move
#             # We average the cost to move to any end loc
#             estimated_costs[loc_idx] = sum(
#                 graph.move_cost(apod, locs[loc_idx], end_loc)
#                 for end_loc in empty_or_non_apod_end_locs
#             ) // len(empty_or_non_apod_end_locs)

#     return sum(estimated_costs)


def solve(
    start: BoardState, end: BoardState, graph: GraphInfo
) -> tuple[int, list[BoardState]]:
    frontier: PriorityQueue[PrioritizableState] = PriorityQueue()
    frontier.put(PrioritizableState(0, start))
    came_from: dict[BoardState, BoardState] = dict()
    cost_so_far: dict[BoardState, int] = dict()
    cost_so_far[start] = 0

    # debug_total_num_steps = 10
    # debug_num_steps = 0

    while not frontier.empty():
        current = frontier.get()
        # print(current)
        # if debug_num_steps == debug_total_num_steps:
        #     print("debug stop")
        #     end = current.state
        #     break

        if current.state == end:
            # print("at end")
            break

        for next_state, next_state_move_cost in current.neighbors(graph):
            new_cost = cost_so_far[current.state] + next_state_move_cost
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                came_from[next_state] = current.state
                priority = new_cost + heuristic(next_state, graph)
                frontier.put(PrioritizableState(priority, next_state))

        # debug_num_steps += 1

    # unwind path
    path = []
    current_state = end
    while current_state in came_from:
        path.append(current_state)
        current_state = came_from[current_state]
    path.append(start)

    return cost_so_far.get(end, -1), path[::-1]


def parse_lines(
    lines: Iterable[str], tunnel_depth: int
) -> tuple[BoardState, BoardState, GraphInfo]:
    lines = [line.strip() for line in lines if line]

    apod_chars = set("ABCD")
    apod_states: list[ApodState] = []
    for depth, line in enumerate(lines[2:], start=1):
        if line.startswith("###"):
            line = line[2:-2]
        for x, c in enumerate(line, start=1):
            if c in apod_chars:
                try:
                    loc = Location(x=x, y=depth)
                except AssertionError:
                    print(f"{line=} {depth=} {x=} {c=}")
                    raise
                apod_states.append(ApodState(location=loc, apod_enum=Apods[c]))

    # print(apod_states)
    start = BoardState(frozenset(apod_states))
    # print(start)
    graph_info = GraphInfo(tunnel_depth)

    return start, end_state(tunnel_depth), graph_info


def solution(lines: Iterable[str], tunnel_depth: int) -> int:
    start, end, graph = parse_lines(lines, tunnel_depth)

    cost, path = solve(start, end, graph)
    for state in path:
        print(state.pretty_print())
    return cost


def part_one(lines: Iterable[str]) -> int:
    return solution(lines, 2)


def part_two(lines: Iterable[str]) -> int:
    lines = [line for line in lines if line]
    lines = lines[:3] + ["  #D#C#B#A#", "  #D#B#A#C#"] + lines[3:]
    return solution(lines, 4)
