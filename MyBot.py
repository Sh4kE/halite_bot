"""
Welcome to my Halite-II bot!
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

# GAME START
game = hlt.Game("Sh4kE")
game_round = 0

MAX_ROUNDS = 300
MAX_DOCKED_SHIPS_PER_PLANET = 6
SPEED_FACTOR = 0.5

logging.info("Starting my Settler bot!")


def all_planets_owned():
    for planet in game.map.all_planets():
        if not planet.is_owned():
            return False
    return True


def move_or_dock_to_planet(planet):
    # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
    if ship.can_dock(planet):
        command_queue.append(ship.dock(planet))
    else:
        navigate_command = ship.navigate(
            ship.closest_point_to(planet),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False,
            ignore_planets=False
        )
        if navigate_command:
            planets_moving_to.append(planet)
            command_queue.append(navigate_command)


def attack_one_of_docked_ships_of_nearest_planet():
    not_my_planets_by_distance = [planet for planet in planets_by_distance
                                  if planet.owner != game.map.get_me()]
    if not_my_planets_by_distance:
        attack_entity(not_my_planets_by_distance[0].all_docked_ships()[0])


def attack_entity(entity):
    navigate_command = ship.navigate(
        entity,
        game_map,
        speed=int(hlt.constants.MAX_SPEED),
        ignore_ships=False,
        ignore_planets=False
    )
    if navigate_command:
        command_queue.append(navigate_command)


while True:
    # TURN START
    # Update the map for the new turn and get the latest version
    game_map = game.update_map()
    game_round += 1

    current_maximum_docked_ships = round(game_round/MAX_ROUNDS * MAX_DOCKED_SHIPS_PER_PLANET * SPEED_FACTOR)

    command_queue = []
    planets_moving_to = []

    for ship in game_map.get_me().all_ships():
        if ship.docking_status == ship.DockingStatus.UNDOCKED:

            entities_by_distance = game_map.nearby_entities_by_distance(ship)
            planets_by_distance = [entities_by_distance[distance][0] for distance in sorted(entities_by_distance)
                                   if isinstance(entities_by_distance[distance][0], hlt.entity.Planet)]

            if all_planets_owned():
                attack_one_of_docked_ships_of_nearest_planet()
            else:
                target_found = False
                for planet in planets_by_distance:
                    if not planet.is_owned() or \
                            (len(planet.all_docked_ships()) <= current_maximum_docked_ships and planet.is_owned_by(game_map.get_me())):

                        if game_round <= 12 and planet in planets_moving_to:
                            continue
                        move_or_dock_to_planet(planet)
                        target_found = True
                        break
                if not target_found:
                    attack_one_of_docked_ships_of_nearest_planet()

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END

