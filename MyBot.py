"""
Welcome to my Halite-II bot!
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

# GAME START
game = hlt.Game("Sh4kE")
logging.info("Starting my Settler bot!")


def all_planets_owned():
    for planet in game.map.all_planets():
        if not planet.is_owned():
            return False
    return True


def move_to_planet(planet):
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


def attack_one_of_docked_ships(planet):
    for enemy_ship in planet.all_docked_ships():
        if enemy_ship not in ships_to_attack:
            ships_to_attack.append(enemy_ship)
            attack_entity(ship)
            break


def attack_entity(entity):
    navigate_command = ship.navigate(
        ship.closest_point_to(entity, 0),
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

    command_queue = []
    planets_moving_to = []
    ships_to_attack = []

    for ship in game_map.get_me().all_ships():
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue

        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        planets_by_distance = [entities_by_distance[distance][0] for distance in sorted(entities_by_distance)
                               if isinstance(entities_by_distance[distance][0], hlt.entity.Planet)]

        for planet in planets_by_distance:
            if all_planets_owned():
                not_my_planets_by_distance = [planet for planet in planets_by_distance
                                              if planet.owner != game.map.get_me()]

                if len(not_my_planets_by_distance) > 0:
                    attack_one_of_docked_ships(not_my_planets_by_distance[0])
                    break

            if planet.is_owned() or planet in planets_moving_to:
                # Otherwise skip this planet
                continue

            move_to_planet(planet)
            break

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    # TURN END
# GAME END

